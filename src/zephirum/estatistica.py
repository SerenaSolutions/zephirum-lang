# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Serena Quantum Solutions
"""Intervalo exato para proporcao, sem dependencia externa.

A regra de decisao continua usando a cota de Hoeffding, que vale para qualquer
distribuicao e e conservadora. Este modulo existe para relatar o intervalo exato
de Clopper-Pearson ao lado do veredito, com cobertura nominal, sem alterar a
decisao. Cota e intervalo respondem perguntas diferentes: a cota limita o pior
caso, o intervalo descreve a amostra.
"""
from __future__ import annotations

import math

__all__ = ["intervalo_exato", "beta_incompleta_regularizada"]

_FPMIN = 1e-300
_EPS = 3e-14
_MAXIT = 300


def _fracao_continuada(a: float, b: float, x: float) -> float:
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    if abs(d) < _FPMIN:
        d = _FPMIN
    d = 1.0 / d
    h = d
    for m in range(1, _MAXIT + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < _FPMIN:
            d = _FPMIN
        c = 1.0 + aa / c
        if abs(c) < _FPMIN:
            c = _FPMIN
        d = 1.0 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < _FPMIN:
            d = _FPMIN
        c = 1.0 + aa / c
        if abs(c) < _FPMIN:
            c = _FPMIN
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < _EPS:
            break
    return h


def beta_incompleta_regularizada(a: float, b: float, x: float) -> float:
    """I_x(a, b), funcao beta incompleta regularizada."""
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    log_beta = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
    frente = math.exp(log_beta + a * math.log(x) + b * math.log1p(-x))
    if x < (a + 1.0) / (a + b + 2.0):
        return frente * _fracao_continuada(a, b, x) / a
    return 1.0 - frente * _fracao_continuada(b, a, 1.0 - x) / b


def _quantil(p: float, a: float, b: float) -> float:
    lo, hi = 0.0, 1.0
    for _ in range(200):
        meio = (lo + hi) / 2.0
        if beta_incompleta_regularizada(a, b, meio) < p:
            lo = meio
        else:
            hi = meio
    return (lo + hi) / 2.0


def intervalo_exato(sucessos: int, shots: int, alpha: float = 0.05) -> tuple[float, float]:
    """Intervalo exato de Clopper-Pearson com cobertura 1 - alpha.

    Nao entra na decisao: e relato. Se shots for invalido, levanta ValueError.
    """
    if shots <= 0:
        raise ValueError("shots deve ser positivo")
    if not 0 <= sucessos <= shots:
        raise ValueError("sucessos devem estar entre 0 e shots")
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha deve estar entre 0 e 1")
    low = 0.0 if sucessos == 0 else _quantil(alpha / 2.0, sucessos, shots - sucessos + 1)
    high = 1.0 if sucessos == shots else _quantil(1.0 - alpha / 2.0, sucessos + 1, shots - sucessos)
    return (low, high)

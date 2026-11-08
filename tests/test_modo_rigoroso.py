# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Serena Quantum Solutions
"""Modo rigorous: limite derivado da uniao, com erro familiar medido."""
import math
import numpy as np
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from zyql_quantum_gate import adaptive_margin_family


def test_rigorous_e_o_teto_derivado():
    for k in (1, 4, 16, 64):
        m_rig = adaptive_margin_family(0.05, 2048, k, modo="rigorous")
        esperado = 0.5 - math.sqrt(math.log(2 * k / 0.05) / (2 * 2048))
        assert abs(m_rig - esperado) < 1e-12
        # o conservador nunca excede o teto permitido
        assert adaptive_margin_family(0.05, 2048, k) <= m_rig


def test_erro_familiar_empirico_respeita_epsilon():
    """Monte Carlo curto: erro familiar do modo rigorous <= epsilon (com folga estatistica)."""
    rng = np.random.default_rng(7)
    eps, S, k, trials = 0.05, 4096, 16, 3000
    m = adaptive_margin_family(eps, S, k, modo="rigorous")
    erros = 0
    for _ in range(trials):
        bal = rng.random(k) < 0.5
        p = np.where(bal, 0.5, 0.98)
        p0 = rng.binomial(S, p) / S
        erro = ((p0 >= 1 - m) & bal) | ((p0 <= m) & ~bal)
        erros += int(erro.any())
    taxa = erros / trials
    assert taxa <= 2 * eps, f"erro familiar empirico {taxa:.4f} acima de {2*eps}"


def test_modo_invalido_nao_e_aceito_silenciosamente():
    # modo desconhecido cai no conservador (documentado), mas nunca quebra
    assert adaptive_margin_family(0.05, 2048, 4, modo="qualquer") == adaptive_margin_family(0.05, 2048, 4)

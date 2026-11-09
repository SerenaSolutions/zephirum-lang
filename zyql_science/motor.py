#!/usr/bin/env python3
"""ZYQL Science — motor de decisão aplicado a todas as áreas.

A mesma régua para qualquer ciência: decisão com erro declarado, recusa honesta
quando a evidência não basta, e recibo assinado para cada veredito.

Cinco estados: 1, 0, REFUSED, INCONCLUSIVE, ERROR. Nunca um sexto estado implícito.
"""
from __future__ import annotations
import hashlib, json, math
from dataclasses import dataclass, field

DELTA_PADRAO = 0.05
MIN_N = 30          # abaixo disso a amostra não sustenta decisão

class RecusaDeContrato(ValueError):
    pass

@dataclass
class Decisao:
    veredito: str
    p: float = None
    epsilon: float = None
    n: int = 0
    regra: str = ""
    motivo: str = ""
    extras: dict = field(default_factory=dict)

    def como_dict(self):
        d = {"veredito": self.veredito, "regra": self.regra, "n": self.n}
        if self.p is not None: d["p"] = self.p
        if self.epsilon is not None: d["epsilon"] = self.epsilon
        if self.motivo: d["motivo"] = self.motivo
        d.update(self.extras)
        return d

    def hash(self):
        return hashlib.sha3_256(json.dumps(self.como_dict(), sort_keys=True).encode()).hexdigest()


def _epsilon(n: int, delta: float) -> float:
    """Hoeffding: limite superior do desvio da proporção observada."""
    return math.sqrt(math.log(2.0 / delta) / (2.0 * n))


def decidir_proporcao(k: int, n: int, limiar: float, delta: float = DELTA_PADRAO,
                      min_n: int = MIN_N, regra: str = "proporcao-v1") -> Decisao:
    """Decide se a proporção real está acima do limiar. Recusa antes de adivinhar."""
    if not (0 <= limiar <= 1):
        return Decisao("REFUSED", regra=regra, motivo="LIMIAR_FORA_DE_0_1")
    if not (0 < delta < 1):
        return Decisao("REFUSED", regra=regra, motivo="DELTA_INVALIDO")
    if k < 0 or n < 0 or k > n:
        return Decisao("ERROR", regra=regra, motivo="CONTAGEM_INCOERENTE")
    if n < min_n:
        return Decisao("REFUSED", regra=regra, n=n, motivo=f"AMOSTRA_INSUFICIENTE_{n}_DE_{min_n}")
    p = k / n
    e = _epsilon(n, delta)
    if p - e > limiar:
        v = "1"
    elif p + e < limiar:
        v = "0"
    else:
        v = "INCONCLUSIVE"
    return Decisao(v, p=round(p, 6), epsilon=round(e, 6), n=n, regra=regra,
                   extras={"k": k, "limiar": limiar, "delta": delta})


def decidir_comparacao(a: tuple[int, int], b: tuple[int, int], delta: float = DELTA_PADRAO,
                       min_n: int = MIN_N, regra: str = "comparacao-v1") -> Decisao:
    """Decide se a proporção A é maior que B, com incerteza combinada."""
    ka, na = a; kb, nb = b
    if min(na, nb) < min_n:
        return Decisao("REFUSED", regra=regra, n=min(na, nb), motivo="AMOSTRA_INSUFICIENTE")
    if not (0 <= ka <= na and 0 <= kb <= nb):
        return Decisao("ERROR", regra=regra, motivo="CONTAGEM_INCOERENTE")
    pa, pb = ka / na, kb / nb
    ea, eb = _epsilon(na, delta), _epsilon(nb, delta)
    dif = pa - pb
    margem = ea + eb
    v = "1" if dif - margem > 0 else ("0" if dif + margem < 0 else "INCONCLUSIVE")
    return Decisao(v, p=round(dif, 6), epsilon=round(margem, 6), n=min(na, nb), regra=regra,
                   extras={"p_a": round(pa, 6), "p_b": round(pb, 6), "epsilon_a": round(ea, 6),
                           "epsilon_b": round(eb, 6)})


def decidir_energia(e1: tuple[float, float], e2: tuple[float, float],
                    regra: str = "energia-v1") -> Decisao:
    """Compara dois candidatos de energia (valor, incerteza). Recusa quando as barras se cruzam."""
    v1, u1 = e1; v2, u2 = e2
    if u1 < 0 or u2 < 0:
        return Decisao("REFUSED", regra=regra, motivo="INCERTEZA_NEGATIVA")
    dif = v1 - v2; margem = u1 + u2
    if dif + margem < 0:   v = "1"     # e1 claramente menor
    elif dif - margem > 0: v = "0"     # e2 claramente menor
    else:                  v = "INCONCLUSIVE"
    return Decisao(v, p=round(dif, 8), epsilon=round(margem, 8), regra=regra,
                   extras={"energia_1": v1, "energia_2": v2, "rotulo": "1 = primeiro menor"})

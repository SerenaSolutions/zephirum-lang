# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Serena Quantum Solutions
"""v2.6.0: o recibo nao pode contradizer o proprio veredito.

Tres guardas, cada uma com o caso que a motivou.
"""
import math

from zyql_quantum_gate import ZYQLQuantumGate, wilson_interval


def test_veredito_exige_limite_inferior_acima_do_limiar():
    """7 acertos em 8 dao p_lo=0.53 com limiar 0.85: antes decidia 1."""
    lo, _ = wilson_interval(17, 20, delta=0.05)
    assert lo < 0.85
    g = ZYQLQuantumGate(2, lambda x: 1)
    d = g._trivalent(17 / 20, 20, margin=0.15)          # cota < 1, intervalo curto
    assert d["decision"] == "REFUSED"
    assert d["refusal_reason"] == "INTERVAL_INSIDE_BAND"
    assert d["p_lo"] < 1 - 0.15
    curto = g._trivalent(7 / 8, 8, margin=0.15)          # 8 disparos: cota >= 1
    assert curto["decision"] == "REFUSED"
    assert curto["refusal_reason"] == "ERROR_BOUND_AT_LEAST_ONE"


def test_cota_de_erro_um_nao_decide():
    """Uma amostra: cota de erro >= 1, informacao zero. Recusa, nao veredito."""
    g = ZYQLQuantumGate(1, lambda x: 1)
    d = g._trivalent(1.0, 1, margin=0.15)
    assert d["decision"] == "REFUSED"
    assert d["refusal_reason"] == "ERROR_BOUND_AT_LEAST_ONE"
    assert d["error_bound"] >= 1.0


def test_banda_larga_demais_nao_vira_semantica():
    """Banda >= 0.5 cabe em qualquer resultado: recusa declarada, nao 'balanceado'."""
    g = ZYQLQuantumGate(2, lambda x: 0)
    d = g._trivalent(1.0, 1, margin=1.358)
    assert d["decision"] == "REFUSED"
    assert d["refusal_reason"] == "BAND_TOO_WIDE"


def test_oraculo_que_viola_a_promessa_dj_nao_vira_veredito():
    """f com 1 marcado em 4 nao e constante nem balanceado: p0=0.25, recusa."""
    g = ZYQLQuantumGate(2, lambda x: 1 if x == 1 else 0)
    r = g.run_quantum(shots=4000, seed=7)
    assert r["decision"] == "REFUSED"
    assert abs(r["p0"] - 0.25) < 0.03

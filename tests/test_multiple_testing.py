# -*- coding: utf-8 -*-
"""v1.9.1 — disciplina do auditor: 'cada alegacao precisa de um teste que
possa falhar'. Cada teste aqui e um teste de FALSIFICACAO: remove a
protecao e o teste quebra.

Protecoes verificadas:
1. Bonferroni: banda cresce com a familia (senao, testes multiplos somam risco)
2. Valor exato da banda (golden) — formula nao pode mudar silenciosamente
3. Risco de familia: k vereditos conjuntos nunca ultrapassam epsilon (Monte Carlo)
4. Taxonomia de recusa: REFUSED sempre diz POR QUE
5. Recusa honesta sob familia grande: mais RECUSAs, zero alegacoes erradas
"""
import math
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import pytest
from zyql_quantum_gate import adaptive_margin_family, ZYQLQuantumGate as ZYQLGate


EPS = 0.05
SHOTS = 256


def test_band_shrinks_with_family():
    """FALSIFICAVEL: correcao Bonferroni desta semantica ENCOLHE a banda.

    A primeira implementacao (alargar banda com eps/k) foi PEGA por este
    teste e revertida: alargar deixava alegacoes MAIS agressivas.
    """
    m1 = adaptive_margin_family(EPS, SHOTS, 1)
    m5 = adaptive_margin_family(EPS, SHOTS, 5)
    m20 = adaptive_margin_family(EPS, SHOTS, 20)
    assert m1 > m5 > m20 > 0, "banda deve ENCOLHER com a familia (mais recusa)"
    assert m1 == pytest.approx(math.sqrt(math.log(2.0 / EPS) / (2 * SHOTS)))


def test_golden_values():
    """FALSIFICAVEL: valores-guia da formula; mudanca silenciosa quebra."""
    m_single = math.sqrt(math.log(2.0 / EPS) / (2 * SHOTS))
    m_fam5 = math.sqrt(math.log(2.0 / (EPS / 5)) / (2 * SHOTS))
    expected = 2 * m_single - m_fam5            # m' = 2*m(eps) - m(eps/k)
    got = adaptive_margin_family(EPS, SHOTS, 5)
    assert abs(got - expected) < 1e-12


def test_invalid_family():
    """FALSIFICAVEL: entrada adversarial deve ser recusada, nao silenciosa."""
    for bad in (0, -1, 2.5, "3"):
        with pytest.raises(ValueError):
            adaptive_margin_family(EPS, SHOTS, bad)


def test_family_risk_control_monte_carlo():
    """FALSIFICAVEL: Monte Carlo do proprio enunciado do auditor.

    k vereditos conjuntos sobre oraculos com p0 na borda da banda.
    Sem correcao (family=1), a probabilidade de AO MENOS UMA alegacao
    errada na familia cresce ~k*eps. Com family=k, deve ficar <= eps.
    """
    import random
    rng = random.Random(1701)
    k = 5
    trials = 400
    wrong_families_corrected = 0
    wrong_families_uncorrected = 0
    m_k = adaptive_margin_family(EPS, SHOTS, k)     # corrigido (ENCOLHE)
    m_1 = adaptive_margin_family(EPS, SHOTS, 1)     # nao corrigido
    # verdade cinzenta NO CINZA do teste unico, mas ABAIXO do limiar
    # de alegacao corrigido (regiao onde o nao-corrigido erra com
    # frequencia OBSERVAVEL: ~1%/teste vs ~0.1%/teste corrigido).
    p_edge = 1 - m_1 - 2.5 * math.sqrt(0.86 * 0.14 / SHOTS)
    for _ in range(trials):
        fam_corrected = fam_uncorrected = False
        for _ in range(k):
            # binomial sampling do p0 observado
            hits = sum(1 for _ in range(SHOTS) if rng.random() < p_edge)
            p0_obs = hits / SHOTS
            if p0_obs >= 1 - m_1:                 # alegou constante
                fam_uncorrected = True             # e falso (p_edge abaixo da banda)
            if p0_obs >= 1 - m_k:
                fam_corrected = True
        wrong_families_uncorrected += fam_uncorrected
        wrong_families_corrected += fam_corrected
    rate_un = wrong_families_uncorrected / trials
    rate_corr = wrong_families_corrected / trials
    # o corrigido controla; o nao-corrigido soma risco. margem de Monte Carlo.
    assert rate_corr <= EPS + 0.10, f"familia corrigida extrapolou eps: {rate_corr}"
    assert rate_corr < rate_un, "correcao Bonferroni nao reduziu o risco de familia"
    # taxa nao-corrigida ~ k*eps: familia soma risco quando nao corrigida
    assert rate_un > 0, "cenario deve expor risco do nao-corrigido"


def test_refusal_taxonomy():
    """FALSIFICAVEL: recusa balanceada != recusa zona cinzenta."""
    g = ZYQLGate(3, lambda x: bin(x).count("1") % 2)      # balanceado
    r = g.run_quantum(shots=2048, epsilon=EPS, family=1)
    assert r["decision"] == "REFUSED"
    assert r.get("refusal_reason") == "BALANCED_ORACLE"
    assert r["mode"] == "DECIDED_BY_INTERFERENCE"

    # zona cinzenta: p0 dentro da banda (oraculo com p0 ~ meio-termo)
    class GrayGate(ZYQLGate):
        def run_quantum(self, shots=2048, seed=1701, epsilon=None, family=1):
            # injeta p0 observado no meio da banda, sem silicio
            return self._trivalent(0.5, shots, margin=0.10,
                                   adaptive=True, epsilon_declared=EPS,
                                   family=family)
    g2 = GrayGate(3, lambda x: 1)
    r2 = g2.run_quantum(shots=SHOTS, epsilon=EPS, family=1)
    assert r2["decision"] == "REFUSED"
    assert r2.get("refusal_reason") == "INSIDE_NOISE_BAND"


def test_decided_verdict_records_family():
    """FALSIFICAVEL: toda decisao carrega a familia declarada no recibo."""
    g = ZYQLGate(3, lambda x: 1)
    r = g.run_quantum(shots=2048, epsilon=EPS, family=4)
    assert r["decision"] in (0, 1)
    assert r["family"] == 4
    assert r["epsilon_family"] == EPS


def test_big_family_refuses_honestly():
    """FALSIFICAVEL: familia gigante com shots curto = recusa, nao risco."""
    m_single = adaptive_margin_family(EPS, 32, 1)
    m_k = adaptive_margin_family(EPS, 32, 1000)
    assert 0 < m_k < m_single / 2, "familia 1000 deve encolher banda drasticamente"
    # familia absurda para os shots: banda negativa => RECUSA TUDO, honesto
    assert adaptive_margin_family(EPS, 32, 100000) <= 0, \
        "familia 100000 com 32 shots deve zerar a banda"
    g = ZYQLGate(3, lambda x: 1)
    r = g.run_quantum(shots=32, epsilon=EPS, family=100000)
    assert r["decision"] == "REFUSED", "familia absurda com shots curto: so recusa"
    assert r["refusal_reason"] == "FAMILY_EXCEEDS_SHOTS"

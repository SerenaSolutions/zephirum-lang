# -*- coding: utf-8 -*-
"""Bateria H-2 (25/10/2026) — os dois buracos que a leitura adversarial interna
apontou na Rodada H, fechados com guardas falsificaveis.

H10 — independencia so no lag-1 e cego por construcao: duas cadeias AR(1)
intercaladas (persistencia 0.9) tem lag-1 ~ 0 (cross-chain) e lag-2 ~ 0.8
(within-chain). Hoeffding 1963 exige independencia MUTUA, nao de ordem 1.
  -> fix: correlation_verdict varre lags 1..5 com banda de familia
     (Bonferroni 95% family-wise, z=2.807 para K=5) e recusa no primeiro
     lag que estourar, declarando QUAL lag traiu.
H11 — o selo de protocolo detectava adulteracao da SPEC, mas nao a quebra
da stopping rule durante a EXECUCAO (decidir antes de todos os shots
selados = peeking em runtime, invisivel pro selo original).
  -> fix: stopping_rule_check amarra o recibo de execucao ao protocolo
     selado: decisao antecipada => REFUSED EARLY_DECISION; shots a mais
     apos a decisao => REFUSED EXTRA_SHOTS.

Tudo falsifiavel: remova qualquer guarda e o teste correspondente quebra.
"""
import numpy as np

from src.zyql_robust import (
    correlation_verdict, protocol_check, protocol_seal, stopping_rule_check)


def _interleaved_ar1(n_total, persistence=0.9, rng=None):
    """Duas cadeias AR(1) binarias independentes, intercaladas.

    lag-1 do fluxo intercalado olha cross-chain (~0); lag-2 olha
    within-chain (~persistence). Este e o ataque que o lag-1 sozinho nao ve.
    """
    rng = rng or np.random.default_rng(4)
    half = n_total // 2
    chains = []
    for _ in range(2):
        x = np.empty(half)
        x[0] = rng.integers(0, 2)
        for k in range(1, half):
            keep = rng.random() < persistence
            x[k] = x[k - 1] if keep else 1 - x[k - 1]
        chains.append(x)
    out = np.empty(n_total, dtype=float)
    out[0::2] = chains[0]
    out[1::2] = chains[1]
    return out


# ---------------- H10: lag-1 sozinho e cego; familia de lags enxerga --------
def test_h10_blind_spot_demo_lag1_clean_but_lag2_dirty():
    """RED-prova: o fluxo intercalado passa na banda do lag-1 (buraco real)
    e mesmo assim e recusado pela guarda de familia — porque o lag-2 trai."""
    bits = _interleaved_ar1(4000)
    N = len(bits)
    band = 2.0 / np.sqrt(N)
    rho1 = abs(np.corrcoef(bits[:-1], bits[1:])[0, 1])
    rho2 = abs(np.corrcoef(bits[:-2], bits[2:])[0, 1])
    assert rho1 < band, "lag-1 deve estar dentro da banda (o cego)"
    assert rho2 > band, "lag-2 deve estourar a banda (a dependencia)"
    v = correlation_verdict(bits)
    assert v["decision"] == "REFUSED"
    assert v["refusal_reason"] == "CORRELATED_SHOTS"
    assert v["lag_detected"] == 2


def test_h10_iid_stream_still_passes():
    """GREEN-sanidade: ruido genuinamente i.i.d. nao e recusado."""
    rng = np.random.default_rng(42)
    bits = rng.integers(0, 2, 4000)
    v = correlation_verdict(bits)
    assert v["decision"] == 1
    assert v["mode"] == "INDEPENDENCE_PLAUSIBLE"
    assert len(v["autocorr_lags"]) == 5


def test_h10_lag1_correlation_still_caught():
    """Regressao: dependencia de ordem 1 (repeticao) continua recusada no lag 1."""
    rng = np.random.default_rng(7)
    bits = [0]
    while len(bits) < 4000:
        nxt = bits[-1] if rng.random() < 0.9 else 1 - bits[-1]
        bits.append(nxt)
    v = correlation_verdict(bits)
    assert v["decision"] == "REFUSED" and v["lag_detected"] == 1


# ---------------- H11: stopping rule amarrada em runtime ------------------
def test_h11_honest_execution_passes():
    spec = {"epsilon": 0.05, "shots": 2048, "family": 1,
            "stopping_rule": "fixed", "hypotheses": ["p0 < 0.5"]}
    sealed = protocol_seal(spec)
    v = stopping_rule_check(sealed, {"shots_observed": 2048,
                                     "decision_at_shot": 2048})
    assert v["decision"] == 1 and v["mode"] == "STOPPING_RULE_HONORED"


def test_h11_early_decision_is_refused():
    """Peeking em runtime: decidir com metade dos shots selados."""
    spec = {"epsilon": 0.05, "shots": 2048, "family": 1,
            "stopping_rule": "fixed", "hypotheses": ["p0 < 0.5"]}
    sealed = protocol_seal(spec)
    v = stopping_rule_check(sealed, {"shots_observed": 1024,
                                     "decision_at_shot": 1024})
    assert v["decision"] == "REFUSED"
    assert v["refusal_reason"] == "EARLY_DECISION"


def test_h11_extra_shots_after_decision_is_refused():
    """Coleta pos-decisao (checar de novo apos ver o resultado) e pos-hoc."""
    spec = {"epsilon": 0.05, "shots": 2048, "family": 1,
            "stopping_rule": "fixed", "hypotheses": ["p0 < 0.5"]}
    sealed = protocol_seal(spec)
    v = stopping_rule_check(sealed, {"shots_observed": 4096,
                                     "decision_at_shot": 2048})
    assert v["decision"] == "REFUSED"
    assert v["refusal_reason"] == "EXTRA_SHOTS"


def test_h11_tampered_spec_still_refused():
    spec = {"epsilon": 0.05, "shots": 2048, "family": 1,
            "stopping_rule": "fixed", "hypotheses": ["p0 < 0.5"]}
    sealed = protocol_seal(spec)
    spec["epsilon"] = 0.10  # peeking pos-hoc no criterio
    v = protocol_check(sealed, spec)
    assert v["decision"] == "REFUSED"
    assert v["refusal_reason"] == "PROTOCOL_TAMPERED"

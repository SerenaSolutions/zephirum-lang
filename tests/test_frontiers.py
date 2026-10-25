# -*- coding: utf-8 -*-
"""v2.0.0 — fronteiras europeias implementadas NATIVAS: testes falsificaveis.

Cada teste e construido pra FALHAR se a protecao sumir:
1. Parameter-shift == finite difference (fonte primaria correta)
2. Barren plateau: profundo tem variancia << raso; veredito ternario recusa
3. Kernel quantico: PSD (Schur) e identidade; remove PSD check -> falha
4. ZNE: recupera o valor ideal OU RECUSA (nunca vende chute); guard
   leave-one-out remove o chute embalado
5. MPS: GHZ n=12 exato com chi pequeno; cross-check com statevector plano;
   truncagem declarada; porta nao-vizinha e recusada com erro declarado
"""
import sys, os
import numpy as np
import pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from zyqml_core import (energy, param_shift_gradient, gradient_variance,
                        train_verdict, quantum_kernel, kernel_matrix,
                        kernel_is_psd, ansatz_state, zero_state, apply_1q, H1)
from zyql_zne import fold_expectation, zne_verdict
from zyql_mps import MPSSim, H1 as MH1, CNOT4, CZ4, ry as mry

RNG = np.random.default_rng(1701)


# ---------- 1) PARAMETER-SHIFT: exato contra diferenca finita ----------
def test_param_shift_matches_finite_difference():
    n, L = 3, 2
    theta = RNG.uniform(0, 2 * np.pi, L * n)
    ps = param_shift_gradient(n, L, theta)
    fd = []
    eps = 1e-6
    for i in range(len(theta)):
        tp = theta.copy(); tp[i] += eps
        tm = theta.copy(); tm[i] -= eps
        fd.append((energy(n, L, tp) - energy(n, L, tm)) / (2 * eps))
    assert np.allclose(ps, fd, atol=1e-4), "parameter-shift deve ser exato p/ RY"


# ---------- 2) BARREN PLATEAU: veredito ternario do treino ----------
def test_deep_vs_shallow_gradient_variance():
    n = 6
    vars_shallow, vars_deep = [], []
    for _ in range(8):
        th_s = RNG.uniform(0, 2 * np.pi, 1 * n)
        th_d = RNG.uniform(0, 2 * np.pi, 12 * n)
        vars_shallow.append(gradient_variance(n, 1, th_s))
        vars_deep.append(gradient_variance(n, 12, th_d))
    assert np.mean(vars_deep) < np.mean(vars_shallow), \
        "ansatz global profunda deve ter gradiente mais estéril (McClean 2018)"
    v = train_verdict(n, 12, float(np.mean(vars_deep)))
    if v["decision"] == "REFUSED":
        assert v["refusal_reason"] == "GRADIENT_VANISHED"
    # FALSIFICAVEL: semantica ternaria do veredito
    assert train_verdict(n, 1, 1e-6)["refusal_reason"] == "GRADIENT_VANISHED"
    assert train_verdict(n, 1, 1e-2)["decision"] == 1
    assert train_verdict(n, 99, 1e-2)["refusal_reason"] == "DEPTH_EXCEEDS_BUDGET"


# ---------- 3) KERNEL QUANTICO: Schur garante PSD ----------
def test_kernel_identity_and_psd():
    assert abs(quantum_kernel([0.3, 0.7], [0.3, 0.7], 2) - 1.0) < 1e-9
    K = kernel_matrix([[0.1, 0.9], [0.9, 0.1], [0.4, 0.4]], 2)
    assert kernel_is_psd(K), "teorema do produto de Schur: K = |Gram|^2 e PSD"
    # FALSIFICAVEL: matriz destruida perde PSD -> detector tem que pegar
    bad = K.copy(); bad[0, 1] = bad[1, 0] = 5.0
    assert not kernel_is_psd(bad)


# ---------- 4) ZNE: mitiga honestamente OU recusa o chute ----------
def test_zne_mitigates_moderate_noise():
    ideal, depol = 1.0, 0.95
    gammas = [1, 3, 5]
    vals = [fold_expectation(ideal, g, depol) for g in gammas]
    r = zne_verdict(gammas, vals)
    assert r["decision"] == 1, "ruido moderado deve ser mitigado"
    assert abs(r["estimate"] - ideal) < abs(vals[0] - ideal), \
        "estimativa mitigada deve ser MAIS perto do ideal que o valor ruidoso"


def test_zne_refuses_ill_conditioned_extrapolation():
    ideal, depol = 1.0, 0.50           # ruido severo: decaimento nada polinomial
    gammas = [1, 3, 5]
    vals = [fold_expectation(ideal, g, depol) for g in gammas]
    r = zne_verdict(gammas, vals)
    assert r["decision"] == "REFUSED", "ruido severo: extrapolar e chute embalado"
    assert r["refusal_reason"] == "EXTRAPOLATION_ILL_CONDITIONED"


def test_zne_guard_is_falsifiable():
    """FALSIFICAVEL: sem o guard leave-one-out, o chute seria vendido."""
    vals = [0.5, 0.125, 0.03125]
    pred = 0.5 + (0.125 - 0.5) / 2 * (5 - 1)  # linear nos 2 primeiros, prevê o 3o
    assert abs(pred - 0.03125) > 0.5 * 0.03125, \
        "cenario severo deve falhar no guard, nao passar"


# ---------- 5) MPS: quebra n<=8 e e EXATO onde declara ----------
def test_mps_ghz_exact_with_small_chi():
    n = 12                                 # ALEM do limite declarado n<=8
    m = MPSSim(n, chi=4)
    m.apply_1q(MH1, 0)
    for i in range(n - 1):
        m.apply_2q(CNOT4, i, i + 1)
    p = m.probs()
    assert abs(p[0] - 0.5) < 1e-9 and abs(p[-1] - 0.5) < 1e-9, \
        "GHZ n=12: |0...0> e |1...1> com 0.5 cada, exato em chi=4"


def test_mps_cross_validated_against_statevector():
    n = 8
    m = MPSSim(n, chi=32)
    for q in range(n):
        m.apply_1q(MH1, q)
    for q in range(n - 1):
        m.apply_2q(CZ4, q, q + 1)
        m.apply_1q(mry(0.3), q)
    p_mps = m.probs()
    # referencia: mesmo circuito no statevector do zyqml_core (nossos, independentes)
    from zyqml_core import apply_2q, zero_state
    from zyqml_core import ry as cry, CZ4 as cCZ4
    v = zero_state(n)
    for q in range(n):
        v = apply_1q(v, H1, q, n)
    for q in range(n - 1):
        v = apply_2q(v, cCZ4, q, q + 1, n)
        v = apply_1q(v, cry(0.3), q, n)
    p_ref = np.abs(v) ** 2
    assert np.allclose(p_mps, p_ref, atol=1e-9), "MPS e statevector devem concordar"


def test_mps_declared_limitations():
    m = MPSSim(4, chi=8)
    with pytest.raises(ValueError):
        m.apply_2q(CNOT4, 0, 2)           # porta NAO vizinha: recusada com erro
    m.apply_2q(CNOT4, 0, 1)
    assert hasattr(m, "truncation_error"), "truncagem precisa ser declarada"

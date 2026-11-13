# SPDX-License-Identifier: Apache-2.0
"""Guardas de entrada: o nucleo recusa o que nao tem sentido, em vez de inventar."""
import math
import pytest
from zyql_quantum_gate import ZYQLQuantumGate, wilson_interval


def test_true_oracle_decides_one_by_declared_convention():
    # convencao declarada: f == 1 em todo ponto -> DECIDE 1
    assert ZYQLQuantumGate(3, lambda x: True).run_quantum(shots=512)["decision"] == 1
    assert ZYQLQuantumGate(3, lambda x: False).run_quantum(shots=512)["decision"] == 0


def test_shots_zero_is_refused_not_zero_division():
    with pytest.raises(ValueError):
        ZYQLQuantumGate(3, lambda x: 0).run_quantum(shots=0)


def test_shots_float_and_bool_rejected():
    with pytest.raises(TypeError):
        ZYQLQuantumGate(3, lambda x: 0).run_quantum(shots=2048.5)
    with pytest.raises(TypeError):
        ZYQLQuantumGate(3, lambda x: 0).run_quantum(shots=True)


def test_negative_n_rejected():
    with pytest.raises(ValueError):
        ZYQLQuantumGate(-1, lambda x: 0)


def test_epsilon_edges_rejected():
    g = ZYQLQuantumGate(3, lambda x: 0)
    for eps in (0, -0.1, 1.5):
        with pytest.raises(ValueError):
            g.run_quantum(shots=512, epsilon=eps)


def test_non_boolean_oracle_rejected():
    for f in (lambda x: 2, lambda x: None, lambda x: "1"):
        with pytest.raises(ValueError):
            ZYQLQuantumGate(3, f)


def test_error_bound_never_exceeds_one():
    d = ZYQLQuantumGate(3, lambda x: 0).run_quantum(shots=2048)
    assert 0 <= d["error_bound"] <= 1
    for shots in (16, 64, 512, 2048):
        r = ZYQLQuantumGate(3, lambda x: 0).run_quantum(shots=shots)
        assert r["error_bound"] <= 1.0


def test_wilson_interval_inside_unit_and_contains_phat():
    for k, n in ((0, 100), (3, 100), (50, 100), (97, 100), (100, 100)):
        lo, hi = wilson_interval(k, n)
        assert 0 <= lo <= k / n <= hi <= 1

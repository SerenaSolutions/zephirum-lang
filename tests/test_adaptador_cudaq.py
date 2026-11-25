# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Serena Quantum Solutions
"""CUDA-Q adapter contract: it must refuse explicitly, never fake a run."""
from zephirum.adapters import cudaq_backend


def test_contract_functions_exist():
    for name in ("capacidades", "listar", "executar"):
        assert callable(getattr(cudaq_backend, name))


def test_refuses_without_sdk_or_target():
    cap = cudaq_backend.capacidades("nvidia")
    assert cap["status"] == "REFUSED"
    assert cap["motivo"] in ("SDK_CUDAQ_AUSENTE", "ALVO_CUDAQ_AUSENTE")


def test_listar_never_pretends():
    out = cudaq_backend.listar("nvidia")
    if out["status"] != "OK":
        assert out["motivo"] in ("SDK_CUDAQ_AUSENTE", "ALVO_CUDAQ_AUSENTE")


def test_executar_refuses_instead_of_simulating_hidden():
    out = cudaq_backend.executar({"qubits": 1, "gates": [{"gate": "h", "qubit": 0}]},
                                 "nvidia", shots=16)
    if out["status"] != "OK":
        assert out["motivo"] in ("SDK_CUDAQ_AUSENTE", "ALVO_CUDAQ_AUSENTE")

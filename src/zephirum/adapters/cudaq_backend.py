# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Serena Quantum Solutions
"""CUDA-Q adapter: the same program contract on NVIDIA's hybrid stack.

Mirrors the qBraid and Qiskit adapters (qubits + gates). It refuses with an
explicit reason when the SDK or the target is unavailable instead of silently
falling back to a local simulation.
"""
from __future__ import annotations

from typing import Any

SDK_MISSING = "SDK_CUDAQ_AUSENTE"
TARGET_MISSING = "ALVO_CUDAQ_AUSENTE"


def _sdk():
    try:
        import cudaq  # type: ignore
    except ImportError:
        return None
    return cudaq


def capacidades(target: str | None = None) -> dict[str, Any]:
    """Report whether this host can run on CUDA-Q, with an explicit reason."""
    cudaq = _sdk()
    if cudaq is None:
        return {"status": "REFUSED", "motivo": SDK_MISSING,
                "detail": "cudaq is not installed; install nvidia-cudaq to enable this target"}
    if not target:
        return {"status": "OK", "motivo": None, "targets": sorted(
            str(t) for t in _targets(cudaq))}
    if target not in _targets(cudaq):
        return {"status": "REFUSED", "motivo": TARGET_MISSING,
                "detail": f"target {target!r} is not offered by this CUDA-Q build"}
    return {"status": "OK", "motivo": None, "target": target}


def _targets(cudaq) -> list[str]:
    try:
        return [str(t) for t in cudaq.get_targets()]
    except Exception:
        return []


def listar(target: str | None = None) -> dict[str, Any]:
    cap = capacidades(target)
    if cap["status"] != "OK":
        return cap
    return {"status": "OK", "devices": cap.get("targets") or [cap.get("target")]}


def executar(programa: dict[str, Any], target: str, shots: int = 1024) -> dict[str, Any]:
    """Run a ZYQL program on a CUDA-Q target and return raw counts."""
    cap = capacidades(target)
    if cap["status"] != "OK":
        return cap
    from zephirum.adapters.qiskit_backend import validar

    validar(programa)
    cudaq = _sdk()
    try:
        cudaq.set_target(target)
        counts = _run_kernel(cudaq, programa, shots)
    except Exception as exc:  # a failed execution is never a result
        return {"status": "REFUSED", "motivo": f"FALHA_EXECUCAO: {type(exc).__name__}",
                "detail": str(exc)[:200]}
    return {"status": "OK", "target": target, "shots": shots, "counts": counts}


def _run_kernel(cudaq, programa: dict[str, Any], shots: int) -> dict[str, int]:
    qubits = int(programa.get("qubits", 1))
    gates = programa.get("gates", [])

    @cudaq.kernel
    def kernel():
        q = cudaq.qvector(qubits)
        for gate in gates:
            name = str(gate.get("gate", "")).lower()
            idx = int(gate.get("qubit", 0))
            if name == "x":
                x(q[idx])
            elif name == "h":
                h(q[idx])
            elif name == "z":
                z(q[idx])
        mz(q)

    result = cudaq.sample(kernel, shots_count=shots)
    return {str(k): int(v) for k, v in result.items()}

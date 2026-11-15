# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Serena Quantum Solutions
"""Adaptador qBraid: roda o mesmo contrato de programa em device do qBraid.

Mesmo contrato do adaptador Qiskit (qubits + gates). Recusa com motivo quando
nao houver credencial ou device, em vez de simular escondido.
"""
from __future__ import annotations

from typing import Any


def _circuito(programa: dict[str, Any]):
    from zephirum.adapters.qiskit_backend import construir, validar

    validar(programa)
    qc = construir(programa)
    qc.measure_all()
    return qc


def listar(api_key: str | None = None) -> dict[str, Any]:
    try:
        from qbraid import QbraidProvider
    except ImportError:
        return {"status": "REFUSED", "motivo": "SDK_QBRAID_AUSENTE"}
    if not api_key:
        return {"status": "REFUSED", "motivo": "CREDENCIAL_AUSENTE"}
    try:
        prov = QbraidProvider(api_key=api_key)
        devs = prov.get_devices()
    except Exception as exc:  # credencial invalida nao vira resultado
        return {"status": "REFUSED", "motivo": f"FALHA_AUTENTICACAO: {type(exc).__name__}"}
    return {"status": "OK", "devices": sorted(d.id for d in devs)}


def executar(programa: dict[str, Any], device: str, api_key: str,
             shots: int = 1024) -> dict[str, Any]:
    try:
        from qbraid import QbraidProvider
    except ImportError:
        return {"status": "REFUSED", "motivo": "SDK_QBRAID_AUSENTE"}
    try:
        prov = QbraidProvider(api_key=api_key)
        dev = prov.get_device(device)
        qc = _circuito(programa)
        job = dev.run(qc, shots=shots)
        res = job.result()
        counts = dict(res.measurement_counts())
    except Exception as exc:
        return {"status": "REFUSED", "motivo": f"EXECUCAO_FALHOU: {type(exc).__name__}: {str(exc)[:90]}"}
    return {"status": "OK", "origem": "qbraid", "device": device,
            "shots": sum(counts.values()), "counts": counts, "job_id": str(getattr(job, "id", ""))}

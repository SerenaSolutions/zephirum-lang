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


def capacidades(device_id: str, chave: str) -> dict:
    """Le o que o provedor declara, sem completar o que ele nao declarou."""
    try:
        from qbraid import QbraidProvider
    except Exception:
        return {"status": "REFUSED", "motivo": "SDK_QBRAID_AUSENTE"}
    if not chave:
        return {"status": "REFUSED", "motivo": "CREDENCIAL_AUSENTE"}
    try:
        meta = QbraidProvider(api_key=chave).get_device(device_id).metadata()
    except Exception as exc:
        return {"status": "REFUSED", "motivo": f"FALHA_LEITURA:{type(exc).__name__}"}
    gates = meta.get("basis_gates")
    return {
        "status": "OK",
        "device": device_id,
        "paradigma": meta.get("paradigm"),
        "qubits": meta.get("num_qubits"),
        "simulador": bool(meta.get("simulator")),
        "portas_declaradas": sorted(gates) if gates else [],
        "ruido_declarado": bool(meta.get("noise_models")),
        "preco": meta.get("pricing") or {},
        "batch": bool(meta.get("batch_job_support")),
    }


def pode_executar(programa: dict, caps: dict) -> dict:
    """Decide se o programa cabe no que o dispositivo declarou.

    Regra: o que o provedor nao declara nao e assumido. Duvida vira recusa com motivo,
    nao tentativa as cegas.
    """
    if caps.get("status") != "OK":
        return {"pode": False, "motivo": caps.get("motivo", "CAPACIDADE_INDISPONIVEL")}
    if caps.get("paradigma") != "gate_model":
        return {"pode": False, "motivo": f"PARADIGMA_NAO_SUPORTADO:{caps.get('paradigma')}"}
    if not caps.get("portas_declaradas"):
        return {"pode": False, "motivo": "PORTAS_NAO_DECLARADAS"}
    exigidas = {str(g.get("op", "")).lower() for g in programa.get("gates", [])}
    nativas = {g.lower() for g in caps["portas_declaradas"]}
    faltando = sorted(exigidas - nativas)
    return {"pode": True, "motivo": "", "portas_a_converter": faltando,
            "aviso": "portas ausentes exigem conversao para o conjunto nativo"}

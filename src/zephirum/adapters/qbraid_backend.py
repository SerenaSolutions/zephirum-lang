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
        # Falha rapida: o qBraid aceita a submissao e so recusa na execucao quando o vinculo
        # com o provedor externo nao existe. Esperar o result() nesse caso so gasta fila.
        import time as _t
        limite = _t.monotonic() + 45
        estado = str(job.status()).upper()
        while _t.monotonic() < limite and "FAIL" not in estado and "CANCEL" not in estado and "COMPLET" not in estado:
            _t.sleep(3)
            try:
                estado = str(job.status()).upper()
            except Exception:
                break
        if "FAIL" in estado or "CANCEL" in estado:
            try:
                detalhe = prov.client.get_job(job.id)
                msg = str(detalhe.get("statusMsg", "")) if isinstance(detalhe, dict) else ""
            except Exception:
                msg = ""
            if "not connected" in msg.lower() or "link it" in msg.lower():
                return {"status": "REFUSED", "motivo": "VINCULO_AUSENTE", "device": device,
                        "detalhe": msg[:120], "job_id": str(getattr(job, "id", ""))}
            return {"status": "REFUSED", "motivo": f"EXECUCAO_FALHOU: {msg[:90] or estado}",
                    "job_id": str(getattr(job, "id", ""))}
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


def converter_para_nativas(programa: dict, caps: dict, conjunto_assumido: list | None = None) -> dict:
    """Reescreve o programa no conjunto de portas que o dispositivo declarou.

    Sem declaracao, nao converte: recusa. A conversao e registrada para que o recibo
    mostre o que foi enviado, e nao o que foi escrito.
    """
    if caps.get("status") != "OK":
        return {"status": "REFUSED", "motivo": caps.get("motivo", "CAPACIDADE_INDISPONIVEL")}
    if caps.get("paradigma") != "gate_model":
        return {"status": "REFUSED", "motivo": f"PARADIGMA_NAO_SUPORTADO:{caps.get('paradigma')}"}
    nativas = [str(g) for g in (caps.get("portas_declaradas") or [])]
    assumido = False
    if not nativas and conjunto_assumido:
        # O chamador pode declarar o conjunto por escrito. Fica marcado no resultado, para
        # que o recibo distinga o que o provedor declarou do que o usuario assumiu.
        nativas = [str(g) for g in conjunto_assumido]
        assumido = True
    if not nativas:
        return {"status": "REFUSED", "motivo": "PORTAS_NAO_DECLARADAS"}
    try:
        from qiskit import transpile
        from qiskit.circuit.library.standard_gates import get_standard_gate_name_mapping
    except ImportError:
        return {"status": "REFUSED", "motivo": "QISKIT_AUSENTE"}
    # O provedor declara portas que o Qiskit nao conhece (ccnot, por exemplo). Elas nao
    # entram como basis_gates: ficam registradas e o conjunto utilizavel e o resto.
    conhecidas = set(get_standard_gate_name_mapping())
    utilizaveis = [g for g in nativas if g.lower() in conhecidas]
    ignoradas = sorted(set(nativas) - set(utilizaveis))
    if not utilizaveis:
        return {"status": "REFUSED", "motivo": "NENHUMA_PORTA_NATIVA_RECONHECIDA",
                "portas_ignoradas": ignoradas}
    try:
        qc = _circuito(programa)
        convertido = transpile(qc, basis_gates=utilizaveis, optimization_level=1)
    except Exception as exc:
        return {"status": "REFUSED", "motivo": f"CONVERSAO_FALHOU:{type(exc).__name__}: {str(exc)[:80]}"}
    operacoes = []
    for instrucao in convertido.data:
        nome = instrucao.operation.name
        if nome in ("barrier", "measure"):
            continue
        operacoes.append({"op": nome, "qubits": [convertido.find_bit(q).index for q in instrucao.qubits]})
    usadas = sorted({o["op"] for o in operacoes})
    fora = sorted(set(usadas) - {n.lower() for n in utilizaveis})
    if fora:
        return {"status": "REFUSED", "motivo": f"PORTA_FORA_DO_CONJUNTO:{','.join(fora)}"}
    escritas = sorted({str(g.get("op", "")).lower() for g in programa.get("gates", [])})
    return {"status": "OK", "programa_nativo": operacoes, "portas_usadas": usadas,
            "profundidade": convertido.depth(), "convertidas": sorted(set(escritas) - set(usadas)),
            "portas_ignoradas": ignoradas, "conjunto_assumido_pelo_chamador": assumido}


def executar_com_conversao(programa: dict, device: str, chave: str, shots: int = 1024,
                           conjunto_assumido: list | None = None) -> dict:
    """Caminho completo: le capacidade, converte, executa e devolve o que foi enviado."""
    caps = capacidades(device, chave)
    conv = converter_para_nativas(programa, caps, conjunto_assumido)
    if conv.get("status") != "OK":
        return {"status": "REFUSED", "motivo": conv.get("motivo"), "etapa": "conversao"}
    saida = executar(programa, device, chave, shots=shots)
    if saida.get("status") == "OK":
        saida["programa_nativo"] = conv["programa_nativo"]
        saida["portas_usadas"] = conv["portas_usadas"]
        saida["conjunto_assumido_pelo_chamador"] = conv.get("conjunto_assumido_pelo_chamador", False)
    return saida

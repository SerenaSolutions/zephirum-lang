# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Serena Quantum Solutions
"""Recibo Q-ROUTE: SHA3-256 canonico + encadeamento com o recibo anterior."""
import datetime
import hashlib
import json
import os
import secrets

CHAVE = "sha3_256"


def canonical(obj):
    """Canon unico da casa (battery_ci.canon).

    Antes esta funcao usava separadores compactos e ensure_ascii=False, o que
    gerava um SEGUNDO canon no repositorio: o mesmo conteudo selado pela regra
    da casa nao conferia por aqui, e vice-versa. Agora ha uma unica regra,
    importada do validador oficial (src/battery_ci.py).
    """
    from battery_ci import canon as _house_canon
    return _house_canon(obj)


def sela(corpo, caminho, anterior=None, seq=None):
    rec = dict(corpo)
    rec["prev_sha3"] = anterior
    # Endurecimento anti-replay: nonce de uso unico e sequencia monotonica.
    # Sem estes campos um recibo valido do passado pode ser reapresentado
    # como prova de uma execucao recente.
    rec["nonce"] = secrets.token_hex(16)
    prev_seq = 0
    if seq is not None:
        prev_seq = int(seq) - 1
    elif os.path.exists(caminho):
        try:
            with open(caminho, encoding="utf-8") as f:
                prev_seq = int(json.load(f).get("seq", 0))
        except (OSError, ValueError, json.JSONDecodeError):
            prev_seq = 0
    rec["seq"] = prev_seq + 1
    rec["data"] = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    rec[CHAVE] = hashlib.sha3_256(canonical(rec).encode()).hexdigest()
    os.makedirs(os.path.dirname(caminho) or ".", exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(rec, f, ensure_ascii=False, indent=1, sort_keys=True)
    return rec


def le_anterior(caminho):
    if caminho and os.path.exists(caminho):
        with open(caminho, encoding="utf-8") as f:
            h = json.load(f).get(CHAVE)
        return h
    return None


def verifica(caminho):
    """Verificacao unificada: uma regra normativa, variantes historicas aceitas.

    Antes esta funcao lia apenas a chave `sha3_256`; recibos emitidos pelo
    interpretador (chave `selo_sha3_256`) respondiam "adulterado" mesmo integros.
    """
    from zqea_canon import verificar_arquivo
    res = verificar_arquivo(caminho)
    with open(caminho, encoding="utf-8") as f:
        rec = json.load(f)
    res["recibo"] = rec
    return res


def verifica_encadeamento(caminho, anterior=None, seq_esperado=None):
    """Confere integridade + anti-replay (nonce presente, seq e prev_sha3 coerentes).

    `anterior` pode ser o caminho do recibo anterior ou o hash esperado.
    Retorna dict com ok, motivos e campos relevantes.
    """
    res = verifica(caminho)
    rec = res.get("recibo", {})
    motivos = list(res.get("motivos", []) or [])
    if not rec.get("nonce"):
        motivos.append("nonce_ausente")
    if not isinstance(rec.get("seq"), int) or rec.get("seq", 0) < 1:
        motivos.append("seq_invalido")
    esperado = anterior
    if anterior and os.path.exists(anterior):
        with open(anterior, encoding="utf-8") as f:
            ant = json.load(f)
        esperado = ant.get(CHAVE)
        if isinstance(rec.get("seq"), int) and isinstance(ant.get("seq"), int) and seq_esperado is not None:
            if rec["seq"] != seq_esperado:
                motivos.append("seq_fora_de_ordem")
    if esperado and rec.get("prev_sha3") != esperado:
        motivos.append("prev_sha3_divergente")
    return {"ok": not motivos, "motivos": motivos, "seq": rec.get("seq"), "nonce": bool(rec.get("nonce"))}

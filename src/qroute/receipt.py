# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Serena Quantum Solutions
"""Recibo Q-ROUTE: SHA3-256 canonico + encadeamento com o recibo anterior."""
import datetime
import hashlib
import json
import os

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


def sela(corpo, caminho, anterior=None):
    rec = dict(corpo)
    rec["prev_sha3"] = anterior
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

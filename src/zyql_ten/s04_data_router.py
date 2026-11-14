# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Serena Quantum Solutions
"""04 Engenheiro de dados: roteamento e deduplicacao."""
from .receipt import selado
import hashlib

@selado
def run(registros, esquema, ja_processados=None):
    ja_processados = ja_processados or set()
    vistos, novos, repetidos, invalidos = set(), [], 0, 0
    for r in registros:
        faltando = [c for c in esquema if c not in r]
        chave = hashlib.sha3_256(
            repr(sorted(r.items())).encode()).hexdigest()[:16]
        if faltando:
            invalidos += 1
            continue
        if chave in vistos or chave in ja_processados:
            repetidos += 1
            continue
        vistos.add(chave)
        novos.append(r)
    total = len(registros)
    if total == 0:
        rota, motivo = "REFUSED", "SEM_ENTRADA"
    elif invalidos / total > 0.5:
        rota, motivo = 0, "ESQUEMA_INVALIDO"
    else:
        rota, motivo = 1, None
    evitados = repetidos + invalidos
    return {"solucao": "04 data router", "rota": rota, "motivo": motivo,
            "recebidos": total, "novos": len(novos),
            "evitados": evitados,
            "redundancia": round(evitados / max(total, 1), 3)}

# SPDX-License-Identifier: Apache-2.0
"""Provedor local para o promptfoo: chama o portao, nao um LLM."""
import json, sys

def call_api(prompt, options, context):
    """Recebe um caso e devolve a decisao do portao deterministico."""
    try:
        caso = json.loads(prompt)
    except Exception:
        return {"output": "ENTRADA_INVALIDA"}
    achados = caso.get("achados", [])
    if not achados:
        return {"output": "REFUSED"}
    if any(a.get("resultado") == "FALHA" and a.get("severidade") in ("critica", "alta") for a in achados):
        return {"output": "BLOQUEADO"}
    if any(a.get("resultado") == "REFUSED" for a in achados):
        return {"output": "REFUSED"}
    return {"output": "APROVADO"}

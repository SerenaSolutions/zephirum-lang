"""Recibo Q-ROUTE: SHA3-256 canonico + encadeamento com o recibo anterior."""
import datetime
import hashlib
import json
import os

CHAVE = "sha3_256"


def canonical(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


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
    with open(caminho, encoding="utf-8") as f:
        rec = json.load(f)
    declarado = rec.get(CHAVE)
    corpo = {k: v for k, v in rec.items() if k != CHAVE}
    calc = hashlib.sha3_256(canonical(corpo).encode()).hexdigest()
    return {"integro": declarado == calc, "declarado": declarado, "calculado": calc, "recibo": rec}

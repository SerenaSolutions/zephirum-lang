# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Serena Quantum Solutions
"""Recibo auditavel por operacao (RF-05).

Todo modulo de setor passa a devolver recibo com SHA3-256 da entrada e da saida.
A assinatura ML-DSA-44 fica declarada como ausente quando o recibo e gerado fora
do ambiente com custodia de chave (RF-06), nunca falsificada.
"""
import functools, hashlib, json, time
from .versions import RECEIPT_SCHEMA_VERSION, ZYQL_GRAMMAR_VERSION


def _canon(obj):
    return json.dumps(obj, sort_keys=True, default=repr, skipkeys=True,
                      ensure_ascii=False, separators=(",", ":"))


def hash_sha3(obj):
    return hashlib.sha3_256(_canon(obj).encode()).hexdigest()


def selar(operacao, entrada, saida, latencia_ms=None, assinatura="ausente"):
    r = {"schema": RECEIPT_SCHEMA_VERSION, "gramatica": ZYQL_GRAMMAR_VERSION,
         "operacao": operacao, "entrada_sha3": hash_sha3(entrada),
         "saida_sha3": hash_sha3(saida), "assinatura": assinatura}
    if latencia_ms is not None:
        r["latencia_ms"] = latencia_ms
    return r


def verificar(resultado):
    """Confere se o recibo corresponde ao conteudo devolvido."""
    rec = resultado.get("recibo")
    if not rec:
        return False
    corpo = {k: v for k, v in resultado.items() if k != "recibo"}
    return rec["saida_sha3"] == hash_sha3(corpo)


def selado(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        t0 = time.perf_counter()
        r = fn(*args, **kwargs)
        ms = round((time.perf_counter() - t0) * 1000, 3)
        if isinstance(r, dict) and "recibo" not in r:
            corpo = dict(r)
            r["recibo"] = selar(fn.__module__.rsplit(".", 1)[-1],
                                {"args": args, "kwargs": kwargs}, corpo,
                                latencia_ms=ms)
        return r
    return wrapper

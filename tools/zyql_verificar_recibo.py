#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Serena Quantum Solutions
"""Verificador de recibo independente do produtor (RF-10, primeira metade).

Nao importa zyql_ten nem zyql_runtime. Reimplementa a canonicalizacao e o SHA3
de proposito: verificador que reusa o codigo auditado nao verifica nada.
Uso:
    python tools/zyql_verificar_recibo.py recibo.json
    cat recibo.json | python tools/zyql_verificar_recibo.py
Saida: ATENDE (0) ou REPROVA (1), com o motivo.
"""
import hashlib, json, sys

SCHEMA_ESPERADO = "1.0.0"
GRAMATICA_ESPERADA = "1.5.0"


def canon(obj):
    return json.dumps(obj, sort_keys=True, default=repr, skipkeys=True,
                      ensure_ascii=False, separators=(",", ":"))


def sha3(obj):
    return hashlib.sha3_256(canon(obj).encode()).hexdigest()


def verificar(payload):
    problemas = []
    if not isinstance(payload, dict):
        return ["entrada nao e um objeto JSON"]
    rec = payload.get("recibo")
    if not isinstance(rec, dict):
        return ["recibo ausente"]
    if rec.get("schema") != SCHEMA_ESPERADO:
        problemas.append(f"schema {rec.get('schema')} != {SCHEMA_ESPERADO}")
    if rec.get("gramatica") != GRAMATICA_ESPERADA:
        problemas.append(f"gramatica {rec.get('gramatica')} != {GRAMATICA_ESPERADA}")
    corpo = {k: v for k, v in payload.items() if k != "recibo"}
    if rec.get("saida_sha3") != sha3(corpo):
        problemas.append("sha3 da saida nao corresponde ao conteudo")
    if rec.get("assinatura") == "ausente":
        problemas.append("AVISO: sem assinatura pos-quantica (RF-06 aberto)")
    return problemas


def main(argv):
    if len(argv) > 1:
        payload = json.load(open(argv[1], encoding="utf-8"))
    else:
        payload = json.load(sys.stdin)
    problemas = verificar(payload)
    erros = [p for p in problemas if not p.startswith("AVISO")]
    for p in problemas:
        print(p, file=sys.stderr)
    if erros:
        print("REPROVA")
        return 1
    print("ATENDE")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

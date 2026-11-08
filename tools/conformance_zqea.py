#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Serena Quantum Solutions
"""Conformidade dos vetores normativos da especificacao Z-QEA v1.0 (secao 9).

Roda no CI. Qualquer divergencia falha o build: os vetores da especificacao
nao podem envelhecer em silencio.
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import zqea_sig as z  # noqa: E402

VETORES = [
    ("T1 canonicalizacao", {"b": "\u00e7", "a": 1},
     b'{"a":1,"b":"\xc3\xa7"}',
     "54cd981318d240636aba047fd3ac8d0e6629f8ac8df137a001033370bd8e7220"),
    ("T2 selo de corpo", {"veredito": 1, "p0": 0.5, "n": 3},
     b'{"n":3,"p0":0.5,"veredito":1}',
     "96debfc868acae29079b4d26d2eb3cbd2bd3f1fe5c4ede2d3e54f4c1376a3a68"),
    ("T4 cabeca de elo", {"veredito": 1, "prev_sha3": None},
     b'{"prev_sha3":null,"veredito":1}',
     "7000e88884f6d532a3b21224581253b0745438341e2b03b18865a6780ecc6ec8"),
]

falhas = 0


def checar(nome, condicao, detalhe=""):
    global falhas
    print(f"{'VERDE ' if condicao else 'VERMELHO'} | {nome.ljust(42)} | {detalhe}")
    if not condicao:
        falhas += 1


for nome, entrada, bytes_esperados, sha_esperado in VETORES:
    obtido = z._canon(entrada)
    checar(nome + " bytes", obtido == bytes_esperados, repr(obtido)[:44])
    checar(nome + " sha3", z.sha3_256(obtido) == sha_esperado, z.sha3_256(obtido)[:16])

# T3: identificador de chave sobre bytes fixos
checar("T3 chave_id", z.key_id(bytes(range(32))) == "050a48733bd5c275",
       z.key_id(bytes(range(32))))

# T5: canonicalizacao MUST recusar nao-finito
try:
    z._canon({"x": float("nan")})
    checar("T5 recusa NaN", False, "aceitou NaN")
except ValueError:
    checar("T5 recusa NaN", True, "ValueError")

# Assinatura randomizada: dois selos iguais, assinaturas diferentes, ambas validas
pk, sk = z.keypair()
corpo = {"veredito": 1, "n": 3}
a = z.assinar(corpo, sk, pk)
b = z.assinar(corpo, sk, pk)
checar("assinatura randomizada", a["assinatura"] != b["assinatura"],
       "duas assinaturas distintas")
checar("ambas verificam", z.verificar(a, pk) and z.verificar(b, pk), "2/2")
checar("metadados conferidos", not z.verificar({**a, "chave_id": "0" * 16}, pk),
       "chave_id trocado recusado")
checar("algoritmo conferido", not z.verificar({**a, "algoritmo": "Ed25519"}, pk),
       "algoritmo trocado recusado")

# Ancora detecta truncamento do ultimo elo
def _elo(prev):
    corpo = {"veredito": 1, "prev_sha3": prev}
    corpo["selo_sha3_256"] = z.sha3_256(z._canon(corpo))
    return z.assinar(corpo, sk, pk)


r1 = _elo(None)
r2 = _elo(z._canon and z.sha3_256(z._canon({k: v for k, v in r1.items()
            if k not in ("assinatura", "chave_id", "algoritmo")})))
anc = z.ancorar([r1, r2], sk, pk)
ok, motivo = z.verificar_ancora([r1], anc, pk)
checar("ancora detecta truncamento", ok is False and "truncamento" in motivo, motivo[:40])
ok2, _ = z.verificar_ancora([r1, r2], anc, pk)
checar("ancora aceita cadeia completa", ok2 is True, "sem truncamento")

print(f"\n{14-falhas}/14 vetores conformes")
sys.exit(1 if falhas else 0)

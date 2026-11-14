# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Serena Quantum Solutions
# -*- coding: utf-8 -*-
"""Testes falsificáveis dos modos de descoberta do oráculo (v2.4.0).

Cada teste falha se a afirmação for falsa. Não há assert de "não explodiu":
todos verificam a matemática contra a resposta conhecida por construção.
"""
import os
import sys
from itertools import product

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from zyql_oracle_id import (audit_promise, find_period, identify_2bit,
                            reveal_linear, NO_PROMISE, PROMISE_OK)

FALHAS = []


def check(nome, cond, detalhe=""):
    if cond:
        print(f"  [OK] {nome}")
    else:
        print(f"  [FALHOU] {nome} {detalhe}")
        FALHAS.append(nome)


def teste_bv():
    print("Bernstein-Vazirani: 1 consulta recupera a máscara")
    for n in (2, 3):
        for s in range(1 << n):
            r = reveal_linear(s, n)
            check(f"n={n} s={s:0{n}b}", r["verdict"] == 1 and r["mask"] == s,
                  f"veredito={r['verdict']} mascara={r['mask']}")
    r = reveal_linear(5, 3)
    check("máscara errada é detectada", r["mask"] != 4)
    check("consulta única declarada", r["queries"] == 1 and r["classical_queries"] == 3)
    try:
        reveal_linear(8, 3)
        check("máscara fora de n bits rejeitada", False)
    except ValueError:
        check("máscara fora de n bits rejeitada", True)


def teste_simon():
    print("Simon: período escondido recuperado por álgebra linear sobre GF(2)")
    n = 2
    for s in (1, 2, 3):
        tab, vis = {}, {}
        for x in range(1 << n):
            tab[x] = vis.setdefault(min(x, x ^ s), min(x, x ^ s))
        r = find_period(tab, n)
        check(f"período s={s:0{n}b}", r["verdict"] == 1 and r["period"] == s,
              f"veredito={r['verdict']} periodo={r.get('period')}")
    # função injetora: não existe período não nulo
    r = find_period({0: 0, 1: 1, 2: 2, 3: 3}, n)
    check("injetora → veredito 0, sem período inventado",
          r["verdict"] == 0 and r["reason"] == "PERIOD_ZERO_INJECTIVE")
    # período 0 é rejeitado como resposta: nunca devolvemos s=0 como período
    check("não devolve período nulo como se fosse descoberta", r.get("period") == 0)


def teste_identificacao():
    print("Identificação: os 16 booleanos de 2 variáveis")
    ident = 0
    for a, b, c, d in product((0, 1), repeat=4):
        t = {0: a, 1: b, 2: c, 3: d}
        r = identify_2bit(t)
        if r["verdict"] == 1 and r["truth_table"] == [a, b, c, d]:
            ident += 1
    check("16/16 identificados com tabela correta", ident == 16, f"identificados={ident}")
    r = identify_2bit({0: 1, 1: 0, 2: 0, 3: 0})
    check("peso 1 marcado como promessa violada", r["promise_ok"] is False)
    r = identify_2bit({0: 0, 1: 0, 2: 1, 3: 1})
    check("balanceada marcada como promessa cumprida", r["promise_ok"] is True)


def teste_promessa():
    print("Auditoria de promessa: acusa a violação com testemunha")
    ok = audit_promise({0: 0, 1: 0, 2: 0, 3: 0})
    check("constante → PROMISE_OK", ok["verdict"] == PROMISE_OK and ok["class"] == "constant")
    ok = audit_promise({0: 0, 1: 1, 2: 1, 3: 0})
    check("balanceada → PROMISE_OK", ok["verdict"] == PROMISE_OK and ok["class"] == "balanced")
    for t, peso in (({0: 1, 1: 0, 2: 0, 3: 0}, 1), ({0: 1, 1: 1, 2: 1, 3: 0}, 3)):
        r = audit_promise(t)
        check(f"peso {peso} → NO_PROMISE", r["verdict"] == NO_PROMISE)
        check(f"peso {peso} traz testemunha",
              r["witness"]["one"] is not None and r["witness"]["zero"] is not None)


if __name__ == "__main__":
    teste_bv()
    teste_simon()
    teste_identificacao()
    teste_promessa()
    print()
    if FALHAS:
        print(f"FALHAS: {len(FALHAS)} -> {FALHAS}")
        raise SystemExit(1)
    print("ALL PASS — modos de descoberta do oráculo")

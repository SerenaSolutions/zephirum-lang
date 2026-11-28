#!/usr/bin/env python3
"""
BATERIA DE REGRESSÃO — correcções Veritas / Red Team, 2026-11-28.
================================================================

Cada caso abaixo é um contraexemplo EXECUTADO pela auditoria matemática
(Veritas) ou pelos ataques do Red Team. Depois das correcções, cada um
passa a ser teste permanente: a falha não pode voltar.

Contrato:
  - expect_value: o motor decide, o veredicto é o CORRECTO e o
    verificador independente aceita o certificado.
  - expect_refusal: o motor RECUSA estruturalmente (§12, ValueError) —
    nunca um veredicto falso, nunca um UNKNOWN mudo.
"""
import sys

from nexa_core import parse_nexa, NCA
from verify_certificate import verify

PASSED = []


def _run(src):
    blocks = parse_nexa(src)
    res = NCA(blocks, "reg").compile()
    ok, why = verify(blocks, res["certificate"])
    return res, ok, why


def expect_value(src, want, name):
    res, ok, why = _run(src)
    assert res["answer"] == want, (name, "answer", res["answer"], "want", want)
    assert ok, (name, "verify", why)
    PASSED.append(name)
    print("PASS %-38s -> %s" % (name, want))


def expect_refusal(src, name):
    try:
        _run(src)
    except ValueError as e:
        PASSED.append(name)
        print("PASS %-38s -> REFUSED (%s)" % (name, str(e)[:50]))
        return
    raise SystemExit("FAIL: %s deveria recusar (§12) e não recusou" % name)


def _ident(n):
    rows = []
    for i in range(n):
        rows.append(",".join("1" if i == j else "0" for j in range(n)))
    return "; ".join(rows)


def main():
    # A1 — mediana exacta em 1e16 (float dava veredicto FALSO)
    expect_value("""ASK:
    question: median > 10000000000000000
CONTRACT:
    absolute_error: 0
MODEL:
    type: raw_data
    data: 10000000000000000, 10000000000000001
""", True, "A1 median 1e16 exact")

    expect_value("""ASK:
    question: median == 2.5
CONTRACT:
    absolute_error: 0
MODEL:
    type: raw_data
    data: 2, 3
""", True, "A1b median 5/2 exact")

    # A2 — safe_eval exacto
    expect_value("""ASK:
    question: value == 1/3
CONTRACT:
    absolute_error: 0
MODEL:
    type: expression
    expr: 1/3
""", True, "A2 1/3 == 1/3 exact")

    expect_value("""ASK:
    question: value > 0.1
CONTRACT:
    absolute_error: 0
MODEL:
    type: expression
    expr: 0.1 + 1/3 - 1/3
""", False, "A2b 0.1+1/3-1/3 not > 0.1")

    expect_refusal("""ASK:
    question: value == 2
CONTRACT:
    absolute_error: 0
MODEL:
    type: expression
    expr: 2 ** 0.5 * 2 ** 0.5
""", "A2c non-integer exponent")

    expect_refusal("""ASK:
    question: value > 0
CONTRACT:
    absolute_error: 0
MODEL:
    type: expression
    expr: (-8) ** 0.5
""", "A2d complex result")

    # A3 — determinante de matriz não quadrada
    expect_refusal("""ASK:
    question: det == 2
CONTRACT:
    absolute_error: 0
MODEL:
    type: triangular_det
    matrix: 1,0,5; 0,2,7
""", "A3 non-square 2x3")

    expect_refusal("""ASK:
    question: det == -3
CONTRACT:
    absolute_error: 0
MODEL:
    type: triangular_det
    matrix: 1,2,3; 4,5,6
""", "A3b non-square 2x3 laplace")

    # A4 — unknown_value fora dos limites
    expect_refusal("""ASK:
    question: sum > 5
CONTRACT:
    absolute_error: 0
MODEL:
    type: threshold_sum
    terms: 1
    unknown: x in 0..10
    unknown_value: 100
""", "A4 unknown_value out of bounds")

    # A5 — limites invertidos na média
    expect_refusal("""ASK:
    question: mean > 5
CONTRACT:
    absolute_error: 0
MODEL:
    type: mean_partial
    known:
    unknown_count: 2
    bounds: 10..0
""", "A5 inverted bounds")

    # A6 — hipótese terms_nonnegative violada pelos dados
    expect_refusal("""ASK:
    question: sum > 3
CONTRACT:
    absolute_error: 0
MODEL:
    type: threshold_sum
    terms: 5, -10
    assumption: terms_nonnegative
""", "A6 assumption violated")

    # F1 — concurrence == -1 em Bell é impossível (Red Team)
    expect_value("""ASK:
    question: concurrence == -1
CONTRACT:
    absolute_error: 0
MODEL:
    type: entanglement
    state: 0.70710678118654752, 0, 0, 0.70710678118654752
""", False, "F1 concurrence == -1 refused")

    # M1 — média com tudo conhecido é decidível
    expect_value("""ASK:
    question: mean > 1
CONTRACT:
    absolute_error: 0
MODEL:
    type: mean_partial
    known: 1,2,3
    unknown_count: 0
""", True, "M1 exact mean when u=0")

    # M3 — geométrica: n negativo ou fraccionário
    expect_refusal("""ASK:
    question: sum == 0
CONTRACT:
    absolute_error: 0
MODEL:
    type: geometric_series
    r: 2
    n: -2
""", "M3 geo n=-2")

    expect_refusal("""ASK:
    question: sum == 7
CONTRACT:
    absolute_error: 0
MODEL:
    type: geometric_series
    r: 2
    n: 2.9
""", "M3b geo n=2.9")

    # M4 — identidade 171x171: custo não pode estourar float
    expect_value("""ASK:
    question: det == 1
CONTRACT:
    absolute_error: 0
MODEL:
    type: triangular_det
    matrix: %s
""" % _ident(171), True, "M4 det 171x171 identity")

    # M5 — média com magnitude 10^400 permanece exacta
    expect_value("""ASK:
    question: mean > 4
CONTRACT:
    absolute_error: 0
MODEL:
    type: mean_partial
    known: %s
    unknown_count: 1
    bounds: 0..10
""" % ("1" + "0" * 400), True, "M5 mean 10^400 exact")

    # M8 — raw_data vazio é recusa estrutural
    expect_refusal("""ASK:
    question: median > 0
CONTRACT:
    absolute_error: 0
MODEL:
    type: raw_data
    data:
""", "M8 empty raw_data")

    print()
    print("RESULTADO: PASS — %d regressões Veritas/Red Team blindadas"
          % len(PASSED))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Fase 8, fatia 2: degraus geométrico e de média na linguagem."""
import random
from fractions import Fraction
from zephirum_lexer import parse_zephirum
from zephirum_vm import ZephirumVM, VMFault


def _cmp(v, op, t):
    return {">": v > t, "<": v < t, ">=": v >= t, "<=": v <= t, "==": v == t}[op]


def _question(blocks):
    parts = blocks["ASK"]["question"].rsplit(" ", 2)
    return parts[1], Fraction(parts[2])


def geometric_src(r, n, op, thr):
    return ("ASK:\n    question: sum %s %s\nMODEL:\n"
            "    type: geometric_series\n    r: %s\n    n: %d\n"
            % (op, thr, r, n))


def geometric_plan(src):
    blocks = parse_zephirum(src)
    model = blocks["MODEL"]
    if model.get("type") != "geometric_series":
        raise VMFault("B2 recusa: modelo não geométrico")
    r, n = Fraction(model["r"]), int(model["n"])
    op, thr = _question(blocks)
    if n < 0 or r == 1:
        raise VMFault("B2 recusa: domínio geométrico inválido")
    # r^0 + ... + r^n = (r^(n+1)-1)/(r-1), expresso em bytecode.
    prog = [("PUSH", 1)]
    for _ in range(n + 1):
        prog += [("PUSH", r), ("MUL",)]
    prog += [("PUSH", 1), ("SUB",), ("PUSH", r - 1), ("DIV",),
             ("CMPT", op, thr), ("HALT",)]
    return {"program": prog, "data": [], "budget": 0,
            "reference": sum(r ** i for i in range(n + 1)),
            "op": op, "thr": thr}


def mean_src(known, unknown_count, lo, hi, op, thr):
    known_text = ", ".join(str(x) for x in known)
    return ("ASK:\n    question: mean %s %s\nMODEL:\n"
            "    type: mean_partial\n    known: %s\n"
            "    unknown_count: %d\n    bounds: %s..%s\n"
            % (op, thr, known_text, unknown_count, lo, hi))


def mean_plan(src):
    blocks = parse_zephirum(src)
    model = blocks["MODEL"]
    if model.get("type") != "mean_partial":
        raise VMFault("B2 recusa: modelo não mean_partial")
    known = [Fraction(x) for x in model["known"].split(",")]
    u = int(model["unknown_count"])
    lo, hi = (Fraction(x) for x in model["bounds"].split(".."))
    op, thr = _question(blocks)
    total_n = len(known) + u
    low = (sum(known) + u * lo) / total_n
    high = (sum(known) + u * hi) / total_n
    if op != ">":
        raise VMFault("B2 recusa: média exacta nesta fatia exige '>'")
    if low > thr:
        verdict, bound = True, lo
    elif high <= thr:
        verdict, bound = False, hi
    else:
        return {"status": "UNKNOWN", "reference": None, "low": low, "high": high}
    # A testemunha carrega apenas os valores conhecidos; o limite é constante.
    prog = [("LOAD", i) for i in range(len(known))]
    prog += [("ADD",)] * (len(known) - 1)
    prog += [("PUSH", u * bound), ("ADD",), ("PUSH", total_n), ("DIV",),
             ("CMPT", op, thr), ("HALT",)]
    return {"status": "DECIDED_WITHOUT_EXECUTION", "program": prog,
            "data": known, "budget": len(known), "reference": verdict,
            "low": low, "high": high}


def run(plan):
    vm = ZephirumVM(plan.get("data", []), plan.get("budget", 0))
    return vm.run(plan["program"])


def main():
    random.seed(802)
    for _ in range(100):
        r = random.choice([Fraction(-3), Fraction(-2), Fraction(2), Fraction(3)])
        n = random.randint(0, 8)
        total = sum(r ** i for i in range(n + 1))
        thr = total - 1
        p = geometric_plan(geometric_src(r, n, ">", thr))
        ans, units, _ = run(p)
        assert ans is True and p["reference"] > thr and units == 0
    for known, u, lo, hi, thr in [
        ([Fraction("1.8"), Fraction("3.1"), Fraction("1.4")], 1, 6, 10, 3),
        ([Fraction("7.8"), Fraction("2.3"), Fraction("4.5")], 1, 1, 3, 4),
    ]:
        p = mean_plan(mean_src(known, u, lo, hi, ">", thr))
        assert p["status"] == "UNKNOWN" or run(p)[0] == p["reference"]
    print("B2 geometric_series + mean_partial: PASS — 100 geométricos, médias exactas")


if __name__ == "__main__":
    main()

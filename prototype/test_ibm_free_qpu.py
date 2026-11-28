#!/usr/bin/env python3
"""
TESTE OFFLINE do harness IBM FREE QUANTUM.
==========================================

Verifica o que NÃO depende de rede nem de token:
  T1  previsões exactas: cada distribuição ideal soma 1 e é Fraction
  T2  verify_counts aceita amostra fiel e REJEITA amostra corrompida
  T3  sem token: SKIP (§12), exit 3, nenhum job_id inventado
  T4  digest do recibo é determinístico
  T5  circuitos Qiskit: só constroem se o SDK existir (SKIP declarado)

A execução REAL na QPU fica para o dono, com o token dele.
"""
import io
import json
import os
import random
import sys
from contextlib import redirect_stdout
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import ibm_free_qpu as h
from decision_kernel import digest


def main():
    ideal = h.predict_exact()

    # T1 — previsões exactas
    for name, dist in ideal.items():
        assert all(isinstance(p, Fraction) for p in dist.values()), name
        assert sum(dist.values()) == 1, (name, sum(dist.values()))
    print("T1 PASS — %d distribuições ideais exactas, todas somam 1" % len(ideal))

    # T2 — verificação aceita amostra fiel, rejeita corrompida
    rng = random.Random(2026)
    dist = ideal["T3_bell"]
    outcomes = list(dist)
    probs = [float(p) for p in dist.values()]
    faithful = {}
    for _ in range(1024):
        o = rng.choices(outcomes, weights=probs)[0]
        faithful[o] = faithful.get(o, 0) + 1
    ok = h.verify_counts(faithful, dist, 1024)
    assert ok["ok"], ok
    corrupted = {"01": 1024}
    bad = h.verify_counts(corrupted, dist, 1024)
    assert not bad["ok"], bad
    print("T2 PASS — amostra fiel CONFIRMADA; amostra corrompida REJEITADA")

    # T3 — sem token: SKIP honesto, sem job inventado
    os.environ.pop("IBM_QUANTUM_TOKEN", None)
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = h.run_on_ibm(shots=64)
    out = buf.getvalue()
    assert code == 3, code
    assert "SKIP (§12)" in out, out
    assert "job_id" not in out, out
    print("T3 PASS — sem token: SKIP (§12), exit 3, zero job inventado")

    # T4 — digest determinístico
    rec = {"a": 1, "b": [2, 3], "c": {"d": "e"}}
    assert digest(rec) == digest(rec) == digest(json.loads(json.dumps(rec)))
    print("T4 PASS — digest do recibo determinístico (memória == JSON)")

    # T5 — circuitos Qiskit: só com SDK
    try:
        import qiskit  # noqa: F401
        circs = h.build_circuits()
        assert set(circs) == set(ideal), (set(circs), set(ideal))
        print("T5 PASS — %d circuitos construídos com qiskit %s"
              % (len(circs), qiskit.__version__))
    except ImportError:
        print("T5 SKIP (§12) — qiskit não instalado; circuitos não construídos "
              "(declarado, não fingido)")

    print()
    print("RESULTADO: PASS — harness pronto para o token do dono")


if __name__ == "__main__":
    main()

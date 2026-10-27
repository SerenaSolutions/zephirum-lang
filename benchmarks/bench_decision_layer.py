# -*- coding: utf-8 -*-
"""BENCHMARK-01 — a camada de DECISAO da ZEPHIRUM sob medida (issue #28).
Tese: nao competimos em velocidade de circuito; competimos em honestidade.
Kernel A (shots-to-verdict): DJ constante n=3, escada dobrando 64->8192,
PARADA NO PRIMEIRO VEREDITO; comparado com os shots exigidos por Hoeffding
(eps=0.05, banda 0.15) e com baseline fixo 8192.
Kernel B (refusal-fidelity): w em {0,1/8,1/4,3/8,1/2} => p0=(1-2w)^2;
200 tentativas por (w, shots); falsificavel: falso-confirma == 0 esperado."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from zyql_quantum_gate import ZYQLQuantumGate, MARGIN

EPSILON = 0.05
HOEFF_N = math.ceil(math.log(1 / EPSILON) / (2 * MARGIN ** 2))

def verdict(f, shots, seed):
    return ZYQLQuantumGate(3, f).run_quantum(shots=shots, seed=seed)

# ---------- KERNEL A: shots-to-verdict (parada antecipada) ----------
def kernel_a():
    const1 = lambda x: 1
    ladder = [64, 128, 256, 512, 1024, 2048, 4096, 8192]
    steps, used, verdict_final = 0, 0, None
    for s in ladder:
        steps += 1
        r = verdict(const1, s, seed=1701)
        used += s
        verdict_final = r["decision"]
        if verdict_final in (1, 0):
            break
    return {"shots_to_verdict": used, "ladder_steps": steps,
            "hoeffding_min_shots": HOEFF_N,
            "economy_vs_8192_pct": round(100 * (1 - used / 8192), 2),
            "verdict": str(verdict_final)}

# ---------- KERNEL B: refusal fidelity ----------
def kernel_b():
    from fractions import Fraction
    out = {}
    for w_num, w_den in [(0, 1), (1, 8), (1, 4), (3, 8), (1, 2)]:
        w = Fraction(w_num, w_den)
        true_p0 = float((1 - 2 * w) ** 2)
        gray = MARGIN < true_p0 < 1 - MARGIN
        row = {"true_p0": true_p0, "gray_zone": gray, "trials": {}, "expect": None}
        for shots in (64, 128, 256):
            false_conf, refuses, confirms = 0, 0, 0
            for t in range(200):
                k = round(float(w) * 8)   # fracao w de uns: os k primeiros inputs
                f = lambda x, kk=k: 1 if x < kk else 0
                r = verdict(f, shots, seed=1000 + t)
                if r["decision"] in (1, 0):
                    confirms += 1
                    if gray: false_conf += 1
                else:
                    refuses += 1
            bound = 2 * math.exp(-2 * shots * MARGIN ** 2)
            row["trials"][shots] = {"confirms": confirms, "refuses": refuses,
                                    "false_confirms": false_conf}
            row["expect"] = "CONFIRM" if true_p0 >= 1 - MARGIN else "REFUSE"
            # semantica trivalente: confirma SO se p0_verdadeiro >= 1-margem;
            # abaixo da margem a resposta correta e REFUSED_BALANCED (recusa informativa)
            ok = (false_conf == 0) if gray else (confirms > 0 if true_p0 >= 1 - MARGIN else refuses > 0)
            row.setdefault("pass_all", True)
            row["pass_all"] = row["pass_all"] and ok
        out[str(w)] = row
    return out

if __name__ == "__main__":
    import json
    A = kernel_a(); B = kernel_b()
    B_ok = all(r["pass_all"] for r in B.values())
    result = {"modulo": "benchmarks/bench_decision_layer.py", "kernel_A": A,
              "kernel_B": B, "kernel_B_all_pass": B_ok,
              "veredito_global": "BENCHMARK_OK" if (A["verdict"] == "1" and B_ok) else "BENCHMARK_REFUSED"}
    print(json.dumps({"kernel_A": A, "kernel_B_all_pass": B_ok,
                      "veredito_global": result["veredito_global"]}, indent=1))
    os.makedirs(os.path.join(os.path.dirname(__file__), "..", "experiments"), exist_ok=True)
    json.dump(result, open(os.path.join(os.path.dirname(__file__), "..", "experiments",
        "bench_decision_receipt.json"), "w"), indent=1)

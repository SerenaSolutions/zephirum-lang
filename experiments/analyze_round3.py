# -*- coding: utf-8 -*-
"""COLHEITA DA RODADA 3 (escalada trivalente). Sela recibo Z-QEA (regra limpa)."""
import os, json, time, hashlib
import numpy as np
from qiskit_ibm_runtime import QiskitRuntimeService

TOKEN = os.environ["IBM_TOKEN"]
META = json.load(open("round3_job_meta.json")); SHOTS = META["shots"]
FUSION = {"00": "ch0", "01": "ch1", "10": "ch2"}

svc = QiskitRuntimeService(token=TOKEN, channel="ibm_quantum_platform", instance="auto")
job = svc.job(META["job_id"])
print("status:", job.status())
st = str(job.status()).upper()
if "DONE" not in st:
    if "ERROR" in st: print("JOB COM ERRO"); raise SystemExit(1)
    raise SystemExit(0)

res = [r.data.c.get_counts() for r in job.result()]
assert len(res) == 15

def p_of(counts, target):
    return counts.get(target, 0) / SHOTS

dj_rows, grover_rows, word_rows = [], [], []
i = 0
for n in (4, 5):
    zero = "0" * n
    for caso in ("const-1", "const-0", "balanceado"):
        c = res[i]; i += 1
        p0 = p_of(c, zero)
        if caso == "const-1":   dec, exp = "1", p0 > 0.9
        elif caso == "const-0": dec, exp = "0", p0 > 0.9
        else:                   dec, exp = "REFUSED", p0 < 0.1
        dj_rows.append({"n": n, "caso": caso, "p_zero_n": round(p0, 4),
                        "decisao": dec, "passou": bool(exp)})
gtheory = {1: 1.0, 2: 0.25, 3: 1.0}
for it in (1, 2, 3):
    c = res[i]; i += 1
    grover_rows.append({"iteracoes": it, "p_11": round(p_of(c, "11"), 4),
                        "teoria_p11": gtheory[it],
                        "dominante": max(c, key=c.get)})
W_theory = {1: "ch2", 2: "ch1", 0: "ch0"}
for k in range(7, 13):
    c = res[i]; i += 1
    dom_bit = max(c, key=c.get)
    dom = FUSION.get(dom_bit, "FORBIDDEN")
    word_rows.append({"k": k, "dominante_medido": dom, "previsto_periodo3": W_theory[k % 3],
                      "bate": dom == W_theory[k % 3]})

dj_pass = sum(1 for r in dj_rows if r["passou"])
word_pass = sum(1 for r in word_rows if r["bate"])
rec = {
    "spec": "Z-QEA", "modulo": "experiments/round3_battery.py + analyze_round3.py",
    "data": time.strftime("%Y-%m-%dT%H:%M:%S-03:00"),
    "modo": "HARDWARE REAL (IBM Heron ibm_fez, laboratorio de teste, sem endosso)",
    "job_id": META["job_id"], "shots": SHOTS, "circuitos": 15,
    "rodada": "3 — ESCALADA DA DECISAO TRIVALENTE",
    "C8_DJ_escala": {"pontos": 6, "aprovados": f"{dj_pass}/6",
        "nota": "p(0^n)>0.9 decide const (1 ou 0); p(0^n)<0.1 => REFUSED (balanceado); 1 chamada de oraculo",
        "detalhe": dj_rows},
    "C9_GROVER_amplificacao": {"pontos": 3, "teoria": "1 iter:1.0, 2:0.25, 3:1.0 (rotacao periodica)",
        "detalhe": grover_rows},
    "C10_palavras_k7_12": {"pontos": 6, "aprovados_periodo3": f"{word_pass}/6", "detalhe": word_rows},
    "selo_regra": "selo = SHA3-256 sobre json.dumps(recibo, sort_keys=True, ensure_ascii=True, default=str) com o campo selo_sha3_256 REMOVIDO da entrada",
}
canon = json.dumps({k: v for k, v in rec.items() if k != "selo_sha3_256"},
                   sort_keys=True, ensure_ascii=True, default=str)
rec["selo_sha3_256"] = hashlib.sha3_256(canon.encode()).hexdigest()
json.dump(rec, open("round3_receipt.json", "w"), indent=2, default=str)
print("SELO R3:", rec["selo_sha3_256"])
print("resumo:", {"dj": f"{dj_pass}/6", "grover_dom": [g['dominante'] for g in grover_rows], "palavras": f"{word_pass}/6"})

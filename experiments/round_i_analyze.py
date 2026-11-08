# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Serena Quantum Solutions
# -*- coding: utf-8 -*-
"""RODADA I — análise do GATE DE MEMÓRIA (idempotente; sela só quando DONE).

Executa a regra de decisão SELADA no protocolo antes do dado:
  veredito 1  = memória detectada (revival na variante MEMÓRIA, controle limpo)
  veredito 0  = regime markoviano confirmado nesta profundidade
  REFUSED     = inconclusivo / anomalia de controle / instrumento comprometido
Sela recibo v2 (SHA3-256 + ML-DSA-44) encadeado no selo da Rodada D.
"""
import json, math, os, sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, "/app/conversations/6a47cbde110fe595b9a5a983/poc")
from zqea_pq import quantum_receipt_id, entropy_provenance, sign_receipt, sha3_seal

STEPS = [0, 1, 2, 3, 4]
BASES = ["X", "Y", "Z"]

meta = json.load(open(os.path.join(HERE, "round_i_jobs.json")))
EPS, SHOTS = meta["eps"], meta["shots"]

from qiskit_ibm_runtime import QiskitRuntimeService
service = QiskitRuntimeService(token=os.environ["IBM_QUANTUM_TOKEN"],
                               channel="ibm_quantum_platform")
job = service.job(meta["job_id"])
st = str(job.status())
print("job", meta["job_id"], ":", st)
if st != "DONE":
    print("pendente: job ainda nao DONE; rode de novo mais tarde")
    sys.exit(0)


def counts_of(pub_result):
    for attr in ("c", "meas"):
        try:
            return dict(getattr(pub_result.data, attr).get_counts())
        except Exception:
            continue
    raise RuntimeError("sem counts no resultado")


res = job.result()
table = {}
for cell, pub in zip(meta["cells"], res):
    key = (cell["variant"], cell["state"], cell["basis"], cell["k"])
    table[key] = counts_of(pub)


def bloch(p0):
    return 2.0 * p0 - 1.0


def trace_distance(variant, k):
    pa, pb = {}, {}
    for basis in BASES:
        for state, store in (("ket0", pa), ("ketplus", pb)):
            key = (variant, state, basis, k)
            if key not in table and k == 0:
                key = ("memory", state, basis, 0)
            counts = table[key]
            total = sum(counts.values())
            p0 = sum(v for b, v in counts.items() if b[-1] == "0") / total
            store[basis] = bloch(p0)
    return 0.5 * math.sqrt((pa["X"] - pb["X"]) ** 2 + (pa["Y"] - pb["Y"]) ** 2 +
                           (pa["Z"] - pb["Z"]) ** 2)


band = meta["band"]
D = {v: [round(trace_distance(v, k), 4) for k in STEPS]
     for v in ("memory", "memoryless")}
DELTA = {v: [round(D[v][i + 1] - D[v][i], 4) for i in range(len(STEPS) - 1)]
         for v in D}

rev_mem = [d for d in DELTA["memory"] if d > band]
rev_ctl = [d for d in DELTA["memoryless"] if d > band]
d0_ok = abs(D["memory"][0] - 0.7071) <= band

if not d0_ok:
    veredito = "REFUSED: instrumento comprometido (D(0) fora da banda)"
elif rev_mem and rev_ctl:
    veredito = "REFUSED: anomalia (controle tambem apresentou revival)"
elif rev_mem:
    veredito = ("1: MEMORIA DETECTADA (revival %.4f > banda %.4f) — banda Hoeffding "
                "nao automaticamente valida nesta profundidade" % (max(rev_mem), band))
elif rev_ctl:
    veredito = "REFUSED: anomalia (somente o controle apresentou revival)"
else:
    veredito = "0: REGIME MARKOVIANO CONFIRMADO (nenhum revival acima da banda)"

rec = {"spec": "Z-QEA/2.2", "modulo": "RODADA I — GATE DE MEMORIA",
       "data": datetime.now(timezone.utc).isoformat(),
       "protocolo": meta["protocolo"], "backend": meta["backend"],
       "job_id": meta["job_id"], "shots": SHOTS, "eps": EPS, "band_D": band,
       "D": D, "delta": DELTA, "D0_esperado": 0.7071, "D0_ok": d0_ok,
       "revivals_memoria": rev_mem, "revivals_controle": rev_ctl,
       "veredito": veredito,
       "contagens_cruas": {"%s|%s|%s|%d" % k: v for k, v in table.items()},
       "receipt_id": quantum_receipt_id(), "entropia": entropy_provenance()}
prev = json.load(open(os.path.join(HERE, "round_d_receipt.json")))
rec["previous_seal"] = prev["selo_sha3_256"]
rec["assinatura_pq"] = sign_receipt({k: v for k, v in rec.items()
                                     if k not in ("selo_sha3_256", "assinatura_pq")})
rec["selo_sha3_256"] = sha3_seal({k: v for k, v in rec.items() if k != "selo_sha3_256"})
out = os.path.join(HERE, "round_i_receipt.json")
json.dump(rec, open(out, "w"), indent=2, ensure_ascii=False)
print("D memoria   :", D["memory"], "Δ", DELTA["memory"])
print("D controle  :", D["memoryless"], "Δ", DELTA["memoryless"])
print("banda D:", band)
print("VEREDITO RODADA I:", veredito)
print("recibo selado:", out)

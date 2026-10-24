# -*- coding: utf-8 -*-
"""RODADA F — analise das fronteiras (CHSH + QEC + Grover n=4, kingston).
Executavel varias vezes: so sela quando TODOS os jobs estao DONE.
Recibo v2 (ML-DSA-44 + entropia quantica) ENCADEADO no selo da Rodada E."""
import os, sys, json, math
from datetime import datetime, timezone
sys.path.insert(0, "/app/conversations/6a47cbde110fe595b9a5a983/poc")
from zqea_pq import quantum_receipt_id, entropy_provenance, sign_receipt, sha3_seal

HERE = os.path.dirname(os.path.abspath(__file__))
meta = json.load(open(os.path.join(HERE, "round_f_jobs.json")))
TOKEN = os.environ["IBM_QUANTUM_TOKEN"]
from qiskit_ibm_runtime import QiskitRuntimeService
service = QiskitRuntimeService(token=TOKEN, channel="ibm_quantum_platform", instance="auto")
SHOTS = meta["shots"]

def counts_of(pub_result):
    for attr in ("c", "meas"):
        try:
            return dict(getattr(pub_result.data, attr).get_counts())
        except Exception:
            continue
    raise RuntimeError("sem counts no resultado")

def correl(counts):
    n = sum(counts.values())
    e = (counts.get("00", 0) + counts.get("11", 0) - counts.get("01", 0) - counts.get("10", 0)) / n
    return e

res = {}
all_done = True

# 1) CHSH
job = service.job(meta["jobs"]["chsh"]); st = str(job.status())
print(f"chsh ({meta['jobs']['chsh']}): {st}")
if st != "DONE": all_done = False
else:
    r = job.result()
    es = [correl(counts_of(r[i])) for i in range(4)]
    S = es[0] - es[1] + es[2] + es[3]   # (0,pi/4),(0,3pi/4),(pi/2,pi/4),(pi/2,3pi/4)
    if S >= 2.20: ver = "1"
    elif S <= 2.0: ver = "0"
    else: ver = "REFUSED"
    res["chsh"] = {"job": meta["jobs"]["chsh"], "correlacoes": [round(e, 4) for e in es],
                   "S": round(S, 4), "tsirelson": 2.8284, "limite_classico": 2.0,
                   "veredito": ver}

# 2) QEC: controle (sem codigo) + codificado
job = service.job(meta["jobs"]["qec"]); st = str(job.status())
print(f"qec ({meta['jobs']['qec']}): {st}")
if st != "DONE": all_done = False
else:
    r = job.result()
    ctrl = counts_of(r[0])
    enc = counts_of(r[1])
    p1_ctrl = (ctrl.get("00000", 0) + sum(v for k, v in ctrl.items() if k[-5] == "1")) / SHOTS
    # erro fisico: bit de dados errado no controle (leitura X de |+> -> '1')
    erro_fisico = 1 - p1_ctrl if p1_ctrl <= 1 else 0
    # codificado: maioria dos 3 bits de dados (bits 2,1,0 do clássico? medidos q0,q1,q2 -> c0,c1,c2)
    ok = 0; per_qubit = [0, 0, 0]
    for k, v in enc.items():
        # counts string: c4 c3 c2 c1 c0 -> dados = c0(q0), c1(q1), c2(q2)
        bits = [k[-1], k[-2], k[-3]]   # q0, q1, q2
        maj = 1 if sum(int(b) for b in bits) >= 2 else 0
        if maj == 1: ok += v
        for i, b in enumerate(bits):
            if b == "1": per_qubit[i] += v
    p_logico_ok = ok / SHOTS
    erro_logico = 1 - p_logico_ok
    p_fisico_medio = sum(per_qubit) / (3 * SHOTS)
    ver = "1" if erro_logico < p_fisico_medio else "REFUSED"
    res["qec"] = {"job": meta["jobs"]["qec"],
                   "erro_logico": round(erro_logico, 4),
                   "p_fisico_medio": round(p_fisico_medio, 4),
                   "erro_fisico_baseline": round(1 - p1_ctrl, 4),
                   "veredito": ver,
                   "nota": "PROTEGIDO se erro logico < fisico medio"}

# 3) Grover n=4
job = service.job(meta["jobs"]["grover4"]); st = str(job.status())
print(f"grover4 ({meta['jobs']['grover4']}): {st}")
if st != "DONE": all_done = False
else:
    counts = counts_of(job.result()[0])
    keys = sorted(counts, key=counts.get, reverse=True)
    alvo_read = meta["alvo_grover"][::-1]
    p_alvo = counts.get(alvo_read, 0) / SHOTS
    p_segundo = counts[keys[0]] / SHOTS if keys[0] != alvo_read else (counts.get(keys[1], 0) / SHOTS if len(keys) > 1 else 0)
    if p_alvo >= 0.50 and p_alvo >= 2 * p_segundo: ver = "1"
    elif p_alvo <= 0.20: ver = "0"
    else: ver = "REFUSED"
    res["grover4"] = {"job": meta["jobs"]["grover4"], "alvo": meta["alvo_grover"],
                      "p_alvo": round(p_alvo, 4), "p_segundo": round(p_segundo, 4),
                      "ideal": 0.957, "veredito": ver}

if not all_done:
    print("pendente: jobs ainda nao DONE; rode de novo mais tarde"); sys.exit(0)

chsh_ok = res.get("chsh", {}).get("veredito") == "1"
qec_ok = res.get("qec", {}).get("veredito") == "1"
gr_ok = res.get("grover4", {}).get("veredito") == "1"
veredito = ("FRONTEIRAS VENCIDAS: nao-localidade (S=%.2f), correcao de erro valida "
            "(logico < fisico), Grover n=4 dominante" % res["chsh"]["S"]
            if (chsh_ok and qec_ok and gr_ok)
            else "FRONTEIRAS PARCIAIS: vereditos honestos registrados (a falha e resultado)")

rec = {"spec": "Z-QEA/2.2", "modulo": "RODADA F",
       "data": datetime.now(timezone.utc).isoformat(),
       "protocolo": meta["protocolo"], "backend": meta["backend"],
       "bandas": meta["bandas"], "resultados": res, "veredito": veredito,
       "receipt_id": quantum_receipt_id(),
       "entropia": entropy_provenance()}
prev_path = os.path.join(HERE, "round_e_receipt.json")
if not os.path.isfile(prev_path): prev_path = os.path.join(HERE, "round_d_receipt.json")
if not os.path.isfile(prev_path): prev_path = os.path.join(HERE, "round_c_receipt.json")
prev = json.load(open(prev_path))
rec["previous_seal"] = prev["selo_sha3_256"]
rec["assinatura_pq"] = sign_receipt({k: v for k, v in rec.items() if k not in ("selo_sha3_256", "assinatura_pq")})
rec["selo_sha3_256"] = sha3_seal({k: v for k, v in rec.items() if k != "selo_sha3_256"})
out = os.path.join(HERE, "round_f_receipt.json")
json.dump(rec, open(out, "w"), indent=2, ensure_ascii=False)
print("VEREDITO RODADA F:", veredito)
print("recibo selado:", out)

# -*- coding: utf-8 -*-
"""COLHEITA DA VARREDURA v2 (calibrada). Se o job nao estiver DONE, imprime status e sai 0
(quem chama re-agenda). Se DONE: mitiga pela matriz de confusao, roda chi2 mitigado,
sela recibo Z-QEA (regra limpa: selo excluido da entrada canonica)."""
import os, json, time, hashlib
import numpy as np
from scipy.stats import chi2 as chi2dist
from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit.circuit.library import UnitaryGate
import math

TOKEN = os.environ["IBM_TOKEN"]
META = json.load(open("sweep2_job_meta.json"))
SHOTS = META["shots"]; LABELS = META["labels"]
FUSION = {"00": "ch0", "01": "ch1", "10": "ch2", "11": "FORBIDDEN"}

def B_R(t):  return np.array([[math.cos(t), 0, math.sin(t)], [0, 1, 0], [-math.sin(t), 0, math.cos(t)]])
def B_S(t):  return np.array([[1, 0, 0], [0, math.cos(t), math.sin(t)], [0, -math.sin(t), math.cos(t)]])
def lift(U3):
    U4 = np.eye(4); U4[:3, :3] = U3; return U4

def theory(U3):
    qc = QuantumCircuit(2); qc.append(UnitaryGate(lift(U3)), [0, 1])
    d = Statevector(qc).probabilities_dict()
    return {FUSION[k]: v for k, v in d.items()}

def counts4(raw):
    return {l: raw.get(l, 0) for l in LABELS}

def chi2_stat(p, probs_theory):
    chi, df = 0.0, -1
    for c in ["ch0", "ch1", "ch2"]:
        e = probs_theory.get(c, 0.0); o = p.get(c, 0.0)
        if e > 0: chi += (o - e) ** 2 / e; df += 1
    return round(chi, 3), max(df, 1), round(float(chi2dist.sf(chi, max(df, 1))), 4)

svc = QiskitRuntimeService(token=TOKEN, channel="ibm_quantum_platform", instance="auto")
job = svc.job(META["job_id"])
status = job.status()
print("status:", status)
if str(status).upper().find("DONE") < 0 or "ERROR" in str(status).upper():
    # ainda na fila ou erro: quem chama decide re-agendar
    if "ERROR" in str(status).upper():
        print("JOB COM ERRO:", status); raise SystemExit(1)
    raise SystemExit(0)

res = [r.data.c.get_counts() for r in job.result()]
spec = [tuple(s) for s in META["specs"]]
assert len(res) == 30

# ---- D_cal: matriz de confusao C[medido][preparado]
C = np.zeros((4, 4))
for i, lab in enumerate(LABELS):
    c = counts4(res[i])
    for m in range(4):
        C[m, i] = c[LABELS[m]] / SHOTS
diag = [round(float(C[i, i]), 4) for i in range(4)]
Cinv = np.linalg.inv(C)

def mitigate(raw_counts):
    p = np.array([raw_counts[l] for l in LABELS]) / SHOTS
    q = Cinv @ p
    q = np.clip(q, 0, None); q = q / q.sum()
    return {FUSION[LABELS[i]]: float(q[i]) for i in range(4)}

def analyze(tag, idx, U3, kpi):
    raw = counts4(res[idx]); p_mit = mitigate(raw)
    th = theory(U3)
    chi_r, df, p_r = chi2_stat({FUSION[l]: raw[l]/SHOTS for l in LABELS}, th)
    chi_m, df2, p_m = chi2_stat(p_mit, th)
    kpi.append({
        tag: True, "indice": idx,
        "chi2_raw": chi_r, "p_raw": p_r, "chi2_mitigado": chi_m, "p_mitigado": p_m,
        "canal_dominante_mitigado": max(p_mit, key=p_mit.get),
        "canal_dominante_teoria": max(th, key=th.get),
        "p_mitigado": {kk: round(v, 5) for kk, v in p_mit.items()},
    })

A2, B2 = [], []
for k in range(1, 11):
    t = math.pi * k / 10
    analyze("A2_RS", 4 + (k - 1) * 2, B_R(t) @ B_S(t), A2)
    analyze("A2_SR", 5 + (k - 1) * 2, B_S(t) @ B_R(t), A2)
BR, BS = B_R(math.pi / 2), B_S(math.pi / 2)
W = BR @ BS
for k in range(1, 7):
    analyze("B2_word", 24 + (k - 1), np.linalg.matrix_power(W, k), B2)

pass_raw = sum(1 for r in A2 if r["p_raw"] > 0.05)
pass_mit = sum(1 for r in A2 if r["p_mitigado"] > 0.05)
dom_ok = sum(1 for r in A2 if r["canal_dominante_mitigado"] == r["canal_dominante_teoria"])

rec = {
    "spec": "Z-QEA", "modulo": "experiments/scientific_sweep2.py + analyze_sweep2.py",
    "data": time.strftime("%Y-%m-%dT%H:%M:%S-03:00"),
    "modo": "HARDWARE REAL (IBM Heron ibm_fez, laboratorio de teste, sem endosso) + MITIGACAO DE LEITURA",
    "job_id": META["job_id"], "shots": SHOTS, "circuitos": 30,
    "hipotese": "a reprovacao do chi2 na v1 (0/10) foi vies de leitura (instrumento), nao fisica",
    "calibracao": {"fidelidade_leitura_diagonal": diag, "fora_da_diagonal_max": round(float(C.max() - min(diag)), 4)},
    "A2_sweep_angulo_mitigado": {
        "pontos": 20, "chi2_5pct_aprovados_raw": f"{pass_raw}/20",
        "chi2_5pct_aprovados_mitigado": f"{pass_mit}/20",
        "canais_dominantes_corretos_mitigado": f"{dom_ok}/20",
        "detalhe": A2,
    },
    "B2_palavra_mitigado": {"pontos": 6, "detalhe": B2},
    "comparacao_v1": {"job_v1": "dbbuh17i0auc73dtpaeg", "chi2_v1_raw": "0/10 aprovados"},
    "selo_regra": "selo = SHA3-256 sobre json.dumps(recibo, sort_keys=True, ensure_ascii=True, default=str) com o campo selo_sha3_256 REMOVIDO da entrada",
}
canon = json.dumps({k: v for k, v in rec.items() if k != "selo_sha3_256"},
                   sort_keys=True, ensure_ascii=True, default=str)
rec["selo_sha3_256"] = hashlib.sha3_256(canon.encode()).hexdigest()
json.dump(rec, open("scientific_sweep2_receipt.json", "w"), indent=2, default=str)
print("SELO v2:", rec["selo_sha3_256"])
print("resumo:", {"chi2_mitigado_aprovados": f"{pass_mit}/20", "dominantes_ok": f"{dom_ok}/20", "diag": diag})

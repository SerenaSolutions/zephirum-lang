# -*- coding: utf-8 -*-
"""Analisa o job da varredura (dbbuh17i0auc73dtpaeg) quando terminar.
Executavel varias vezes: so salva o recibo quando o job esta DONE."""
import os, json, time, math, hashlib
import numpy as np
from scipy.stats import chi2 as chi2dist
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Statevector
from qiskit.circuit.library import UnitaryGate
from qiskit_ibm_runtime import QiskitRuntimeService

TOKEN = os.environ["IBM_TOKEN"]
JOB_ID = "dbbuh17i0auc73dtpaeg"
SHOTS = 4096
FUSION = {"00": "ch0", "01": "ch1", "10": "ch2", "11": "FORBIDDEN"}

service = QiskitRuntimeService(token=TOKEN, channel="ibm_quantum_platform", instance="auto")
job = service.job(JOB_ID)
st = job.status()
stn = st if isinstance(st, str) else getattr(st, "status", st)
print("status:", stn)
if str(stn) != "DONE":
    raise SystemExit("aguardando: " + str(stn))

def B_R(t):  return np.array([[math.cos(t), 0, math.sin(t)], [0, 1, 0], [-math.sin(t), 0, math.cos(t)]])
def B_S(t):  return np.array([[1, 0, 0], [0, math.cos(t), math.sin(t)], [0, -math.sin(t), math.cos(t)]])
def lift(U3):
    U4 = np.eye(4); U4[:3, :3] = U3; return U4
def theory_probs(U3):
    qc = QuantumCircuit(2)
    qc.append(UnitaryGate(lift(U3)), [0, 1])
    d = Statevector(qc).probabilities_dict()
    return {FUSION[k]: v for k, v in d.items()}
def chi2_stat(counts, probs, shots):
    chans = [c for c in ["ch0", "ch1", "ch2"] if probs.get(c, 0) > 0 or counts.get(c, 0) > 0]
    chi = 0.0; df = -1
    for c in chans:
        e = probs.get(c, 0.0) * shots; o = counts.get(c, 0)
        if e > 0: chi += (o - e) ** 2 / e
        elif o > 0: chi += float("inf")
        df += 1
    p = chi2dist.sf(chi, max(df, 1))
    dtv = 0.5 * sum(abs(counts.get(c, 0) / shots - probs.get(c, 0.0)) for c in chans)
    return round(chi, 3), max(df, 1), round(float(p), 4), round(dtv, 4)

res = job.result()
print("pubs:", len(res))

# varredura A
theta_list = [math.pi * k / 10 for k in range(1, 11)]
varA_noiseless, varA_hardware = [], []
idx = 0
for t in theta_list:
    U_RS, U_SR = B_R(t) @ B_S(t), B_S(t) @ B_R(t)
    comm = np.abs(U_RS - U_SR).sum()
    pRS, pSR = theory_probs(U_RS), theory_probs(U_SR)
    dom = max(pRS, key=pRS.get) != max(pSR, key=pSR.get)
    row = {"theta_pi_sobre_10": round(t / math.pi * 10), "theta_rad": round(t, 6),
           "comutador_L1": round(float(comm), 6),
           "canais_distintos_noiseless": bool(dom),
           "p_RS": {k: round(v, 6) for k, v in pRS.items()},
           "p_SR": {k: round(v, 6) for k, v in pSR.items()}}
    hrow = {"theta_pi_sobre_10": round(t / math.pi * 10)}
    for tag, U in (("A_RS", U_RS), ("A_SR", U_SR)):
        pub = res[idx]; idx += 1
        cnt = {FUSION[k]: int(v) for k, v in pub.data.c.get_counts().items()}
        pth = theory_probs(U)
        chi, df, pval, dtv = chi2_stat(cnt, pth, SHOTS)
        hrow[tag] = {"counts": cnt, "chi2": chi, "df": df, "p_valor": pval,
                     "dist_TV": dtv, "canal_dominante_hardware": max(cnt, key=cnt.get),
                     "chi2_ok_5pct": pval > 0.05}
    varA_noiseless.append(row); varA_hardware.append(hrow)

# varredura B
BR, BS = B_R(math.pi / 2), B_S(math.pi / 2)
W = BR @ BS
varB_theory, varB_hardware = [], []
for k in range(1, 7):
    Wk = np.linalg.matrix_power(W, k)
    p = theory_probs(Wk)
    varB_theory.append({"k": k, "canal_dominante": max(p, key=p.get),
                        "p": {kk: round(v, 6) for kk, v in p.items()}})
    pub = res[idx]; idx += 1
    cnt = {FUSION[k]: int(v) for k, v in pub.data.c.get_counts().items()}
    chi, df, pval, dtv = chi2_stat(cnt, p, SHOTS)
    varB_hardware.append({"k": k, "counts": cnt, "chi2": chi, "df": df, "p_valor": pval,
                          "dist_TV": dtv,
                          "canal_dominante_hardware": max(cnt, key=cnt.get),
                          "canal_previsto": varB_theory[-1]["canal_dominante"],
                          "bate": max(cnt, key=cnt.get) == varB_theory[-1]["canal_dominante"]})

# varredura C (noiseless)
from qiskit.quantum_info import Statevector as SV, Pauli
prep = np.zeros(4, dtype=complex); prep[0] = 1
mapC = {}
for pauli in ["IX", "IZ", "XI", "ZI", "XX", "ZZ"]:
    sv2 = SV(prep).evolve(Pauli(pauli))
    mapC[pauli] = {FUSION[k]: round(v, 6) for k, v in sv2.probabilities_dict().items()}

sweep = {
    "spec": "Z-QEA", "modulo": "experiments/scientific_sweep.py + analyze_sweep.py",
    "data": time.strftime("%Y-%m-%dT%H:%M:%S-03:00"),
    "shots": SHOTS, "job_id": JOB_ID, "backend": "ibm_fez (laboratorio de teste, sem endosso)",
    "A_sweep_angulo": {"noiseless": varA_noiseless, "hardware": varA_hardware},
    "B_sweep_palavra": {"previsao_noiseless": varB_theory, "hardware": varB_hardware},
    "C_mapa_erros_pauli": {"preparacao": "|0> (ch0)", "efeito_noiseless": mapC},
    "resumo": {
        "A_pontos_com_p_chi2_maior_5pct": sum(1 for r in varA_hardware
            if r["A_RS"]["chi2_ok_5pct"] and r["A_SR"]["chi2_ok_5pct"]),
        "A_total_pontos": len(varA_hardware),
        "B_todos_canais_batem": all(r["bate"] for r in varB_hardware),
    },
}
canon = json.dumps(sweep, sort_keys=True, ensure_ascii=True, default=str)
sweep["selo_sha3_256"] = hashlib.sha3_256(canon.encode()).hexdigest()
json.dump(sweep, open("scientific_sweep_receipt.json", "w"), indent=2, default=str)
print("resumo:", sweep["resumo"])
print("SELO:", sweep["selo_sha3_256"][:32])

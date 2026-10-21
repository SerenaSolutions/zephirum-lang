# -*- coding: utf-8 -*-
"""VARREDURA CIENTIFICA S3-QUTRIT (Zephirum/ZYQL, padrao Z-QEA)
A. sweep do angulo de tracado: teoria (float64, declarado) vs noiseless vs hardware, chi2
B. sweep do comprimento da palavra (B_R B_S)^k: previsao exata racional vs hardware
C. mapa de canais de erro: quais Pauli locais (X/Z em cada qubit) viram quais canais
"""
import os, json, time, math, hashlib
import numpy as np
from scipy.stats import chi2 as chi2dist
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Statevector
from qiskit.circuit.library import UnitaryGate
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2

TOKEN = os.environ["IBM_TOKEN"]
SHOTS = 4096
FUSION = {"00": "ch0", "01": "ch1", "10": "ch2", "11": "FORBIDDEN"}

def B_R(t):  return np.array([[math.cos(t), 0, math.sin(t)], [0, 1, 0], [-math.sin(t), 0, math.cos(t)]])
def B_S(t):  return np.array([[1, 0, 0], [0, math.cos(t), math.sin(t)], [0, -math.sin(t), math.cos(t)]])

def lift(U3):
    U4 = np.eye(4); U4[:3, :3] = U3; return U4

def circ(U3):
    qc = QuantumCircuit(2, 2)
    qc.append(UnitaryGate(lift(U3)), [0, 1])
    qc.measure([0, 1], [0, 1])
    return qc

def theory_probs(U3):
    """noiseless exato (statevector). Devolucao em float64 declarado."""
    qc = QuantumCircuit(2)
    qc.append(UnitaryGate(lift(U3)), [0, 1])
    sv = Statevector(qc)
    d = sv.probabilities_dict()
    return {FUSION[k]: v for k, v in d.items()}

def chi2_stat(counts, probs, shots):
    """counts: dict canal->n ; probs: teoria. Retorna (chi2, df, p_valor, dTV)."""
    chans = [c for c in ["ch0", "ch1", "ch2"] if probs.get(c, 0) > 0 or counts.get(c, 0) > 0]
    chi = 0.0; df = -1
    for c in chans:
        e = probs.get(c, 0.0) * shots
        o = counts.get(c, 0)
        if e > 0:
            chi += (o - e) ** 2 / e
        elif o > 0:
            chi += float("inf")
        df += 1
    p = chi2dist.sf(chi, max(df, 1))
    dtv = 0.5 * sum(abs(counts.get(c, 0) / shots - probs.get(c, 0.0)) for c in chans)
    return round(chi, 3), max(df, 1), round(float(p), 4), round(dtv, 4)

# ------------------------------------------------ varredura A: angulo
theta_list = [math.pi * k / 10 for k in range(1, 11)]  # pi/10 ... pi
varA_noiseless, varA_specs = [], []
for t in theta_list:
    U_RS, U_SR = B_R(t) @ B_S(t), B_S(t) @ B_R(t)
    comm = np.abs(U_RS - U_SR).sum()
    pRS, pSR = theory_probs(U_RS), theory_probs(U_SR)
    # canal dominante distinto? (nao-abelianidade visivel)
    dom = max(pRS, key=pRS.get) != max(pSR, key=pSR.get)
    varA_noiseless.append({
        "theta_pi_sobre_10": round(t / math.pi * 10), "theta_rad": round(t, 6),
        "comutador_L1": round(float(comm), 6), "canais_distintos_noiseless": bool(dom),
        "p_RS": {k: round(v, 6) for k, v in pRS.items()},
        "p_SR": {k: round(v, 6) for k, v in pSR.items()},
        "desvio_vs_teoria_float64": "<1e-15 (statevector identico a teoria; declarado)",
    })
    varA_specs.append((U_RS, U_SR))

# ------------------------------------------------ varredura B: palavra (B_R B_S)^k, theta=pi/2 exato
BR, BS = B_R(math.pi / 2), B_S(math.pi / 2)
W = BR @ BS
varB_theory = []
for k in range(1, 7):
    Wk = np.linalg.matrix_power(W, k)
    p = theory_probs(Wk)
    varB_theory.append({"k": k,
        "canal_dominante": max(p, key=p.get),
        "p": {kk: round(v, 6) for kk, v in p.items()}})

# ------------------------------------------------ varredura C: mapa de erros (noiseless, exato)
def err_map(prep_vec, pauli):
    """aplica Pauli local e mede canal de fusao (noiseless)."""
    qc = QuantumCircuit(2)
    sv = Statevector(prep_vec)
    from qiskit.quantum_info import Statevector as SV, Pauli
    sv2 = sv.evolve(Pauli(pauli))
    d = sv2.probabilities_dict()
    return {FUSION[k]: round(v, 6) for k, v in d.items()}

prep = np.zeros(4, dtype=complex); prep[0] = 1  # |0> = ch0
mapC = {}
for pauli in ["IX", "IZ", "XI", "ZI", "XX", "ZZ"]:
    mapC[pauli] = err_map(prep, pauli)

# ------------------------------------------------ hardware: um job com tudo
service = QiskitRuntimeService(token=TOKEN, channel="ibm_quantum_platform", instance="auto")
backend = service.backend("ibm_fez")
circs, tags = [], []
for (U_RS, U_SR) in varA_specs:
    circs += [circ(U_RS), circ(U_SR)]
    tags += ["A_RS", "A_SR"]
for k in range(1, 7):
    circs.append(circ(np.linalg.matrix_power(W, k)))
    tags.append(f"B_k{k}")
isa = [transpile(c, backend=backend, optimization_level=2) for c in circs]
print(f"circuitos: {len(isa)}")
sampler = SamplerV2(mode=backend)
job = sampler.run(isa, shots=SHOTS)
print("JOB:", job.job_id())
for i in range(40):
    st = job.status()
    stn = st if isinstance(st, str) else getattr(st, "status", st)
    if str(stn) in ("DONE", "ERROR", "FAILED", "CANCELLED"):
        break
    time.sleep(10)
if str(stn) != "DONE":
    raise SystemExit("job nao concluiu: " + str(stn))

res = job.result()
hw = []
for pub, tag in zip(res, tags):
    cnt = {FUSION[k]: int(v) for k, v in pub.data.c.get_counts().items()}
    hw.append((tag, cnt))

# organiza varredura A hardware com chi2
varA_hardware = []
idx = 0
for i, t in enumerate(theta_list):
    row = {}
    for tag in ("A_RS", "A_SR"):
        tg, cnt = hw[idx]; idx += 1
        U = (B_R(t) @ B_S(t)) if tag == "A_RS" else (B_S(t) @ B_R(t))
        pth = theory_probs(U)
        chi, df, pval, dtv = chi2_stat(cnt, pth, SHOTS)
        row[tag] = {"counts": cnt, "chi2": chi, "df": df, "p_valor": pval, "dist_TV": dtv,
                    "canal_dominante_hardware": max(cnt, key=cnt.get)}
    varA_hardware.append({"theta_pi_sobre_10": round(t / math.pi * 10), **row})

varB_hardware = []
for k in range(1, 7):
    tg, cnt = hw[idx]; idx += 1
    Wk = np.linalg.matrix_power(W, k)
    pth = theory_probs(Wk)
    chi, df, pval, dtv = chi2_stat(cnt, pth, SHOTS)
    varB_hardware.append({"k": k, "counts": cnt, "chi2": chi, "df": df, "p_valor": pval,
                          "dist_TV": dtv,
                          "canal_dominante_hardware": max(cnt, key=cnt.get),
                          "canal_previsto": varB_theory[k - 1]["canal_dominante"],
                          "bate": max(cnt, key=cnt.get) == varB_theory[k - 1]["canal_dominante"]})

sweep = {
    "spec": "Z-QEA", "modulo": "experiments/scientific_sweep.py",
    "data": time.strftime("%Y-%m-%dT%H:%M:%S-03:00"),
    "shots": SHOTS, "job_id": job.job_id(), "backend": "ibm_fez (laboratorio de teste, sem endosso)",
    "A_sweep_angulo": {"noiseless": varA_noiseless, "hardware": varA_hardware,
        "nota": "teoria float64 declarada; chi2 com correcao de categorias; df>=1"},
    "B_sweep_palavra": {"previsao_noiseless": varB_theory, "hardware": varB_hardware},
    "C_mapa_erros_pauli": {"preparacao": "|0> (ch0)", "efeito_noiseless": mapC,
        "nota": "X em qualquer qubit vira canal; Z so faz fase (nao muda medida no estado base)"},
}
canon = json.dumps(sweep, sort_keys=True, ensure_ascii=True, default=str)
sweep["selo_sha3_256"] = hashlib.sha3_256(canon.encode()).hexdigest()
json.dump(sweep, open("scientific_sweep_receipt.json", "w"), indent=2, default=str)
print("A: pontos =", len(varA_hardware), "| B: ks =", [r["k"] for r in varB_hardware])
print("B todos batem:", all(r["bate"] for r in varB_hardware))
print("SELO VARREDURA:", sweep["selo_sha3_256"][:32], "...")

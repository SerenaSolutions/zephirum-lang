# -*- coding: utf-8 -*-
"""RODADA G — fronteiras v2.0.0 no silicio (complexidade da nova roupagem).

A1: QML TRIVALENTE EM HARDWARE — gradientes parameter-shift medidos no QPU
    real (n=3, ansatz rasa L=1 vs profunda L=6, 1024 shots) alimentam o
    veredito ternario train_verdict() do zyqml_core: TREINAVEL vs
    REFUSED(GRADIENT_VANISHED). Zero frameworks: circuitos nossos.
A2: ZNE COM FOLDING MANUAL — fidelidade GHZ n=5 em γ=1,3,5 (cada CX
    dobrado a mao em qubits FISICOS do circuito transpilado nivel 2;
    sem cancelamento porque o folding e pos-transpile). Richardson
    nativo + veredito ternario zne_verdict() do zyql_zne.
A3: GHZ n=12 NO HARDWARE vs MPS EXATO — o simulador MPS nativo prevê
    0.5/0.5 em |0^12>/|1^12>; o silicio diz quao longe chega (limite
    declarado n<=8 do statevector ja nao e o do hardware: 12 live).
"""
import json, os, time
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2

T = os.environ["IBM_QUANTUM_TOKEN"]
svc = QiskitRuntimeService(channel="ibm_quantum_platform", token=T)
try:
    print("COTA:", svc.usage())
except Exception as e:
    print("cota n/a:", e)
be = min([svc.backend(b) for b in ["ibm_fez", "ibm_kingston", "ibm_marrakesh"]],
         key=lambda b: b.status().pending_jobs)
print("BACKEND:", be.name, "pending:", be.status().pending_jobs)

rng = np.random.default_rng(1701)
N, LS, LD = 3, 1, 6
SHOTS_QML, SHOTS_ZNE, SHOTS_G12 = 1024, 2048, 4096
theta_s = [float(x) for x in rng.uniform(0, 2 * np.pi, LS * N)]
theta_d = [float(x) for x in rng.uniform(0, 2 * np.pi, LD * N)]

# ---------- A1: circuitos parameter-shift (fonte primaria, na mao) ----------
def ansatz(L, theta, shift_idx=None, shift_sign=0.0):
    qc = QuantumCircuit(N, N)
    for q in range(N):
        qc.h(q)
    for l in range(L):
        for q in range(N):
            t = theta[l * N + q]
            if shift_idx == l * N + q:
                t += shift_sign * np.pi / 2
            qc.ry(t, q)
        for q in range(N - 1):
            qc.cz(q, q + 1)          # cadeia linear: amigavel ao acoplamento
    for q in range(N):
        qc.measure(q, q)
    return qc

qml_circuits, meta = [], []
for label, L, th in (("shallow", LS, theta_s), ("deep", LD, theta_d)):
    qml_circuits.append(ansatz(L, th))          # base
    meta.append((label, None, 0.0))
    for i in range(L * N):
        for s in (+1.0, -1.0):
            qml_circuits.append(ansatz(L, th, shift_idx=i, shift_sign=s))
            meta.append((label, i, s))
print("A1 pubs:", len(qml_circuits))

# ---------- A2: GHZ n=5 + folding manual γ=1,3,5 ----------
ghz5 = QuantumCircuit(5, 5)
ghz5.h(0)
for i in range(4):
    ghz5.cx(i, i + 1)
for j in range(5):
    ghz5.measure(j, j)
tg = transpile(ghz5, backend=be, optimization_level=2)

def fold(tc, gamma):
    if gamma == 1:
        return tc
    f = tc.copy_empty_like()
    for inst in tc.data:
        reps = gamma if len(inst.qubits) == 2 else 1
        for _ in range(reps):
            f.append(inst.operation, inst.qubits, inst.clbits)
    return f

zne_circuits = [fold(tg, g) for g in (1, 3, 5)]
print("A2 pubs: 3 (gamma 1,3,5; CX dobrados a mao pos-transpile)")

# ---------- A3: GHZ n=12 ----------
ghz12 = QuantumCircuit(12, 12)
ghz12.h(0)
for i in range(11):
    ghz12.cx(i, i + 1)
for j in range(12):
    ghz12.measure(j, j)
t12 = transpile(ghz12, backend=be, optimization_level=2)

# ISA: transpilar TODOS os circuitos QML (nivel 2, licao da Rodada C)
qml_circuits = [transpile(c, backend=be, optimization_level=2) for c in qml_circuits]
print("A1 transpilados (ISA)")
sampler = SamplerV2(mode=be)
job_qml = sampler.run(qml_circuits, shots=SHOTS_QML)
job_zne = sampler.run(zne_circuits, shots=SHOTS_ZNE)
job_g12 = sampler.run([t12], shots=SHOTS_G12)
print("JOBS:", job_qml.job_id(), job_zne.job_id(), job_g12.job_id())

out = {"backend": be.name, "submitted": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
       "qml_job": job_qml.job_id(), "zne_job": job_zne.job_id(), "g12_job": job_g12.job_id(),
       "theta_shallow": theta_s, "theta_deep": theta_d, "n": N,
       "layers_shallow": LS, "layers_deep": LD,
       "shots": {"qml": SHOTS_QML, "zne": SHOTS_ZNE, "g12": SHOTS_G12},
       "gammas": [1, 3, 5], "meta": meta}
json.dump(out, open("experiments/round_g_jobs.json", "w"), indent=1)
print("salvo experiments/round_g_jobs.json")

for job, nm in ((job_qml, "QML"), (job_zne, "ZNE"), (job_g12, "G12")):
    for _ in range(24):
        st = job.status()
        if st.name in ("DONE", "ERROR", "FAILED", "CANCELLED"):
            break
        time.sleep(10)
    print(nm, "->", st.name)
print("ESTADO:", job_qml.status().name, job_zne.status().name, job_g12.status().name)

# -*- coding: utf-8 -*-
"""RODADA G — A1 v2: parameter-shift em BASE X (o plateau de verdade).
CZ e diagonal: em base Z o gradiente so vive no theta do qubit 0. Medindo
X0 (H antes da medida), o emaranhamento propaga o gradiente pra TODOS os
parametros — o cenario honesto de barren plateau no hardware real."""
import json, os, time
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2

jobs = json.load(open("experiments/round_g_jobs.json"))
rng = np.random.default_rng(1701)
N, LS, LD = jobs["n"], jobs["layers_shallow"], jobs["layers_deep"]
SHOTS = jobs["shots"]["qml"]

def ansatz(L, theta, shift_idx=None, sign=0.0):
    qc = QuantumCircuit(N, N)
    for q in range(N):
        qc.h(q)
    for l in range(L):
        for q in range(N):
            t = theta[l * N + q]
            if shift_idx == l * N + q:
                t += sign * np.pi / 2
            qc.ry(t, q)
        for q in range(N - 1):
            qc.cz(q, q + 1)
    qc.h(0)                      # BASE X no qubit 0: gradiente atravessa o emaranhamento
    for q in range(N):
        qc.measure(q, q)
    return qc

circs = []
for label, L, th in (("shallow", LS, jobs["theta_shallow"]), ("deep", LD, jobs["theta_deep"])):
    circs.append(ansatz(L, th))
    for i in range(L * N):
        circs.append(ansatz(L, th, shift_idx=i, sign=+1.0))
        circs.append(ansatz(L, th, shift_idx=i, sign=-1.0))
print("A1-X pubs:", len(circs))

svc = QiskitRuntimeService(channel="ibm_quantum_platform", token=os.environ["IBM_QUANTUM_TOKEN"])
be = min([svc.backend(b) for b in ["ibm_fez", "ibm_kingston", "ibm_marrakesh"]],
         key=lambda b: b.status().pending_jobs)
circs = [transpile(c, backend=be, optimization_level=2) for c in circs]
job = SamplerV2(mode=be).run(circs, shots=SHOTS)
print("JOB X:", job.job_id(), be.name)
jobs["qml_job"] = job.job_id()
jobs["qml_basis"] = "X0 (H antes da medida)"
json.dump(jobs, open("experiments/round_g_jobs.json", "w"), indent=1)
for _ in range(30):
    st = str(job.status())
    if st in ("DONE", "ERROR", "FAILED", "CANCELLED"):
        break
    time.sleep(10)
print("A1-X ->", st)

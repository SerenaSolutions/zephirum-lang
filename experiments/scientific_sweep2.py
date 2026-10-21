# -*- coding: utf-8 -*-
"""VARREDURA CIENTIFICA S3-QUTRIT v2 — COM CALIBRACAO DE LEITURA (Z-QEA)
Hipotese (da v1): a reprovacao do chi2 em 10/10 pontos foi vies de leitura
(instrumento), nao fisica. v2 mede a matriz de confusao de leitura (4 estados
da base) e a usa para mitigar as distribuicoes ANTES do chi2.
Roteiro: D_cal (4) + A2 (10 ang x 2 ordens = 20) + B2 (palavra k=1..6 = 6) = 30 circuitos.
"""
import os, json, math, hashlib
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import UnitaryGate
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2

TOKEN = os.environ["IBM_TOKEN"]
SHOTS = 4096
BACKEND = "ibm_fez"
LABELS = ["00", "01", "10", "11"]  # convencao qiskit: bitstring c1c0

def B_R(t):  return np.array([[math.cos(t), 0, math.sin(t)], [0, 1, 0], [-math.sin(t), 0, math.cos(t)]])
def B_S(t):  return np.array([[1, 0, 0], [0, math.cos(t), math.sin(t)], [0, -math.sin(t), math.cos(t)]])
def lift(U3):
    U4 = np.eye(4); U4[:3, :3] = U3; return U4

def cal_circuit(b):
    """prepara o estado da base correspondente ao bitstring b (c1c0) e mede"""
    qc = QuantumCircuit(2, 2)
    if b[0] == "1": qc.x(1)   # c1 = q1
    if b[1] == "1": qc.x(0)   # c0 = q0
    qc.measure([0, 1], [0, 1])
    return qc

def braid_circuit(U3):
    qc = QuantumCircuit(2, 2)
    qc.append(UnitaryGate(lift(U3)), [0, 1])
    qc.measure([0, 1], [0, 1])
    return qc

# ---- monta os 30 circuitos, na ordem: cal(4), A2(20), B2(6)
circs, specs = [], []
for b in LABELS:
    circs.append(cal_circuit(b)); specs.append(("D_cal", b))
for k in range(1, 11):
    t = math.pi * k / 10
    circs.append(braid_circuit(B_R(t) @ B_S(t))); specs.append(("A2_RS", k))
    circs.append(braid_circuit(B_S(t) @ B_R(t))); specs.append(("A2_SR", k))
BR, BS = B_R(math.pi / 2), B_S(math.pi / 2)
W = BR @ BS
for k in range(1, 7):
    circs.append(braid_circuit(np.linalg.matrix_power(W, k))); specs.append(("B2_word", k))
assert len(circs) == 30

svc = QiskitRuntimeService(token=TOKEN, channel="ibm_quantum_platform", instance="auto")
backend = svc.backend(BACKEND)
tqc = transpile(circs, backend=backend, optimization_level=1)
job = SamplerV2(backend).run(tqc, shots=SHOTS)
print("job:", job.job_id())
json.dump({"job_id": job.job_id(), "backend": BACKEND, "shots": SHOTS,
           "specs": [list(s) for s in specs], "labels": LABELS,
           "submetido_em": __import__("time").strftime("%Y-%m-%dT%H:%M:%S-03:00")},
          open("sweep2_job_meta.json", "w"), indent=2)
print("meta salvo em sweep2_job_meta.json")

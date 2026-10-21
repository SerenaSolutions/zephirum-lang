# -*- coding: utf-8 -*-
"""RODADA 3 — ESCALADA DA DECISAO TRIVALENTE (Zephirum/ZYQL, Z-QEA)
C8: Deutsch-Jozsa escalando n=4 e n=5 (const-1 / const-0 / balanceado) — a decisao
    trivalente sobrevive a qubits a mais? p(0^n) decide 1/0, balanceado -> REFUSED
C9: Grover 2-qubits, 1..3 iteracoes — curva de amplificacao (periodo 3, eco do trançado)
C10: palavras de tracado (B_R B_S)^k para k=7..12 — estresse do periodo 3 medido
15 circuitos, 4096 shots, ibm_fez.
"""
import os, json, math, hashlib
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import UnitaryGate
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2

TOKEN = os.environ["IBM_TOKEN"]; SHOTS = 4096; BACKEND = "ibm_fez"

def B_R(t):  return np.array([[math.cos(t), 0, math.sin(t)], [0, 1, 0], [-math.sin(t), 0, math.cos(t)]])
def B_S(t):  return np.array([[1, 0, 0], [0, math.cos(t), math.sin(t)], [0, -math.sin(t), math.cos(t)]])
def lift(U3):
    U4 = np.eye(4); U4[:3, :3] = U3; return U4

def dj(n, caso):
    """DJ com n qubits de entrada + 1 ancilla em |->. Mede os n de entrada."""
    qc = QuantumCircuit(n + 1, n)
    qc.h(range(n))
    qc.x(n); qc.h(n)
    if caso == "const-1":
        qc.x(n)                                   # f(x)=1: flip sempre (phase kickback global)
    elif caso == "const-0":
        pass                                      # f(x)=0: identidade
    else:                                          # balanceado: x0⊕x1
        qc.cx(0, n); qc.cx(1, n)
    qc.h(range(n))
    qc.measure(range(n), range(n))
    return qc

def grover2(iters):
    qc = QuantumCircuit(2, 2)
    qc.h([0, 1])
    for _ in range(iters):
        qc.cz(0, 1)                               # oraculo |11>
        qc.h([0, 1]); qc.x([0, 1]); qc.cz(0, 1); qc.x([0, 1]); qc.h([0, 1])  # difusor
    qc.measure([0, 1], [0, 1])
    return qc

def braid_word(k):
    qc = QuantumCircuit(2, 2)
    W = B_R(math.pi / 2) @ B_S(math.pi / 2)
    qc.append(UnitaryGate(lift(np.linalg.matrix_power(W, k))), [0, 1])
    qc.measure([0, 1], [0, 1])
    return qc

circs, specs = [], []
for n in (4, 5):
    for caso in ("const-1", "const-0", "balanceado"):
        circs.append(dj(n, caso)); specs.append(("C8_DJ", n, caso))
for it in (1, 2, 3):
    circs.append(grover2(it)); specs.append(("C9_GROVER", it, None))
for k in range(7, 13):
    circs.append(braid_word(k)); specs.append(("C10_WORD", k, None))
assert len(circs) == 15

svc = QiskitRuntimeService(token=TOKEN, channel="ibm_quantum_platform", instance="auto")
backend = svc.backend(BACKEND)
tqc = transpile(circs, backend=backend, optimization_level=1)
job = SamplerV2(backend).run(tqc, shots=SHOTS)
print("job:", job.job_id())
json.dump({"job_id": job.job_id(), "backend": BACKEND, "shots": SHOTS,
           "specs": [list(map(lambda v: v, s)) for s in specs],
           "submetido_em": __import__("time").strftime("%Y-%m-%dT%H:%M:%S-03:00")},
          open("round3_job_meta.json", "w"), indent=2)
print("meta salvo")

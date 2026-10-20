# -*- coding: utf-8 -*-
"""Submissao dos circuitos da miniatura S3 ao IBM Heron (ibm_fez).
Padrao da casa: job IDs no recibo; IBM citada como laboratorio de teste, sem endosso."""
import os, json, time, math
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import UnitaryGate
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2

TOKEN = os.environ["IBM_TOKEN"]
service = QiskitRuntimeService(token=TOKEN, channel="ibm_quantum_platform", instance="auto")
backend = service.backend("ibm_fez")
print("backend:", backend.name, "| qubits:", backend.num_qubits)

B_R = np.array([[0, 0, 1], [0, 1, 0], [-1, 0, 0]], dtype=float)
B_S = np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]], dtype=float)

def lift(U3):
    U4 = np.eye(4); U4[:3, :3] = U3; return U4

def braid_circ(U3, prep=None):
    qc = QuantumCircuit(2, 2)
    if prep == "uniform3":
        sv = np.zeros(4); sv[0] = sv[1] = sv[2] = 1 / math.sqrt(3)
        qc.initialize(sv, [0, 1])
    qc.append(UnitaryGate(lift(U3)), [0, 1])
    qc.measure([0, 1], [0, 1])
    return qc

# DJ constante-1, via ancilla padrao (3 qubits: 2 dados + 1 ancilla)
qc_dj = QuantumCircuit(3, 2)
qc_dj.h(0); qc_dj.h(1)
qc_dj.x(2); qc_dj.h(2)
qc_dj.cx(0, 2); qc_dj.cx(1, 2)   # f(x)=x0 XOR x1 -> balanceado na verdade!
# ATENCAO: para constante-1 a oracle e I no dado + flip na ancilla:
qc_dj = QuantumCircuit(3, 2)
qc_dj.h(0); qc_dj.h(1)
qc_dj.x(2); qc_dj.h(2)
qc_dj.z(2)                        # constante-1: flip de fase na ancilla para todo |x>
qc_dj.h(0); qc_dj.h(1)
qc_dj.measure([0, 1], [0, 1])

circs = {
    "tracado_RS": braid_circ(B_R @ B_S),
    "tracado_SR": braid_circ(B_S @ B_R),
    "fusao_uniforme": braid_circ(np.eye(3), prep="uniform3"),
    "DJ_constante1": qc_dj,
}
isa = {k: transpile(c, backend=backend, optimization_level=2) for k, c in circs.items()}
for k, c in isa.items():
    print(f"{k}: depth={c.depth()} ops={dict(c.count_ops())}")

sampler = SamplerV2(mode=backend)
job = sampler.run(list(isa.values()), shots=4096)
meta = {"job_id": job.job_id(), "backend": backend.name,
        "submetido_em": time.strftime("%Y-%m-%dT%H:%M:%S-03:00"),
        "shots": 4096,
        "circuitos": {k: {"depth": c.depth(), "ops": {str(a): int(b) for a, b in c.count_ops().items()}} for k, c in isa.items()}}
json.dump(meta, open("job_meta.json", "w"), indent=2)
print("JOB:", job.job_id())

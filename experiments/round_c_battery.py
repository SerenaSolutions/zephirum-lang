# -*- coding: utf-8 -*-
"""
RODADA C — UPGRADE v1.9.0 NO SILICIO (Zephirum/ZYQL, Z-QEA)
Valida no hardware as duas semânticas novas do núcleo:
  (1) PORTA DE INTEGRIDADE GHZ: estado GHZ_3 medido no QPU; a fidelidade
      (|000>+|111>) decide se o DISPOSITIVO é confiável antes de qualquer
      veredito. Semântica inédita: a decisão desconfia do próprio QPU.
  (2) DECISÃO ADAPTATIVA: DJ n=3 (const-1, const-0, balanceado) com banda
      adaptativa epsilon=0.05 (Hoeffding inverso) — veredito declara o erro.
2 jobs no IBM Heron ibm_kingston, 256 shots cada.
"""
import os, json, math
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2

BACKEND_NAME = "ibm_kingston"
SHOTS = 256
EPS = 0.05

def ghz_circuit(n=3):
    qc = QuantumCircuit(n, n)
    qc.h(0)
    for t in range(1, n):
        qc.cx(0, t)
    qc.measure(range(n), range(n))
    return qc

def dj_circuit(n, caso):
    qc = QuantumCircuit(n + 1, n)
    qc.h(range(n)); qc.x(n); qc.h(n)
    if caso == "const-1": qc.x(n)
    elif caso == "const-0": pass
    elif caso == "balanceado":
        qc.cx(0, n); qc.cx(1, n)
    else: raise ValueError(caso)
    qc.h(range(n)); qc.measure(range(n), range(n))
    return qc

def adaptive_margin(eps, shots):
    return math.sqrt(math.log(2.0 / eps) / (2.0 * shots))

def trivalent(p0, shots, margin):
    hoeff = min(eps, 2 * math.exp(-2 * shots * margin ** 2))
    if p0 >= 1 - margin:
        return 1, hoeff, "adaptive band>=%.4f" % (1 - margin)
    if p0 <= margin:
        return "REFUSED", hoeff, "adaptive band<=%.4f" % margin
    return "REFUSED", hoeff, "inside adaptive band (+-%.4f)" % margin

def main():
    token = os.environ["IBM_QUANTUM_TOKEN"]
    service = QiskitRuntimeService(token=token, channel="ibm_quantum_platform", instance="auto")
    backend = service.backend(BACKEND_NAME)
    margin = adaptive_margin(EPS, SHOTS)
    print(f"banda adaptativa: +-{margin:.4f} (eps={EPS}, shots={SHOTS})")

    # JOB 1: porta GHZ
    ghz = transpile(ghz_circuit(3), backend=backend, optimization_level=2)
    sampler = SamplerV2(mode=backend)
    j1 = sampler.run([ghz], shots=SHOTS)
    print("job GHZ:", j1.job_id())

    # JOB 2: bateria DJ adaptativa
    circs = [transpile(dj_circuit(3, c), backend=backend, optimization_level=2)  # licao Rodada C: nivel 1 mapeou em qubits ruidosos
             for c in ("const-1", "const-0", "balanceado")]
    j2 = sampler.run(circs, shots=SHOTS)
    print("job DJ:", j2.job_id())

    with open("/tmp/round_c_jobs.json", "w") as f:
        json.dump({"ghz_job": j1.job_id(), "dj_job": j2.job_id(),
                   "backend": BACKEND_NAME, "shots": SHOTS, "eps": EPS,
                   "margin": margin}, f, indent=1)
    print("jobs submetidos. Rode experiments/round_c_analyze.py quando DONE.")

if __name__ == "__main__":
    main()

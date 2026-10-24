# -*- coding: utf-8 -*-
"""
RODADA D — MATRIZ DE REPRODUTIBILIDADE 3 QPUs (Zephirum/ZYQL, Z-QEA)
Protocolo de consolidacao: a MESMA bateria (porta GHZ + DJ n=3 adaptativa,
eps=0.05, shots 64 e 256) rodando em ibm_fez e ibm_marrakesh. O ibm_kingston
ja foi validado na Rodada B/C — Rodada D fecha a matriz 3 dispositivos.
Veredito de consolidacao: mesma bateria, tres QPUs, vereditos identicos.

Licoes herdadas: optimization_level=2 (nivel 1 mapeou em qubits ruidosos),
GHZ antes de qualquer veredito (porta de integridade v1.9.0).
"""
import os, json, math
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2

BACKENDS = ["ibm_fez", "ibm_marrakesh"]
SHOT_LEVELS = [64, 256]
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

def main():
    token = os.environ["IBM_QUANTUM_TOKEN"]
    service = QiskitRuntimeService(token=token, channel="ibm_quantum_platform", instance="auto")
    jobs = {}
    for name in BACKENDS:
        backend = service.backend(name)
        sampler = SamplerV2(mode=backend)
        ghz = transpile(ghz_circuit(3), backend=backend, optimization_level=2)
        j_ghz = sampler.run([ghz], shots=256)
        dj_jobs = {}
        for shots in SHOT_LEVELS:
            circs = [transpile(dj_circuit(3, c), backend=backend, optimization_level=2)
                     for c in ("const-1", "const-0", "balanceado")]
            j = sampler.run(circs, shots=shots)
            dj_jobs[str(shots)] = j.job_id()
        jobs[name] = {"ghz_job": j_ghz.job_id(), "dj_jobs": dj_jobs}
        print(f"{name}: GHZ {j_ghz.job_id()} | DJ {dj_jobs}")
    out = {"rodada": "D", "protocolo": "matriz de reprodutibilidade 3 QPUs",
           "backends": BACKENDS, "shots_levels": SHOT_LEVELS, "eps": EPS,
           "margins": {str(s): adaptive_margin(EPS, s) for s in SHOT_LEVELS},
           "jobs": jobs, "referencia_rodada_b_c": "ibm_kingston (jobs dbdac41gv2cc738hnen0/dbdac4c24mrc73cl3ia0 + GHZ dbdlb7424mrc739iievg)"}
    with open("/tmp/round_d_jobs.json", "w") as f:
        json.dump(out, f, indent=1)
    print("jobs submetidos. Analise com experiments/round_d_analyze.py quando DONE.")

if __name__ == "__main__":
    main()

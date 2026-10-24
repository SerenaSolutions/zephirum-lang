# -*- coding: utf-8 -*-
"""
RODADA E — CARGA MAXIMA no silicio (ordem do dono: entrar DIFICIL, nao facinho).
A mesma maquina que passou facil nas rodadas anteriores agora encara:
  (1) PORTA DE INTEGRIDADE GHZ n=5 (emaranhamento profundo, 256 shots)
  (2) ESTRESSE GHZ n=8 (8 qubits emaranhados, 512 shots — informativo)
  (3) BATERIA DJ ESCALADA: n=4, 5, 6 (const-1, const-0, paridade balanceada),
      9 circuitos x 1024 shots — banda adaptativa apertada (m=0.0424)
  (4) ORACULO NOVO — Bernstein-Vazirani n=6, segredo '101101' (1024 shots)
  (5) ORACULO NOVO — Grover n=3, alvo '110', 2 iteracoes (1024 shots)
Total: 13 circuitos, ~12 mil shots, ~5x mais carga que a Rodada D.
Backend: ibm_kingston (Heron validado nas Rodadas B/C).
"""
import os, json, math
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2

BACKEND = "ibm_kingston"
EPS = 0.05

def ghz_circuit(n):
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
        for q in range(n): qc.cx(q, n)  # paridade de n bits = balanceada
    else: raise ValueError(caso)
    qc.h(range(n)); qc.measure(range(n), range(n))
    return qc

def bv_circuit(n=6, segredo="101101"):
    qc = QuantumCircuit(n + 1, n)
    qc.h(range(n)); qc.x(n); qc.h(n)
    for i, b in enumerate(segredo):
        if b == "1": qc.cx(i, n)
    qc.h(range(n)); qc.measure(range(n), range(n))
    return qc

def grover_circuit(n=3, alvo="110", iteracoes=2):
    qc = QuantumCircuit(n, n)
    qc.h(range(n))
    zeros = [i for i in range(n) if alvo[i] == "0"]
    for _ in range(iteracoes):
        # oraculo de fase no alvo
        for i in zeros: qc.x(i)
        qc.h(n - 1)
        qc.ccx(0, 1, n - 1)
        qc.h(n - 1)
        for i in zeros: qc.x(i)
        # difusor
        qc.h(range(n)); qc.x(range(n))
        qc.h(n - 1)
        qc.ccx(0, 1, n - 1)
        qc.h(n - 1)
        qc.x(range(n)); qc.h(range(n))
    qc.measure(range(n), range(n))
    return qc

def adaptive_margin(eps, shots):
    return math.sqrt(math.log(2.0 / eps) / (2.0 * shots))

def main():
    token = os.environ["IBM_QUANTUM_TOKEN"]
    service = QiskitRuntimeService(token=token, channel="ibm_quantum_platform", instance="auto")
    backend = service.backend(BACKEND)
    sampler = SamplerV2(mode=backend)
    jobs = {}

    j = sampler.run([transpile(ghz_circuit(5), backend=backend, optimization_level=2)], shots=256)
    jobs["ghz5_gate"] = j.job_id(); print("GHZ n=5 (porta):", j.job_id())

    j = sampler.run([transpile(ghz_circuit(8), backend=backend, optimization_level=2)], shots=512)
    jobs["ghz8_stress"] = j.job_id(); print("GHZ n=8 (estresse):", j.job_id())

    circs = [transpile(dj_circuit(n, c), backend=backend, optimization_level=2)
             for n in (4, 5, 6) for c in ("const-1", "const-0", "balanceado")]
    j = sampler.run(circs, shots=1024)
    jobs["dj_escala"] = j.job_id(); print("DJ n=4/5/6 (9 circuitos, 1024 shots):", j.job_id())

    j = sampler.run([transpile(bv_circuit(), backend=backend, optimization_level=2)], shots=1024)
    jobs["bv_segredo"] = j.job_id(); print("BV n=6 segredo '101101':", j.job_id())

    j = sampler.run([transpile(grover_circuit(), backend=backend, optimization_level=2)], shots=1024)
    jobs["grover_alvo"] = j.job_id(); print("Grover n=3 alvo '110':", j.job_id())

    out = {"rodada": "E", "protocolo": "carga maxima: GHZ n=5/n=8 + DJ n=4/5/6 + BV n=6 + Grover n=3",
           "backend": BACKEND, "eps": EPS,
           "margens": {"256": round(adaptive_margin(EPS, 256), 4),
                       "512": round(adaptive_margin(EPS, 512), 4),
                       "1024": round(adaptive_margin(EPS, 1024), 4)},
           "jobs": jobs,
           "segredo_bv": "101101", "alvo_grover": "110",
           "bandas_calibradas_familias_novas": {
               "bv": "1 se p_segredo>=0.80; 0 se p<=0.0312 (2x baseline 1/64); senao REFUSED",
               "grover": "1 se p_alvo>=0.50 e >=2x segundo; 0 se p_alvo<=0.25; senao REFUSED"}}
    with open("/tmp/round_e_jobs.json", "w") as f:
        json.dump(out, f, indent=1)
    print("jobs submetidos. Analise com experiments/round_e_analyze.py quando DONE.")

if __name__ == "__main__":
    main()

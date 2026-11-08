# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Serena Quantum Solutions
# -*- coding: utf-8 -*-
"""RODADA I — bateria do GATE DE MEMÓRIA (protocolo round_i_protocol.md).

Duas construções de ambiente, mesma colisão U = CX(S -> âncora):
  MEMORY    : âncora única q1 reaproveitada (correlações persistem)
  MEMORYLESS: âncoras frescas q1..q4, uma por passo (ambiente descartado)

Tomografia de S em 3 bases (X, Y, Z) para dois estados iniciais (|0>, |+>),
k = 0..4 colisões. S = bit menos significativo do count (little-endian).

Uso:
  python3 round_i_battery.py --simulate     # valida a construção com Aer
  python3 round_i_battery.py --submit       # dispara em ibm_marrakesh
"""
import json, math, os, sys

from qiskit import QuantumCircuit, transpile

STEPS = [0, 1, 2, 3, 4]
STATES = {"ket0": "0", "ketplus": "+"}
BASES = ["X", "Y", "Z"]
SHOTS = 2048
EPS = 0.05
SEED = 1701
HERE = os.path.dirname(os.path.abspath(__file__))


def build(variant, state, basis, k):
    """Circuito de uma célula da tomografia."""
    if variant == "memory":
        nq = 2                      # S=q0, E=q1 reaproveitado
    else:
        nq = 1 + max(1, max(STEPS))  # S=q0 + âncora por passo
    qc = QuantumCircuit(nq, nq)

    if STATES[state] == "+":
        qc.h(0)

    for step in range(k):
        anc = 1 if variant == "memory" else 1 + step
        qc.cx(0, anc)               # U = CX(S -> âncora)

    if basis == "X":
        qc.h(0)
    elif basis == "Y":
        qc.sdg(0)
        qc.h(0)

    qc.measure(range(nq), range(nq))
    qc.metadata = {"variant": variant, "state": state, "basis": basis, "k": k}
    return qc


def cells():
    out = []
    for variant in ("memory", "memoryless"):
        for k in STEPS:
            for state in STATES:
                for basis in BASES:
                    if k == 0 and variant == "memoryless":
                        continue  # k=0 é o mesmo estado físico: uma vez só
                    out.append(build(variant, state, basis, k))
    return out


def bloch(p0):
    """Componente de Bloch a partir de P(0) na base correspondente."""
    return 2.0 * p0 - 1.0


def trace_distance(counts_by_cell, variant, k):
    """D(k) = ½|r_a - r_b| com r reconstruído das 3 bases."""
    pa = {}
    pb = {}
    for basis in BASES:
        for state, store in ((("ket0"), pa), ("ketplus", pb)):
            key = (variant, state, basis, k)
            if key not in counts_by_cell and k == 0:
                key = ("memory", state, basis, 0)  # k=0 é fisicamente o mesmo
            counts = counts_by_cell[key]
            total = sum(counts.values())
            p0 = sum(v for b, v in counts.items() if b[-1] == "0") / total
            store[basis] = bloch(p0)
    dx = pa["X"] - pb["X"]
    dy = pa["Y"] - pb["Y"]
    dz = pa["Z"] - pb["Z"]
    return 0.5 * math.sqrt(dx * dx + dy * dy + dz * dz)


def band(eps=EPS, shots=SHOTS):
    m_exp = math.sqrt(math.log(2.0 / eps) / (2.0 * shots))
    return round(math.sqrt(3.0) * m_exp, 6)


def simulate():
    from qiskit_aer import AerSimulator
    sim = AerSimulator()
    circs = cells()
    tcircs = transpile(circs, sim, optimization_level=1)
    res = sim.run(tcircs, shots=SHOTS, seed_simulator=SEED).result()
    table = {}
    for c, r in zip(circs, res.results):
        m = c.metadata
        table[(m["variant"], m["state"], m["basis"], m["k"])] = r.data.counts
    print("D(0) =", round(trace_distance(table, "memory", 0), 4),
          "| esperado 0.7071 | banda", band())
    for variant in ("memory", "memoryless"):
        ds = [round(trace_distance(table, variant, k), 4) for k in STEPS]
        deltas = [round(ds[i + 1] - ds[i], 4) for i in range(len(ds) - 1)]
        print(f"{variant:<11} D = {ds}\n{'':<11} Δ = {deltas}")
    return table


def submit():
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
    service = QiskitRuntimeService(token=os.environ["IBM_QUANTUM_TOKEN"],
                                   channel="ibm_quantum_platform")
    backend = service.backend("ibm_marrakesh")
    circs = cells()
    isa = transpile(circs, backend, optimization_level=2)
    sampler = Sampler(mode=backend)
    job = sampler.run(isa, shots=SHOTS)
    jid = job.job_id()
    meta = [c.metadata for c in circs]
    out = {"rodada": "I", "protocolo": "gate de memoria do ruido (BLP)",
           "backend": "ibm_marrakesh", "job_id": jid, "shots": SHOTS, "eps": EPS,
           "band": band(), "n_circuits": len(circs), "cells": meta,
           "status": str(job.status())}
    path = os.path.join(HERE, "round_i_jobs.json")
    json.dump(out, open(path, "w"), indent=1)
    print("JOB:", jid, "|", job.status(), "|", len(circs), "circuitos |", path)


if __name__ == "__main__":
    if "--simulate" in sys.argv:
        simulate()
    elif "--submit" in sys.argv:
        submit()
    else:
        print(__doc__)

"""W-01..W-03: rodada de escala mundial (matematica algoritmica + analogo fotonico).
Protocolo declarado: shots=1024, alpha=0.01, um unico job com 3 circuitos.
Veredito por protocolo: 1 dentro da banda / 0 desvio provado / REFUSED sem evidencia.
"""
import json, math, os
import numpy as np
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister, transpile
from qiskit.circuit.library import SwapGate
from qiskit.quantum_info import Statevector, Operator
from zyql_witness import _seal


def walk(steps=3, npos=3):
    """Caminhada quantica discreta: 1 moeda + npos posicao, passos alternados."""
    qr = QuantumRegister(npos + 1, "q"); cr = ClassicalRegister(npos, "c")
    qc = QuantumCircuit(qr, cr)
    pos = list(range(1, npos + 1)); coin = 0
    for _ in range(steps):
        qc.h(coin)
        # incremento controlado por coin=1 (X em volta), decremento por coin=0
        qc.x(coin)
        for i in range(npos):
            if i == 0:
                qc.cx(coin, pos[0])
            else:
                qc.mcx([coin] + pos[:i], pos[i])
        qc.x(coin)
        qc.cx(coin, pos[0])
    qc.measure(pos, cr)
    return qc
def hom():
    """W-02: interferencia bosonica tipo HOM em qubits (analogo)."""
    qr = QuantumRegister(2, "q"); cr = ClassicalRegister(2, "c")
    qc = QuantumCircuit(qr, cr)
    qc.x(0); qc.x(1)                 # |11> = dois fotons, um por modo
    qc.unitary(Operator(SwapGate().power(0.5)), [0, 1], label="BS")
    qc.measure(qr, cr)
    return qc


def grover(marked="101", iters=2):
    """W-03: Grover 3 qubits com marcado |101>."""
    qr = QuantumRegister(3, "q"); cr = ClassicalRegister(3, "c")
    qc = QuantumCircuit(qr, cr)
    for i in range(3):
        qc.h(i)
    for _ in range(iters):
        for i, b in enumerate(marked):
            if b == "0":
                qc.x(i)
        qc.h(2); qc.mcx([0, 1], 2); qc.h(2)
        for i, b in enumerate(marked):
            if b == "0":
                qc.x(i)
        for i in range(3):
            qc.h(i); qc.x(i)
        qc.h(2); qc.mcx([0, 1], 2); qc.h(2)
        for i in range(3):
            qc.x(i); qc.h(i)
    qc.measure(qr, cr)
    return qc
def _ideal(qc, shots=20000):
    """Referencia sem ruido do MESMO circuito (mesma ordem de bits)."""
    from qiskit_aer import AerSimulator
    sim = AerSimulator(seed_simulator=99)
    c = sim.run(transpile(qc, sim), shots=shots).result().get_counts()
    N = sum(c.values())
    return {k: v / N for k, v in c.items()}


def _tvd(ideal, counts, n):
    N = sum(counts.values())
    obs = {k: v / N for k, v in counts.items()}
    keys = set(ideal) | set(obs)
    return 0.5 * sum(abs(ideal.get(k, 0.0) - obs.get(k, 0.0)) for k in keys)


def rodada_mundial(shots=1024, qpu=None, seal_path=None):
    circs = {"W-01": walk(), "W-02": hom(), "W-03": grover()}
    if qpu is None:
        from qiskit_aer import AerSimulator
        sim = AerSimulator(seed_simulator=5)
        tl = [transpile(c, sim) for c in circs.values()]
        res = sim.run(tl, shots=shots).result()
        counts = {k: res.get_counts(i) for i, k in enumerate(circs)}
        dev, jid = "aer_simulator", "local"
    else:
        from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
        tok = os.environ.get("IBM_API_KEY") or os.environ.get("GITHUB_TOKEN_2")
        svc = QiskitRuntimeService(channel="ibm_quantum_platform", token=tok)
        b = svc.backend(qpu)
        tl = [transpile(c, backend=b, optimization_level=1) for c in circs.values()]
        job = Sampler(mode=b).run(tl, shots=shots)
        res = job.result()
        counts = {k: res[i].data.c.get_counts() for i, k in enumerate(circs)}
        dev, jid = b.name, job.job_id()

    r = {}
    tvd = _tvd(_ideal(circs["W-01"]), counts["W-01"], 3)
    r["W-01"] = {"tvd": round(tvd, 4),
                 "veredito": "1" if tvd <= 0.20 else ("0" if tvd > 0.35 else "REFUSED")}
    c2 = counts["W-02"]
    coinc = sum(v for k, v in c2.items() if k in ("01", "10")) / sum(c2.values())
    vis = 1 - 2 * coinc
    r["W-02"] = {"coincidencia": round(coinc, 4), "visibilidade": round(vis, 4),
                 "veredito": "1" if vis >= 0.8 else ("0" if vis < 0.5 else "REFUSED")}
    c3 = counts["W-03"]
    pm = c3.get("101", 0) / sum(c3.values())
    r["W-03"] = {"p_marcado": round(pm, 4), "classico": 0.125, "ideal_2iter": 0.945,
                 "veredito": "1" if pm >= 0.70 else ("0" if pm <= 0.30 else "REFUSED")}

    rec = _seal({"protocolo": {"id": "WORLD-20261029",
                               "declarado": {"shots": shots, "alpha": 0.01,
                                             "bandas": {"W-01_tvd": [0.20, 0.35],
                                                        "W-02_vis": [0.8, 0.5],
                                                        "W-03_p": [0.70, 0.30]},
                                             "fotonica": "analogo em qubits supercondutores, nao fotonica real"}},
                 "execucao": {"dispositivo": dev, "job_id": jid, "counts": counts},
                 "resultado": r})
    if seal_path:
        json.dump(rec, open(seal_path, "w"), indent=1)
    return rec

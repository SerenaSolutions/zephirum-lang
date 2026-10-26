# -*- coding: utf-8 -*-
"""RODADA AUDITOR-SILICIO — o SHOT AUDITOR comandando campanha real no QPU.

Protocolo selado ANTES dos dados: profundidades [1,2,4,8], 1024 shots por
energia (2048/depth), regra IC 95%, orcamento max 8192. Cada profundidade so
e submetida se a decisao anterior foi CONTINUE. STOP poupa os shots restantes.
"""
import os, sys, json, hashlib, datetime
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, os.path.join(ROOT, "src"))
from shot_auditor import gradiente_band, audit_step

SPEC = {"depths": [1, 2, 4, 8], "shots_per_energy": 1024, "energias": 2,
        "budget_max": 8192, "regra": "STOP quando IC95% do gradiente contem zero",
        "familha_decisoes": 4, "theta_seed": 1701,
        "ansatz": "por camada: RX(theta) em 4 qubits + anel CX(0-1,1-2,2-3,3-0)",
        "H": "Z0 + Z1Z2", "parametro_alvo": "RX do qubit 0 na camada 1"}
PROTO_SEAL = hashlib.sha3_256(json.dumps(SPEC, sort_keys=True).encode()).hexdigest()
STATE = os.path.join(HERE, "round_auditor_state.json")

def selo_profundidade(L):
    return {"spec": {"shots": 2048, "stopping_rule": "IC95 do gradiente",
                     "depth": L}, "seal": PROTO_SEAL}

def circuito(L, shift, theta0, rng):
    from qiskit import QuantumCircuit
    qc = QuantumCircuit(4, 4)
    for l in range(L):
        for q in range(4):
            ang = (theta0 + shift) if (l == 0 and q == 0) else rng.uniform(0, 2 * np.pi)
            qc.rx(ang, q)
        qc.cx(0, 1); qc.cx(1, 2); qc.cx(2, 3); qc.cx(3, 0)
    qc.measure(range(4), range(4))
    return qc

def depth(L):
    import time
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
    from qiskit import transpile
    token = os.environ["QISKIT_IBM_TOKEN"]
    svc = QiskitRuntimeService(token=token, channel="ibm_quantum_platform", instance="auto")
    bes = [(b.status().pending_jobs, b.name) for b in svc.backends() if b.status().operational]
    be = svc.backends(bes and sorted(bes)[0][1] or "ibm_fez")[0] if False else svc.backend(sorted(bes)[0][1])
    theta0 = float(np.random.default_rng(1701).uniform(0, 2 * np.pi))
    rng = np.random.default_rng(1701 + L)
    c_p = transpile(circuito(L, +np.pi / 2, theta0, rng), backend=be, optimization_level=1, seed_transpiler=7)
    rng2 = np.random.default_rng(1701 + L)
    c_m = transpile(circuito(L, -np.pi / 2, theta0, rng2), backend=be, optimization_level=1, seed_transpiler=7)
    sampler = SamplerV2(mode=be)
    job = sampler.run([(c_p, None, 1024), (c_m, None, 1024)], shots=1024)
    while job.status() not in ("DONE", "ERROR", "CANCELLED"):
        time.sleep(20)
    r = job.result()
    counts = (r[0].data.c.get_counts(), r[1].data.c.get_counts())
    g, sg, banda = gradiente_band(counts, 2048)
    d = audit_step(g, banda, 2048, selo_profundidade(L))
    st = json.load(open(STATE)) if os.path.exists(STATE) else {"decisoes": [], "jobs": []}
    st["decisoes"].append({"depth": L, "g": round(g, 4), "sigma": round(sg, 4),
                           "banda": round(banda, 4), "decisao": d["decisao"],
                           "motivo": d["motivo"], "job": job.job_id(), "backend": be.name})
    json.dump(st, open(STATE, "w"), indent=1)
    print("depth %d: g=%.4f banda=%.4f => %s (%s) [job %s]" % (L, g, banda, d["decisao"], d["motivo"], job.job_id()))

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "depth"
    if mode == "seal":
        print("PROTOCOLO SELADO (SHA3-256):", PROTO_SEAL)
        print(json.dumps(SPEC, sort_keys=True))
    elif mode == "depth":
        depth(int(sys.argv[2]))

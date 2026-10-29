# -*- coding: utf-8 -*-
"""P-08 (ZNE vs C†) e P-10 (fronteira clássica vs hardware). Recibos selados."""
import json, os
import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from zyql_witness import _dj, _ideal_probs, _tvd, _seal

def _body(n, kind="balanced"):
    qc = QuantumCircuit(QuantumRegister(n + 1, "q"))
    qc.x(n)
    for i in range(n + 1):
        qc.h(i)
    if kind == "const1":
        qc.x(n)
    elif kind == "balanced":
        qc.cx(0, n)
    for i in range(n):
        qc.h(i)
    return qc

def _run_batch(circuits, shots, qpu):
    if qpu is None:
        from qiskit_aer import AerSimulator
        sim = AerSimulator(seed_simulator=11)
        tq = [transpile(c, sim) for c in circuits]
        r = sim.run(tq, shots=shots).result()
        return [r.get_counts(i) for i in range(len(tq))], "aer_simulator", "local"
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
    tok = os.environ.get("IBM_API_KEY") or os.environ.get("GITHUB_TOKEN_2")
    svc = QiskitRuntimeService(channel="ibm_quantum_platform", token=tok)
    b = svc.backend(qpu)
    tq = [transpile(c, backend=b, optimization_level=1) for c in circuits]
    job = Sampler(mode=b).run(tq, shots=shots)
    r = job.result()
    return [r[i].data.c.get_counts() for i in range(len(tq))], b.name, job.job_id()

def protocolo_p10(dims=(3, 4, 5), shots=4096, qpu=None, seal_path=None):
    circs = [_dj("balanced", n) for n in dims]
    counts, dev, jid = _run_batch(circs, shots, qpu)
    linhas = []
    for n, c in zip(dims, counts):
        linhas.append({"n": n, "tvd": round(_tvd(_ideal_probs("balanced", n), c, n), 4)})
    payload = {"protocolo": {"id": "P-10", "declarado": {"dims": list(dims), "shots": shots,
               "metrica": "TVD entre ideal clássico e contagens do hardware"}},
               "execucao": {"dispositivo": dev, "job_id": jid}, "resultado": linhas}
    rec = _seal(payload)
    if seal_path:
        json.dump(rec, open(seal_path, "w"), ensure_ascii=False, indent=1)
    return rec, linhas

def _folded(n, f, kind="balanced"):
    U, Ud = _body(n, kind), _body(n, kind).inverse()
    qc = QuantumCircuit(QuantumRegister(n + 1, "q"), ClassicalRegister(n, "c"))
    qc.compose(U, inplace=True)
    for _ in range((f - 1) // 2):
        qc.compose(Ud, inplace=True)
        qc.compose(U, inplace=True)
    qc.measure(list(range(n)), qc.clbits)
    return qc

def protocolo_p08(n=4, folds=(1, 3, 5), shots=2048, qpu=None, seal_path=None):
    circs = [_folded(n, f) for f in folds]
    mir = QuantumCircuit(QuantumRegister(n + 1, "q"), ClassicalRegister(n + 1, "c"))
    U = _body(n)
    mir.compose(U, inplace=True)
    mir.compose(U.inverse(), inplace=True)
    mir.measure(list(range(n + 1)), mir.clbits)
    counts, dev, jid = _run_batch(circs + [mir], shots, qpu)
    p0 = [c.get("0" * n, 0) / shots for c in counts[:-1]]
    sc = counts[-1].get("0" * (n + 1), 0) / shots
    zne = float(np.polyfit(folds, p0, 1)[1])
    payload = {"protocolo": {"id": "P-08", "declarado": {"n": n, "folds": list(folds),
               "shots": shots, "estimador": "p0(fold) em f=0 por regressao linear"}},
               "execucao": {"dispositivo": dev, "job_id": jid, "p0_por_fold": p0,
                            "selfcheck_p0": round(sc, 4)},
               "resultado": {"p0_zne": round(zne, 4), "p0_medio_sem_zne": round(float(np.mean(p0)), 4)}}
    rec = _seal(payload)
    if seal_path:
        json.dump(rec, open(seal_path, "w"), ensure_ascii=False, indent=1)
    return rec, payload["resultado"]

# -*- coding: utf-8 -*-
"""ZYQL REFUSAL WITNESS — abstenção com PROVA (v0.1)

A pergunta silenciosa de todo resultado quântico: "o dispositivo executou o que eu
pedi?" Esta primitiva responde com semântica trivalente:

  1  CERTIFICADO  -> TVD (distância variacional total) entre a distribuição ideal
                     (referência exata) e a medida cabe dentro de epsilon, com
                     confiança 1-alpha.
  0  REPROVADO    -> a TVD PROVA desvio além de epsilon: qualquer veredito
                     subsequente do dispositivo NÃO é sustentável.
  REFUSED         -> evidência insuficiente para afirmar fidelidade OU desvio
                     (limite estatístico largo demais): mais shots são necessários.

Limite declarado ANTES da execução (Hoeffding + união sobre K=2^n resultados):
  delta = sqrt( K * ln(2/alpha) / (2*N) )
Veredito: upper = tvd_hat + delta; lower = max(0, tvd_hat - delta)
  upper <= eps -> 1 | lower > eps -> 0 | senão -> REFUSED

Sem bibliotecas de terceiros além do driver Qiskit (simulação ideal + hardware).
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import time
from dataclasses import dataclass, field, asdict

import numpy as np


@dataclass
class Witness:
    verdict: str
    mode: str
    tvd: float
    delta: float
    epsilon: float
    shots: int
    n: int
    qpu: str = "local"
    job_id: str = ""
    latency_ms: int = 0
    receipt: dict = field(default=None, repr=False, compare=False)


def _dj(kind: str, n: int):
    """Circuito de decisão DJ (mede só as n entradas)."""
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
    qr = QuantumRegister(n + 1, "q")
    cr = ClassicalRegister(n, "c")
    qc = QuantumCircuit(qr, cr)
    qc.x(qr[n])
    for i in range(n):
        qc.h(qr[i])
    qc.h(qr[n])
    if kind == "const1":
        qc.x(qr[n])
    elif kind == "balanced":
        qc.cx(qr[0], qr[n])
    elif kind != "const0":
        raise ValueError(f"oráculo desconhecido: {kind}")
    for i in range(n):
        qc.h(qr[i])
    qc.measure(qr[:n], cr)
    return qc


def _ideal_probs(kind: str, n: int) -> dict:
    """Distribuição ideal exata via statevector do circuito SEM medição."""
    from qiskit import QuantumCircuit, QuantumRegister
    from qiskit.quantum_info import Statevector
    qr = QuantumRegister(n + 1, "q")
    qc = QuantumCircuit(qr)
    qc.x(qr[n])
    for i in range(n):
        qc.h(qr[i])
    qc.h(qr[n])
    if kind == "const1":
        qc.x(qr[n])
    elif kind == "balanced":
        qc.cx(qr[0], qr[n])
    for i in range(n):
        qc.h(qr[i])
    sv = Statevector(qc)
    probs = np.zeros(2 ** n)
    for i, amp in enumerate(sv.data):
        # mede só as n entradas: soma sobre o ancilar
        probs[i % (2 ** n)] += abs(amp) ** 2
    return {format(k, f"0{n}b"): float(v) for k, v in enumerate(probs) if v > 1e-12}


def _run_local(circuit, shots: int):
    from qiskit_aer import AerSimulator
    sim = AerSimulator(seed_simulator=1701)
    r = sim.run(circuit, shots=shots).result()
    return r.get_counts(), "aer_simulator", "local"


def _run_ibm(circuit, shots: int, qpu: str):
    from qiskit import transpile
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
    tok = (os.environ.get("IBM_API_KEY") or os.environ.get("GITHUB_TOKEN_2")
           or os.environ.get("IBM_QUANTUM_TOKEN"))
    if not tok:
        raise RuntimeError("sem chave IBM Quantum no ambiente (IBM_API_KEY)")
    svc = QiskitRuntimeService(channel="ibm_quantum_platform", token=tok)
    backend = svc.backend(qpu)
    tqc = transpile(circuit, backend=backend, optimization_level=1)
    sampler = Sampler(mode=backend)
    job = sampler.run([tqc], shots=shots)
    res = job.result()
    counts = res[0].data.c.get_counts()
    return counts, backend.name, job.job_id()


def _tvd(ideal: dict, counts: dict, n: int) -> float:
    total = sum(counts.values())
    obs = {k.replace(" ", ""): v / total for k, v in counts.items()}
    keys = set(ideal) | set(obs)
    return 0.5 * sum(abs(ideal.get(k, 0.0) - obs.get(k, 0.0)) for k in keys)


def _seal(payload: dict) -> dict:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()
    payload = dict(payload)
    payload["receipt_sha3_256"] = hashlib.sha3_256(raw).hexdigest()
    return payload


def witness(kind: str = "const1", n: int = 3, epsilon: float = 0.10,
            shots: int = 4096, alpha: float = 0.01, qpu: str | None = None,
            seal_path: str | None = None) -> Witness:
    """Testemunha de abstenção: o dispositivo executou o circuito pretendido?"""
    if not (0 < epsilon < 1):
        raise ValueError("epsilon fora de (0,1)")
    if not (64 <= shots <= 200_000):
        raise ValueError("shots fora da banda 64..200000")
    t0 = time.perf_counter()

    circ = _dj(kind, n)
    ideal = _ideal_probs(kind, n)
    ref_hash = hashlib.sha3_256(
        json.dumps(ideal, sort_keys=True).encode()).hexdigest()

    # protocolo declarado ANTES da execução
    K = max(len(ideal), 2 ** n)
    delta_rule = "sqrt(K*ln(2/alpha)/(2N)); veredito por [lower,upper] vs epsilon"

    if qpu:
        counts, dev, jid = _run_ibm(circ, shots, qpu)
    else:
        counts, dev, jid = _run_local(circ, shots)

    tvd_hat = _tvd(ideal, counts, n)
    delta = math.sqrt(K * math.log(2 / alpha) / (2 * shots))
    upper, lower = tvd_hat + delta, max(0.0, tvd_hat - delta)
    if upper <= epsilon:
        verdict, mode = "1", "CERTIFICADO"
    elif lower > epsilon:
        verdict, mode = "0", "REPROVADO"
    else:
        verdict, mode = "REFUSED", "REFUSED_EVIDENCIA_INSUFICIENTE"

    payload = {
        "protocolo": {"primitiva": "refusal_witness", "oraculo": kind, "n": n,
                      "epsilon": epsilon, "alpha": alpha, "shots": shots,
                      "limite": delta_rule, "K": K,
                      "semantica": "1=certificado, 0=reprovado, REFUSED=insuficiente"},
        "referencia_ideal_sha3": ref_hash,
        "execucao": {"dispositivo": dev, "job_id": jid, "counts": counts},
        "resultado": {"tvd": round(tvd_hat, 6), "delta": round(delta, 6),
                      "lower": round(lower, 6), "upper": round(upper, 6),
                      "veredito": verdict, "modo": mode},
    }
    receipt = _seal(payload)
    if seal_path:
        with open(seal_path, "w", encoding="utf-8") as fh:
            json.dump(receipt, fh, ensure_ascii=False, indent=1)
    w = Witness(verdict=verdict, mode=mode, tvd=tvd_hat, delta=delta,
                epsilon=epsilon, shots=shots, n=n, qpu=dev, job_id=jid,
                latency_ms=int((time.perf_counter() - t0) * 1000), receipt=receipt)
    return w


def verify_receipt(path: str) -> bool:
    with open(path, encoding="utf-8") as fh:
        payload = json.load(fh)
    sig = payload.pop("receipt_sha3_256", None)
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()
    return sig == hashlib.sha3_256(raw).hexdigest()

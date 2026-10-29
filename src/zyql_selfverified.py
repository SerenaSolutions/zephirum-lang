# -*- coding: utf-8 -*-
"""ZYQL SELF-VERIFIED DEVICE DECISION.

Decisão trivalente executada EM QPU, onde a própria QPU certifica a execução:

1) AUTO-VERIFICAÇÃO (espelho C†): o mesmo job inclui o circuito da decisão
   seguido do seu inverso; o estado final medido deve ser |0...0>. A taxa de
   zeros observada é a métrica de auto-verificação do dispositivo, carimbada
   no recibo. Abaixo do limiar declarado -> REFUSED (abstenção trivalente).
2) EVIDÊNCIA SEQUENCIAL: a decisão é enviada em lotes; a regra de parada
   (alpha-spending geométrico) é DECLARADA ANTES da execução e permite parar
   cedo quando a evidência cruza a fronteira, ou recusar se esgotar os lotes.
3) RECIBO: protocolo declarado + contagens por lote + selfcheck + veredito,
   selado com SHA3-256 (integridade de conteúdo, não autoria).

Nada aqui é hand-rolled além do protocolo: a execução usa o driver oficial
Qiskit/IBM Quantum (infraestrutura de acesso), como o resto do ecossistema.
"""
import hashlib
import json
import math
import time
from dataclasses import dataclass, field

VERSAO = "zyql-selfverified-0.1"


@dataclass
class SelfVerifiedDecision:
    verdict: object
    p0: float
    selfcheck_p0: float
    batches_used: int
    shots_used: int
    error_bound: float
    mode: str
    qpu: str
    job_id: str
    latency_ms: float
    receipt: dict = field(default=None, repr=False, compare=False)


def _dj_circuit(n, kind, mirror=False):
    """Circuito Deutsch-Jozsa: kind in {'const0','const1','balanced'}."""
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
    qr = QuantumRegister(n + 1, "q")
    cr = ClassicalRegister(n + 1 if mirror else n, "c")
    qc = QuantumCircuit(qr, cr)
    anc = n
    qc.x(anc)
    for i in range(n + 1):
        qc.h(i)
    if kind == "const1":
        qc.x(anc)
    elif kind == "balanced":
        qc.cx(0, anc)
    for i in range(n):
        qc.h(i)
    if mirror:
        # U^dagger: mesma sequência em ordem reversa (portas auto-inversas)
        for i in range(n - 1, -1, -1):
            qc.h(i)
        if kind == "balanced":
            qc.cx(0, anc)
        elif kind == "const1":
            qc.x(anc)
        for i in range(n, -1, -1):
            qc.h(i)
        qc.x(anc)
    qc.measure(qr[: (n + 1 if mirror else n)], cr)
    return qc


def _p0(counts):
    """Fração de |0...0> nas contagens."""
    tot = sum(counts.values())
    if tot == 0:
        return 0.0
    z = sum(v for k, v in counts.items() if set(k) <= {"0"})
    return z / tot


def _run_local(circuits, shots_per, seed=1701):
    from qiskit_aer import AerSimulator
    sim = AerSimulator(seed_simulator=seed)
    res = sim.run(circuits, shots=shots_per).result()
    return [res.get_counts(i) for i in range(len(circuits))], "aer_simulator", "local"


def _run_ibm(circuits, shots_per, backend_name, token_env="IBM_QUANTUM_TOKEN"):
    import os
    from qiskit import transpile
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
    tok = (os.environ.get("IBM_API_KEY") or os.environ.get("GITHUB_TOKEN_2")
           or os.environ.get(token_env))
    if not tok:
        raise RuntimeError("sem chave IBM Quantum no ambiente (IBM_API_KEY)")
    svc = QiskitRuntimeService(channel="ibm_quantum_platform", token=tok)
    backend = svc.backend(backend_name)
    trans = transpile(circuits, backend=backend, optimization_level=1,
                      seed_transpiler=1701)
    sampler = Sampler(mode=backend)
    job = sampler.run(trans, shots=shots_per)
    res = job.result()
    counts = [res[i].data.c.get_counts() for i in range(len(circuits))]
    return counts, backend_name, job.job_id()


def decide_selfverified(kind="const1", n=3, batches=4, shots_per_batch=128,
                        alpha=0.01, selfcheck_min=0.80, qpu=None,
                        seal_path=None, seed=1701):
    """Decisão trivalente com auto-verificação e evidência sequencial."""
    t0 = time.perf_counter()
    # PROTOCOLO DECLARADO ANTES DA EXECUÇÃO (auditável no recibo)
    protocolo = {
        "regra_de_parada": "sequencial_batelada_alpha_spending_geometrico",
        "alpha_total": alpha,
        "alpha_por_lote": "alpha/2^k (k=indice do lote)",
        "fronteira": "t_k = sqrt(ln(2/alpha_k)/(2*N_k)); cruzar 0.5+/-t_k decide",
        "lotes_max": batches,
        "shots_por_lote": shots_per_batch,
        "limiar_selfcheck": selfcheck_min,
        "inconclusivo": "REFUSED (sem retry silencioso)",
        "hipotese": "shots i.i.d.; ruido correlacionado fora do escopo",
    }

    circuits = [_dj_circuit(n, kind, mirror=False) for _ in range(batches)]
    circuits.append(_dj_circuit(n, kind, mirror=True))

    if qpu:
        counts_all, qpu_nome, job_id = _run_ibm(circuits, shots_per_batch, qpu)
    else:
        counts_all, qpu_nome, job_id = _run_local(circuits, shots_per_batch, seed)

    lotes = counts_all[:batches]
    selfcheck_p0 = _p0(counts_all[batches])

    # EVIDÊNCIA SEQUENCIAL
    acc = {}
    verdict = "REFUSED"
    mode = "REFUSED_INCONCLUSIVO_SEQUENCIAL"
    usados = 0
    for k, c in enumerate(lotes, start=1):
        for key, v in c.items():
            acc[key] = acc.get(key, 0) + v
        usados = k
        N = sum(acc.values())
        a_k = alpha / (2 ** k)
        t_k = math.sqrt(math.log(2.0 / a_k) / (2.0 * N))
        p0 = _p0(acc)
        if p0 >= 0.5 + t_k:
            verdict, mode = "1", "SEQUENCIAL_CONSTANTE"
            break
        if p0 <= 0.5 - t_k:
            verdict, mode = "0", "SEQUENCIAL_CONSTANTE_FALSE"
            break

    p0_final = _p0(acc)
    N_final = sum(acc.values()) or 1
    erro = math.sqrt(math.log(2.0 / alpha) / (2.0 * N_final))

    if selfcheck_p0 < selfcheck_min:
        verdict, mode = "REFUSED", (
            "REFUSED_SELFCHECK_FALHOU (p0_espelho=%.3f < %.2f)"
            % (selfcheck_p0, selfcheck_min))

    lat = round((time.perf_counter() - t0) * 1000, 1)
    foi_qpu = bool(qpu)
    receipt = None
    if seal_path:
        payload = {
            "veredito": verdict, "p0_final": round(p0_final, 6),
            "selfcheck_p0": round(selfcheck_p0, 6),
            "lotes_usados": usados, "shots_usados": N_final,
            "erro_limite": round(erro, 6), "modo": mode,
            "qpu": qpu_nome, "job_id": job_id,
            "hardware_real": foi_qpu, "n": n, "oraculo": kind,
            "protocolo": protocolo,
            "contagens_por_lote": lotes,
            "selado_por": VERSAO,
        }
        selo = hashlib.sha3_256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
        receipt = {"payload": payload, "selo_sha3_256": selo}
        with open(seal_path, "w") as fh:
            json.dump(receipt, fh, indent=1, ensure_ascii=False)

    return SelfVerifiedDecision(verdict=verdict, p0=p0_final,
                                selfcheck_p0=selfcheck_p0, batches_used=usados,
                                shots_used=N_final, error_bound=erro, mode=mode,
                                qpu=qpu_nome, job_id=job_id, latency_ms=lat,
                                receipt=receipt)


def verify_receipt(path):
    rec = json.load(open(path))
    payload = rec["payload"]
    return rec["selo_sha3_256"] == hashlib.sha3_256(
        json.dumps(payload, sort_keys=True).encode()).hexdigest()

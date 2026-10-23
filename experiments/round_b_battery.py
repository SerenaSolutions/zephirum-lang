# -*- coding: utf-8 -*-
"""
RODADA B — LACUNA DE SHOTS BAIXOS (Zephirum/ZYQL, Z-QEA)
A Rodada B validou o protocolo estatístico em 512..16384 shots (ibm_fez) e
DECLAROU a lacuna abaixo de 512. Esta rodada fecha a lacuna: a mesma bateria
Deutsch-Jozsa n=3 (const-1, const-0, balanceado) em {64, 128, 256, 384} shots
no IBM Heron ibm_kingston (cross-hardware: conta nova, backend diferente).
4 jobs (um por nível de shots), cada job com os 3 circuitos da bateria.
"""
import os
import json
import time
from datetime import datetime, timezone
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2

TOKEN_PATH = ""  # token vem de IBM_QUANTUM_TOKEN no ambiente
BACKEND_NAME = "ibm_kingston"
SHOT_LEVELS = [64, 128, 256, 384]
CASOS = ["const-1", "const-0", "balanceado"]


def load_token():
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, "r") as f:
            return f.read().strip()
    elif os.environ.get("IBM_QUANTUM_TOKEN"):
        return os.environ["IBM_QUANTUM_TOKEN"]
    elif os.environ.get("IBM_TOKEN"):
        return os.environ["IBM_TOKEN"]
    else:
        raise RuntimeError(f"Token IBM nao encontrado em {TOKEN_PATH} ou os.environ['IBM_TOKEN']")


def dj_circuit(n, caso):
    """Deutsch-Jozsa circuit with n input qubits + 1 ancilla qubit."""
    qc = QuantumCircuit(n + 1, n)
    qc.h(range(n))
    qc.x(n)
    qc.h(n)

    if caso == "const-1":
        qc.x(n)  # f(x) = 1 ∀x: phase kickback -1
    elif caso == "const-0":
        pass     # f(x) = 0 ∀x: identity
    elif caso == "balanceado":
        qc.cx(0, n)
        qc.cx(1, n)
    else:
        raise ValueError(f"Caso desconhecido: {caso}")

    qc.h(range(n))
    qc.measure(range(n), range(n))
    return qc


def main():
    token = load_token()
    service = QiskitRuntimeService(token=token, channel="ibm_quantum_platform", instance="auto")
    backend = service.backend(BACKEND_NAME)
    print(f"Conectado ao backend: {backend.name} ({backend.num_qubits} qubits)")

    # Construir e transpilar circuitos
    circuits = [dj_circuit(3, c) for c in CASOS]
    transpiled_circuits = transpile(circuits, backend=backend, optimization_level=2)

    for c_name, tqc in zip(CASOS, transpiled_circuits):
        print(f"Circuito {c_name}: depth={tqc.depth()}, ops={dict(tqc.count_ops())}")

    sampler = SamplerV2(mode=backend)
    jobs_info = []

    submetido_em = datetime.now(timezone.utc).astimezone().isoformat()

    for shots in SHOT_LEVELS:
        print(f"Submetendo job com {shots} shots...")
        job = sampler.run(transpiled_circuits, shots=shots)
        job_id = job.job_id()
        print(f"  -> Job ID ({shots} shots): {job_id}")
        jobs_info.append({
            "shots": shots,
            "job_id": job_id,
            "casos": CASOS
        })

    meta = {
        "backend": backend.name,
        "submetido_em": submetido_em,
        "jobs": jobs_info
    }

    meta_path = os.path.join(os.path.dirname(__file__), "refusal_round_b_job_meta.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)

    print(f"\nMetadata salvo em {meta_path}:")
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rodada de testes no QPU (IBM Quantum) — bateria trivalente mínima, com recibo selado.

Quatro provas, as mesmas do primeiro voo (13/10/2026):
  DJ constante   -> veredito 0 esperado
  DJ balanceado  -> veredito 1 esperado
  Bell base Z    -> correlação esperada >= teto declarado
  Bell base X    -> correlação esperada >= teto declarado

Uso:
    python experiments/qpu_round.py --sim                      # simulador local (prova o fluxo)
    python experiments/qpu_round.py --backend ibm_fez --shots 256
    python experiments/qpu_round.py --list                     # mostra filas

Credencial: variável de ambiente IBM_QUANTUM_TOKEN (nunca em arquivo, nunca em log).
Sem credencial válida o script falha com código 2 — nunca finge rodada.
"""
from __future__ import annotations
import argparse, datetime, hashlib, json, os, sys

BANDA = 0.15
TETO_CORR = 0.70


def selar(payload: dict) -> dict:
    canon = json.dumps(payload, sort_keys=True, ensure_ascii=True, default=str)
    return {"payload": payload, "selo_sha3_256": hashlib.sha3_256(canon.encode()).hexdigest()}


def circuitos(n=3):
    from qiskit import QuantumCircuit
    cs = []
    # DJ constante: oráculo identidade
    qc = QuantumCircuit(n + 1, n)
    qc.x(n)
    for i in range(n + 1): qc.h(i)
    for i in range(n): qc.h(i)
    qc.measure(range(n), range(n)); cs.append(("DJ_constant", qc, "0"))
    # DJ balanceado: oráculo CNOT do qubit 0 no ancilla
    qc = QuantumCircuit(n + 1, n)
    qc.x(n)
    for i in range(n + 1): qc.h(i)
    qc.cx(0, n)
    for i in range(n): qc.h(i)
    qc.measure(range(n), range(n)); cs.append(("DJ_balanced", qc, "1"))
    # Bell
    bell = QuantumCircuit(2, 2)
    bell.h(0); bell.cx(0, 1); bell.measure([0, 1], [0, 1])
    cs.append(("BELL_Z", bell, "corr>=%.2f" % TETO_CORR))
    bellx = QuantumCircuit(2, 2)
    bellx.h(0); bellx.cx(0, 1); bellx.h(0); bellx.h(1); bellx.measure([0, 1], [0, 1])
    cs.append(("BELL_X", bellx, "corr>=%.2f" % TETO_CORR))
    return cs


def corr_z(counts):
    tot = sum(counts.values()) or 1
    return (counts.get("00", 0) + counts.get("11", 0)) / tot


def corr_x(counts, cr):
    tot = sum(counts.values()) or 1
    a = {f"{r[1]}{r[0]}": v for r, v in cr.items()}
    return (a.get("00", 0) + a.get("11", 0)) / tot


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--sim", action="store_true")
    ap.add_argument("--backend", default=None)
    ap.add_argument("--shots", type=int, default=256)
    ap.add_argument("--outdir", default=None)
    a = ap.parse_args()

    tok = os.environ.get("IBM_QUANTUM_TOKEN") or os.environ.get("IBM_CLOUD_API_KEY")
    inst = os.environ.get("IBM_QUANTUM_INSTANCE") or None
    svc = None
    if not a.sim:
        if not tok:
            print("SEM CREDENCIAL: IBM_QUANTUM_TOKEN/IBM_CLOUD_API_KEY ausente. Nada foi executado.", file=sys.stderr)
            return 2
        from qiskit_ibm_runtime import QiskitRuntimeService
        try:
            svc = QiskitRuntimeService(channel="ibm_quantum_platform", token=tok, instance=inst) if inst else QiskitRuntimeService(channel="ibm_quantum_platform", token=tok)
            svc.backends(operational=True, simulator=False)
        except Exception as exc:
            print("CREDENCIAL INVALIDA: %s" % str(exc)[:120], file=sys.stderr)
            return 2
        if a.list:
            for b in svc.backends(operational=True, simulator=False):
                try:
                    print("%-18s fila %5d  qubits %d" % (b.name, b.status().pending_jobs, b.num_qubits))
                except Exception:
                    pass
            return 0

    cs = circuitos()
    ZERO_KEY = "0" * 3   # mede-se os qubits de DADOS (n=3); o ancilla fica fora
    circuits = [qc for _, qc, _ in cs]

    if a.sim:
        from qiskit_aer import AerSimulator
        sim = AerSimulator(); backend_name = "aer_simulator(local)"
        from qiskit import transpile
        tq = transpile(circuits, sim, seed_transpiler=1701)
        job = sim.run(tq, shots=a.shots); res = job.result()
        counts = [res.get_counts(i) for i in range(len(tq))]
        job_id = "sim-%s" % datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        mode = "simulator"
    else:
        from qiskit import transpile
        from qiskit_ibm_runtime import SamplerV2
        backend = svc.backend(a.backend) if a.backend else min(
            [b for b in svc.backends(operational=True, simulator=False)],
            key=lambda b: b.status().pending_jobs)
        backend_name = backend.name
        tq = transpile(circuits, backend)
        sampler = SamplerV2(mode=backend)
        job = sampler.run(tq, shots=a.shots)
        job_id = job.job_id()
        res = job.result()
        counts = []
        for i in range(len(tq)):
            d = res[i].data
            reg = list(d.keys())[0]
            counts.append(dict(getattr(d, reg).get_counts()))
        mode = "qpu"

    provas, passes = [], 0
    for (nome, _, esperado), c in zip(cs, counts):
        tot = sum(c.values())
        if nome.startswith("DJ"):
            p0 = c.get(ZERO_KEY, 0) / tot
            veredito = "0" if p0 >= 1 - BANDA else ("1" if p0 <= BANDA else "REFUSED")
            ok = (veredito == esperado)
            provas.append(dict(teste=nome, esperado=esperado, observado=veredito,
                               p0=round(p0, 6), shots=tot, pass_=ok))
        else:
            corr = corr_z(c)
            ok = corr >= TETO_CORR
            provas.append(dict(teste=nome, esperado=esperado, correlacao=round(corr, 6),
                               shots=tot, pass_=ok))
        passes += 1 if ok else 0

    payload = dict(
        experiment="zyql_qpu_round", mode=mode, backend=backend_name, job_id=job_id,
        hardware_executed=(mode == "qpu"), shots=a.shots, banda=BANDA,
        teto_correlacao=TETO_CORR,
        gerado_em=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        autore="Serena Solutions", provas=provas,
        resumo=dict(pass_=passes, total=len(provas), flagged=len(provas) - passes),
        canon="selo_sha3_256 sobre este payload canonico (sort_keys, ensure_ascii)",
    )
    rec = selar(payload)
    outdir = a.outdir or os.path.join("experiments", "qpu_round_%s" % datetime.datetime.now().strftime("%Y%m%d"))
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "receipt.json")
    json.dump(rec, open(path, "w"), indent=2, sort_keys=True)

    print("modo      :", mode, "| backend:", backend_name)
    print("job       :", job_id)
    for p in provas:
        print(("  [%s] %-12s esperado %-10s obs %s" % ("PASS" if p["pass_"] else "FAIL",
              p["teste"], p["esperado"], p.get("observado") or p.get("correlacao"))))
    print("resumo    : %d/%d PASS" % (passes, len(provas)))
    print("recibo    :", path, "| selo", rec["selo_sha3_256"][:16])
    return 0 if passes == len(provas) else 1


if __name__ == "__main__":
    sys.exit(main())

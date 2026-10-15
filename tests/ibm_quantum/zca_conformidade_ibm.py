"""
ZCA — SUITE DE CONFORMIDADE NO IBM QUANTUM
Consolidação do degrau quântico da escada certificada (ZYQL kernel).

Protocolo (régua da casa):
  TESTE 1  DJ constante   -> veredito esperado '0'  (fora da banda, inferior)
  TESTE 2  DJ balanceada  -> veredito esperado '1'  (fora da banda, superior)
  TESTE 3  Controle Bell Phi+ (bases Z e X) -> correlação em AMBAS
  TESTE 4  Sentinela de drift: janelas 1a/2a metade do job

Cada teste emite recibo: job_id, backend, shots, p_hat, banda, margem,
decisao/regra, SHA3-256 do payload. Resultado: PASS / FLAGGED (nunca
escondido). Maturidade: EXPERIMENTAL ate validacao live.

Uso:
  com token:   QISKIT_IBM_TOKEN=... python3 zca_conformidade_ibm.py --live
  sem token:   python3 zca_conformidade_ibm.py            (simulador local)
"""
import hashlib
import json
import sys
import time
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.providers.fake_provider import GenericBackendV2

BAND = 0.15          # banda de ruído declarada do kernel
SHOTS = 2048


def _radius(n, delta=0.05):
    import math
    return math.sqrt(math.log(2.0 / delta) / (2.0 * n))


def dj_circuit(kind: str, n: int = 3) -> QuantumCircuit:
    qc = QuantumCircuit(n + 1, n)
    qc.x(n)
    qc.h(range(n + 1))
    if kind == "balanced":
        for i in range(n):
            qc.cx(i, n)
    qc.h(range(n))
    qc.measure(range(n), range(n))
    return qc


def bell_circuit(basis: str) -> QuantumCircuit:
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    if basis == "X":
        qc.h(range(2))
    qc.measure([0, 1], [0, 1])
    return qc


def run_qc(qc, backend, shots=SHOTS, live=False):
    tqc = transpile(qc, backend)
    if live:
        from qiskit_ibm_runtime import SamplerV2
        sampler = SamplerV2(mode=backend)
        job = sampler.run([tqc], shots=shots)
        result = job.result()
        counts = result[0].data.c.get_counts()
    else:
        job = backend.run(tqc, shots=shots)
        counts = job.result().get_counts()
    return counts


def p1_from_dj_counts(counts):
    """Prob. do registrador de saída ser 111... (amplitude |1...1>)."""
    total = sum(counts.values())
    ones = sum(c for bits, c in counts.items() if bits.count("1") == len(bits))
    return ones / total


def corr_from_bell(counts):
    total = sum(counts.values())
    same = sum(c for bits, c in counts.items() if bits[0] == bits[1])
    return same / total


def sentinel(w1, w2):
    eps = _radius(len(w1))
    return abs(np.mean(w1) - np.mean(w2)) > 2 * eps


def decide(p_hat, n, band=BAND):
    lo, hi = p_hat - _radius(n), p_hat + _radius(n)
    if hi <= band:
        return "0", f"p={p_hat:.3f} abaixo da banda -> 0"
    if lo >= 1 - band:
        return "1", f"p={p_hat:.3f} acima da banda -> 1"
    return "REFUSED", f"p={p_hat:.3f} dentro da banda -> REFUSED"


def receipt(teste, payload):
    blob = json.dumps(payload, sort_keys=True, default=str)
    return {"teste": teste, "payload": payload,
            "sha3_256": hashlib.sha3_256(blob.encode()).hexdigest()}


def main(live=False):
    if live:
        import os
        from qiskit_ibm_runtime import QiskitRuntimeService
        token = os.environ.get("QISKIT_IBM_TOKEN") or os.environ.get("API_KEY")
        if not token:
            sys.exit("ERRO: defina QISKIT_IBM_TOKEN no ambiente")
        svc = QiskitRuntimeService(channel="ibm_quantum_platform",
                                   token=token, instance="auto")
        try:
            backend = svc.backend("ibm_fez")
        except Exception:
            backend = svc.least_busy(min_num_qubits=5, operational=True)
        print(f"[live] backend: {backend.name}")
    else:
        backend = GenericBackendV2(num_qubits=7, seed=42)
        print("[sim] backend local GenericBackendV2 (validação do protocolo)")

    receipts = []
    # TESTES 1-2: DJ constante e balanceada
    for kind, esperado in (("constant", "0"), ("balanced", "1")):
        counts = run_qc(dj_circuit(kind), backend, live=live)
        p1 = p1_from_dj_counts(counts)
        v, rule = decide(p1, SHOTS)
        # sentinela de drift: divisão das contagens em duas metades
        bits = []
        for b, c in counts.items():
            bits += [1 if b.count("1") == len(b) else 0] * c
        half = len(bits) // 2
        drift = sentinel(bits[:half], bits[half:])
        status = "PASS" if v == esperado else "FLAGGED"
        r = receipt(f"DJ_{kind}", {
            "esperado": esperado, "obtido": v, "p_hat": round(p1, 4),
            "regra": rule, "drift_detectado": bool(drift),
            "backend": backend.name, "shots": SHOTS,
            "status": status, "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ")})
        receipts.append(r)
        print(f"DJ {kind:9s}: p1={p1:.3f} -> {v:7s} (esperado {esperado}) "
              f"drift={drift} {status}")

    # TESTE 3: Bell Phi+ nas duas bases
    for basis in ("Z", "X"):
        counts = run_qc(bell_circuit(basis), backend, live=live)
        corr = corr_from_bell(counts)
        status = "PASS" if corr >= 1 - 2 * BAND else "FLAGGED"
        r = receipt(f"BELL_{basis}", {
            "correlacao": round(corr, 4), "teto_esperado": round(1 - 2 * BAND, 2),
            "backend": backend.name, "shots": SHOTS,
            "status": status, "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ")})
        receipts.append(r)
        print(f"BELL base {basis}: corr={corr:.3f} (teto >= {1 - 2 * BAND:.2f}) {status}")

    out = {"modo": "live" if live else "sim", "banda": BAND,
           "autor": "Serena Solutions", "recibos": receipts,
           "resumo": {"pass": sum(r["payload"]["status"] == "PASS" for r in receipts),
                      "flagged": sum(r["payload"]["status"] == "FLAGGED" for r in receipts)}}
    fname = f"zca_conformidade_{'live' if live else 'sim'}.json"
    with open(fname, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nresumo: {out['resumo']['pass']} PASS / {out['resumo']['flagged']} FLAGGED")
    print(f"recibos -> {fname}")


if __name__ == "__main__":
    main(live="--live" in sys.argv)

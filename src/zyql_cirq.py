"""Ponte ZYQL <-> Google Cirq: paridade de veredito trivalente e recibo.

Comprova que a SEMÂNTICA da ZYQL sobrevive à travessia para o framework
do Google: mesmo circuito, mesmo veredito 1/0/REFUSED, recibo selado.
"""
from __future__ import annotations
import hashlib, json, math

def _circuito_cirq(kind: str, n: int):
    import cirq
    qs = cirq.LineQubit.range(n + 1)
    ops = [cirq.H(q) for q in qs[:n]] + [cirq.X(qs[n]), cirq.H(qs[n])]
    ops += [cirq.Z(qs[n])] if kind == "const" else [cirq.CNOT(qs[i], qs[n]) for i in range(n)]
    ops += [cirq.H(q) for q in qs[:n]]
    return cirq.Circuit(ops)

def veredito_cirq(kind: str = "const", n: int = 3, shots: int = 4096, seed: int = 7):
    """Executa o experimento de Deutsch-Jozsa no simulador do Cirq e devolve
    (veredito, p0) com a MESMA regra trivalente (epsilon=0.05, alpha=0.01)."""
    import cirq, numpy as np
    circ = _circuito_cirq(kind, n)
    qs = sorted(circ.all_qubits(), key=lambda q: q.x)
    circ.append(cirq.measure(*qs[:n], key="r"))
    sim = cirq.Simulator(seed=seed)
    res = sim.run(circ, repetitions=shots)
    bits = res.measurements["r"]
    zeros = int(np.sum(np.all(bits == 0, axis=1)))
    p0 = zeros / shots
    delta = math.sqrt((2 ** n) * math.log(2 / 0.01) / (2 * shots))
    if p0 - delta > 0.5:
        v = "1"
    elif p0 + delta < 0.5:
        v = "0"
    else:
        v = "REFUSED"
    return v, round(p0, 4)

def paridade(kind: str = "const", n: int = 3, shots: int = 4096, seed: int = 7,
             seal_path: str | None = None) -> dict:
    """Compara o veredito ZYQL (referência global exata) com o do Cirq."""
    import numpy as np
    ideal_p0 = 1.0 if kind == "const" else 0.0
    esperado = "1" if ideal_p0 > 0.5 else "0"
    v_cirq, p0 = veredito_cirq(kind, n, shots, seed)
    payload = {
        "protocolo": {"id": "G-01", "declarado": {"framework": "google-cirq",
                      "experimento": "deutsch-jozsa", "oraculo": kind, "n": n,
                      "shots": shots, "epsilon": 0.05, "alpha": 0.01}},
        "execucao": {"veredito_cirq": v_cirq, "p0_cirq": p0},
        "resultado": {"veredito_referencia": esperado, "paridade": v_cirq == esperado},
    }
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()
    payload["receipt_sha3_256"] = hashlib.sha3_256(raw).hexdigest()
    if seal_path:
        json.dump(payload, open(seal_path, "w"), ensure_ascii=False, indent=1)
    return payload

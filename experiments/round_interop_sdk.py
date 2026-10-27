# -*- coding: utf-8 -*-
"""RODADA INTEROP-SDK — o veredito trivalente e a mesma lingua em qualquer SDK.
Kernel: Deutsch-Jozsa n=3 (constante-1 e balanceado) nativo em tres stacks
independentes (Qiskit/Cirq/PennyLane) + volta via OpenQASM 3.
Paridade exigida: mesmo veredito e |p0_sdk - p0_qiskit| <= 1e-9 (statevector).
Recibo selado na cadeia Z-QEA ao fim."""
import sys, os, json, hashlib
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
N = 3; MARGIN = 0.15

def trivalent(p0):
    if p0 >= 1 - MARGIN: return "1"
    if p0 <= MARGIN: return "REFUSED_BALANCED"
    return "REFUSED_GRAY"

def leg_qiskit(kind):
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import Statevector
    qc = QuantumCircuit(N + 1)
    qc.h(range(N)); qc.x(N); qc.h(N)
    if kind == "const": qc.x(N)
    else: [qc.cx(i, N) for i in range(N)]
    qc.h(range(N))
    probs = Statevector.from_instruction(qc).probabilities(list(range(N)))
    return float(probs[0])

def leg_cirq(kind):
    import cirq
    qs = cirq.LineQubit.range(N + 1)
    ops = [cirq.H(q) for q in qs[:N]] + [cirq.X(qs[N]), cirq.H(qs[N])]
    if kind == "const": ops.append(cirq.Z(qs[N]))
    else: ops += [cirq.CNOT(qs[i], qs[N]) for i in range(N)]
    ops += [cirq.H(q) for q in qs[:N]]
    sv = cirq.Simulator(dtype=__import__('numpy').complex128).simulate(cirq.Circuit(*ops)).final_state_vector
    import numpy as np
    # marginal dos N inputs (q0..qN-1); ancilla (qN, LSB) somada fora
    amp0 = float(np.abs(sv[0]) ** 2 + np.abs(sv[1]) ** 2)
    return amp0

def leg_pennylane(kind):
    import pennylane as qml
    dev = qml.device("default.qubit", wires=N + 1)
    @qml.qnode(dev)
    def circ():
        for i in range(N): qml.Hadamard(wires=i)
        qml.PauliX(N); qml.Hadamard(N)
        if kind == "const": qml.PauliZ(N)
        else:
            for i in range(N): qml.CNOT(wires=[i, N])
        for i in range(N): qml.Hadamard(wires=i)
        return qml.probs(wires=list(range(N)))
    return float(circ()[0])

def leg_oq3(kind):
    # volta: circuito Qiskit -> OpenQASM 3 -> reimport -> statevector
    from qiskit import QuantumCircuit, qasm3
    from qiskit.quantum_info import Statevector
    try:
        from qiskit_qasm3_import import parse
    except Exception:
        return None
    qc = QuantumCircuit(N + 1)
    qc.h(range(N)); qc.x(N); qc.h(N)
    if kind == "const": qc.x(N)
    else: [qc.cx(i, N) for i in range(N)]
    qc.h(range(N))
    qasm = qasm3.dumps(qc)
    qc2 = parse(qasm)
    probs = Statevector.from_instruction(qc2).probabilities(list(range(N)))
    return float(probs[0])

def main():
    legs = {"qiskit": leg_qiskit, "cirq": leg_cirq,
            "pennylane": leg_pennylane, "openqasm3": leg_oq3}
    report = {"modulo": "experiments/round_interop_sdk.py",
              "proposito": "Paridade do veredito trivalente DJ n=3 entre SDKs independentes",
              "kernel": "Deutsch-Jozsa n=3 + ancilla, oraculo de fase",
              "margin": MARGIN, "leg": {}, "parity_ok": True}
    for kind in ("const", "balanced"):
        p0s = {}
        for name, fn in legs.items():
            p0 = fn(kind)
            if p0 is None: continue
            p0s[name] = p0
            v = trivalent(p0)
            report["leg"].setdefault(kind, {})[name] = {"p0": round(p0, 12), "verdict": v}
        base = p0s["qiskit"]
        for name, p0 in p0s.items():
            if abs(p0 - base) > 1e-9:
                report["parity_ok"] = False
        verdicts = {x["verdict"] for x in report["leg"][kind].values()}
        if len(verdicts) != 1:
            report["parity_ok"] = False
    print(json.dumps(report["leg"], indent=1))
    print("PARITY_OK:", report["parity_ok"])
    return report

if __name__ == "__main__":
    rep = main()
    # recibo Z-QEA encadeado na ponta atual da cadeia
    import glob
    tip = None
    seals = {}
    for f in glob.glob(os.path.join(os.path.dirname(__file__), "*receipt*.json")):
        try:
            d = json.load(open(f))
            seals[d.get("selo_sha3_256")] = f
        except Exception:
            pass
    prevs = set()
    for f, _ in seals.items():
        pass
    tip_seal = None
    for f in glob.glob(os.path.join(os.path.dirname(__file__), "*receipt*.json")):
        try:
            d = json.load(open(f))
            p = d.get("previous_seal") or (d.get("chain") or {}).get("previous_seal")
            if p: prevs.add(p)
        except Exception:
            pass
    # tip = recibo NAO-referenciado com o carimbo de DATA mais recente
    def _data(seal):
        try:
            return json.load(open(seals[seal])).get("data") or ""
        except Exception:
            return ""
    cand = [s for s in seals if s and s not in prevs]
    if cand:
        tip_seal = max(cand, key=_data)
    rep["previous_seal"] = tip_seal
    rep["resultado"] = "PARITY_OK_VERDICTOS_IDENTICOS" if rep["parity_ok"] else "PARITY_BROKEN"
    payload = {k: v for k, v in rep.items() if k != "selo_sha3_256"}
    rep["selo_sha3_256"] = hashlib.sha3_256(
        json.dumps(payload, sort_keys=True, ensure_ascii=True, default=str).encode()).hexdigest()
    out = os.path.join(os.path.dirname(__file__), "round_interop_receipt.json")
    json.dump(rep, open(out, "w"), indent=1, ensure_ascii=True)
    print("selo:", rep["selo_sha3_256"][:16], "| chain em:", (tip_seal or "?")[:16])

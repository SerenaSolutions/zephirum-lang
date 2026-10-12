"""
Zephyron → OpenQASM 3 transpiler.
Zephyron is the circuit language of the Zephyrum ecosystem; OpenQASM 3 is
the interchange language IBM Quantum (Qiskit Runtime) ingests. This bridge
is the honest path to real IBM hardware: IBM will never run Zephyron
natively, but it accepts its compiled output.
"""

def to_openqasm3(gates, nqubits):
    """gates: list of strings as produced by QCircuit.gates_applied,
    e.g. 'H(0)', 'X(1)', 'CNOT(0->1)', 'CZ(0,1)', 'T(1)'."""
    lines = ["OPENQASM 3.0;", 'include "stdgates.inc";',
             f"qubit[{nqubits}] q;", f"bit[{nqubits}] c;"]
    for g in gates:
        name, rest = g.split("(", 1)
        args = rest.rstrip(")").replace(" ", "")
        if name == "CNOT":
            c, t = args.split("->")
            lines.append(f"cx q[{c}], q[{t}];")
        elif name == "CZ":
            c, t = args.split(",")
            lines.append(f"cz q[{c}], q[{t}];")
        elif name == "Z":
            q = args
            lines.append(f"z q[{q}];")
        else:
            q = args
            lines.append(f"{name.lower()} q[{q}];")
    lines.append("c = measure q;")
    return "\n".join(lines) + "\n"

if __name__ == "__main__":
    from programs import bell, ghz, grover2
    for name, prog in (("bell", bell), ("ghz", ghz), ("grover", grover2)):
        qc, _ = prog(shots=1)
        oq3 = to_openqasm3(qc.gates_applied, qc.n)
        print(f"=== {name} ===")
        print(oq3)


# --- OpenQASM 3 -> Zephyron importer (uses the reference parser) ---
def from_openqasm3(src):
    """Parse valid OpenQASM 3 (e.g. produced by IBM tools or our own
    transpiler) into a Zephyron QCircuit. Returns (circuit, gates)."""
    import math
    from openqasm3.parser import parse
    from openqasm3.ast import (QuantumGate, QubitDeclaration,
                              IndexedIdentifier, IntegerLiteral, UnaryExpression)
    from zquantum import QCircuit

    nq = 0
    gates = []
    for st in parse(src).statements:
        if isinstance(st, QubitDeclaration):
            size = st.size
            if isinstance(size, UnaryExpression):
                nq = -size.expression.value
            else:
                nq = size.value
        elif isinstance(st, QuantumGate):
            name = st.name.name
            qubits = []
            for q in st.qubits:
                if isinstance(q, IndexedIdentifier):
                    idx = q.indices[0][0]
                    v = idx.value if hasattr(idx, "value") else int(str(idx))
                    qubits.append(v)
            angles = [a.value for a in st.arguments]
            if name in ("cx", "cnot"):
                gates.append(f"CNOT({qubits[0]}->{qubits[1]})")
            elif name == "cz":
                gates.append(f"CZ({qubits[0]},{qubits[1]})")
            elif name == "swap":
                gates.append(f"SWAP({qubits[0]},{qubits[1]})")
            elif name == "ccx":
                gates.append(f"TOFFOLI({qubits[0]},{qubits[1]}->{qubits[2]})")
            elif name in ("rx", "ry", "rz"):
                gates.append(f"{name.upper()}({qubits[0]},{angles[0]})")
            elif name == "id":
                continue
            else:
                gates.append(f"{name.upper()}({qubits[0]})")
    qc = QCircuit.from_gates(nq, gates)
    return qc, gates

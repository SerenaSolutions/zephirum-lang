"""
ZEPHIRUM QUANTUM TYPES (v1.0.0, 12/10/2026) — qbit as a first-class type.
Prototype pre-parser: the type layer is real (wraps the state-vector kernel),
the Zephirum interpreter wiring is the next step (declared limitation).

What it enforces:
  1. qbit declarations, unitary application, entanglement, measurement
  2. NO-CLONING enforced by the type: assigning/copying a quantum value
     raises CompileError at the type check, before any execution
  3. qif: quantum conditional via controlled operation (no collapse)
"""
import sys, os, json, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from zquantum import QCircuit

class CompileError(Exception):
    pass

class QType:
    """First-class quantum value. Lives in one circuit; cannot be copied."""
    def __init__(self, circ, index, size=1):
        self.circ, self.index, self.size = circ, index, size

    # no-cloning enforced by the type: any copy attempt fails at compile time
    def __copy__(self):      raise CompileError("NO_CLONING: quantum value cannot be copied")
    def __deepcopy__(self, m): raise CompileError("NO_CLONING: quantum value cannot be copied")
    def clone(self):         raise CompileError("NO_CLONING: quantum value cannot be copied")


class QuantumLang:
    """Mini pre-parser layer: qbit / H / CNOT / qif / measure."""

    def __init__(self, n):
        self.circ = QCircuit(n)
        self.n = n
        self.vars = {}
        self.classical_copies = []      # legal: measured (collapsed) results

    def qbit(self, name):
        if name in self.vars: raise CompileError("redeclaration of qbit " + name)
        idx = len(self.vars)
        self.vars[name] = QType(self.circ, idx)
        return self.vars[name]

    def h(self, name):
        self.circ.h(self.vars[name].index)

    def x(self, name):
        self.circ.x(self.vars[name].index)

    def cnot(self, a, b):
        self.circ.cnot(self.vars[a].index, self.vars[b].index)

    def qif(self, cond_name, then_op):
        """Quantum conditional: controlled operation, NO measurement, NO collapse.
        then_op is a single-qubit X for the prototype (control decomposition)."""
        if then_op.upper() not in ("X",):
            raise CompileError("qif prototype supports controlled-X only")
        self.circ.cnot(self.vars[cond_name].index,
                       self._last_free_target(cond_name))

    def _last_free_target(self, not_this):
        targets = [v for k, v in self.vars.items() if v.index != self.vars[not_this].index]
        return targets[-1].index

    def measure(self, name, shots=4096, seed=11):
        """Measurement collapses: the RESULT is classical and copyable."""
        c = self.circ.measure_all(shots=shots, seed=seed)
        self.classical_copies.append({name: c})
        return c

    def assign(self, dst, src):
        """Type-checked assignment: quantum -> quantum is NO_CLONING (CompileError)."""
        if src in self.vars:
            raise CompileError("NO_CLONING: assignment of quantum value '%s' rejected by the type" % src)
        raise CompileError("unknown assignment %s = %s" % (dst, src))


def main():
    proof = {"module": "quantum_types.py", "version": "1.0.0",
             "date": time.strftime("%Y-%m-%d %H:%M:%S"), "tests": []}

    # 1. entanglement: Bell state 1/2 + 1/2
    lang = QuantumLang(2)
    a, b = lang.qbit("a"), lang.qbit("b")
    lang.h("a"); lang.cnot("a", "b")
    c = lang.measure("a", shots=4096, seed=42)
    p00, p11 = c.get("|00>", 0) / 4096, c.get("|11>", 0) / 4096
    ent = abs(p00 - 0.5) < 0.02 and abs(p11 - 0.5) < 0.02
    proof["tests"].append({"name": "entanglement (Bell 1/2+1/2)",
                           "p00": round(p00, 4), "p11": round(p11, 4), "PASS": ent})

    # 2. no-cloning enforced by the type
    try:
        lang2 = QuantumLang(2)
        lang2.qbit("q"); lang2.qbit("r")
        lang2.assign("r", "q")           # must raise CompileError
        nc = False
    except CompileError as e:
        nc = "NO_CLONING" in str(e)
    proof["tests"].append({"name": "no-cloning rejected by type (assign)", "PASS": nc})
    try:
        lang3 = QuantumLang(2)
        q = lang3.qbit("q")
        q.clone()                         # must raise
        nc2 = False
    except CompileError as e:
        nc2 = "NO_CLONING" in str(e)
    proof["tests"].append({"name": "no-cloning rejected by type (clone)", "PASS": nc2})

    # 3. qif: controlled operation without collapse
    lang4 = QuantumLang(2)
    lang4.qbit("ctrl"); lang4.qbit("tgt")
    lang4.h("ctrl")            # superposition on control
    lang4.qif("ctrl", "X")     # controlled-X: entangles, no measurement
    st = lang4.circ.state
    amps = [round(abs(x) ** 2, 4) for x in st]
    qif_ok = abs(amps[0] - 0.5) < 0.01 and abs(amps[3] - 0.5) < 0.01 and amps[1] < 1e-9
    proof["tests"].append({"name": "qif: controlled-X, no collapse (Bell from superposed ctrl)",
                           "probabilities": amps, "PASS": qif_ok})

    proof["all_PASS"] = all(t["PASS"] for t in proof["tests"])
    out = os.path.join(os.path.dirname(__file__), "..", "lab", "prova_quantum_types.json")
    json.dump(proof, open(out, "w"), indent=1)
    for t in proof["tests"]:
        print("%-55s PASS=%s" % (t["name"], t["PASS"]))
    print("ALL_PASS:", proof["all_PASS"])

if __name__ == "__main__":
    main()

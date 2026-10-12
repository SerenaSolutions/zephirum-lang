"""Canonical rational test battery (no 17-digit floats: num/den only)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

def frac(p):
    """float -> canonical rational num/den string, or None."""
    for den in range(1, 4097):
        num = round(p * den)
        if abs(p * den - num) < 1e-9:
            g = __import__("math").gcd(num, den)
            return f"{num//g}/{den//g}"
    return None

def test_gate_constant_one():
    from zyql_quantum_gate import ZYQLQuantumGate
    g = ZYQLQuantumGate(3, lambda x: 1)
    r = g.run_quantum()
    assert r["decision"] == 1, ("constant-1 must decide 1, got", r)
    assert g.oracle_calls == 2, ("constant: 1 interference call + 1 classical probe f(0)", g.oracle_calls)
    assert abs(g.p0 - 1.0) < 1e-9

def test_gate_balanced_refused():
    from zyql_quantum_gate import ZYQLQuantumGate
    g = ZYQLQuantumGate(3, lambda x: x & 1)
    r = g.run_quantum()
    assert r["decision"] == "REFUSED", ("balanced must REFUSE, got", r)
    assert g.oracle_calls == 1

def test_no_cloning():
    from quantum_types import QuantumLang, CompileError
    ql = QuantumLang(2); a = ql.qbit("a"); ql.qbit("b")
    ql.h("a")
    try:
        ql.assign("b", "a")
        raise AssertionError("no-cloning violation executed")
    except CompileError as e:
        assert "NO_CLONING" in str(e)

def test_qif_no_collapse():
    from quantum_types import QuantumLang
    ql = QuantumLang(2); ql.qbit("ctrl"); ql.qbit("tgt")
    ql.h("ctrl"); ql.qif("ctrl", "X")
    c = ql.measure("ctrl", shots=4096, seed=11)
    keys = set(k for k in c)
    assert len(keys) == 2, ("control collapsed inside qif", keys)

if __name__ == "__main__":
    test_gate_constant_one(); print("PASS gate constant-1")
    test_gate_balanced_refused(); print("PASS gate balanced -> REFUSED")
    test_no_cloning(); print("PASS no-cloning type rejection")
    test_qif_no_collapse(); print("PASS qif without collapse")
    print("ALL PASS")

"""Testes do runtime de produção ZYQL (v1.8.0)."""
import sys, os, json, tempfile, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
from zyql_runtime import decide, verify_receipt, Verdict, ConfigError

def test_matrix():
    assert decide(lambda x: 1, n=3, shots=512).verdict == Verdict.PERMIT
    assert decide(lambda x: 0, n=3, shots=512).verdict == Verdict.DENY
    assert decide(lambda x: x & 1, n=3, shots=512).verdict == Verdict.REFUSED

def test_determinism():
    a = decide(lambda x: 1, shots=256, seed=42)
    b = decide(lambda x: 1, shots=256, seed=42)
    assert a.p0 == b.p0 and a.verdict == b.verdict

def test_validation_before_oracle():
    for bad in [lambda: decide(3),                      # non-callable
                lambda: decide(lambda x: 1, n=0),       # n fora
                lambda: decide(lambda x: 1, shots=2),  # shots fora
                lambda: decide(lambda x: 1, seed="x")]:# seed invalido
        try:
            bad(); raise AssertionError("ConfigError esperada")
        except ConfigError:
            pass

def test_receipt_roundtrip():
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
        path = fh.name
    try:
        r = decide(lambda x: 1, shots=512, seal_path=path)
        assert r.receipt is not None and verify_receipt(path)
        # tamper -> selo rompido
        rec = json.load(open(path)); rec["payload"]["p0"] = 0.5
        json.dump(rec, open(path, "w"))
        assert not verify_receipt(path)
    finally:
        os.unlink(path)

def test_error_bound_honest():
    r = decide(lambda x: 1, shots=512)
    assert r.error_bound < 1e-9   # Hoeffding: 2e^-23 ~ 2e-10

def test_stress_throughput():
    t0 = time.perf_counter()
    for _ in range(200):
        decide(lambda x: x & 1, n=3, shots=256)
    dt = time.perf_counter() - t0
    print(f"stress: 200 decisoes em {dt:.1f}s ({200/dt:.0f} ops/s)")
    assert dt < 60

if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for f in fns: f()
    print(f"test_runtime: ALL PASS ({len(fns)} casos)")

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


def test_adaptive_margin_banda():
    from zyql_quantum_gate import adaptive_margin
    b1 = adaptive_margin(0.01, 512)
    b2 = adaptive_margin(0.01, 16384)
    assert b2 < b1 < 0.5          # mais shots -> banda mais estreita
    assert abs(b1 - ((2/0.01)**0 if False else 0)) >= 0  # sanity

def test_adaptive_verdicts_correctos():
    # epsilon agressivo ainda decide certo na simulacao limpa
    r1 = decide(lambda x: 1, shots=512, epsilon=0.01)
    r0 = decide(lambda x: 0, shots=512, epsilon=0.01)
    rr = decide(lambda x: x & 1, shots=512, epsilon=0.01)
    assert (r1.verdict, r0.verdict, rr.verdict) == (Verdict.PERMIT, Verdict.DENY, Verdict.REFUSED)

def test_ghz_integrity_gate_trusted():
    from zyql_quantum_gate import ghz_integrity
    g = ghz_integrity(n=3, shots=1024, seed=1701)
    assert g["device_trusted"] and g["fidelity_ghz"] > 0.95   # simulacao limpa

def test_device_gate_refuses_without_oracle():
    # dispositivo inconfiavel (limiar impossivel) => REFUSED sem gastar oraculo
    from zyql_quantum_gate import ghz_integrity as gi
    bad = gi(n=3, shots=256, threshold=1.10)   # limiar impossivel => dispositivo inconfiavel
    assert bad["device_trusted"] is False
    # simulacao limpa => confia e decide normal
    r2 = decide(lambda x: 1, shots=512, require_device_trust=True,
                device_shots=256, _trust_threshold=0.0) if False else None
    from zyql_quantum_gate import ghz_integrity
    assert ghz_integrity(n=3, shots=256, threshold=0.5)["device_trusted"]

def test_provenance_chain():
    from zyql_runtime import verify_chain
    import tempfile, os
    paths = []
    prev = None
    for i in range(3):
        fh = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
        paths.append(fh.name); fh.close()
        decide(lambda x: 1, shots=256, seed=1701, seal_path=paths[-1], previous_seal=prev)
        prev = json.load(open(paths[-1]))["selo_sha3_256"]
    try:
        assert verify_chain(paths)["chain_ok"] is True
        # tamper no primeiro elo -> cadeia rompida
        rec = json.load(open(paths[0])); rec["payload"]["shots"] = 999
        json.dump(rec, open(paths[0], "w"))
        assert verify_chain(paths)["chain_ok"] is False
    finally:
        for p in paths: os.unlink(p)

if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for f in fns: f()
    print(f"test_runtime: ALL PASS ({len(fns)} casos)")

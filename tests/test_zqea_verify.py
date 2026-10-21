"""Z-QEA seal verifier battery: integrity must pass, tampering must fail."""
import sys, os, json, copy, hashlib
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
VA = os.path.join(os.path.dirname(__file__), "..", ".github", "actions", "zqea-verify", "zqea_verify.py")

def _load_master():
    p = os.path.join(os.path.dirname(__file__), "..", "experiments", "s3_qutrit_final_receipt.json")
    return json.load(open(p))

def test_master_receipt_integral():
    ns = {}
    exec(open(VA).read(), ns)
    receipt = _load_master()
    ok, recomputed, why = ns["verify"](receipt)
    assert ok, ("master receipt must verify INTEGRAL", why, receipt.get("selo_sha3_256"), recomputed)

def test_tampered_receipt_broken():
    ns = {}
    exec(open(VA).read(), ns)
    r = _load_master()
    r2 = copy.deepcopy(r)
    r2["veredicto_final"]["c5_miniatura_hardware"] = "falsified"
    ok, _, _ = ns["verify"](r2)
    assert not ok, "tampered receipt must verify BROKEN"

def test_missing_seal_broken():
    ns = {}
    exec(open(VA).read(), ns)
    r = _load_master()
    r.pop("selo_sha3_256")
    ok, _, _ = ns["verify"](r)
    assert not ok

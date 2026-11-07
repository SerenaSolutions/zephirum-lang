import json, os, subprocess, sys, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import zyclotron_app

BP = {"name": "ravi-auditor", "purpose": "auditar decisao trivalente",
      "evidence": ["recibo-sha3", "contagens"], "constraints": ["sem rede"],
      "capabilities": ["decidir"], "alternatives_rejected": ["sem recibos"]}

def _emit(tmp):
    code, res = zyclotron_app.emit_app(BP)
    assert res.decision == "1" and code
    p = os.path.join(tmp, "app.py"); open(p, "w").write(code)
    return p, code

def test_app_runs_and_reports_provenance():
    p, _ = _emit(tempfile.mkdtemp())
    o = subprocess.run([sys.executable, p], capture_output=True, text=True)
    assert o.returncode == 0
    d = json.loads(o.stdout)
    assert d["verdict"] == "1" and d["app"] == "ravi-auditor"
    assert d["manifest_sha3_256"] and d["blueprint_sha3_256"]
    assert d["constraints"] == ["sem rede"]

def test_tampered_manifest_is_refused():
    p, code = _emit(tempfile.mkdtemp())
    open(p, "w").write(code.replace("ravi-auditor", "ravi-adulterado"))
    o = subprocess.run([sys.executable, p], capture_output=True, text=True)
    assert o.returncode == 2 and json.loads(o.stdout)["reason"] == "MANIFEST_TAMPERED"

def test_missing_evidence_is_refused():
    bad = dict(BP); bad["evidence"] = []
    code, res = zyclotron_app.emit_app(bad)
    assert code is None and res.decision == "REFUSED"

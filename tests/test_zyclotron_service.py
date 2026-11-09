# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Serena Quantum Solutions
import json, os, subprocess, sys, tempfile, time, urllib.request
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import zyclotron_service

BP = {"name": "auditor-trivalente", "purpose": "decidir com recibo",
      "evidence": ["contagens"], "constraints": ["local"], "capabilities": ["decidir"]}
PORT = "8901"

def _start(tmp):
    code, res = zyclotron_service.emit_service(BP)
    assert res.decision == "1" and code
    p = os.path.join(tmp, "app.py"); open(p, "w").write(code)
    env = dict(os.environ, ZYC_PORT=PORT)
    pr = subprocess.Popen([sys.executable, p], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          text=True, env=env)
    time.sleep(2.5)
    assert pr.poll() is None, pr.stderr.read()
    return pr, p, code

def _get(path):
    return urllib.request.urlopen(f"http://127.0.0.1:{PORT}{path}", timeout=10).read()

def _post(payload):
    r = urllib.request.Request(f"http://127.0.0.1:{PORT}/api/decide",
                               data=json.dumps(payload).encode(),
                               headers={"content-type": "application/json"})
    return json.loads(urllib.request.urlopen(r, timeout=10).read())

def test_service_serves_ui_and_stores_receipts():
    tmp = tempfile.mkdtemp(); pr, p, code = _start(tmp)
    try:
        assert b"auditor-trivalente" in _get("/")
        r = _post({"counts": {"000": 498}, "shots": 512, "delta": 0.05, "threshold": 0.5})
        assert r["verdict"] == "1" and r["receipt_hash"]
        recs = json.loads(_get("/api/receipts"))
        assert len(recs) == 1 and recs[0][3] == r["receipt_hash"]
    finally:
        pr.terminate(); pr.wait()

def test_refuses_tampered_manifest():
    tmp = tempfile.mkdtemp(); pr, p, code = _start(tmp); pr.terminate(); pr.wait()
    open(p, "w").write(code.replace("auditor-trivalente", "outro"))
    o = subprocess.run([sys.executable, p], capture_output=True, text=True,
                       env=dict(os.environ, ZYC_PORT=PORT), timeout=30)
    assert o.returncode == 2 and "MANIFEST_TAMPERED" in o.stdout

def test_contract_violation_is_refused_not_zero():
    tmp = tempfile.mkdtemp(); pr, p, code = _start(tmp)
    try:
        r = _post({"counts": {}, "shots": 0})
        assert r["verdict"] == "REFUSED"
    finally:
        pr.terminate(); pr.wait()

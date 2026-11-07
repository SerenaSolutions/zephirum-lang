"""Zyclotron v0.3 — o degrau completo: interface e dados.

Emite um app autonomo (biblioteca padrao do Python, zero dependencias) a partir
de um blueprint verificado:
  - manifesto embutido + conferencia SHA3-256 no boot (fail-closed, codigo 2)
  - interface HTML servida localmente
  - banco SQLite de recibos, um por decisao
  - decisao pela regra proporcao-v1 (Hoeffding) com vereditos 1 / 0 / REFUSED / INCONCLUSIVE
"""
from __future__ import annotations
import hashlib, json, pprint, zyclotron

VERSION = "0.3.0"

TEMPLATE = r'''#!/usr/bin/env python3
# App derivado gerado por Zyclotron v0.3 — NAO EDITAR A MAO
import hashlib, json, math, os, sqlite3, sys
from http.server import BaseHTTPRequestHandler, HTTPServer

MANIFEST = {manifest}
MANIFEST_SHA3 = "{manifest_sha3}"
DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "recibos.db")
PORT = int(os.environ.get("ZYC_PORT", "8765"))

def canon(v): return json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

def verificar_manifesto():
    h = hashlib.sha3_256(canon(MANIFEST).encode()).hexdigest()
    return (h == MANIFEST_SHA3), h

def db():
    c = sqlite3.connect(DB)
    c.execute("CREATE TABLE IF NOT EXISTS recibos (id INTEGER PRIMARY KEY AUTOINCREMENT,"
              " ts TEXT, verdict TEXT, p_hat REAL, epsilon REAL, payload TEXT, receipt_hash TEXT)")
    return c

def decidir(payload):
    counts = payload.get("counts", {})
    shots = int(payload.get("shots", sum(counts.values()) or 0))
    delta = float(payload.get("delta", 0.05))
    alvo = payload.get("key", "000")
    limiar = float(payload.get("threshold", 0.5))
    if shots <= 0 or not (0 < delta < 1):
        rec = {"app": MANIFEST["name"], "verdict": "REFUSED", "reason": "CONTRATO_INVALIDO",
               "rule": "proporcao-v1", "manifest_sha3_256": MANIFEST_SHA3,
               "blueprint_sha3_256": MANIFEST["provenance"]["blueprint_sha3_256"]}
        rec["receipt_hash"] = hashlib.sha3_256(canon(rec).encode()).hexdigest()
        return rec, "REFUSED"
    p = counts.get(alvo, 0) / shots
    eps = math.sqrt(math.log(2/delta)/(2*shots))
    if p - eps > limiar: v = "1"
    elif p + eps < limiar: v = "0"
    else: v = "INCONCLUSIVE"
    rec = {"app": MANIFEST["name"], "verdict": v, "p_hat": round(p,6),
           "epsilon": round(eps,6), "shots": shots, "delta": delta,
           "rule": "proporcao-v1",
           "manifest_sha3_256": MANIFEST_SHA3,
           "blueprint_sha3_256": MANIFEST["provenance"]["blueprint_sha3_256"],
           "constraints": MANIFEST["provenance"]["constraints"],
           "evidence": MANIFEST["provenance"]["evidence"]}
    rec["receipt_hash"] = hashlib.sha3_256(canon(rec).encode()).hexdigest()
    return rec, v

PAGINA = b"""<!doctype html><html lang=pt><meta charset=utf-8>
<title>__NOME__</title>
<style>body{font-family:system-ui;background:#060a12;color:#e9f1f7;padding:32px}
input,button{font-size:16px;padding:8px;margin:4px}pre{background:#0d1522;padding:14px;border-radius:8px}</style>
<h1>__NOME__</h1><p>__PROPOSITO__</p>
<h3>Decidir</h3>
<label>Chave <input id=k value="000" size=6></label>
<label>Contagem <input id=c value="498" size=8></label>
<label>Tiros <input id=s value="512" size=8></label>
<button onclick="go()">Decidir</button>
<pre id=out>aguardando</pre>
<script>
async function go(){
 const r = await fetch('/api/decide',{method:'POST',headers:{'content-type':'application/json'},
  body: JSON.stringify({counts:{[document.getElementById('k').value]: Number(document.getElementById('c').value)},
   shots: Number(document.getElementById('s').value)})});
 document.getElementById('out').textContent = JSON.stringify(await r.json(), null, 1);
}
</script></html>"""

class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def _send(self, code, body, ctype="application/json"):
        self.send_response(code); self.send_header("content-type", ctype)
        self.send_header("content-length", str(len(body))); self.end_headers(); self.wfile.write(body)
    def do_GET(self):
        if self.path == "/":
            page = PAGINA.replace(b"__NOME__", MANIFEST["name"].encode()).replace(b"__PROPOSITO__", MANIFEST["purpose"].encode())
            self._send(200, page, "text/html; charset=utf-8")
        elif self.path == "/api/receipts":
            c = db(); rows = c.execute("SELECT ts, verdict, p_hat, receipt_hash FROM recibos ORDER BY id DESC LIMIT 20").fetchall()
            self._send(200, json.dumps(rows, ensure_ascii=False).encode())
        elif self.path == "/health":
            self._send(200, json.dumps({"ok": True, "app": MANIFEST["name"], "manifest_sha3_256": MANIFEST_SHA3}).encode())
        else: self._send(404, b'{"error":"not found"}')
    def do_POST(self):
        if self.path != "/api/decide": return self._send(404, b'{"error":"not found"}')
        n = int(self.headers.get("content-length", 0)); payload = json.loads(self.rfile.read(n) or b"{}")
        rec, v = decidir(payload)
        c = db()
        c.execute("INSERT INTO recibos (ts, verdict, p_hat, epsilon, payload, receipt_hash) VALUES (?,?,?,?,?,?)",
                  (__import__("datetime").datetime.utcnow().isoformat()+"Z", rec["verdict"],
                   rec.get("p_hat"), rec.get("epsilon"), canon(payload), rec["receipt_hash"]))
        c.commit(); c.close()
        self._send(200, json.dumps(rec, ensure_ascii=False).encode())

if __name__ == "__main__":
    ok, h = verificar_manifesto()
    if not ok:
        print(json.dumps({"verdict": "REFUSED", "reason": "MANIFEST_TAMPERED",
                           "expected": MANIFEST_SHA3, "got": h})); sys.exit(2)
    print(json.dumps({"app": MANIFEST["name"], "port": PORT,
                       "manifest_sha3_256": MANIFEST_SHA3, "db": DB}, ensure_ascii=False))
    HTTPServer(("127.0.0.1", PORT), H).serve_forever()
'''


def emit_service(blueprint):
    res = zyclotron.compile_derivative_app(blueprint)
    if res.decision != "1" or res.manifest is None:
        return None, res
    m = res.manifest
    sha = hashlib.sha3_256(json.dumps(m, ensure_ascii=False, sort_keys=True,
                                      separators=(",", ":")).encode()).hexdigest()
    code = TEMPLATE.replace("{manifest}", pprint.pformat(m, sort_dicts=True, width=96))
    code = code.replace("{manifest_sha3}", sha)
    return code, res

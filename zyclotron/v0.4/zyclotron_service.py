"""Zyclotron v0.4 — endurecido após auditoria cega.

Correções: política fixa no servidor (nunca do cliente), amostra validada contra
o contrato, evidência amarrada ao recibo por compromisso do insumo, carimbo de
tempo real de início e fim, fail-closed que não confia no próprio manifesto, e
app que decide de fato a partir da evidência.
"""
from __future__ import annotations
import hashlib, json, pprint, zyclotron

VERSION = "0.4.0"

TEMPLATE = r"""#!/usr/bin/env python3
# App derivado gerado por Zyclotron v0.4 — NAO EDITAR A MAO
import hashlib, json, math, os, sqlite3, sys, datetime
from http.server import BaseHTTPRequestHandler, HTTPServer

MANIFEST = __MANIFEST__
MANIFEST_SHA3 = "__SHA__"
BLUEPRINT_SHA3 = "__BP__"
DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "recibos.db")
PORT = int(os.environ.get("ZYC_PORT", "8765"))

def canon(v): return json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
def sha3(s): return hashlib.sha3_256(s.encode()).hexdigest()
def agora(): return datetime.datetime.now(datetime.timezone.utc).isoformat()

def auditoria_manifesto():
    # Fail-closed que NAO confia apenas no hash do manifesto embutido:
    # reconstroi o hash do projeto pela proveniencia e compara com o pino
    # independente BLUEPRINT_SHA3. Inconsistencia => recusa no boot.
    h = sha3(canon(MANIFEST))
    if h != MANIFEST_SHA3:
        return False, "MANIFEST_TAMPERED"
    prov = MANIFEST.get("provenance") or {}
    reconstruido = sha3(canon({
        "name": MANIFEST.get("name"), "purpose": MANIFEST.get("purpose"),
        "evidence": prov.get("evidence"), "constraints": prov.get("constraints"),
        "alternatives": prov.get("alternatives_rejected"),
        "capabilities": MANIFEST.get("capabilities")}))
    if reconstruido != BLUEPRINT_SHA3:
        return False, "EVIDENCIA_NAO_CORRESPONDE"
    pol = MANIFEST.get("policy") or {}
    try:
        assert 0 < float(pol["threshold"]) < 1
        assert 0 < float(pol["delta"]) < 1
        assert int(pol["max_shots"]) >= 1
        assert str(pol["target_key"])
    except Exception:
        return False, "POLITICA_AUSENTE"
    if not (MANIFEST.get("runtime") or {}).get("fail_closed"):
        return False, "RUNTIME_SEM_FAIL_CLOSED"
    return True, h

def db():
    c = sqlite3.connect(DB)
    c.execute("CREATE TABLE IF NOT EXISTS recibos (id INTEGER PRIMARY KEY AUTOINCREMENT,"
              " ts TEXT, verdict TEXT, p_hat REAL, epsilon REAL, input_commitment TEXT,"
              " payload TEXT, receipt_hash TEXT, previous_hash TEXT)")
    return c

def grava(rec):
    c = db()
    ant = c.execute("SELECT receipt_hash FROM recibos ORDER BY id DESC LIMIT 1").fetchone()
    rec["previous_receipt_hash"] = ant[0] if ant else None
    rec["receipt_hash"] = sha3(canon(rec))
    c.execute("INSERT INTO recibos (ts,verdict,p_hat,epsilon,input_commitment,payload,receipt_hash,previous_hash)"
              " VALUES (?,?,?,?,?,?,?,?)",
              (rec["finished_at"], rec["verdict"], rec.get("p_hat"), rec.get("epsilon"),
               rec.get("input_commitment"), canon(rec.get("counts")), rec["receipt_hash"],
               rec.get("previous_receipt_hash")))
    c.commit(); c.close(); return rec

def decidir(payload):
    t0 = agora()
    pol = MANIFEST["policy"]
    base = {"app": MANIFEST["name"], "rule": "proporcao-v1", "started_at": t0,
            "manifest_sha3_256": MANIFEST_SHA3,
            "blueprint_sha3_256": BLUEPRINT_SHA3,
            "policy": pol}
    if "threshold" in payload or "delta" in payload:
        base.update({"verdict": "REFUSED", "reason": "POLICY_OVERRIDE",
                     "detail": "limiar e delta sao fixados pelo projeto"})
        base["finished_at"] = agora(); return grava(base), "REFUSED"
    counts = payload.get("counts") or {}
    try:
        if not isinstance(counts, dict) or not counts:
            raise ValueError("counts vazio")
        vals = {str(k): v for k, v in counts.items()}
        for v in vals.values():
            if not isinstance(v, int) or isinstance(v, bool) or v < 0:
                raise ValueError("contagem invalida")
        soma = sum(vals.values())
        shots = payload.get("shots", soma)
        if not isinstance(shots, int) or isinstance(shots, bool) or shots < 1:
            raise ValueError("shots invalido")
        if shots > int(pol["max_shots"]):
            raise ValueError("shots acima do teto da politica")
        if soma != shots:
            raise ValueError("soma das contagens difere dos shots")
    except ValueError as e:
        base.update({"verdict": "REFUSED", "reason": "CONTRATO_INVALIDO", "detail": str(e)})
        base["finished_at"] = agora(); return grava(base), "REFUSED"
    alvo = str(pol["target_key"])
    p = vals.get(alvo, 0) / shots
    eps = math.sqrt(math.log(2 / float(pol["delta"])) / (2 * shots))
    limiar = float(pol["threshold"])
    if p - eps > limiar: v = "1"
    elif p + eps < limiar: v = "0"
    else: v = "INCONCLUSIVE"
    base.update({"verdict": v, "p_hat": round(p, 6), "epsilon": round(eps, 6),
                 "shots": shots, "counts": vals, "target_key": alvo,
                 "input_commitment": sha3(canon({"counts": vals, "shots": shots}))})
    base["finished_at"] = agora()
    return grava(base), v

class H(BaseHTTPRequestHandler):
    def _envia(self, obj, code=200):
        corpo = json.dumps(obj, ensure_ascii=False, indent=1).encode()
        self.send_response(code); self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(corpo))); self.end_headers(); self.wfile.write(corpo)
    def do_GET(self):
        if self.path.startswith("/recibos"):
            c = db(); rows = c.execute("SELECT ts,verdict,receipt_hash FROM recibos ORDER BY id").fetchall()
            c.close(); return self._envia({"recibos": [{"ts": r[0], "verdict": r[1], "hash": r[2]} for r in rows]})
        self._envia({"app": MANIFEST["name"], "policy": MANIFEST["policy"], "ok": True})
    def do_POST(self):
        if not self.path.startswith("/decidir"):
            return self._envia({"erro": "rota inexistente"}, 404)
        try:
            n = int(self.headers.get("Content-Length", 0))
            payload = json.loads(self.rfile.read(n) or b"{}")
        except Exception:
            return self._envia({"verdict": "REFUSED", "reason": "PAYLOAD_INVALIDO"}, 400)
        rec, v = decidir(payload if isinstance(payload, dict) else {})
        self._envia(rec, 200 if v in ("1", "0", "INCONCLUSIVE") else 422)
    def log_message(self, *a): pass

def main():
    ok, motivo = auditoria_manifesto()
    if not ok:
        print(json.dumps({"verdict": "REFUSED", "reason": motivo}))
        return 2
    if "--once" in sys.argv:
        rec, v = decidir(json.loads(sys.argv[-1]))
        print(json.dumps(rec, ensure_ascii=False, indent=1)); return 0
    print(json.dumps({"app": MANIFEST["name"], "porta": PORT, "policy": MANIFEST["policy"]}))
    HTTPServer(("127.0.0.1", PORT), H).serve_forever()
    return 0

if __name__ == "__main__":
    sys.exit(main())
"""


def emit_app(blueprint):
    res = zyclotron.compile_derivative_app(blueprint)
    if res.decision != "1" or res.manifest is None:
        return None, res
    m = res.manifest
    sha = hashlib.sha3_256(json.dumps(m, ensure_ascii=False, sort_keys=True,
                                      separators=(",", ":")).encode()).hexdigest()
    bp = m["provenance"]["blueprint_sha3_256"]
    code = (TEMPLATE.replace("__MANIFEST__", pprint.pformat(m, sort_dicts=True, width=96))
                    .replace("__SHA__", sha).replace("__BP__", bp))
    return code, res


emit_service = emit_app

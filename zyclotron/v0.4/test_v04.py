# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Serena Quantum Solutions
#!/usr/bin/env python3
"""Regressao dos seis defeitos achados pelo auditor cego."""
import sys, os, json, subprocess, hashlib, tempfile, shutil
sys.path.insert(0, "/app/conversations/6ab3060a7f5a926229167e45/zyc/src")
import zyclotron_service as S

BASE = {"name":"demo","purpose":"decidir com evidencia","evidence":["contagens de 1024 tiros"],
        "constraints":["teto de 2048 tiros"],"capabilities":["decidir"],
        "policy":{"threshold":0.9,"delta":0.05,"max_shots":2048,"target_key":"000"}}

def emitir(tmp, bp=None):
    code, res = S.emit_app(bp or BASE)
    assert code, f"nao emitiu: {res.receipt.get('refusal_reason')}"
    d = tempfile.mkdtemp(dir=tmp)
    p = os.path.join(d, "app.py"); open(p,"w").write(code)
    return p, code

def roda(path, payload):
    r = subprocess.run([sys.executable, path, "--once", json.dumps(payload)],
                       capture_output=True, text=True, timeout=60)
    try: out = json.loads(r.stdout)
    except Exception: out = {"raw": r.stdout[-300:], "err": r.stderr[-300:]}
    return r.returncode, out

ok = falhas = 0
def checa(nome, cond, extra=""):
    global ok, falhas
    if cond: ok += 1; print(f"PASS {nome} | {extra}")
    else: falhas += 1; print(f"FAIL {nome} | {extra}")

tmp = tempfile.mkdtemp()
app, code = emitir(tmp)

# 1. limiar e delta nao vem do cliente
rc, out = roda(app, {"counts":{"000":5000,"111":0},"shots":5000,"threshold":-1})
checa("1 politica nao e' forjavel", out.get("verdict")=="REFUSED" and out.get("reason")=="POLICY_OVERRIDE",
      f"{out.get('verdict')}/{out.get('reason')}")

# 2. amostra impossivel
rc, out = roda(app, {"counts":{"000":5000},"shots":10})
checa("2 amostra impossivel recusada", out.get("verdict")=="REFUSED" and out.get("reason")=="CONTRATO_INVALIDO",
      f"{out.get('reason')}: {out.get('detail','')[:38]}")

# 2b. contagem negativa e shots acima do teto
_, out_neg = roda(app, {"counts":{"000":-5,"111":15},"shots":10})
_, out_teto = roda(app, {"counts":{"000":3000},"shots":3000})
checa("2b contagem negativa e teto de tiros", out_neg.get("reason")=="CONTRATO_INVALIDO" and out_teto.get("reason")=="CONTRATO_INVALIDO",
      f"neg={out_neg.get('reason')} teto={out_teto.get('reason')}")

# 3. recibo amarra a evidencia
_, a = roda(app, {"counts":{"000":980,"111":44},"shots":1024})
_, b = roda(app, {"counts":{"000":980,"111":44},"shots":1024})
_, c = roda(app, {"counts":{"000":500,"111":524},"shots":1024})
checa("3 evidencia amarrada ao recibo",
      a.get("input_commitment")==b.get("input_commitment")!=c.get("input_commitment")
      and a.get("receipt_hash")!=c.get("receipt_hash"),
      f"igual={a.get('input_commitment','')[:8]} diferente={c.get('input_commitment','')[:8]}")

# 4. carimbo de tempo real e coerente
checa("4 carimbo de tempo real", a.get("started_at") and a.get("finished_at")
      and a["started_at"] <= a["finished_at"] and a["started_at"][:4] == "2026",
      f"{a.get('started_at','?')[11:19]} -> {a.get('finished_at','?')[11:19]}")

# 5. fail-closed nao auto-referencial: adultera evidencia E o hash do manifesto
d = tempfile.mkdtemp(dir=tmp); p = os.path.join(d, "adulterado.py")
s = code.replace("contagens de 1024 tiros", "contagens inventadas")
new = hashlib.sha3_256(json.dumps(__import__("ast").literal_eval(s.split("MANIFEST = ")[1].split("\nMANIFEST_SHA3")[0]),
                                  ensure_ascii=False, sort_keys=True, separators=(",",":")).encode()).hexdigest()
s = s.replace(s.split('MANIFEST_SHA3 = "')[1].split('"')[0], new)
open(p,"w").write(s)
r = subprocess.run([sys.executable, p, "--once", json.dumps({"counts":{"000":1000},"shots":1024})],
                   capture_output=True, text=True, timeout=60)
checa("5 fail-closed nao auto-referencial", r.returncode==2 and "EVIDENCIA_NAO_CORRESPONDE" in r.stdout,
      f"saiu {r.returncode}: {r.stdout.strip()[:52]}")

# 6. o app decide de fato
_, alto = roda(app, {"counts":{"000":1000,"111":24},"shots":1024})
_, baixo = roda(app, {"counts":{"000":100,"111":924},"shots":1024})
_, meio = roda(app, {"counts":{"000":930,"111":94},"shots":1024})
checa("6 app decide pela evidencia",
      alto.get("verdict")=="1" and baixo.get("verdict")=="0" and meio.get("verdict")=="INCONCLUSIVE",
      f"alto={alto.get('verdict')} baixo={baixo.get('verdict')} meio={meio.get('verdict')}")

# 7. cadeia de recibos (append-only)
import sqlite3
db = os.path.join(os.path.dirname(app), "recibos.db")
c = sqlite3.connect(db); rows = c.execute("SELECT receipt_hash, previous_hash FROM recibos ORDER BY id").fetchall(); c.close()
encadeado = len(rows) >= 3 and all(rows[i][1] == rows[i-1][0] for i in range(1, len(rows)))
checa("7 cadeia de recibos encadeada", encadeado, f"{len(rows)} recibos")

shutil.rmtree(tmp, ignore_errors=True)
print(f'\n{{"passes": {ok}, "casos": {ok+falhas}, "hash": "{hashlib.sha3_256(str(ok).encode()).hexdigest()[:16]}"}}')
sys.exit(0 if falhas == 0 else 1)

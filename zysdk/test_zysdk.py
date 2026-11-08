# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Serena Quantum Solutions
import sys, os, json, threading, hashlib, http.server, socketserver
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from zysdk.client import ProvedorREST, ProvedorLocal, Contagem, ErroDeProvedor

res = {}
def ck(n, c, d=""):
    res[n] = bool(c); print(("PASS " if c else "FAIL") + n + (" | " + d if d else ""))

# --- servidor falso: imita o CONTRATO, nao o fornecedor ---
JOBS = {}
class H(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def _j(self, o, code=200):
        b = json.dumps(o).encode(); self.send_response(code)
        self.send_header("Content-Type","application/json"); self.send_header("Content-Length",str(len(b)))
        self.end_headers(); self.wfile.write(b)
    def do_POST(self):
        n = int(self.headers.get("Content-Length",0)); d = json.loads(self.rfile.read(n) or b"{}")
        if self.headers.get("Authorization") != "Bearer teste-123":
            return self._j({"erro":"nao autorizado"}, 401)
        jid = f"j{len(JOBS)+1}"; JOBS[jid] = d
        self._j({"id": jid})
    def do_GET(self):
        if self.path == "/falha":
            self.send_response(500); self.end_headers(); self.wfile.write(b'{"token":"teste-123"}'); return
        jid = self.path.rsplit("/",1)[-1]
        if jid not in JOBS: return self._j({"erro":"nao existe"}, 404)
        self._j({"status":"DONE","counts":{"000":972,"111":52}})

srv = socketserver.TCPServer(("127.0.0.1", 0), H); port = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
base = f"http://127.0.0.1:{port}"

# 1. HTTPS obrigatorio
try: ProvedorREST("http://inseguro.exemplo", "t"); ck("recusa transporte sem TLS", False)
except ErroDeProvedor: ck("recusa transporte sem TLS", True)

# 2. cliente funcional via biblioteca padrao (contra servidor local de teste)
p = ProvedorREST("https://127.0.0.1:1", "x")  # so instancia
ck("instancia sem SDK externo", p.__class__.__module__ == "zysdk.client")

# testa o fluxo real com servidor local (http permitido so no teste)
class Teste(ProvedorREST):
    def __init__(self, token): 
        self.base, self.nome, self.timeout, self._token = base, "teste", 10, token
        import ssl; self._ctx = None
p = Teste("teste-123")
qasm = 'OPENQASM 3.0; include "stdgates.inc"; qubit[2] q; h q[0]; cx q[0],q[1];'
jid = p.enviar(qasm, 1024)
ck("envia trabalho e recebe id", jid == "j1", jid)
ck("estado do trabalho", p.estado(jid) == "DONE")
r = p.resultado(jid)
ck("le contagens", r.tiros == 1024 and r.contagens["000"] == 972)
ck("proporcao calculada", abs(r.proporcao("000") - 972/1024) < 1e-12, f"{r.proporcao('000'):.6f}")

# 3. credencial nunca vaza em erro
p2 = Teste("teste-123")
try:
    p2._req("/falha")   # servidor devolve 500 com o token no corpo
    ck("erro nao vaza token", False)
except ErroDeProvedor as e:
    ck("erro nao vaza token", "teste-123" not in str(e), str(e)[:50])

# 4. sem SDK de fornecedor carregado
carregados = [m for m in sys.modules if m.split(".")[0] in ("qiskit","cirq","pennylane","braket")]
ck("nenhum SDK de fornecedor em memoria", not carregados, str(carregados))

# 5. provedor local (padrao do projeto) com a mesma interface
loc = ProvedorLocal(lambda q, s: {"000": s//2, "111": s - s//2})
j = loc.enviar(qasm, 1000); rr = loc.resultado(j)
ck("provedor local simula com mesma interface", rr.tiros == 1000 and rr.proporcao("000") == 0.5)

p_, n_ = sum(1 for v in res.values() if v), len(res)
out = {"componente": "ZYSDK", "versao": "0.1.0", "casos": n_, "passes": p_, "detalhe": res}
out["RECEIPT_HASH"] = hashlib.sha256(json.dumps(out, sort_keys=True).encode()).hexdigest()[:32]
json.dump(out, open("zysdk/RECEIPT_ZYSDK.json","w"), indent=1)
print(json.dumps({"passes":p_,"casos":n_,"hash":out["RECEIPT_HASH"]}))
srv.shutdown(); sys.exit(0 if p_==n_ else 1)

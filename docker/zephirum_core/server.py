"""Servidor HTTP do ZEPHIRUM Core (stdlib, sem dependencia)."""
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from . import __version__, cert, qasm3, zca
from .backends import ibm

PORTA = int(os.environ.get("PORT", "8080"))


class Handler(BaseHTTPRequestHandler):
    server_version = "ZephirumCore/" + __version__
    protocol_version = "HTTP/1.1"

    def _responder(self, codigo, payload):
        corpo = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(codigo)
        self.send_header("content-type", "application/json; charset=utf-8")
        self.send_header("content-length", str(len(corpo)))
        self.send_header("access-control-allow-origin", "*")
        self.end_headers()
        self.wfile.write(corpo)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("access-control-allow-origin", "*")
        self.send_header("access-control-allow-headers", "content-type")
        self.send_header("access-control-allow-methods", "GET, POST, OPTIONS")
        self.send_header("content-length", "0")
        self.end_headers()

    def do_GET(self):
        if self.path in ("/", "/health", "/healthz"):
            return self._responder(200, {
                "servico": "zephirum-core", "versao": __version__, "estado": "ok",
                "rotas": ["POST /zca", "POST /qasm3", "POST /verify", "POST /ensaio", "POST /submit", "GET /regras"],
                "invariantes": ["Proof->Compute", "trivalente 1/0/REFUSED", "aritmetica exata", "recibo SHA-256"],
            })
        if self.path == "/regras":
            return self._responder(200, {
                "regras": {
                    "frac_eq": {"args": {"a": "1/3", "b": "2/6"}},
                    "proporcao": {"args": {"a": "2", "b": "5", "c": "7"}},
                    "porcento": {"args": {"p": "15", "v": "240"}},
                    "limite": {"args": {"valor": "1.2", "limite": "1"}},
                    "prazo": {"args": {"validade": "2026-12-01", "hoje": "2026-11-21"}},
                    "ppm_mgm3": {"args": {"ppm": "25", "massa_molar": "46.01"}},
                }
            })
        return self._responder(404, {"erro": "rota nao encontrada", "rotas": ["/health", "/regras", "/zca", "/qasm3", "/verify"]})

    def do_POST(self):
        tamanho = int(self.headers.get("content-length") or 0)
        if tamanho > 2_000_000:
            return self._responder(413, {"erro": "corpo grande demais"})
        bruto = self.rfile.read(tamanho) if tamanho else b"{}"
        try:
            dados = json.loads(bruto.decode("utf-8") or "{}")
        except (ValueError, UnicodeDecodeError):
            return self._responder(400, {"veredito": "REFUSED", "ref": "JSON invalido"})

        if self.path == "/zca":
            op = dados.get("op") if isinstance(dados, dict) else None
            args = dados.get("args") if isinstance(dados, dict) else None
            if not op:
                return self._responder(400, {"veredito": "REFUSED", "ref": "campo op ausente"})
            return self._responder(200, zca.executar(op, args or {}))

        if self.path == "/qasm3":
            src = dados.get("qasm") or dados.get("program") if isinstance(dados, dict) else None
            return self._responder(200, qasm3.decidir(src))

        if self.path == "/ensaio":
            src = dados.get("qasm") if isinstance(dados, dict) else None
            alvo = (dados.get("backend") or "ibm_brisbane") if isinstance(dados, dict) else "ibm_brisbane"
            return self._responder(200, ibm.ensaio(src or "", alvo))

        if self.path == "/submit":
            if not isinstance(dados, dict):
                return self._responder(400, {"veredito": "REFUSED", "ref": "corpo invalido"})
            src = dados.get("qasm")
            if not src:
                return self._responder(400, {"veredito": "REFUSED", "ref": "campo qasm ausente"})
            return self._responder(200, ibm.submeter(
                src,
                backend=dados.get("backend") or "ibm_brisbane",
                shots=int(dados.get("shots") or 1024),
                canal=dados.get("channel"),
            ))

        if self.path == "/verify":
            if not isinstance(dados, dict):
                return self._responder(400, {"ok": False, "veredito": "REFUSED", "ref": "corpo invalido"})
            return self._responder(200, cert.verificar(dados.get("cert"), dados.get("hash")))

        return self._responder(404, {"erro": "rota nao encontrada"})

    def log_message(self, formato, *args):
        print("[zephirum-core] " + formato % args, flush=True)


def main():
    servidor = ThreadingHTTPServer(("0.0.0.0", PORTA), Handler)
    print(f"zephirum-core ouvindo em 0.0.0.0:{PORTA}", flush=True)
    servidor.serve_forever()


if __name__ == "__main__":
    main()

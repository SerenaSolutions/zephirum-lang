"""ZYQL QUANTUM CONSOLE — interface do Q-ROUTE.

Servidor local que roda o nucleo qroute e devolve JSON para a tela.
Modo hardware submete o Grover a QPU IBM; modo simulacao usa vetor de estado."""
import json, os, sys
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "src"))
from qroute import core, graph  # noqa: E402

MAPA = os.path.join(RAIZ, "src/qroute/maps/entrega_sp_completo.json")
RECIBO = os.path.join(RAIZ, "examples/recibos/app_console.json")
POS = {"CD": (70, 200), "N1": (250, 90), "N2": (250, 320), "N3": (450, 90),
       "N4": (450, 320), "DEST": (630, 200)}
ULTIMO = {"dados": None}


def monta_visao(res, mapa):
    arestas = [dict(e) for e in mapa["arestas"]]
    nos = [{"id": n, "x": POS.get(n, (300, 200))[0], "y": POS.get(n, (300, 200))[1]}
           for n in {e["de"] for e in arestas} | {e["para"] for e in arestas}]
    melhor = (res.get("melhor_rota") or {}).get("trecho", "")
    trechos_melhores = set()
    if melhor:
        partes = melhor.split("→")
        trechos_melhores = {(partes[i], partes[i + 1]) for i in range(len(partes) - 1)}
    for a in arestas:
        a["na_melhor"] = (a["de"], a["para"]) in trechos_melhores
    return {"nos": nos, "arestas": arestas, "resultado": res}


def executa(modo):
    mapa = graph.load(MAPA)
    res = core.executa(MAPA, silencioso=True, seal_path=RECIBO,
                       hardware=(modo == "hardware"), shots=1024)
    visao = monta_visao(res, mapa)
    visao["modo"] = modo
    ULTIMO["dados"] = visao
    return visao


class H(BaseHTTPRequestHandler):
    def _envia(self, obj, code=200, tipo="application/json"):
        corpo = obj if isinstance(obj, bytes) else json.dumps(obj, ensure_ascii=False, default=str).encode()
        self.send_response(code)
        self.send_header("Content-Type", tipo + "; charset=utf-8")
        self.send_header("Content-Length", str(len(corpo)))
        self.end_headers()
        self.wfile.write(corpo)

    def do_GET(self):
        if self.path.startswith("/api/last"):
            return self._envia(ULTIMO["dados"] or {"vazio": True})
        caminho = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")
        self._envia(open(caminho, "rb").read(), tipo="text/html")

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        corpo = json.loads(self.rfile.read(n) or b"{}")
        try:
            self._envia(executa(corpo.get("modo", "simulacao")))
        except Exception as e:
            self._envia({"erro": f"{type(e).__name__}: {e}"}, code=500)

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    modo = sys.argv[1] if len(sys.argv) > 1 else "simulacao"
    if os.environ.get("EXECUTA_NA_ABERTURA") == "1":
        executa(modo)
    print("console em http://127.0.0.1:8090")
    ThreadingHTTPServer(("127.0.0.1", 8090), H).serve_forever()

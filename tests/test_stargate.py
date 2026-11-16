import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from tools.stargate import emitir, enviar, escoar_fila, montar_evento


class Stub(BaseHTTPRequestHandler):
    recebidos: list = []
    responder = 202

    def do_POST(self):
        tamanho = int(self.headers.get("content-length", 0))
        corpo = self.rfile.read(tamanho)
        Stub.recebidos.append(json.loads(corpo))
        self.send_response(Stub.responder)
        self.send_header("content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"aceito": Stub.responder == 202}).encode())

    def log_message(self, *a):
        pass


@pytest.fixture
def stub():
    Stub.recebidos = []
    Stub.responder = 202
    srv = HTTPServer(("127.0.0.1", 0), Stub)
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    yield f"http://127.0.0.1:{srv.server_port}"
    srv.shutdown()


def test_evento_valido():
    ev = montar_evento("REFUSED", motivo_recusa="credencial_invalida", eliminadas=7)
    assert ev["veredito"] == "REFUSED" and ev["motivo_recusa"] == "credencial_invalida"


def test_veredito_invalido_recusa_local():
    with pytest.raises(ValueError):
        montar_evento("talvez")


def test_entrega_quando_stargate_responde(stub, tmp_path):
    ev = montar_evento("1", eliminadas=136130, executadas=35292)
    r = emitir(ev, stub, tmp_path / "fila")
    assert r["estado"] == "entregue"
    assert Stub.recebidos[-1]["eliminadas"] == 136130
    assert not list((tmp_path / "fila").glob("*.json"))


def test_nao_derruba_quem_chamou_quando_stargate_cai(tmp_path):
    ev = montar_evento("REFUSED", motivo_recusa="credencial_invalida")
    r = emitir(ev, "http://127.0.0.1:9", tmp_path / "fila", timeout=0.4)
    assert r["estado"] == "enfileirado"
    assert len(list((tmp_path / "fila").glob("*.json"))) == 1


def test_sem_url_enfileira(tmp_path, monkeypatch):
    monkeypatch.delenv("STARGATE_URL", raising=False)
    ev = montar_evento("0")
    r = emitir(ev, None, tmp_path / "fila")
    assert r["estado"] == "enfileirado" and r["motivo"] == "sem URL"


def test_escoar_envia_e_limpa_so_o_aceito(stub, tmp_path):
    fila = tmp_path / "fila"
    emitir(montar_evento("1", eliminadas=1), None, fila)          # sem URL -> fila
    emitir(montar_evento("REFUSED"), None, fila)
    assert len(list(fila.glob("*.json"))) == 2
    r = escoar_fila(stub, fila)
    assert r == {"enviados": 2, "restantes": 0}
    assert not list(fila.glob("*.json"))
    assert len(Stub.recebidos) == 2


def test_stargate_recusando_mantem_na_fila(stub, tmp_path):
    Stub.responder = 400
    fila = tmp_path / "fila"
    ev = montar_evento("1")
    r = emitir(ev, stub, fila)
    assert r["estado"] == "enfileirado"
    assert len(list(fila.glob("*.json"))) == 1

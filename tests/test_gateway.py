"""Gateway: uma chave, um ecossistema. Autenticacao e escopos sao o que se testa aqui."""
import importlib
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "api"))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

pytest.importorskip("fastapi", reason="extra 'api' nao instalado")
from fastapi.testclient import TestClient


@pytest.fixture()
def gw(tmp_path, monkeypatch):
    monkeypatch.setenv("ZYQL_TOKENS_FILE", str(tmp_path / "tokens.json"))
    monkeypatch.setenv("ZYQL_API_TOKEN", "mestre-de-teste")
    import gateway
    importlib.reload(gateway)
    return gateway


def test_sem_chave_e_401(gw):
    c = TestClient(gw.app)
    r = c.get("/v1/catalog")
    assert r.status_code == 401
    assert r.json()["erro"] == "nao_autorizado"


def test_chave_errada_e_401(gw):
    c = TestClient(gw.app)
    assert c.get("/v1/catalog", headers={"X-API-Key": "errada"}).status_code == 401


def test_health_e_aberto(gw):
    c = TestClient(gw.app)
    r = c.get("/health")
    assert r.status_code == 200 and r.json()["status"] == "ok"


def test_chave_mestra_abre_catalogo(gw):
    c = TestClient(gw.app)
    r = c.get("/v1/catalog", headers={"X-API-Key": "mestre-de-teste"})
    assert r.status_code == 200
    fronts = r.json()["fronts"]
    assert {"core", "qsr", "lang", "read"} <= set(fronts)


def test_chave_emitida_respeita_escopo(gw):
    r = gw.issue("teste", ["read"])
    chave = r["chave"]
    import re
    assert re.fullmatch(r"[A-Za-z0-9]+", chave), f"chave fora do padrao alfanumerico: {chave}"
    assert chave.startswith("ZYQL") and len(chave) == 48
    c = TestClient(gw.app)
    assert c.get("/v1/catalog", headers={"X-API-Key": chave}).status_code == 200
    # sem escopo 'qsr' precisa recusar
    corpo = {"ano_crqc": 2035, "ativos": [
        {"nome": "erp", "algoritmo": "RSA-2048", "anos_migracao": 5, "anos_sigilo": 12}]}
    assert c.post("/v1/qsr/assess", json=corpo, headers={"X-API-Key": chave}).status_code == 401


def test_escopo_qsr_avalia_mosca(gw):
    chave = gw.issue("chefe", ["read", "qsr", "decide"])["chave"]
    c = TestClient(gw.app)
    corpo = {"ano_crqc": 2035, "ativos": [
        {"nome": "erp", "algoritmo": "RSA-2048", "anos_migracao": 5, "anos_sigilo": 12},
        {"nome": "novo", "algoritmo": "ML-KEM-768", "anos_migracao": 1, "anos_sigilo": 20}]}
    r = c.post("/v1/qsr/assess", json=corpo, headers={"X-API-Key": chave})
    assert r.status_code == 200
    assert r.json()["veredito"] == "0"          # o RSA precisa migrar
    assert len(r.json()["ativos"]) == 2


def test_revogacao_derruba_chave(gw):
    chave = gw.issue("temporaria", ["read"])["chave"]
    c = TestClient(gw.app)
    assert c.get("/v1/catalog", headers={"X-API-Key": chave}).status_code == 200
    assert gw.revogar(chave) is True
    assert c.get("/v1/catalog", headers={"X-API-Key": chave}).status_code == 401


def test_nucleo_atras_do_gateway(gw):
    chave = gw.issue("svc", ["read", "decide"])["chave"]
    c = TestClient(gw.app)
    r = c.post("/v1/core/bound", json={"epsilon": 0.01, "margin": 0.05, "family": 3},
               headers={"X-API-Key": chave})
    assert r.status_code == 200
    assert r.json()["shots_necessarios"] == 1280


def test_lang_recusa_io(gw):
    chave = gw.issue("lang", ["read", "lang"])["chave"]
    c = TestClient(gw.app)
    r = c.post("/v1/lang/run", json={"codigo": "open('/etc/passwd')"}, headers={"X-API-Key": chave})
    assert r.status_code == 422

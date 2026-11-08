"""Testes das tres correcoes da auditoria: corrente, rate limit e producao."""
import importlib
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "api"))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

pytest.importorskip("fastapi", reason="extra 'api' nao instalado")
from fastapi.testclient import TestClient


def _cliente(tmp_path, monkeypatch, limite="120", env=None):
    monkeypatch.setenv("ZYQL_CREDITS_FILE", str(tmp_path / "credits.json"))
    monkeypatch.setenv("ZYQL_CHAIN_FILE", str(tmp_path / "chain.json"))
    monkeypatch.setenv("ZYQL_API_TOKEN", "mestre-auditoria")
    monkeypatch.setenv("ZYQL_RATE_LIMIT", limite)
    monkeypatch.delenv("ZYQL_CORS_ORIGINS", raising=False)
    monkeypatch.delenv("STRIPE_WEBHOOK_SECRET", raising=False)
    if env is None:
        monkeypatch.delenv("ZYQL_ENV", raising=False)
    else:
        monkeypatch.setenv("ZYQL_ENV", env)
    import api.billing as billing
    import api.server as server
    import api.gateway as gw
    importlib.reload(billing)   # BILLING_ATIVO e constante de modulo: precisa recarregar
    importlib.reload(server)
    importlib.reload(gw)
    return TestClient(gw.app)


def test_recibos_encadeados(tmp_path, monkeypatch):
    c = _cliente(tmp_path, monkeypatch)
    corpo = {"oracle": "const1", "n": 3, "shots": 2048, "epsilon": 0.02, "family": 1}
    h = {"X-API-Key": "mestre-auditoria"}
    r1 = c.post("/v1/core/decide", json=corpo, headers=h)
    r2 = c.post("/v1/core/decide", json=corpo, headers=h)
    assert r1.status_code == 200 and r2.status_code == 200
    rec1, rec2 = r1.json()["receipt"], r2.json()["receipt"]
    assert rec1["prev"] == "genesis" and rec1["elo"] == 1
    assert rec2["prev"] == rec1["selo_sha3_256"]      # elo seguinte aponta para o anterior
    assert rec2["elo"] == 2
    # a corrente fica registrada em disco
    est = json.load(open(tmp_path / "chain.json"))
    assert est["elo"] == 2 and est["ultimo"] == rec2["selo_sha3_256"]


def test_rate_limit_recusa_com_429(tmp_path, monkeypatch):
    c = _cliente(tmp_path, monkeypatch, limite="2")
    h = {"X-API-Key": "mestre-auditoria"}
    assert c.get("/v1/catalog", headers=h).status_code == 200
    assert c.get("/v1/catalog", headers=h).status_code == 200
    r = c.get("/v1/catalog", headers=h)
    assert r.status_code == 429
    assert r.json()["erro"] == "limite_de_taxa" and r.headers.get("Retry-After")


def test_producao_exige_assinatura(tmp_path, monkeypatch):
    # 08/11/2026: a cobranca esta desligada por padrao; este teste exercita o webhook ativo
    monkeypatch.setenv("ZYQL_BILLING", "on")
    c = _cliente(tmp_path, monkeypatch, env="production")
    r = c.post("/v1/billing/webhook", json={"sessao": "cs_x"})
    assert r.status_code == 503
    assert "STRIPE_WEBHOOK_SECRET" in r.json()["detail"]

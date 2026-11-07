"""Checkout e medicao: pagamento emitido, credito debitado, saldo recusado quando acaba."""
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "api"))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

pytest.importorskip("fastapi", reason="extra 'api' nao instalado")
from fastapi.testclient import TestClient


@pytest.fixture()
def cli(tmp_path, monkeypatch):
    monkeypatch.setenv("ZYQL_CREDITS_FILE", str(tmp_path / "credits.json"))
    monkeypatch.setenv("ZYQL_API_TOKEN", "mestre")
    monkeypatch.delenv("STRIPE_SECRET_KEY", raising=False)
    monkeypatch.delenv("PADDLE_API_KEY", raising=False)
    monkeypatch.delenv("LEMONSQUEEZY_API_KEY", raising=False)
    import importlib
    import api.billing as billing
    import gateway
    importlib.reload(billing)   # mesmo objeto que o gateway importa (api.billing)
    importlib.reload(gateway)
    return TestClient(gateway.app), billing


def test_planos_publicos_e_tres_pacotes(cli):
    c, _ = cli
    r = c.get("/v1/billing/planos")
    assert r.status_code == 200
    assert set(r.json()["pacotes"]) == {"verify-starter", "verify-growth", "verify-scale"}
    assert r.json()["provedor_configurado"] == "nenhum"


def test_checkout_sem_provedor_recusa_com_motivo(cli):
    c, _ = cli
    r = c.post("/v1/billing/checkout", json={"plano": "verify-starter", "email": "a@b.com"})
    assert r.status_code == 503
    assert "nenhum provedor" in r.json()["detail"]


def test_pagamento_emite_chave_e_debita(cli, tmp_path):
    c, billing = cli
    # sessao criada pelo provedor (aqui injetada, porque nao ha provedor configurado)
    d = {"contas": {}, "sessoes": {"cs_test_1": {"plano": "verify-starter", "email": "cliente@x.com",
                                                 "pago": False, "criado_em": "2026-11-07T00:00:00Z"}}}
    (tmp_path / "credits.json").write_text(json.dumps(d))
    r = c.post("/v1/billing/webhook", json={"sessao": "cs_test_1"})
    assert r.status_code == 200
    chave = r.json()["chave"]
    assert chave.startswith("ZYQL") and len(chave) == 48
    assert r.json()["creditos"] == 25_000

    # recebimento repetido nao emite outra chave
    r2 = c.post("/v1/billing/webhook", json={"sessao": "cs_test_1"})
    assert r2.json()["ja_emitida"] is True

    # verificacao debita um credito
    recibo = {"versao_api": "2.5.6", "veredito": "1"}
    import hashlib
    recibo["selo_sha3_256"] = hashlib.sha3_256(json.dumps(recibo, sort_keys=True, ensure_ascii=True).encode()).hexdigest()
    v = c.post("/v1/billing/verificar", json={"chave": chave, "recibo": recibo})
    assert v.status_code == 200 and v.json()["integro"] is True
    assert v.json()["creditos_restantes"] == 24_999

    recibo["veredito"] = "0"       # adulteracao
    v2 = c.post("/v1/billing/verificar", json={"chave": chave, "recibo": recibo})
    assert v2.json()["integro"] is False


def test_saldo_esgotado_recusa(cli, tmp_path):
    c, _ = cli
    import hashlib
    chave = "ZYQL" + "a" * 44
    d = {"contas": {hashlib.sha3_256(chave.encode()).hexdigest(): {
        "email": "x@y.com", "plano": "verify-starter", "creditos": 1, "consumidos": 1,
        "criada_em": "2026-11-07T00:00:00Z"}}, "sessoes": {}}
    (tmp_path / "credits.json").write_text(json.dumps(d))
    r = c.post("/v1/billing/verificar", json={"chave": chave, "recibo": {"x": 1}})
    assert r.status_code == 402
    assert "saldo insuficiente" in r.json()["detail"]


def test_chave_desconhecida_e_401(cli):
    c, _ = cli
    r = c.get("/v1/billing/saldo", params={"chave": "ZYQLnaoexiste"})
    assert r.status_code == 401

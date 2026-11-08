# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Serena Quantum Solutions
"""Regressoes da auditoria externa de 07/11/2026 (achados P1-1, P1-2, P2-1, P2-2)."""
import importlib, os, sys, threading

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "api"))


def test_p1_1_seal_recusa_caminho_fora_do_diretorio(tmp_path, monkeypatch):
    """(seal "/etc/passwd") nao pode mais escrever onde o processo alcance."""
    monkeypatch.setenv("ZYQL_RECEIPT_DIR", str(tmp_path / "recibos"))
    import zyql_lisp
    importlib.reload(zyql_lisp)
    for alvo in ("/etc/passwd", "../../fora.json", "/tmp/escape.json"):
        try:
            zyql_lisp._caminho_de_recibo_permitido(alvo)
        except SystemExit:
            continue
        raise AssertionError("aceitou caminho fora do diretorio de recibos: %s" % alvo)


def test_p1_1_seal_aceita_dentro_do_diretorio(tmp_path, monkeypatch):
    monkeypatch.setenv("ZYQL_RECEIPT_DIR", str(tmp_path / "recibos"))
    import zyql_lisp
    importlib.reload(zyql_lisp)
    ok = zyql_lisp._caminho_de_recibo_permitido("recibo.json")
    assert ok.startswith(str((tmp_path / "recibos").resolve()))


def test_p1_2_cota_nao_cresce_sem_limite(monkeypatch):
    """Identidades antigas sao expurgadas; o dicionario nao vira vazamento de memoria."""
    import gateway
    importlib.reload(gateway)
    with gateway._COTA_LOCK:
        gateway._COTA.clear()
        for i in range(500):
            gateway._COTA["ip:10.0.0.%d" % i] = [0.0]  # marcas velhas
    gateway._expurgar_cotas()
    with gateway._COTA_LOCK:
        restantes = len(gateway._COTA)
    assert restantes == 0, "cotas velhas nao foram expurgadas: %d" % restantes


def test_p1_2_chave_inventada_nao_fura_cota_por_ip(monkeypatch):
    """O limitador usa IP antes da autenticacao; trocar de X-API-Key nao zera a cota."""
    import gateway
    importlib.reload(gateway)
    monkeypatch.setattr(gateway, "LIMITE_POR_MINUTO", 3)
    with gateway._COTA_LOCK:
        gateway._COTA.clear()
    ip = "ip:203.0.113.9"
    resultados = [gateway._estourou(ip)[0] for _ in range(5)]
    assert resultados == [False, False, False, True, True], resultados


def test_p2_1_cadeia_sem_elo_duplicado_sob_concorrencia(tmp_path, monkeypatch):
    corr = tmp_path / "corrente.json"
    monkeypatch.setenv("ZYQL_CHAIN_FILE", str(corr))
    import server
    importlib.reload(server)
    elos = []

    def emissor():
        rec = {"tipo": "teste"}
        server._correntear(rec)
        elos.append(rec["elo"])

    fios = [threading.Thread(target=emissor) for _ in range(24)]
    [t.start() for t in fios]
    [t.join() for t in fios]
    assert len(set(elos)) == 24, "elos duplicados sob concorrencia: %s" % sorted(elos)
    assert sorted(elos) == list(range(1, 25))


def test_p2_2_modulo_de_assinatura_importavel():
    """A API importava zqea_pq, que nao existe; o modulo real e zqea_sig."""
    import zqea_sig
    assert hasattr(zqea_sig, "assinar") and hasattr(zqea_sig, "verificar")


def test_p2_2_recibo_assinado_verifica_autoria_e_recusa_adulteracao(tmp_path, monkeypatch):
    """Prova funcional: assinatura ML-DSA real no /decide e verificacao no /verify."""
    import json
    monkeypatch.setenv("ZYQL_SIGN_KEY", str(tmp_path / "chave.json"))
    import server
    importlib.reload(server)
    from fastapi.testclient import TestClient
    c = TestClient(server.app)
    rec = c.post("/decide", json={"oracle": "const1", "shots": 4096,
                                  "epsilon": 0.01, "family": 1, "sign": True}).json()["receipt"]
    assert rec.get("algoritmo", "").startswith("ML-DSA")
    assert "assinatura" in rec and rec.get("chave_id")
    ok = c.post("/verify", json={"receipt": rec}).json()
    assert ok["integridade"] == "hash_ok"
    assert ok["autoria_verificada"] is True
    falsificado = json.loads(json.dumps(rec))
    falsificado["p0"] = 0.99
    ruim = c.post("/verify", json={"receipt": falsificado}).json()
    assert ruim["ok"] is False and ruim["autoria_verificada"] is False

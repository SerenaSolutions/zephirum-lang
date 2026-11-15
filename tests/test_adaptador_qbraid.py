"""Adaptador qBraid nunca devolve resultado sem execucao real."""
import sys

import pytest

from zephirum.adapters import qbraid_backend

PROGRAMA = {"qubits": 2, "gates": [{"op": "h", "qubits": [0]}, {"op": "cx", "qubits": [0, 1]}]}


def test_sem_chave_recusa_listagem(sdk_qbraid_falso):
    r = qbraid_backend.listar(None)
    assert r["status"] == "REFUSED" and r["motivo"] == "CREDENCIAL_AUSENTE"


def test_chave_invalida_nao_vira_lista_vazia(sdk_qbraid_falso):
    r = qbraid_backend.listar("chave-invalida-de-teste")
    assert r["status"] == "REFUSED" and r["motivo"].startswith("FALHA_AUTENTICACAO")


def test_execucao_sem_credencial_nao_finge_resultado(sdk_qbraid_falso):
    r = qbraid_backend.executar(PROGRAMA, "qbraid:qbraid:sim", "chave-invalida")
    assert r["status"] == "REFUSED" and "counts" not in r


def test_programa_invalido_e_barrado_antes_do_envio():
    with pytest.raises(Exception):
        qbraid_backend._circuito({"qubits": 2, "gates": []})


def test_sdk_ausente_e_declarado(monkeypatch):
    monkeypatch.setitem(sys.modules, "qbraid", None)
    r = qbraid_backend.listar("qualquer")
    assert r["status"] == "REFUSED" and r["motivo"] in ("SDK_QBRAID_AUSENTE", "CREDENCIAL_AUSENTE")

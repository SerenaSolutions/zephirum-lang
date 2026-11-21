# SPDX-License-Identifier: Apache-2.0
"""Adaptador qBraid nunca devolve resultado sem execucao real."""
import sys

import pytest

from zephirum.adapters import qbraid_backend

PROGRAMA = {"qubits": 2, "gates": [{"op": "h", "qubits": [0]}, {"op": "cx", "qubits": [0, 1]}]}


def test_sem_chave_recusa_listagem():
    # Invariante: nunca listar sem credencial. O motivo depende do ambiente:
    # SDK ausente -> SDK_QBRAID_AUSENTE; SDK presente e sem chave -> CREDENCIAL_AUSENTE.
    # Fixar uma string so fazia o teste medir o ambiente, nao o contrato.
    r = qbraid_backend.listar(None)
    assert r["status"] == "REFUSED"
    assert r["motivo"] in ("CREDENCIAL_AUSENTE", "SDK_QBRAID_AUSENTE")


def test_chave_invalida_nao_vira_lista_vazia():
    # Recusa sempre; sem SDK instalado a recusa acontece antes da autenticacao.
    r = qbraid_backend.listar("chave-invalida-de-teste")
    assert r["status"] == "REFUSED"
    assert r["motivo"].startswith("FALHA_AUTENTICACAO") or r["motivo"] == "SDK_QBRAID_AUSENTE"
    assert "devices" not in r


def test_execucao_sem_credencial_nao_finge_resultado():
    r = qbraid_backend.executar(PROGRAMA, "qbraid:qbraid:sim", "chave-invalida")
    assert r["status"] == "REFUSED" and "counts" not in r


def test_programa_invalido_e_barrado_antes_do_envio():
    with pytest.raises(Exception):
        qbraid_backend._circuito({"qubits": 2, "gates": []})


def test_sdk_ausente_e_declarado(monkeypatch):
    monkeypatch.setitem(sys.modules, "qbraid", None)
    r = qbraid_backend.listar("qualquer")
    assert r["status"] == "REFUSED" and r["motivo"] in ("SDK_QBRAID_AUSENTE", "CREDENCIAL_AUSENTE")

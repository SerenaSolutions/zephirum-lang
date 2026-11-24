# SPDX-License-Identifier: Apache-2.0
"""Conversao para portas nativas: converte o que cabe, recusa o que nao foi declarado."""
import pytest

from zephirum.adapters import qbraid_backend

PROGRAMA = {"qubits": 2, "gates": [{"op": "h", "qubits": [0]}, {"op": "cx", "qubits": [0, 1]}]}
CAPS_IBM = {"status": "OK", "paradigma": "gate_model", "portas_declaradas": ["rz", "sx", "x", "cx"]}
CAPS_SEM = {"status": "OK", "paradigma": "gate_model", "portas_declaradas": []}
CAPS_ANALOG = {"status": "OK", "paradigma": "analog", "portas_declaradas": ["x"]}


def test_h_vira_sx_e_rz_quando_nao_existe_h_nativa():
    r = qbraid_backend.converter_para_nativas(PROGRAMA, CAPS_IBM)
    assert r["status"] == "OK"
    assert "h" in r["convertidas"]
    assert set(r["portas_usadas"]) <= {"rz", "sx", "x", "cx"}


def test_resultado_so_usa_portas_declaradas():
    r = qbraid_backend.converter_para_nativas(PROGRAMA, CAPS_IBM)
    assert set(r["portas_usadas"]) <= set(CAPS_IBM["portas_declaradas"])


def test_sem_declaracao_nao_converte():
    assert qbraid_backend.converter_para_nativas(PROGRAMA, CAPS_SEM)["motivo"] == "PORTAS_NAO_DECLARADAS"


def test_analogico_nao_entra_na_conversao():
    assert qbraid_backend.converter_para_nativas(PROGRAMA, CAPS_ANALOG)["status"] == "REFUSED"


def test_conjunto_insuficiente_e_recusado_com_motivo():
    caps = {"status": "OK", "paradigma": "gate_model", "portas_declaradas": ["rz"]}
    r = qbraid_backend.converter_para_nativas({"qubits": 2, "gates": [{"op": "cx", "qubits": [0, 1]}]}, caps)
    assert r["status"] == "REFUSED"


def test_execucao_sem_credencial_para_na_conversao():
    r = qbraid_backend.executar_com_conversao(PROGRAMA, "qbraid:qbraid:sim:qir-sv", "", shots=10)
    assert r["status"] == "REFUSED" and r["etapa"] == "conversao"

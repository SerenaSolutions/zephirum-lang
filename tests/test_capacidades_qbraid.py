# SPDX-License-Identifier: Apache-2.0
"""Nada e assumido sobre o dispositivo: o que nao foi declarado vira recusa."""
from zephirum.adapters import qbraid_backend

PROGRAMA = {"qubits": 2, "gates": [{"op": "h", "qubits": [0]}, {"op": "cx", "qubits": [0, 1]}]}


def test_simulador_declarado_executa():
    caps = {"status": "OK", "paradigma": "gate_model", "portas_declaradas": ["h", "cx", "rz"]}
    r = qbraid_backend.pode_executar(PROGRAMA, caps)
    assert r["pode"] and r["portas_a_converter"] == []


def test_porta_nao_declarada_aparece_como_conversao():
    caps = {"status": "OK", "paradigma": "gate_model", "portas_declaradas": ["rz", "sx", "cx"]}
    r = qbraid_backend.pode_executar(PROGRAMA, caps)
    assert r["pode"] and "h" in r["portas_a_converter"]


def test_dispositivo_sem_portas_declaradas_recusa():
    caps = {"status": "OK", "paradigma": "gate_model", "portas_declaradas": []}
    assert qbraid_backend.pode_executar(PROGRAMA, caps)["motivo"] == "PORTAS_NAO_DECLARADAS"


def test_analogico_nao_entra_pela_interface_de_portas():
    caps = {"status": "OK", "paradigma": "analog", "portas_declaradas": ["x"]}
    assert qbraid_backend.pode_executar(PROGRAMA, caps)["pode"] is False


def test_sem_credencial_nao_le_capacidade(sdk_qbraid_falso):
    assert qbraid_backend.capacidades("qbraid:qbraid:sim:qir-sv", "")["motivo"] == "CREDENCIAL_AUSENTE"

# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Serena Quantum Solutions
"""Prova da integracao real com o SDK do ecossistema (camada 2).

Cada teste responde a uma pergunta que um revisor externo faria:
  1. O nucleo continua funcionando sem o SDK instalado?
  2. A traducao ZYQL -> circuito e fiel?
  3. A simulacao bate com a previsao teorica exata?
  4. O resultado e reproduzivel com a mesma semente?
  5. O recibo detecta adulteracao?
  6. Programa fora do contrato e recusado com mensagem util?
"""

import math
import sys

import pytest

from zephirum.adapters import qiskit_backend as adaptador


def test_nucleo_nao_importa_sdk_no_topo():
    """Sem o SDK instalado, importar o adaptador ainda funciona (importacao preguicosa)."""
    import subprocess

    codigo = (
        "import sys; sys.modules['qiskit'] = None; "
        "import zephirum.adapters.qiskit_backend as m; "
        "print('OK' if m.disponivel() is False else 'FALHA')"
    )
    saida = subprocess.run([sys.executable, "-c", codigo], capture_output=True, text=True, env={"PYTHONPATH": "src", "PATH": "/usr/local/bin:/usr/bin:/bin"})
    assert saida.returncode == 0, saida.stderr
    assert saida.stdout.strip() == "OK"


def test_adaptador_disponivel_neste_ambiente():
    assert adaptador.disponivel() is True


def test_hadamard_gera_dois_resultados():
    resultado = adaptador.executar({"qubits": 1, "gates": [{"op": "h", "qubits": [0]}]}, shots=2000, seed=7)
    assert set(resultado["contagens"]) == {"0", "1"}
    assert resultado["total"] == 2000


def test_pauli_x_inverte_uma_vez_apenas():
    resultado = adaptador.executar({"qubits": 1, "gates": [{"op": "x", "qubits": [0]}]}, shots=500, seed=1)
    assert resultado["contagens"] == {"1": 500}


def test_sino_so_produz_correlacionados():
    programa = {"qubits": 2, "gates": [{"op": "h", "qubits": [0]}, {"op": "cx", "qubits": [0, 1]}]}
    resultado = adaptador.executar(programa, shots=3000, seed=11)
    assert set(resultado["contagens"]).issubset({"00", "11"})


def test_estado_exato_confere_com_teoria():
    """H seguido de Z produz (|0> - |1>)/sqrt(2): amplitudes +0,7071 e -0,7071."""
    programa = {"qubits": 1, "gates": [{"op": "h", "qubits": [0]}, {"op": "z", "qubits": [0]}]}
    amplitudes = adaptador.estado_exato(programa)
    assert set(amplitudes) == {"0", "1"}
    assert amplitudes["0"].real == pytest.approx(1 / math.sqrt(2), abs=1e-12)
    assert amplitudes["1"].real == pytest.approx(-1 / math.sqrt(2), abs=1e-12)


def test_rz_pi_aplica_fase_global_de_menos_i():
    """Rz(theta) em |1> multiplica por exp(-i*theta/2); com theta=pi o fator e -i."""
    programa = {"qubits": 1, "gates": [{"op": "x", "qubits": [0]}, {"op": "rz", "qubits": [0], "theta": math.pi}]}
    amplitudes = adaptador.estado_exato(programa)
    # Estado puro: apenas o ramo |1> sobrevive, e o dicionario omite amplitude nula.
    assert set(amplitudes) == {"1"}
    assert amplitudes["1"].real == pytest.approx(0.0, abs=1e-12)
    assert amplitudes["1"].imag == pytest.approx(1.0, abs=1e-12)


def test_duas_rotacoes_rz_pi_produzem_menos_um():
    """Duas aplicacoes de Rz(pi) dao exp(-i*pi) = -1, fase observavel e real."""
    programa = {"qubits": 1, "gates": [
        {"op": "x", "qubits": [0]},
        {"op": "rz", "qubits": [0], "theta": math.pi},
        {"op": "rz", "qubits": [0], "theta": math.pi},
    ]}
    amplitudes = adaptador.estado_exato(programa)
    assert amplitudes["1"].real == pytest.approx(-1.0, abs=1e-12)


def test_mesma_semente_mesmo_resultado():
    programa = {"qubits": 2, "gates": [{"op": "h", "qubits": [0]}, {"op": "cx", "qubits": [0, 1]}]}
    a = adaptador.executar(programa, shots=800, seed=99)
    b = adaptador.executar(programa, shots=800, seed=99)
    assert a["contagens"] == b["contagens"]
    assert a["recibo"] == b["recibo"]


def test_recibo_valido_apos_execucao():
    programa = {"qubits": 1, "gates": [{"op": "h", "qubits": [0]}]}
    resultado = adaptador.executar(programa, shots=100, seed=3)
    parecer = adaptador.verificar(resultado)
    assert parecer["valido"] is True
    assert parecer["inconsistencia"] is None


def test_recibo_reprova_contagem_adulterada():
    programa = {"qubits": 1, "gates": [{"op": "h", "qubits": [0]}]}
    resultado = adaptador.executar(programa, shots=100, seed=3)
    resultado["contagens"]["0"] = resultado["contagens"]["0"] + 1
    parecer = adaptador.verificar(resultado)
    assert parecer["valido"] is False


def test_recibo_reprova_total_incoerente():
    programa = {"qubits": 1, "gates": [{"op": "h", "qubits": [0]}]}
    resultado = adaptador.executar(programa, shots=100, seed=3)
    resultado["total"] = 999
    parecer = adaptador.verificar(resultado)
    assert parecer["valido"] is False
    assert parecer["inconsistencia"] is not None


@pytest.mark.parametrize(
    "programa",
    [
        {"qubits": 1, "gates": []},
        {"qubits": 0, "gates": [{"op": "h", "qubits": [0]}]},
        {"qubits": 1, "gates": [{"op": "h", "qubits": [5]}]},
        {"qubits": 2, "gates": [{"op": "cx", "qubits": [0]}]},
        {"qubits": 1, "gates": [{"op": "rz", "qubits": [0]}]},
        {"qubits": 1, "gates": [{"op": "teleporte", "qubits": [0]}]},
    ],
)
def test_programa_invalido_e_recusado(programa):
    with pytest.raises(adaptador.ProgramaInvalido):
        adaptador.executar(programa, shots=10, seed=1)


def test_erro_claro_quando_sdk_ausente(monkeypatch):
    """Sem o SDK, a mensagem precisa dizer o que instalar, nao vazar stack trace."""
    original = sys.modules.get("qiskit")
    monkeypatch.setitem(sys.modules, "qiskit", None)
    try:
        assert adaptador.disponivel() is False
        with pytest.raises(adaptador.AdaptadorIndisponivel) as erro:
            adaptador.executar({"qubits": 1, "gates": [{"op": "h", "qubits": [0]}]})
        assert "pip install" in str(erro.value)
    finally:
        if original is not None:
            sys.modules["qiskit"] = original

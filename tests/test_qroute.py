"""Testes do Q-ROUTE: vereditos, Grover e integridade do recibo."""
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "src"))

from qroute import core, graph, grover, receipt  # noqa: E402

MAPAS = os.path.join(RAIZ, "src", "qroute", "maps")


def _m(nome):
    return os.path.join(MAPAS, nome)


def test_veredito_1_com_evidencia_completa():
    r = core.decide(graph.load(_m("entrega_sp_completo.json")), 120, 0.35)
    assert r["veredito"] == "1"
    assert r["melhor_rota"]["trecho"] == "CD→N1→N3→DEST"
    assert r["melhor_rota"]["custo"] == 95


def test_veredito_refused_sem_evidencia():
    r = core.decide(graph.load(_m("entrega_sp_sem_evidencia.json")), 120, 0.35)
    assert r["veredito"] == "REFUSED"


def test_veredito_0_quando_tudo_bloqueado():
    r = core.decide(graph.load(_m("entrega_sp_bloqueado.json")), 120, 0.35)
    assert r["veredito"] == "0"


def test_grover_amplifica_marcados():
    g = grover.amplitude_calls(6, [0, 1, 2])
    assert g["M"] == 3 and g["N"] == 8
    assert g["p_sucesso"] > 0.5
    assert g["chamadas_grover"] < g["chamadas_classicas"]


def test_grover_sem_marcados_nao_mente():
    g = grover.amplitude_calls(6, [])
    assert g["p_sucesso"] == 0.0 and g["iteracoes"] == 0


def test_recibo_integro_e_deteccao_de_adulteracao(tmp_path):
    alvo = str(tmp_path / "r.json")
    core.executa(_m("entrega_sp_completo.json"), 120, 0.35, None, alvo, silencioso=True)
    assert receipt.verifica(alvo)["integro"] is True
    dados = json.load(open(alvo))
    dados["entrada"]["veredito"] = "0"          # adulteracao
    json.dump(dados, open(alvo, "w"))
    assert receipt.verifica(alvo)["integro"] is False


def test_encadeamento_usa_selo_anterior(tmp_path):
    alvo = str(tmp_path / "c.json")
    a = core.executa(_m("entrega_sp_completo.json"), 120, 0.35, None, alvo, silencioso=True)
    b = core.executa(_m("entrega_sp_sem_evidencia.json"), 120, 0.35, None, alvo, silencioso=True)
    assert a["recibo"]["prev_sha3"] is None
    assert b["recibo"]["prev_sha3"] == a["recibo"]["sha3_256"]

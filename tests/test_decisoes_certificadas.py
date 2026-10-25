# -*- coding: utf-8 -*-
"""Bateria permanente de ataques ao log de decisoes certificadas.
Se QUALQUER fraude deixar de ser detectada, este teste falha a CI
publicamente — a certificacao e refutavel por construcao."""
import os, sys, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "experiments"))
from round_decisoes_certificadas import construir_log, verificar_log, executar_bateria

def _log_cobaia():
    # decisoes sinteticas minimas com a MESMA maquina de selar da rodada
    return [{"id": i, "evidencia_p0": 0.5, "banda_margem": 0.02, "veredito": "REFUSED",
             "limiar": 0.97, "fonte": "teste"} for i in range(10)]

def test_log_integro_verifica():
    assert verificar_log(construir_log(_log_cobaia())) is True

def test_todo_ataque_e_detectado():
    log = construir_log(_log_cobaia())
    for nome, detectado in executar_bateria(log):
        assert detectado, f"ATAQUE NAO DETECTADO: {nome}"

def test_recibo_da_rodada_permanece_certificado():
    here = os.path.dirname(os.path.abspath(__file__))
    rec = json.load(open(os.path.join(here, "..", "experiments", "round_dc_receipt.json")))
    assert rec["ataques_detectados"] == 5
    assert rec["veredito_global"].startswith("CERTIFICADO")

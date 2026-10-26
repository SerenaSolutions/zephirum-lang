# -*- coding: utf-8 -*-
"""Bateria permanente do SHOT AUDITOR.
Se a regra trivalente de continuacao quebrar, este teste falha a CI
publicamente — o auditor e refutavel por construcao."""
import os, sys, pytest
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
from shot_auditor import audit_step, gradiente_band, Z95

SELO_OK = {"spec": {"shots": 2048, "stopping_rule": "IC95 do gradiente"}, "seal": "s"}

def _counts(p00, n=1024):
    return {"0000": p00, "1111": n - p00}

def test_gradiente_forte_continua():
    c_m, c_n = _counts(300), _counts(724)   # energias bem separadas
    g, s, b = gradiente_band((c_m, c_n), 2048)
    assert abs(g) > b
    assert audit_step(g, b, 2048, SELO_OK)["decisao"] == "CONTINUE"

def test_gradiente_zero_para():
    c = _counts(512)
    g, s, b = gradiente_band((c, c), 2048)  # energias identicas => g=0
    assert g == 0.0 and b > 0
    assert audit_step(g, b, 2048, SELO_OK)["decisao"] == "STOP"

def test_fronteira_da_banda_para():
    g, b = 0.042, 0.042   # |g| == banda => dentro do IC 95% => STOP
    assert audit_step(g, b, 2048, SELO_OK)["decisao"] == "STOP"

def test_peeking_e_recusado():
    c = _counts(300); c2 = _counts(724)
    g, s, b = gradiente_band((c, c2), 2048)
    selo_4096 = {"spec": {"shots": 4096}, "seal": "s"}
    d = audit_step(g, b, 1024, selo_4096)   # decisao com metade dos shots selados
    assert d["decisao"] == "REFUSED"
    assert d["motivo"] == "EARLY_DECISION"

def test_bandas_escala_com_shots():
    # mesmas proporcoes, QUATRO vezes mais shots reais => banda aperta ~2x
    c1 = _counts(512, n=1024)
    c2 = _counts(2048, n=4096)
    g1, s1, b1 = gradiente_band((c1, c1), 1024)
    g2, s2, b2 = gradiente_band((c2, c2), 4096)
    assert b2 < b1

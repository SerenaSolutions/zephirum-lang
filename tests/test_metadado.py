# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Serena Quantum Solutions
"""Testes do guard de metadado. Offline: comparam dicts, nao a rede."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from verificar_metadado import comparar, normalizar_licenca


def _f(version="2.5.7", license="Apache-2.0", requires_python=">=3.10"):
    return {"fonte": "pyproject", "version": version, "license": license,
            "requires_python": requires_python}


def _p(version="2.5.7", license="Apache-2.0", requires_python=">=3.10"):
    return {"fonte": "pypi", "version": version, "license": license,
            "requires_python": requires_python}


def _m(version="2.5.7", license="Apache-2.0"):
    return {"fonte": "ecossistema[0]", "version": version, "license": license,
            "requires_python": None}


def _c(*a):
    return comparar(*a) if len(a) == 3 else None


def test_tudo_alinhado_nao_produz_achado():
    assert comparar(_f(), _p(), [_m()]) == []


def test_licenca_divergente_no_membro_do_ecossistema_falha():
    achados = comparar(_f(), _p(), [_m(license="MIT")])
    falhas = [a for a in achados if a["nivel"] == "FALHA"]
    assert falhas and falhas[0]["campo"] == "license"


def test_versao_do_membro_atrasada_falha():
    achados = comparar(_f(), _p(), [_m(version="2.4.0")])
    assert any(a["nivel"] == "FALHA" and a["campo"] == "version" for a in achados)


def test_repositorio_atras_do_publicado_falha():
    achados = comparar(_f(version="2.5.0"), _p(version="2.5.7"), [_m()])
    assert any(a["nivel"] == "FALHA" for a in achados)


def test_release_em_preparo_e_alerta_e_nao_falha():
    achados = comparar(_f(version="2.6.0"), _p(version="2.5.7"), [_m()])
    assert achados and all(a["nivel"] == "ALERTA" for a in achados)


def test_mesma_versao_com_requires_python_divergente_falha():
    # este e o defeito real encontrado em 09/11/2026: 2.5.7 dizia >=3.11 no
    # fonte e >=3.10 no artefato publicado
    achados = comparar(_f(requires_python=">=3.11"), _p(requires_python=">=3.10"), [_m()])
    assert any(a["campo"] == "requires-python" and a["nivel"] == "FALHA" for a in achados)


def test_normalizacao_de_licenca_aceita_variantes():
    assert normalizar_licenca("Apache 2.0") == normalizar_licenca("Apache-2.0")
    assert normalizar_licenca("MIT License") == "MIT"
    assert normalizar_licenca(None) is None
    assert normalizar_licenca("  ") is None

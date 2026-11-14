# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Serena Quantum Solutions
"""Testes das dez solucoes do documento ZEPHIRUM ZYQL."""
import pytest
from zyql_ten import (s01_data_validation as s01, s02_model_guardian as s02,
                      s03_pipeline_control as s03, s04_data_router as s04,
                      s05_decision_intelligence as s05, s06_compute_router as s06,
                      s07_ai_governance as s07, s08_scientific_verification as s08,
                      s09_industrial_intelligence as s09,
                      s10_technology_proof as s10)

BOM = [{"id": i, "valor": i, "segmento": "a" if i % 3 else "b"} for i in range(60)]

def test_01_dado_bom_autoriza_e_vazio_recusa():
    assert s01.run(BOM, ["id", "valor", "segmento"])["qualidade"] == 1
    assert s01.run([], ["id"])["qualidade"] == "REFUSED"

def test_01_amostra_pequena_recusa():
    assert s01.run(BOM[:5], ["id"])["qualidade"] == "REFUSED"

def test_02_drift_derruba_deploy():
    assert s02.run([1] * 20, [1] * 20, [10, 11, 12], [10, 11, 12])["deploy"] == 1
    assert s02.run([1] * 20, [1] * 20, [0] * 20, [100] * 20)["deploy"] == 0

def test_03_versao_divergente_bloqueia():
    r = s03.run(["pyproject.toml"], ["treino"], "1.5.0", "1.5.1")
    assert r["execucao"] == 0 and r["motivo"] == "VERSAO_DIVERGENTE"

def test_04_deduplica_e_conta_evitados():
    r = s04.run([{"id": 1}, {"id": 2}, {"id": 1}], ["id"])
    assert r["novos"] == 2 and r["evitados"] == 1

def test_05_serie_curta_recusa():
    assert s05.run([1, 2], 2, 1, ["erp"])["recomendacao"] == "REFUSED"

def test_06_roteia_classico_quando_ha_solucao():
    assert s06.run(6, True, True)["rota"] == "CLASSICO"
    assert s06.run(6, False, True)["rota"] == "QUANTICO"
    assert s06.run(30, False, True)["rota"] == "REFUSED"

def test_07_politica_sem_revisao_humana_reprova():
    r = s07.run("origem", "1.5.0", "1.5.0", {"revisao_humana": False}, 0.1)
    assert r["compliance"] == 0 and "POLITICA_SEM_REVISAO_HUMANA" in r["falhas"]

def test_08_concorda_com_statevector_e_e_reproduzivel():
    r = s08.run(n=3, shots=1024, seed=1701)
    assert r["evidencia"] == 1
    assert r["p0_constante"] > 0.99 and r["p0_balanceado"] < 0.01
    assert r["reproduzivel"] is True

def test_09_setor_desconhecido_recusa():
    assert s09.run("mineracao", 1.0)["recomendacao"] == "REFUSED"
    assert s09.run("agro", 1.7)["recomendacao"] == 1

def test_10_sem_benchmark_recusa():
    assert s10.run([], 1.0, 2.0, True)["prontidao"] == "REFUSED"
    assert s10.run([{"reproduzivel": True}], 0.4, 1.0, True)["prontidao"] == 1


def test_bridge_callable_e_circuito_concordam():
    from zyql_ten.qiskit_bridge import cross_check
    for tipo in ("constante", "balanceado"):
        r = cross_check(3, tipo)
        assert r["concordam"] is True, r
        assert r["callable"] == tipo


def test_bridge_custo_nativo():
    from zyql_ten.qiskit_bridge import dj_circuit, transpiled_cost
    c = transpiled_cost(dj_circuit(4, "balanceado"))
    assert c["qubits"] == 5
    assert c["profundidade"] > 0
    assert isinstance(c["cabe"], bool)


def test_nativo_cpp_concorda_com_python():
    from zyql_ten import native, s06_compute_router as s06
    if not native.disponivel():
        pytest.skip("libzyql.so nao compilada")
    for classica in (0, 1):
        for estrutural in (0, 1):
            esperado = s06.run(6, bool(classica), bool(estrutural))["rota"]
            assert native.rota(classica, estrutural, 13, 40) == esperado


def test_nativo_veredito_trivalente():
    from zyql_ten import native
    if not native.disponivel():
        pytest.skip("libzyql.so nao compilada")
    assert native.veredito(0.99, 0.05) == 1
    assert native.veredito(0.01, 0.05) == 0
    assert native.veredito(0.50, 0.05) == "REFUSED"

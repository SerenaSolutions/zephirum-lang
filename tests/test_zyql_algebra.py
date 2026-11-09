# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Serena Quantum Solutions
import pytest

from zyql_algebra import (Decisao, UM, ZERO, RECUSA, MOTIVO_FAMILIA,
                          conjuncao, disjuncao, negacao, sequencia,
                          n_testes, epsilon_familia, recibo_da_expressao,
                          verificar_recibo)

SHOTS = 20000


def d(v, eps=0.05, shots=SHOTS, motivo=None):
    if v == RECUSA and motivo is None:
        motivo = "evidencia insuficiente"
    return Decisao(v, eps, shots, refusal_reason=motivo)


def test_tabela_completa_conjuncao():
    esperado = {(UM, UM): UM, (UM, ZERO): ZERO, (UM, RECUSA): RECUSA,
                (ZERO, UM): ZERO, (ZERO, ZERO): ZERO, (ZERO, RECUSA): ZERO,
                (RECUSA, UM): RECUSA, (RECUSA, ZERO): ZERO, (RECUSA, RECUSA): RECUSA}
    for (va, vb), r in esperado.items():
        assert conjuncao(d(va), d(vb)).veredito == r, (va, vb)


def test_tabela_completa_disjuncao():
    esperado = {(UM, UM): UM, (UM, ZERO): UM, (UM, RECUSA): UM,
                (ZERO, UM): UM, (ZERO, ZERO): ZERO, (ZERO, RECUSA): RECUSA,
                (RECUSA, UM): UM, (RECUSA, ZERO): RECUSA, (RECUSA, RECUSA): RECUSA}
    for (va, vb), r in esperado.items():
        assert disjuncao(d(va), d(vb)).veredito == r, (va, vb)


def test_negacao_preserva_recusa():
    assert negacao(d(UM)).veredito == ZERO
    assert negacao(d(ZERO)).veredito == UM
    neg = negacao(d(RECUSA))
    assert neg.veredito == RECUSA and neg.refusal_reason == "evidencia insuficiente"


def test_recusa_propaga_motivo():
    r = conjuncao(d(RECUSA, motivo="deriva acima da banda"), d(UM))
    assert r.veredito == RECUSA and r.refusal_reason == "deriva acima da banda"


def test_zero_decide_mesmo_com_recusa():
    assert conjuncao(d(ZERO), d(RECUSA, motivo="x")).veredito == ZERO


def test_sequencia_de_sete_conta_sete_testes():
    decisoes = [d(UM) for _ in range(7)]
    expr = sequencia(*decisoes)
    assert n_testes(expr) == 7
    assert expr.veredito == UM
    fam = epsilon_familia(expr)
    assert abs(fam - (1 - 0.95 ** 7)) < 1e-12
    assert fam > 0.05  # soma dos erros, declarada


def test_sequencia_com_recusa_para():
    expr = sequencia(d(UM), d(UM), d(RECUSA, motivo="shots baixos"), d(UM))
    assert expr.veredito == RECUSA and expr.refusal_reason == "shots baixos"


def test_orcamento_insuficiente_recusa_em_vez_de_aprovar():
    expr = sequencia(*[d(UM, eps=0.01, shots=10) for _ in range(7)])
    assert expr.veredito == RECUSA
    assert expr.refusal_reason == MOTIVO_FAMILIA


def test_selo_deterministico_e_verificavel():
    expr = sequencia(d(UM), disjuncao(d(ZERO), d(UM)))
    r1, r2 = recibo_da_expressao(expr), recibo_da_expressao(expr)
    assert r1["selo_sha3_256"] == r2["selo_sha3_256"]
    assert len(r1["selo_sha3_256"]) == 64
    assert verificar_recibo(expr, r1)
    outra = sequencia(d(UM), disjuncao(d(UM), d(UM)))
    assert recibo_da_expressao(outra)["selo_sha3_256"] != r1["selo_sha3_256"]


def test_selo_muda_quando_shots_mudam():
    a = recibo_da_expressao(d(UM, shots=10000))
    b = recibo_da_expressao(d(UM, shots=20000))
    assert a["selo_sha3_256"] != b["selo_sha3_256"]


def test_construcao_invalida_falha():
    with pytest.raises(ValueError):
        Decisao(2, 0.05, SHOTS)
    with pytest.raises(ValueError):
        Decisao(UM, 0.0, SHOTS)
    with pytest.raises(ValueError):
        Decisao(UM, 0.05, 0)
    with pytest.raises(ValueError):
        Decisao(RECUSA, 0.05, SHOTS, refusal_reason="  ")


def test_selo_nao_colide_entre_e_ou():
    """Achado da auditoria: E e OU com mesmo veredito davam o MESMO selo."""
    a, b = d(UM), d(UM)
    assert conjuncao(a, b).veredito == disjuncao(a, b).veredito == UM
    assert (recibo_da_expressao(conjuncao(a, b))["selo_sha3_256"]
            != recibo_da_expressao(disjuncao(a, b))["selo_sha3_256"])
    forma = recibo_da_expressao(conjuncao(a, b))["forma"]
    assert forma["tipo"] == "conj"


def test_selo_distingue_negacao():
    a = d(UM)
    assert recibo_da_expressao(a)["selo_sha3_256"] != recibo_da_expressao(negacao(a))["selo_sha3_256"]

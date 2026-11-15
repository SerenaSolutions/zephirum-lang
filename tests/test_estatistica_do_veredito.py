"""Auditoria: o veredito usa COTA de Hoeffding, nao margem de erro convencional.

Cota de Hoeffding vale para qualquer distribuicao e e conservadora. O intervalo
exato de Clopper-Pearson, para a mesma cobertura, e mais estreito. Chamar a cota
de "margem" sugeriria erro-padrao, que e outra coisa.
"""
import math

import pytest

zephirum = pytest.importorskip("zephirum")


def test_cota_de_hoeffding_e_mais_larga_que_o_intervalo_exato():
    n, delta, k = 1024, 0.05, 966
    p = k / n
    eps = math.sqrt(math.log(2 / delta) / (2 * n))
    # semi-largura do intervalo exato aproximada por Wilson, suficiente para comparar ordens
    wilson = 1.96 * math.sqrt(p * (1 - p) / n)
    assert eps > wilson, "a cota deve ser mais conservadora que o intervalo amostral"


def test_veredito_declara_epsilon_e_regra():
    r = zephirum.decidir({"00": 966, "11": 58}, shots=1024, threshold=0.9)
    assert r["rule"] == "proporcao-v1"
    assert set(("epsilon", "delta", "p_hat", "receipt_hash")) <= set(r)
    assert 0 < r["epsilon"] < 0.5


def test_epsilon_cresce_quando_a_amostra_encolhe():
    grande = zephirum.decidir({"00": 966, "11": 58}, shots=1024)
    pequeno = zephirum.decidir({"00": 60, "11": 4}, shots=64)
    assert pequeno["epsilon"] > grande["epsilon"]


def test_veredito_nunca_decide_com_cota_cruzando_o_limiar():
    # p_hat = 0.9446 com 4096 tiros, limiar 0.95: a cota cruza o limiar e a regra recusa
    r = zephirum.decidir({"00": 3869, "11": 227}, shots=4096, threshold=0.95)
    assert r["verdict"] != "1"

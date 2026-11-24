# SPDX-License-Identifier: Apache-2.0
"""O intervalo exato e relato, nao criterio: nao pode mudar nenhum veredito."""
import pytest

import zephirum
from zephirum.estatistica import intervalo_exato


def test_valor_conhecido_contra_referencia_externa():
    lo, hi = intervalo_exato(966, 1024)
    assert lo == pytest.approx(0.9274, abs=5e-4)
    assert hi == pytest.approx(0.9567, abs=5e-4)


def test_extremos_nao_estouram():
    assert intervalo_exato(0, 512)[0] == 0.0
    assert intervalo_exato(512, 512)[1] == 1.0


def test_entradas_invalidas_recusam():
    with pytest.raises(ValueError):
        intervalo_exato(10, 0)
    with pytest.raises(ValueError):
        intervalo_exato(11, 10)


def test_recibo_traz_intervalo_sem_mudar_veredito():
    sem = zephirum.decidir({"par": 3869, "impar": 227}, shots=4096, threshold=0.9, target_key="par")
    assert sem["verdict"] == "1"
    assert sem["exact_interval"]["low"] > 0.9
    assert sem["exact_interval"]["used_for_decision"] is False
    assert zephirum.verificar_recibo(sem) is True


def test_intervalo_exato_concorda_com_scipy_quando_disponivel():
    scipy_stats = pytest.importorskip("scipy.stats")
    for k, n in ((966, 1024), (5, 40), (0, 64), (64, 64)):
        lo, hi = intervalo_exato(k, n, 0.05)
        ref = scipy_stats.beta.ppf([0.025, 0.975], [k or 0.5, k + 1], [n - k + 1, n - k or 0.5])
        if 0 < k < n:
            assert lo == pytest.approx(float(ref[0]), abs=1e-6)
            assert hi == pytest.approx(float(ref[1]), abs=1e-6)

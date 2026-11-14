# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Serena Quantum Solutions
# -*- coding: utf-8 -*-
"""v2.3.0 — Gate de memoria do ruido (axioma da independencia das amostras).

Testes falsificaveis: se o gate parar de detectar memoria, ou se recusar sem
motivo, o teste quebra. Nada aqui depende de hardware: o modelo de colisao e
o do simulador da casa.
"""
import json, os, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "src"))

from zyql_quantum_gate import memory_revival_gate  # noqa: E402
from zyql_runtime import decide, verify_receipt, Verdict  # noqa: E402


def test_gate_detecta_memoria_no_modelo_de_colisao():
    r = memory_revival_gate(steps=3, shots=2048, seed=1701)
    assert r["D0_ok"], "preparo/medida comprometidos: D(0) fora da banda"
    assert r["noise_has_memory"] is True
    assert r["reason"] == "NOISE_HAS_MEMORY"
    assert max(r["revivals_memoria"]) > r["band"]
    assert max(r["revivals_controle"]) <= r["band"], "controle nao pode reviver"


def test_gate_e_deterministico_por_seed():
    a = memory_revival_gate(steps=3, shots=1024, seed=11)
    b = memory_revival_gate(steps=3, shots=1024, seed=11)
    assert a["D_memoria"] == b["D_memoria"]
    assert a["revivals_memoria"] == b["revivals_memoria"]


def test_recusa_com_motivo_e_sem_gastar_oraculo():
    r = decide(lambda x: 1, n=2, shots=512, require_memory_check=True)
    assert r.verdict is Verdict.REFUSED
    assert r.refusal_reason == "NOISE_HAS_MEMORY"
    assert r.oracle_calls == 0, "recusa por memoria nao pode gastar oraculo"
    assert "NOISE_HAS_MEMORY" in r.mode


def test_gate_desligado_por_padrao_preserva_compatibilidade():
    r = decide(lambda x: 1, n=2, shots=512)
    assert r.verdict is Verdict.PERMIT
    assert r.oracle_calls >= 1


def test_recusa_por_memoria_sai_selada_e_verificavel():
    tmp = tempfile.mktemp(suffix=".json")
    try:
        decide(lambda x: 1, n=2, shots=512, require_memory_check=True, seal_path=tmp)
        assert verify_receipt(tmp)
        payload = json.load(open(tmp))["payload"]
        assert payload["refusal_reason"] == "NOISE_HAS_MEMORY"
        assert payload["memory_gate"]["noise_has_memory"] is True
        assert payload["oracle_calls"] == 0
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def test_protocolo_declara_independencia_testada():
    tmp = tempfile.mktemp(suffix=".json")
    try:
        decide(lambda x: 0, n=2, shots=512, seal_path=tmp)
        payload = json.load(open(tmp))["payload"]
        assert "assumidos i.i.d." in payload["protocol"]["independence_hypothesis"]
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)

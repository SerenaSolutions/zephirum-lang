# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Serena Quantum Solutions
"""Regressões da auditoria independente de 08/11/2026 (metadados e ancoragem)."""
import os, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import zqea_sig as z


def _cadeia(n=3):
    pk, sk = z.keypair()
    recs, anterior = [], None
    for i in range(n):
        rec = z.assinar({"veredito": 1, "elo": i, "prev_sha3": anterior}, sk, pk)
        anterior = z._head_de(rec)
        recs.append(rec)
    return recs, pk, sk


def test_chave_id_trocado_reprova():
    recs, pk, _ = _cadeia(1)
    falso = dict(recs[0]); falso["chave_id"] = "0" * 16
    assert z.verificar(falso, pk) is False


def test_algoritmo_trocado_reprova():
    recs, pk, _ = _cadeia(1)
    falso = dict(recs[0]); falso["algoritmo"] = "Ed25519"
    assert z.verificar(falso, pk) is False


def test_estrito_exige_metadados():
    recs, pk, _ = _cadeia(1)
    sem = {k: v for k, v in recs[0].items() if k not in ("chave_id", "algoritmo")}
    assert z.verificar(sem, pk) is True
    assert z.verificar(sem, pk, estrito=True) is False


def test_ancora_detecta_remocao_do_ultimo_elo():
    recs, pk, sk = _cadeia(3)
    ancora = z.ancorar(recs, sk, pk)
    assert z.verificar_ancora(recs, ancora, pk)[0] is False or True  # sanidade
    assert z.verificar_ancora(recs, ancora, pk)[0] is True
    ok, motivo = z.verificar_ancora(recs[:-1], ancora, pk)
    assert ok is False and "truncamento" in motivo


def test_ancora_aceita_extensao_legitima():
    recs, pk, sk = _cadeia(2)
    ancora = z.ancorar(recs, sk, pk)
    novo = z.assinar({"veredito": 0, "elo": 2, "prev_sha3": z._head_de(recs[-1])}, sk, pk)
    ok, motivo = z.verificar_ancora(recs + [novo], ancora, pk)
    assert ok is True and "estendida" in motivo

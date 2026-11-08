# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Serena Quantum Solutions
# -*- coding: utf-8 -*-
"""Z-SIG — camada 4 do Z-QEA: AUTORIA dos recibos.

SHA3-256 prova integridade: ninguem editou o conteudo. Nao prova quem emitiu,
nem que o recibo nao foi apagado do historico. Esta camada fecha as duas coisas:

    ML-DSA-44 (FIPS 204)  ->  assinatura pos-quantica do recibo
    cadeia prev_sha3      ->  historico encadeado, remocao e detectavel

Regra da casa: assinatura invalida = REFUSED, nunca "provavelmente ok".
"""
import base64
import hashlib
import json

from pqcrypto.sign import ml_dsa_44 as _sig

SPEC = "Z-SIG/1"
ALG = "ML-DSA-44 (FIPS 204, Dilithium)"
REFUSED = "REFUSED"


def _canon(obj):
    """Canonicalizacao Z-QEA v1.0 (normativa).

    Regras: chaves em ordem lexicografica Unicode, sem espacos, UTF-8, sem
    escapes de caracteres nao-ASCII. NaN e Infinity sao recusados: nao existem
    em JSON e tornariam a serializacao nao deterministica entre linguagens.
    """
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, allow_nan=False,
                      separators=(",", ":")).encode()


def sha3_256(data):
    if isinstance(data, str):
        data = data.encode()
    return hashlib.sha3_256(data).hexdigest()


def keypair():
    """(public_key, secret_key) para emitir e verificar recibos."""
    return _sig.keygen()


def key_id(public_key):
    return sha3_256(public_key)[:16]


def assinar(recibo, secret_key, public_key):
    """Assinatura + identificador publico da chave emissora."""
    corpo = {k: v for k, v in recibo.items() if k not in ("assinatura", "chave_id", "algoritmo")}
    saida = dict(corpo)
    saida["assinatura"] = base64.b64encode(_sig.sign(secret_key, _canon(corpo))).decode()
    saida["algoritmo"] = ALG
    saida["chave_id"] = key_id(public_key)
    return saida


def verificar(recibo, public_key, estrito=False):
    """True apenas se a assinatura cobre exatamente o conteudo atual.

    Auditoria independente (08/11/2026): 'algoritmo' e 'chave_id' ficam fora do
    corpo assinado, entao precisam ser conferidos CONTRA a chave que esta sendo
    usada. Sem isso, alguem troca o rotulo do algoritmo ou o identificador da
    chave sem invalidar a assinatura. Com estrito=True, a ausencia dos campos
    tambem reprova (recibos legados nao trazem esses campos).
    """
    try:
        assinatura = base64.b64decode(recibo["assinatura"])
    except (KeyError, ValueError):
        return False
    alg = recibo.get("algoritmo")
    cid = recibo.get("chave_id")
    if estrito and (alg is None or cid is None):
        return False
    if alg is not None and alg != ALG:
        return False
    if cid is not None and cid != key_id(public_key):
        return False
    corpo = {k: v for k, v in recibo.items() if k not in ("assinatura", "chave_id", "algoritmo")}
    try:
        _sig.verify(public_key, _canon(corpo), assinatura)
        return True
    except Exception:
        return False


def cadeia(recibos, secret_key, public_key):
    """Encadeia recibos: cada um carrega o sha3 do anterior.

    Apagar ou reordenar um elo quebra a verificacao, o que a assinatura
    isolada nao detecta.
    """
    saida, anterior = [], None
    for rec in recibos:
        elo = dict(rec)
        elo["prev_sha3"] = anterior
        assinado = assinar(elo, secret_key, public_key)
        anterior = sha3_256(_canon({k: v for k, v in assinado.items()
                                    if k not in ("assinatura", "chave_id", "algoritmo")}))
        saida.append(assinado)
    return saida


def verificar_cadeia(recibos, public_key):
    """(ok, motivo). Verifica assinatura de cada elo e o encadeamento."""
    anterior = None
    for pos, rec in enumerate(recibos):
        if not verificar(rec, public_key):
            return False, f"elo {pos}: assinatura invalida"
        if rec.get("prev_sha3") != anterior:
            return False, f"elo {pos}: encadeamento quebrado"
        corpo = {k: v for k, v in rec.items() if k not in ("assinatura", "chave_id", "algoritmo")}
        anterior = sha3_256(_canon(corpo))
    return True, "cadeia integra"

def _head_de(recibo):
    """Hash do conteudo de um elo (mesma regra usada no encadeamento)."""
    corpo = {k: v for k, v in recibo.items() if k not in ("assinatura", "chave_id", "algoritmo")}
    return sha3_256(_canon(corpo))


def ancorar(recibos, secret_key, public_key):
    """Ancora externa do ultimo elo.

    Auditoria independente (08/11/2026): a cadeia detecta adulteracao, reordenacao
    e remocao de elos intermediarios, mas nao a remocao do ULTIMO recibo. A ancora
    registra (n_elos, head_sha3) assinados; quem guarda a ancora fora do repositorio
    detecta truncamento. Publicar o hash em local externo (tag, release, DOI, email
    selado) e o que fecha o buraco: a ancora sozinha, no mesmo diretorio, nao prova.
    """
    ok, motivo = verificar_cadeia(recibos, public_key)
    if not ok:
        raise ValueError(motivo)
    if not recibos:
        raise ValueError("cadeia vazia nao pode ser ancorada")
    corpo = {"tipo": "Z-QEA-ANCORA", "n_elos": len(recibos), "head_sha3": _head_de(recibos[-1])}
    return assinar(corpo, secret_key, public_key)


def verificar_ancora(recibos, ancora, public_key):
    """(ok, motivo). Detecta truncamento do fim da cadeia contra a ancora assinada."""
    if not verificar(ancora, public_key, estrito=True):
        return False, "ancora com assinatura invalida"
    if ancora.get("tipo") != "Z-QEA-ANCORA":
        return False, "ancora de tipo desconhecido"
    n = ancora.get("n_elos")
    if not isinstance(n, int) or n < 1:
        return False, "ancora sem n_elos valido"
    if len(recibos) < n:
        return False, f"truncamento: ancora cobre {n} elos, recebidos {len(recibos)}"
    if _head_de(recibos[n - 1]) != ancora.get("head_sha3"):
        return False, f"elo {n - 1}: head divergente da ancora"
    if len(recibos) > n:
        return True, f"cadeia integra e estendida ({len(recibos) - n} elos novos nao ancorados)"
    return True, "cadeia integra e identica a ancora"

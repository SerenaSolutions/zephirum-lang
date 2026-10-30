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
    return json.dumps(obj, sort_keys=True, ensure_ascii=False,
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


def verificar(recibo, public_key):
    """True apenas se a assinatura cobre exatamente o conteudo atual."""
    try:
        assinatura = base64.b64decode(recibo["assinatura"])
    except (KeyError, ValueError):
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

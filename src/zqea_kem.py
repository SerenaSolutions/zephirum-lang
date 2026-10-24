# -*- coding: utf-8 -*-
"""Z-KEM — camada 3 do Z-QEA: CONFIDENCIALIDADE pos-quantica da linguagem.

O Z-QEA protege integridade (SHA3-256) e autenticidade (ML-DSA-44, FIPS 204).
Faltava sigilo: quem nao tem a chave nao pode LER os dados de decisao da
linguagem (protecao contra vazamento). A camada 3 fecha isso com
ENCAPSULAMENTO hibrido pos-quantico:

    ML-KEM-768 (FIPS 203, Kyber)  ->  segredo compartilhado
    AES-256-GCM                    ->  cifracao autenticada do payload

Quem segura a SECRET KEY do destinatario abre o envelope; quem nao segura,
nao le nada. Tamper no envelope = REFUSED, sem vazar nada.
"""
import os
import json
import base64

from pqcrypto import ml_kem_768 as _kem
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

SPEC = "Z-KEM/1"
ALG = "ML-KEM-768 (FIPS 203) + AES-256-GCM"
REFUSED = "REFUSED"


def keypair():
    """Par de chaves do destinatario: (public_key, secret_key)."""
    return _kem.keygen()


def seal(payload, recipient_pk, sender_note=None):
    """Encapsula: cifra o payload (dict) para o dono do recipient_pk.
    Retorna envelope Z-KEM. O payload so abre com a secret key."""
    ct_kem, ss = _kem.encaps(recipient_pk)
    nonce = os.urandom(12)
    aead = AESGCM(ss)
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    sealed = aead.encrypt(nonce, body, associated_data=b"z-kem/1")
    env = {
        "spec": SPEC, "alg": ALG,
        "ciphertext_kem": base64.b64encode(ct_kem).decode(),
        "nonce": base64.b64encode(nonce).decode(),
        "sealed": base64.b64encode(sealed).decode(),
        "sender_note": sender_note,
    }
    return env


def open_(envelope, recipient_sk):
    """Abre o envelope com a secret key. Retorna (payload_dict, "1").
    Qualquer adulteracao, chave errada ou envelope antigo -> (None, REFUSED).
    Nada do conteudo vaza no erro."""
    try:
        if envelope.get("spec") != SPEC:
            return None, REFUSED
        ct_kem = base64.b64decode(envelope["ciphertext_kem"])
        ss = _kem.decaps(recipient_sk, ct_kem)
        nonce = base64.b64decode(envelope["nonce"])
        sealed = base64.b64decode(envelope["sealed"])
        aead = AESGCM(ss)
        body = aead.decrypt(nonce, sealed, associated_data=b"z-kem/1")
        return json.loads(body.decode("utf-8")), "1"
    except Exception:
        return None, REFUSED

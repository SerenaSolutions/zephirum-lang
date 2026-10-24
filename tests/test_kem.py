# -*- coding: utf-8 -*-
"""Bateria Z-KEM: confidencialidade pos-quantica (camada 3 do Z-QEA).
6 casos: roundtrip, chave errada, tamper no ciphertext KEM, tamper no
payload selado, tamper no nonce, e envelope antigo (spec)."""
import json
import copy
import base64

from zqea_kem import keypair, seal, open_, SPEC, REFUSED


def test_roundtrip():
    pk, sk = keypair()
    env = seal({"decisao": "1", "receipt_id": "abc123"}, pk, sender_note="lab")
    payload, verdict = open_(env, sk)
    assert verdict == "1"
    assert payload["decisao"] == "1"
    assert payload["receipt_id"] == "abc123"


def test_wrong_key():
    pk, _ = keypair()
    _, sk2 = keypair()
    env = seal({"segredo": "ZYQL"}, pk)
    payload, verdict = open_(env, sk2)
    assert verdict == REFUSED and payload is None


def test_tamper_kem_ciphertext():
    pk, sk = keypair()
    env = seal({"segredo": "ZYQL"}, pk)
    tampered = copy.deepcopy(env)
    ct = bytearray(base64.b64decode(tampered["ciphertext_kem"]))
    ct[0] ^= 0x01
    tampered["ciphertext_kem"] = base64.b64encode(bytes(ct)).decode()
    payload, verdict = open_(tampered, sk)
    assert verdict == REFUSED and payload is None


def test_tamper_sealed_payload():
    pk, sk = keypair()
    env = seal({"segredo": "ZYQL"}, pk)
    tampered = copy.deepcopy(env)
    s = bytearray(base64.b64decode(tampered["sealed"]))
    s[-1] ^= 0x01
    tampered["sealed"] = base64.b64encode(bytes(s)).decode()
    payload, verdict = open_(tampered, sk)
    assert verdict == REFUSED and payload is None


def test_tamper_nonce():
    pk, sk = keypair()
    env = seal({"segredo": "ZYQL"}, pk)
    tampered = copy.deepcopy(env)
    n = bytearray(base64.b64decode(tampered["nonce"]))
    n[0] ^= 0x01
    tampered["nonce"] = base64.b64encode(bytes(n)).decode()
    payload, verdict = open_(tampered, sk)
    assert verdict == REFUSED and payload is None


def test_wrong_spec():
    pk, sk = keypair()
    env = seal({"segredo": "ZYQL"}, pk)
    env["spec"] = "Z-KEM/0-old"
    payload, verdict = open_(env, sk)
    assert verdict == REFUSED and payload is None

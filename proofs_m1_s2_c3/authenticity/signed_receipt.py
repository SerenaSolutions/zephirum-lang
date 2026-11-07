#!/usr/bin/env python3
"""ZYQL — RECIBO ASSINADO (autenticidade real) + verificador independente.

Niveis de evidencia da casa, agora com o que faltava:
  1. INTEGRIDADE   — hash do conteudo (ja tinhamos)
  2. AUTENTICIDADE — assinatura Ed25519 com chave privada do emissor (NOVO)
  3. REPRODUTIBILIDADE — evidencias brutas reproduzem o numero
  4. CORRECAO      — a regra aplicada sobre a evidencia da o mesmo veredito

Distincao mantida: recibo valido NAO prova execucao segura. Assinatura prova
origem e integridade, nao a verdade do resultado.
"""
from __future__ import annotations
import json, hashlib, base64
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature


def canon(obj) -> bytes:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def sha3(obj) -> str:
    return hashlib.sha3_256(canon(obj)).hexdigest()


def keypair():
    sk = Ed25519PrivateKey.generate()
    pk = sk.public_key()
    sk_b = sk.private_bytes(serialization.Encoding.Raw, serialization.PrivateFormat.Raw,
                            serialization.NoEncryption())
    pk_b = pk.public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    return base64.b64encode(sk_b).decode(), base64.b64encode(pk_b).decode()


def sign_receipt(receipt: dict, sk_b64: str, signer_id: str) -> dict:
    """Assina o corpo (sem o campo de assinatura) e devolve copia assinada."""
    corpo = {k: v for k, v in receipt.items() if k != "_signature"}
    digest = sha3(corpo)
    sk = Ed25519PrivateKey.from_private_bytes(base64.b64decode(sk_b64))
    sig = sk.sign(canon({"hash": digest}))
    out = dict(corpo)
    out["_signature"] = {"algorithm": "Ed25519",
                         "signer_key_id": signer_id,
                         "value": base64.b64encode(sig).decode()}
    return out


def verify_receipt(receipt: dict, pk_b64: str) -> tuple[bool, str]:
    """Verifica assinatura sem conhecer o emissor: so a chave publica."""
    sig = (receipt or {}).get("_signature") or {}
    if sig.get("algorithm") != "Ed25519":
        return False, "ASSINATURA_AUSENTE"
    corpo = {k: v for k, v in receipt.items() if k != "_signature"}
    digest = sha3(corpo)
    pk = Ed25519PublicKey.from_public_bytes(base64.b64decode(pk_b64))
    try:
        pk.verify(base64.b64decode(sig["value"]), canon({"hash": digest}))
        return True, "ASSINATURA_VALIDA"
    except InvalidSignature:
        return False, "ASSINATURA_INVALIDA"


def verify_chain(receipts: list[dict], pk_b64: str) -> tuple[bool, list[str]]:
    problemas = []
    for i, r in enumerate(receipts):
        ok, motivo = verify_receipt(r, pk_b64)
        if not ok:
            problemas.append(f"[{i}] {motivo}")
        if i > 0:
            esperado = sha3({k: v for k, v in receipts[i-1].items() if k != "_signature"})
            if r.get("previous_receipt_hash") not in (None, esperado):
                problemas.append(f"[{i}] CADEIA_QUEBRADA")
    return (len(problemas) == 0), problemas

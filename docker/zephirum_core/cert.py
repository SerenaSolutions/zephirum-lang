"""Recibo: forma canonica (RFC 8785 simplificado) + SHA-256."""
import hashlib
import json


def canon(obj):
    """JSON canonico: chaves ordenadas, sem espaco, UTF-8."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(obj):
    return hashlib.sha256(canon(obj).encode("utf-8")).hexdigest()


def emitir(payload):
    """Devolve (cert, hash). O hash cobre o cert sem o proprio campo hash."""
    cert = dict(payload)
    cert.pop("hash", None)
    return {**cert, "hash": digest(cert)}


def verificar(cert, hash_informado):
    """Recalcula: nao confia em quem emitiu."""
    h = (hash_informado or "").strip().lower()
    if len(h) != 64 or any(c not in "0123456789abcdef" for c in h):
        return {"ok": False, "veredito": "REFUSED", "ref": "hash deve ter 64 hexadecimais"}
    corpo = dict(cert)
    corpo.pop("hash", None)
    recalculado = digest(corpo)
    ok = recalculado == h
    return {
        "ok": ok,
        "veredito": 1 if ok else 0,
        "hash_informado": h,
        "hash_recomputado": recalculado,
        "explicacao": "conteudo integro" if ok else "conteudo alterado ou hash de outro recibo",
    }

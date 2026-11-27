# SPDX-License-Identifier: Apache-2.0
"""Recibo e certificado estruturado (Core Hardening 1.1, frente D).

Distincao obrigatoria:
- hash (SHA3-256/SHA-256) = INTEGRIDADE do conteudo. Nao e prova matematica,
  nao e prova de autoria e nao e prova de verdade.
- certificado = {inputs, regra, versao, output, premissas, testemunha} +
  hash de integridade. So vale se um verificador INDEPENDENTE reconferir a
  regra a partir dos inputs e da testemunha.
"""
import hashlib
import json

ALGORITMOS = {"sha3_256": hashlib.sha3_256, "sha256": hashlib.sha256}
ALGORITMO_PADRAO = "sha256"  # SHA-256 por compatibilidade; SHA3-256 via RFC-001


def canon(obj):
    """JSON canonico: chaves ordenadas, sem espaco, UTF-8."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(obj, alg=ALGORITMO_PADRAO):
    h = ALGORITMOS.get(alg)
    if h is None:
        raise ValueError(f"algoritmo nao suportado: {alg}")
    return h(canon(obj).encode("utf-8")).hexdigest()


def emitir(payload, alg=ALGORITMO_PADRAO):
    """Recibo simples: devolve cert com hash de integridade (sem o campo hash)."""
    cert = dict(payload)
    cert.pop("hash", None)
    cert.setdefault("hash_alg", "SHA3-256" if alg == "sha3_256" else "SHA-256")
    return {**cert, "hash": digest(cert, alg)}


def emitir_certificado(inputs, regra, output, versao="1.0.0", premissas=None, testemunha=None):
    """Certificado estruturado: resultado calculado != prova verificada."""
    corpo = {
        "tipo": "certificado_estruturado",
        "versao": versao,
        "regra": regra,
        "inputs": inputs,
        "output": output,
        "premissas": premissas or [],
        "testemunha": testemunha,
        "prova_verificada": False,  # so o verificador independente promove
    }
    return emitir(corpo)


def _alg_do_cert(cert):
    """Normaliza 'SHA-256' / 'sha256' / 'SHA3-256' para a chave do algoritmo."""
    nome = str((cert or {}).get("hash_alg") or "SHA-256").lower().replace("-", "").replace("_", "")
    if nome.startswith("sha3"):
        return "sha3_256"
    return "sha256"


def verificar(cert, hash_informado):
    """Recalcula o hash: nao confia em quem emitiu."""
    h = (hash_informado or "").strip().lower()
    if len(h) != 64 or any(c not in "0123456789abcdef" for c in h):
        return {"ok": False, "veredito": "REFUSED", "ref": "hash deve ter 64 hexadecimais"}
    corpo = dict(cert or {})
    corpo.pop("hash", None)
    alg = _alg_do_cert(corpo)
    recalculado = digest(corpo, alg)
    ok = recalculado == h
    return {
        "ok": ok,
        "veredito": 1 if ok else 0,
        "hash_alg": alg,
        "hash_informado": h,
        "hash_recomputado": recalculado,
        "explicacao": "conteudo integro (integridade nao e prova matematica)"
        if ok else "conteudo alterado ou hash de outro recibo",
    }


def verificar_certificado(cert, regras):
    """Verificacao INDEPENDENTE: reexecuta a regra a partir dos inputs.

    regras: dict {nome_da_regra: callable(inputs) -> output}.
    Devolve veredito trivalente. REFUSED quando nao ha como conferir.
    """
    if not isinstance(cert, dict) or cert.get("tipo") != "certificado_estruturado":
        return {"veredito": "REFUSED", "ref": "nao e certificado estruturado"}
    nome = cert.get("regra")
    fn = (regras or {}).get(nome)
    if fn is None:
        return {"veredito": "REFUSED", "ref": f"sem verificador independente para a regra {nome!r}"}
    integridade = verificar(cert, cert.get("hash"))
    if not integridade["ok"]:
        return {"veredito": "REFUSED", "ref": "integridade do certificado falhou",
                "detalhe": integridade}
    try:
        recomputado = fn(cert.get("inputs"))
    except Exception as e:  # regra nao executavel com esses inputs
        return {"veredito": "REFUSED", "ref": f"verificador falhou: {str(e)[:120]}"}
    confere = recomputado == cert.get("output")
    return {
        "veredito": 1 if confere else 0,
        "recomputado": recomputado,
        "output_certificado": cert.get("output"),
        "integridade": "ok",
        "explicacao": "regra reconferida por verificador independente" if confere
        else "output do certificado nao reproduz a regra",
    }

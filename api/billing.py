# -*- coding: utf-8 -*-
"""BILLING — checkout e medição da verificacao de recibo (item 4 da oferta).

Fluxo: cliente escolhe pacote -> sessao de checkout -> pagamento confirmado por webhook
-> chave emitida com saldo de verificacoes -> cada verificacao debita 1 credito e devolve
recibo selado. Saldo insuficiente e 402, nunca verificacao de graca.

Sem provedor configurado a rota responde 503 com motivo explicito: nao se simula
pagamento recebido.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
import time
import urllib.parse
import urllib.request
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

ARQ = Path(os.environ.get("ZYQL_CREDITS_FILE", ".credits.json"))

PLANOS = {
    "verify-starter": {"creditos": 25_000, "preco_usd": 50.0, "descricao": "verificacoes avulsas"},
    "verify-growth": {"creditos": 150_000, "preco_usd": 250.0, "descricao": "operacao continua"},
    "verify-scale": {"creditos": 2_000_000, "preco_usd": 3_000.0, "descricao": "alto volume"},
}


def _h(s: str) -> str:
    return hashlib.sha3_256(s.encode()).hexdigest()


def _ler() -> dict:
    if ARQ.exists():
        try:
            return json.loads(ARQ.read_text())
        except Exception:
            pass
    return {"contas": {}, "sessoes": {}}


def _gravar(d: dict) -> None:
    ARQ.write_text(json.dumps(d, indent=1))
    try:
        ARQ.chmod(0o600)
    except Exception:
        pass


def _provedor() -> str:
    if os.environ.get("STRIPE_SECRET_KEY"):
        return "stripe"
    if os.environ.get("PADDLE_API_KEY"):
        return "paddle"
    if os.environ.get("LEMONSQUEEZY_API_KEY"):
        return "lemonsqueezy"
    return "nenhum"


def criar_sessao(plano: str, email: str, sucesso_url: str) -> dict:
    if plano not in PLANOS:
        raise HTTPException(422, f"pacote invalido: escolha entre {sorted(PLANOS)}")
    p = PLANOS[plano]
    prov = _provedor()
    if prov == "nenhum":
        raise HTTPException(503, "checkout indisponivel: nenhum provedor de pagamento configurado "
                                 "(defina STRIPE_SECRET_KEY, PADDLE_API_KEY ou LEMONSQUEEZY_API_KEY)")
    if prov == "stripe":
        dados = urllib.parse.urlencode({
            "mode": "payment",
            "success_url": sucesso_url,
            "cancel_url": sucesso_url + "?cancelado=1",
            "customer_email": email,
            "line_items[0][quantity]": 1,
            "line_items[0][price_data][currency]": "usd",
            "line_items[0][price_data][unit_amount]": int(p["preco_usd"] * 100),
            "line_items[0][price_data][product_data][name]": f"ZYQL verificacao de recibo - {plano}",
            "line_items[0][price_data][product_data][description]": f'{p["creditos"]} verificacoes',
            "metadata[plano]": plano,
            "metadata[email]": email,
        }).encode()
        req = urllib.request.Request("https://api.stripe.com/v1/checkout/sessions", data=dados,
                                     headers={"Authorization": f"Bearer {os.environ['STRIPE_SECRET_KEY']}",
                                              "Content-Type": "application/x-www-form-urlencoded"})
        try:
            with urllib.request.urlopen(req, timeout=25) as r:
                s = json.loads(r.read())
        except Exception as e:
            raise HTTPException(502, f"falha ao criar sessao no provedor: {type(e).__name__}")
        d = _ler()
        d["sessoes"][s["id"]] = {"plano": plano, "email": email, "pago": False,
                                 "criado_em": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
        _gravar(d)
        return {"provedor": "stripe", "sessao": s["id"], "url": s["url"], "preco_usd": p["preco_usd"],
                "creditos": p["creditos"]}
    raise HTTPException(503, f"provedor '{prov}' ainda nao implementado neste checkout")


def confirmar(sessao: str, email: str | None = None) -> dict:
    """Confirma o pagamento e emite a chave com saldo. Idempotente por sessao."""
    d = _ler()
    sess = d["sessoes"].get(sessao)
    if not sess:
        raise HTTPException(404, "sessao desconhecida")
    if sess.get("pago"):
        existente = sess.get("chave_emitida")
        return {"ja_emitida": True, "chave_prefixo": (existente or "")[:12] + "..."}
    plano = sess["plano"]
    chave = "ZYQL" + "".join(secrets.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789") for _ in range(44))
    d["contas"][_h(chave)] = {"email": sess.get("email") or email, "plano": plano,
                              "creditos": PLANOS[plano]["creditos"],
                              "criada_em": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                              "consumidos": 0}
    sess["pago"] = True
    sess["chave_emitida"] = chave
    sess["pago_em"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    _gravar(d)
    return {"ja_emitida": False, "chave": chave, "creditos": PLANOS[plano]["creditos"], "plano": plano}


def saldo(chave: str) -> dict:
    d = _ler()
    c = d["contas"].get(_h(chave))
    if not c:
        raise HTTPException(401, "chave desconhecida")
    return {"plano": c["plano"], "creditos_restantes": c["creditos"] - c["consumidos"],
            "consumidos": c["consumidos"]}


def debitar(chave: str, n: int = 1) -> dict:
    d = _ler()
    reg = d["contas"].get(_h(chave))
    if not reg:
        raise HTTPException(401, "chave desconhecida")
    restante = reg["creditos"] - reg["consumidos"]
    if restante < n:
        raise HTTPException(402, f"saldo insuficiente: {restante} verificacoes restantes")
    reg["consumidos"] += n
    _gravar(d)
    return {"debitado": n, "restante": reg["creditos"] - reg["consumidos"]}


router = APIRouter()


class CheckoutIn(BaseModel):
    plano: str = Field(..., description="verify-starter, verify-growth ou verify-scale")
    email: str
    sucesso_url: str = "https://serenasolutions.github.io/zephirum-lang/obrigado"


class WebhookIn(BaseModel):
    sessao: str
    email: str | None = None
    segredo: str | None = Field(None, description="exigido quando ZYQL_WEBHOOK_SECRET esta definido")


class VerifyIn(BaseModel):
    chave: str
    recibo: dict


@router.get("/planos")
def planos():
    return {"pacotes": PLANOS, "moeda": "USD",
            "nota": "verificacao avulsa a US$ 0,002; pacotes acima aplicam desconto por volume",
            "provedor_configurado": _provedor()}


@router.post("/checkout")
def checkout(req: CheckoutIn):
    return criar_sessao(req.plano, req.email, req.sucesso_url)


def _assinar(segredo: str, t: str, corpo: bytes) -> str:
    return hmac.new(segredo.encode(), t.encode() + b"." + corpo, hashlib.sha256).hexdigest()


def validar_assinatura_stripe(corpo: bytes, cabecalho: str | None, segredo: str,
                              tolerancia_s: int = 300) -> tuple[bool, str]:
    """Valida Stripe-Signature: t=<ts>,v1=<hmac>. Rejeita fora da tolerancia."""
    if not cabecalho:
        return False, "cabecalho Stripe-Signature ausente"
    partes: dict[str, list[str]] = {}
    for item in cabecalho.split(","):
        if "=" in item:
            k, v = item.split("=", 1)
            partes.setdefault(k.strip(), []).append(v.strip())
    t = (partes.get("t") or [None])[0]
    v1 = partes.get("v1") or []
    if not t or not v1:
        return False, "prefixos t e v1 obrigatorios"
    try:
        idade = abs(time.time() - float(t))
    except ValueError:
        return False, "timestamp nao numerico"
    if idade > tolerancia_s:
        return False, f"timestamp fora da tolerancia ({int(idade)}s)"
    esperado = _assinar(segredo, t, corpo)
    if not any(secrets.compare_digest(esperado, v) for v in v1):
        return False, "hmac nao confere"
    return True, "ok"


@router.post("/webhook")
async def webhook(request: Request):
    """Confirma pagamento. Sem verificacao configurada, recusa em vez de aceitar."""
    corpo = await request.body()
    seg_stripe = os.environ.get("STRIPE_WEBHOOK_SECRET")
    seg_proprio = os.environ.get("ZYQL_WEBHOOK_SECRET")
    # em producao, modo degradado nao e permitido
    if not seg_stripe and os.environ.get("ZYQL_ENV", "").lower() == "production":
        raise HTTPException(503, "producao exige STRIPE_WEBHOOK_SECRET: assinatura obrigatoria")
    if seg_stripe:
        ok, motivo = validar_assinatura_stripe(corpo, request.headers.get("Stripe-Signature"), seg_stripe)
        if not ok:
            raise HTTPException(401, f"assinatura invalida: {motivo}")
    elif seg_proprio:
        try:
            dado_ = json.loads(corpo or b"{}")
        except Exception:
            raise HTTPException(400, "corpo nao e json")
        if not secrets.compare_digest(str(dado_.get("segredo") or ""), seg_proprio):
            raise HTTPException(401, "segredo de webhook invalido")
    else:
        raise HTTPException(503, "webhook sem verificacao: configure STRIPE_WEBHOOK_SECRET")
    try:
        dado = json.loads(corpo or b"{}")
    except Exception:
        raise HTTPException(400, "corpo nao e json")
    sessao, email = dado.get("sessao"), dado.get("email")
    if str(dado.get("type", "")).startswith("checkout.session"):
        obj = (dado.get("data") or {}).get("object") or {}
        sessao = obj.get("id") or sessao
        email = ((obj.get("customer_details") or {}).get("email")) or email
    if not sessao:
        raise HTTPException(422, "sessao ausente no evento")
    r = confirmar(sessao, email)
    if not r.get("ja_emitida"):
        r["aviso"] = "guarde a chave: ela nao e exibida novamente"
    return r


@router.get("/saldo")
def consultar_saldo(chave: str):
    return saldo(chave)


@router.post("/verificar")
def verificar(req: VerifyIn):
    """Verifica um recibo e debita um credito. A conta e feita no servidor."""
    d = _ler()
    sess = d["contas"].get(_h(req.chave))
    if not sess:
        raise HTTPException(401, "chave desconhecida")
    corpo = {k: v for k, v in req.recibo.items() if k != "selo_sha3_256"}
    selo_calc = hashlib.sha3_256(json.dumps(corpo, sort_keys=True, ensure_ascii=True,
                                            default=str).encode()).hexdigest()
    integro = selo_calc == req.recibo.get("selo_sha3_256")
    cobranca = debitar(req.chave, 1)
    return {"integro": integro, "selo_informado": req.recibo.get("selo_sha3_256"),
            "selo_calculado": selo_calc, "creditos_restantes": cobranca["restante"],
            "verificado_em": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}

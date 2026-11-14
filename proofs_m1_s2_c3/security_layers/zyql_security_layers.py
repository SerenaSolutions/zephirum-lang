#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Serena Quantum Solutions
"""ZYQL — CAMADAS DE CIBERSEGURANCA (L1..L7) para a linguagem e para os apps.

Regra da casa: cada camada tem codigo, teste e limite declarado. Camada sem
teste e' intencao, nao controle.

L1 ENTRADA       validacao, limite de tamanho, tipo, caracteres de controle
L2 AUTENTICIDADE assinatura verificada em toda fronteira (Ed25519)
L3 AUTORIZACAO   politica nega por padrao (S2 policy gate)
L4 CONFIDENCIAL  redacao de segredos em logs e mensagens de erro
L5 INTEGRIDADE   hash chain e recibo assinado
L6 DISPONIBIL   limite de taxa, timeout, teto de concorrencia
L7 SUPERFICIE    bind local, sem rede externa, cabecalhos de seguranca, zero dependencia
"""
from __future__ import annotations
import json, re, time
from collections import deque

MAX_INPUT = 64 * 1024
CTRL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")
SEGREDOS = re.compile(
    r"(?i)(api[_-]?key|token|secret|password|senha|authorization|bearer)"
    r"[\"'\s:=]+([A-Za-z0-9_\-\.\/+]{8,})")


class RecusaDeSeguranca(ValueError):
    """Recusa explicita: a camada barrou. Nunca silencio."""


# ---------------- L1 ENTRADA ----------------
def validar_entrada(dados, maximo=MAX_INPUT):
    if isinstance(dados, str):
        bruto = dados.encode()
    elif isinstance(dados, (bytes, bytearray)):
        bruto = bytes(dados)
    else:
        raise RecusaDeSeguranca("L1_TIPO_INVALIDO")
    if len(bruto) > maximo:
        raise RecusaDeSeguranca("L1_TAMANHO_EXCEDIDO")
    txt = bruto.decode("utf-8", errors="strict")
    if CTRL.search(txt):
        raise RecusaDeSeguranca("L1_CARACTERE_DE_CONTROLE")
    return txt


def json_seguro(bruto, maximo=MAX_INPUT):
    """Le JSON sem executar nada, com profundidade limitada."""
    txt = validar_entrada(bruto, maximo)
    if txt.count("{") + txt.count("[") > 500:
        raise RecusaDeSeguranca("L1_PROFUNDIDADE_EXCEDIDA")
    try:
        return json.loads(txt)
    except json.JSONDecodeError:
        raise RecusaDeSeguranca("L1_JSON_INVALIDO")


# ---------------- L4 CONFIDENCIALIDADE ----------------
def redigir(valor):
    """Remove segredos de qualquer texto antes de log/erro."""
    if not isinstance(valor, str):
        valor = json.dumps(valor, ensure_ascii=False, default=str) if not isinstance(valor, (int, float)) else str(valor)
    return SEGREDOS.sub(lambda m: f"{m.group(1)}=[REDIGIDO]", valor)


def log_seguro(evento: dict) -> dict:
    """Todo evento de log passa por aqui: nada de chave em claro."""
    return {k: (redigir(v) if isinstance(v, str) else v) for k, v in evento.items()}


# ---------------- L6 DISPONIBILIDADE ----------------
class LimiteDeTaxa:
    """Janela deslizante simples, sem dependencia externa."""
    def __init__(self, maximo: int = 60, janela_s: float = 60.0):
        if maximo < 1 or janela_s <= 0:
            raise RecusaDeSeguranca("L6_CONFIG_INVALIDA")
        self.maximo, self.janela = maximo, janela_s
        self._hits = deque()

    def permitir(self, agora=None) -> bool:
        agora = time.monotonic() if agora is None else agora
        while self._hits and agora - self._hits[0] > self.janela:
            self._hits.popleft()
        if len(self._hits) >= self.maximo:
            return False
        self._hits.append(agora)
        return True


# ---------------- L7 SUPERFICIE ----------------
CABECALHOS = {
    "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'",
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "no-referrer",
    "Permissions-Policy": "geolocation=(), camera=(), microphone=()",
    "Cache-Control": "no-store",
}


def cabecalhos_de_seguranca() -> dict:
    return dict(CABECALHOS)


def bind_seguro(host: str) -> str:
    """So loopback por padrao. Expor na rede exige decisao explicita."""
    if host not in ("127.0.0.1", "localhost", "::1"):
        raise RecusaDeSeguranca("L7_BIND_EXTERNO_NEGADO")
    return host


def politica_de_dependencias(deps) -> list:
    """Zero dependencia e' a politica. Qualquer item e' recusado ate revisao."""
    if deps:
        raise RecusaDeSeguranca(f"L7_DEPENDENCIA_NAO_REVISADA:{len(deps)}")
    return []


MAPA = {
    "L1_entrada": "validar_entrada / json_seguro",
    "L2_autenticidade": "signed_receipt.verify_receipt (Ed25519)",
    "L3_autorizacao": "policy_gate.PolicyGate (nega por padrao)",
    "L4_confidencialidade": "redigir / log_seguro",
    "L5_integridade": "sha3 chain + recibo assinado",
    "L6_disponibilidade": "LimiteDeTaxa + timeout",
    "L7_superficie": "cabecalhos_de_seguranca / bind_seguro / politica_de_dependencias",
}

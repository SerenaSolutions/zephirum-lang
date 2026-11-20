# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Serena Quantum Solutions
"""Curated public facts and safe, allow-listed ZYQL API calls for the chat."""
from __future__ import annotations

import json
import os
import re
from urllib.parse import urlparse
from urllib.request import Request, urlopen

CHAT_CONTEXT = """Você é o assistente oficial de documentação do ZEPHIRUM/ZYQL. Responda em português (ou no idioma do usuário), de forma clara e cite fontes com links Markdown quando relevantes. Use os fatos abaixo como contexto de projeto e não invente capacidades.

Fatos canônicos: ZEPHIRUM é a linguagem e ZYQL seu núcleo de decisões trivalentes: 1, 0 e REFUSED. REFUSED indica evidência insuficiente. O pacote oficial é zephirum; o repositório oficial é https://github.com/SerenaSolutions/zephirum-lang; licença Apache-2.0. SHA3-256 prova integridade, não autoria. O projeto não possui certificação FIPS/CAVP/CMVP nem validação independente completa. ZEPHIRUM não substitui nem embrulha Qiskit. Hardware só pode ser declarado quando houver evidência/recibo correspondente; não confunda simulação com hardware. Os registros técnicos publicados são experimentais e alegações devem ser limitadas ao que código, recibos e testes sustentam.

Fontes públicas canônicas:
- Fatos e correções: https://github.com/SerenaSolutions/zephirum-lang/blob/main/docs/FACTS.md
- Escopo e limitações: https://github.com/SerenaSolutions/zephirum-lang/blob/main/README.md#known-limitations
- Especificação de recibos: https://github.com/SerenaSolutions/zephirum-lang/blob/main/docs/receipts.md
- Código e exemplos: https://github.com/SerenaSolutions/zephirum-lang

Ferramentas: só chame zyql_decide ou zyql_bound quando o usuário pedir explicitamente uma execução/cálculo. Explique que resultados são da API configurada e de simulação, não validação científica nem hardware. Não solicite nem mostre segredos. Nunca prometa que uma resposta de IA é uma decisão ZYQL. Não afirme que verificou um documento completo quando só recebeu o contexto resumido."""

MAX_MESSAGES = 12
MAX_MESSAGE_CHARS = 4_000


def validate_messages(messages: object) -> list[dict[str, str]]:
    if not isinstance(messages, list) or not messages or len(messages) > MAX_MESSAGES:
        raise ValueError("Envie entre 1 e 12 mensagens de conversa.")
    clean: list[dict[str, str]] = []
    for item in messages:
        if not isinstance(item, dict) or item.get("role") not in ("user", "assistant"):
            raise ValueError("Formato de conversa inválido.")
        content = item.get("content")
        if not isinstance(content, str) or not content.strip() or len(content) > MAX_MESSAGE_CHARS:
            raise ValueError("Cada mensagem deve ter texto de até 4.000 caracteres.")
        clean.append({"role": item["role"], "content": content.strip()})
    if clean[-1]["role"] != "user":
        raise ValueError("A última mensagem deve ser do usuário.")
    return clean


def _api_base() -> str:
    value = os.environ.get("ZYQL_API_URL", "").strip().rstrip("/")
    parsed = urlparse(value)
    if parsed.scheme not in ("https", "http") or not parsed.netloc or parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError("Configure ZYQL_API_URL como URL base segura da API ZYQL.")
    if parsed.scheme != "https" and parsed.hostname not in ("localhost", "127.0.0.1"):
        raise ValueError("ZYQL_API_URL deve usar HTTPS fora do ambiente local.")
    return value


def _post_zyql(path: str, body: dict) -> dict:
    base = _api_base()
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    token = os.environ.get("ZYQL_API_KEY", "").strip()
    if token:
        headers["X-API-Key"] = token
    req = Request(base + path, data=json.dumps(body).encode("utf-8"), headers=headers, method="POST")
    with urlopen(req, timeout=20) as response:
        raw = response.read(100_001)
    if len(raw) > 100_000:
        raise ValueError("Resposta da API ZYQL acima do limite.")
    result = json.loads(raw)
    return result if isinstance(result, dict) else {"result": result}


def execute_zyql_tool(name: str, args: object) -> dict:
    """Run only the two safe, simulation-only API operations exposed as tools."""
    if not isinstance(args, dict):
        raise ValueError("Argumentos da ferramenta devem ser um objeto JSON.")
    if name == "zyql_decide":
        allowed = {"oracle", "n", "shots", "epsilon", "family", "seed"}
        if set(args) - allowed:
            raise ValueError("Parâmetros não permitidos para decisão.")
        oracle = args.get("oracle", "const1")
        n = args.get("n", 3)
        shots = args.get("shots", 2048)
        epsilon = args.get("epsilon", 0.05)
        family = args.get("family", 1)
        seed = args.get("seed", 1701)
        if oracle not in ("const1", "const0", "parity"):
            raise ValueError("Oracle deve ser const1, const0 ou parity.")
        if type(n) is not int or not 1 <= n <= 8:
            raise ValueError("n deve ser inteiro entre 1 e 8.")
        if type(shots) is not int or not 1 <= shots <= 100000:
            raise ValueError("shots deve ser inteiro entre 1 e 100000.")
        if type(epsilon) not in (float, int) or not 0 < epsilon < 0.5:
            raise ValueError("epsilon deve estar entre 0 e 0.5.")
        if type(family) is not int or not 1 <= family <= 1000 or type(seed) is not int:
            raise ValueError("family ou seed inválidos.")
        payload = {"oracle": oracle, "n": n, "shots": shots, "epsilon": epsilon,
                   "family": family, "seed": seed, "hardware": False, "sign": False}
        return _post_zyql("/decide", payload)
    if name == "zyql_bound":
        allowed = {"epsilon", "shots", "margin", "family"}
        if set(args) - allowed:
            raise ValueError("Parâmetros não permitidos para banda.")
        epsilon = args.get("epsilon", 0.05)
        shots = args.get("shots")
        margin = args.get("margin")
        family = args.get("family", 1)
        if type(epsilon) not in (float, int) or not 0 < epsilon < 0.5:
            raise ValueError("epsilon deve estar entre 0 e 0.5.")
        if shots is not None and (type(shots) is not int or not 1 <= shots <= 100000):
            raise ValueError("shots deve ser null ou inteiro de 1 a 100000.")
        if margin is not None and (type(margin) not in (float, int) or not 0 < margin < 0.5):
            raise ValueError("margin deve ser null ou estar entre 0 e 0.5.")
        if type(family) is not int or not 1 <= family <= 1000:
            raise ValueError("family deve ser inteiro de 1 a 1000.")
        return _post_zyql("/bound", {"epsilon": epsilon, "shots": shots, "margin": margin, "family": family})
    raise ValueError("Ferramenta desconhecida.")

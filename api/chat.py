# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Serena Quantum Solutions
"""Serverless ZEPHIRUM chat endpoint for Vercel.

Requires OPENAI_API_KEY. Optional ZYQL_API_URL and ZYQL_API_KEY enable the
allow-listed, simulation-only ZYQL tools. Conversation history stays in the
visitor's browser; request bodies are not persisted by this function.
"""
from __future__ import annotations

import json
import os
import time
from collections import defaultdict, deque
from http.server import BaseHTTPRequestHandler
from threading import Lock
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from zyql_chat import CHAT_CONTEXT, execute_zyql_tool, validate_messages

OPENAI_URL = "https://api.openai.com/v1/responses"
MAX_BODY = 20_000
MAX_OUTPUT_TOKENS = 700
MAX_TOOL_ROUNDS = 2
RATE_LIMIT = 12
RATE_WINDOW = 60
_rate_lock = Lock()
_rate = defaultdict(deque)


def _take_rate_slot(ip: str, now: float | None = None) -> bool:
    """Best-effort per-instance rate limit; configure provider-level limits too."""
    now = time.time() if now is None else now
    with _rate_lock:
        slots = _rate[ip]
        while slots and slots[0] <= now - RATE_WINDOW:
            slots.popleft()
        if len(slots) >= RATE_LIMIT:
            return False
        slots.append(now)
        return True


def _response_text(payload: dict) -> str:
    chunks = []
    for item in payload.get("output", []):
        if item.get("type") == "message":
            for part in item.get("content", []):
                if part.get("type") == "output_text" and isinstance(part.get("text"), str):
                    chunks.append(part["text"])
    return "\n".join(chunks).strip()


def _function_calls(payload: dict) -> list[dict]:
    return [item for item in payload.get("output", []) if item.get("type") == "function_call"]


def _zyql_tools() -> list[dict]:
    if not os.environ.get("ZYQL_API_URL", "").strip():
        return []
    return [
        {
            "type": "function", "name": "zyql_decide",
            "description": "Executa uma decisão ZYQL na API configurada, somente em simulação. Nunca usa QPU nem assina recibos.",
            "parameters": {
                "type": "object", "properties": {
                    "oracle": {"type": "string", "enum": ["const1", "const0", "parity"]},
                    "n": {"type": "integer", "minimum": 1, "maximum": 8},
                    "shots": {"type": "integer", "minimum": 1, "maximum": 100000},
                    "epsilon": {"type": "number", "exclusiveMinimum": 0, "exclusiveMaximum": 0.5},
                    "family": {"type": "integer", "minimum": 1, "maximum": 1000},
                    "seed": {"type": "integer"}
                }, "additionalProperties": False
            }, "strict": True
        },
        {
            "type": "function", "name": "zyql_bound",
            "description": "Calcula a banda estatística declarada pela API ZYQL; não é execução em hardware.",
            "parameters": {
                "type": "object", "properties": {
                    "epsilon": {"type": "number", "exclusiveMinimum": 0, "exclusiveMaximum": 0.5},
                    "shots": {"type": ["integer", "null"], "minimum": 1, "maximum": 100000},
                    "margin": {"type": ["number", "null"], "exclusiveMinimum": 0, "exclusiveMaximum": 0.5},
                    "family": {"type": "integer", "minimum": 1, "maximum": 1000}
                }, "additionalProperties": False
            }, "strict": True
        }
    ]


def _openai_request(body: dict) -> dict:
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key:
        raise RuntimeError("Chat temporariamente indisponível: falta configurar OPENAI_API_KEY no ambiente do deploy.")
    request = Request(
        OPENAI_URL,
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request, timeout=35) as response:
        data = response.read(1_000_001)
    if len(data) > 1_000_000:
        raise RuntimeError("Resposta do provedor excedeu o limite permitido.")
    return json.loads(data)


class handler(BaseHTTPRequestHandler):
    def _send(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Allow", "POST, OPTIONS")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_GET(self) -> None:
        self._send(405, {"error": "Use POST."})

    def do_POST(self) -> None:
        origin = self.headers.get("Origin")
        allowed = {item.strip().rstrip("/") for item in os.environ.get("CHAT_ALLOWED_ORIGINS", "").split(",") if item.strip()}
        if origin and allowed and origin.rstrip("/") not in allowed:
            self._send(403, {"error": "Origem não permitida."})
            return
        if origin and not allowed:
            parsed = urlparse(origin)
            host = self.headers.get("Host", "").split(":", 1)[0].lower()
            if parsed.hostname and parsed.hostname.lower() != host:
                self._send(403, {"error": "Origem não permitida. Configure CHAT_ALLOWED_ORIGINS no deploy."})
                return
        ip = self.headers.get("x-forwarded-for", "").split(",", 1)[0].strip() or self.client_address[0]
        if not _take_rate_slot(ip):
            self._send(429, {"error": "Muitas solicitações. Aguarde um minuto e tente novamente."})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            length = 0
        if length <= 0 or length > MAX_BODY:
            self._send(413 if length > MAX_BODY else 400, {"error": "Corpo inválido ou acima do limite de 20 KB."})
            return
        try:
            data = json.loads(self.rfile.read(length))
            messages = validate_messages(data.get("messages"))
            model = os.environ.get("OPENAI_MODEL", "gpt-4.1-mini").strip()
            if not model or len(model) > 100:
                raise ValueError("OPENAI_MODEL inválido.")
            tools = _zyql_tools()
            request_body = {
                "model": model,
                "instructions": CHAT_CONTEXT,
                "input": messages,
                "max_output_tokens": MAX_OUTPUT_TOKENS,
                "store": False,
            }
            if tools:
                request_body["tools"] = tools
                request_body["tool_choice"] = "auto"
            result = _openai_request(request_body)
            for _ in range(MAX_TOOL_ROUNDS):
                calls = _function_calls(result)
                if not calls:
                    break
                outputs = []
                for call in calls[:2]:
                    try:
                        args = json.loads(call.get("arguments", "{}"))
                        output = execute_zyql_tool(call.get("name", ""), args)
                    except (ValueError, TypeError) as exc:
                        output = {"error": str(exc)}
                    outputs.append({"type": "function_call_output", "call_id": call.get("call_id", ""), "output": json.dumps(output, ensure_ascii=False)})
                request_body["input"] = messages + result.get("output", []) + outputs
                result = _openai_request(request_body)
            text = _response_text(result)
            if not text:
                text = "Não consegui produzir uma resposta. Tente reformular a pergunta."
            self._send(200, {"reply": text, "model": model})
        except (json.JSONDecodeError, UnicodeDecodeError, ValueError) as exc:
            self._send(400, {"error": str(exc) or "JSON inválido."})
        except HTTPError as exc:
            if exc.code in (401, 403):
                message = "Falha de autenticação do provedor. Verifique OPENAI_API_KEY no deploy."
            elif exc.code == 429:
                message = "Limite de uso do provedor atingido. Tente novamente mais tarde."
            else:
                message = f"O provedor de IA respondeu com erro HTTP {exc.code}."
            self._send(502, {"error": message})
        except (URLError, TimeoutError):
            self._send(504, {"error": "Tempo limite ao consultar o provedor. Tente novamente."})
        except RuntimeError as exc:
            self._send(503, {"error": str(exc)})
        except Exception:
            self._send(500, {"error": "Erro interno no chat. Nenhum detalhe sensível foi registrado."})

    def log_message(self, *_args) -> None:
        # Do not log prompts, IPs, API payloads, or provider responses.
        pass

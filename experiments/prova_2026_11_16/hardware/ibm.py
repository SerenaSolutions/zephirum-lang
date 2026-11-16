"""Acesso ao hardware real da IBM (IBM Quantum Platform, API v1).

A autenticacao vai por curl porque o Cloudflare bloqueia a assinatura TLS do urllib
(erro 1010). O token nunca e impresso.
"""
from __future__ import annotations

import json
import os
import subprocess

BASE = "https://quantum.cloud.ibm.com/api/v1"
CRN = os.environ.get(
    "IBM_CRN",
    "crn:v1:bluemix:public:quantum-computing:us-east:"
    "a/95c41207c62e44b4836797c50afa51b8:52de7392-9adb-443b-9b46-ea0b88a0145f::",
)
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0 Safari/537.36")

_cache: dict[str, str] = {}


def token() -> str:
    if "t" in _cache:
        return _cache["t"]
    chave = os.environ.get("IBM_API_KEY") or os.environ.get("IBM_QUANTUM_TOKEN")
    if not chave:
        raise RuntimeError("IBM_API_KEY ausente no ambiente")
    saida = subprocess.run(
        ["curl", "-s", "-X", "POST", "https://iam.cloud.ibm.com/identity/token",
         "-H", "content-type: application/x-www-form-urlencoded",
         "--data-urlencode", "grant_type=urn:ibm:params:oauth:grant-type:apikey",
         "--data-urlencode", f"apikey={chave}",
         "--data-urlencode", "response_type=cloud_iam"],
        capture_output=True, text=True, timeout=60)
    dados = json.loads(saida.stdout or "{}")
    if "access_token" not in dados:
        raise RuntimeError(f"IAM recusou: {str(dados)[:120]}")
    _cache["t"] = dados["access_token"]
    return _cache["t"]


def chamar(metodo: str, caminho: str, corpo: dict | None = None, timeout: int = 60) -> tuple[int, dict]:
    args = ["curl", "-s", "-w", "\n%{http_code}", "-m", str(timeout), "-X", metodo,
            f"{BASE}{caminho}",
            "-H", f"Authorization: Bearer {token()}",
            "-H", f"Service-CRN: {CRN}",
            "-H", "IBM-API-Version: 2025-05-01",
            "-H", "Accept: application/json",
            "-H", f"User-Agent: {UA}"]
    if corpo is not None:
        args += ["-H", "content-type: application/json", "-d", json.dumps(corpo)]
    saida = subprocess.run(args, capture_output=True, text=True, timeout=timeout + 15)
    texto = saida.stdout.rsplit("\n", 1)
    corpo_txt = texto[0] if len(texto) == 2 else ""
    codigo = int(texto[1]) if len(texto) == 2 and texto[1].strip().isdigit() else 0
    try:
        return codigo, json.loads(corpo_txt or "{}")
    except json.JSONDecodeError:
        return codigo, {"bruto": corpo_txt[:400]}


def dispositivos() -> list[dict]:
    codigo, dados = chamar("GET", "/backends")
    if codigo != 200:
        raise RuntimeError(f"listagem falhou: {codigo} {str(dados)[:160]}")
    return dados.get("devices", [])

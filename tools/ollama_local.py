"""Inferencia local contra um servidor Ollama em 127.0.0.1:11434.

Usado pelo workflow ollama-lab. Nao consome API paga: o modelo roda no proprio
runner. Gera recibo de integridade SHA3-256 do prompt e da resposta.
"""
from __future__ import annotations

import hashlib
import json
import os
import platform
import sys
import time
import urllib.request

PROMPT = "/tmp/prompt.txt"
RESPOSTA = "/tmp/resposta.txt"
RECIBO = "/tmp/recibo_ollama.json"
ENDPOINT = "http://127.0.0.1:11434/api/generate"


def sha3(caminho: str) -> str:
    h = hashlib.sha3_256()
    with open(caminho, "rb") as f:
        for bloco in iter(lambda: f.read(65536), b""):
            h.update(bloco)
    return h.hexdigest()


def main() -> int:
    modelo = os.environ.get("MODELO", "").strip()
    if not modelo:
        print("erro: variavel MODELO nao definida", file=sys.stderr)
        return 2

    prompt = open(PROMPT, encoding="utf-8").read()
    corpo = json.dumps(
        {"model": modelo, "prompt": prompt, "stream": False, "options": {"num_predict": 320}}
    ).encode("utf-8")
    req = urllib.request.Request(
        ENDPOINT, data=corpo, headers={"Content-Type": "application/json"}
    )

    t0 = time.time()
    with urllib.request.urlopen(req, timeout=900) as r:
        dados = json.loads(r.read())
    dt = time.time() - t0

    texto = (dados.get("response") or "").strip()
    open(RESPOSTA, "w", encoding="utf-8").write(texto + "\n")

    tokens = dados.get("eval_count") or 0
    print(f"modelo: {modelo} | tempo total: {dt:.1f}s")
    print(f"tokens gerados: {tokens} | {tokens / dt:.1f} tokens/s (CPU do runner)")

    recibo = {
        "tipo": "recibo-integridade-sha3",
        "origem": "ollama local no runner",
        "modelo": modelo,
        "sha3_256_prompt": sha3(PROMPT),
        "sha3_256_resposta": sha3(RESPOSTA),
        "commit": os.environ.get("GITHUB_SHA"),
        "run_id": os.environ.get("GITHUB_RUN_ID"),
        "tokens_gerados": tokens,
        "custo_api": "0 (inferencia local)",
        "python": platform.python_version(),
    }
    json.dump(recibo, open(RECIBO, "w", encoding="utf-8"), indent=1)
    print(json.dumps(recibo, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

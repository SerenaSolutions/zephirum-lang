#!/usr/bin/env python3
"""Guarda de pureza: a linguagem nao carrega cobranca, chave de API nem CORS.

Motivo: revisor de linguagem nao deve auditar Stripe. Se este checador falhar,
o codigo comercial entrou no repositorio errado.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
PROIBIDOS = {
    "stripe": r"\bstripe\b",
    "cobranca": r"\bbilling\b",
    "chave de api": r"x-api-key",
    "cors": r"cors_origins|corsmiddleware",
    "creditos pagos": r"credit_balance|plandef|plan_id",
}
IGNORAR = {"tools/check_language_purity.py", "tools/check_compliance.py"}
EXT = {".py", ".js", ".ts", ".toml", ".yml", ".yaml"}


def main() -> int:
    # Escopo: o que a instalacao leva. Teste de desenvolvimento nao e pacote.
    alvos = [f for f in (RAIZ / "src").rglob("*") if f.suffix in EXT]
    alvos += [f for f in RAIZ.glob("*.py")]
    alvos += [RAIZ / "pyproject.toml"]
    achados = []
    for f in alvos:
        if not f.is_file():
            continue
        rel = f.relative_to(RAIZ).as_posix()
        if rel in IGNORAR:
            continue
        try:
            texto = f.read_text(errors="ignore").lower()
        except Exception:
            continue
        for nome, padrao in PROIBIDOS.items():
            for m in re.finditer(padrao, texto):
                linha = texto[: m.start()].count("\n") + 1
                achados.append(f"{rel}:{linha}: {nome}")
    if achados:
        print("IMPUREZA: camada comercial dentro da linguagem")
        for a in achados[:20]:
            print("  " + a)
        return 1
    print(f"linguagem pura: nenhum termo comercial em {len(EXT)} tipos de arquivo")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

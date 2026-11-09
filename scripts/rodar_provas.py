#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Roda as provas em formato de script, uma por processo.

Sao os arquivos que o pytest nao coleta porque encerram no import. Aqui eles
executam de verdade, e o codigo de saida de cada um e o veredito.
"""
from __future__ import annotations

import os
import pathlib
import subprocess
import sys

RAIZ = pathlib.Path(__file__).resolve().parents[1]


def encerra_no_import(caminho: pathlib.Path) -> bool:
    import ast
    try:
        arvore = ast.parse(caminho.read_text(encoding="utf-8", errors="ignore"))
    except SyntaxError:
        return False
    for no in arvore.body:
        for sub in ast.walk(no):
            if isinstance(sub, ast.Call) and getattr(sub.func, "attr", getattr(sub.func, "id", "")) in ("exit", "_exit"):
                return True
    return False


def main() -> int:
    provas = [p for p in sorted(RAIZ.rglob("test_*.py"))
              if ".git" not in p.parts and encerra_no_import(p)]
    ambiente = dict(os.environ, PYTHONPATH=str(RAIZ / "src"), PYTHONDONTWRITEBYTECODE="1")
    falhas = []
    for prova in provas:
        r = subprocess.run([sys.executable, str(prova)], cwd=RAIZ, env=ambiente,
                           capture_output=True, text=True, timeout=900)
        marca = "PASS" if r.returncode == 0 else "FAIL"
        print(f"[{marca}] {prova.relative_to(RAIZ)}")
        if r.returncode != 0:
            falhas.append(prova)
            print((r.stdout or "")[-600:])
            print((r.stderr or "")[-600:])
    print(f"\n{len(provas) - len(falhas)}/{len(provas)} provas passaram")
    return 1 if falhas else 0


if __name__ == "__main__":
    raise SystemExit(main())

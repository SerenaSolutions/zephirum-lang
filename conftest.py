# SPDX-License-Identifier: Apache-2.0
"""Regras de coleta da suite.

Parte das evidencias do projeto foram escritas como script: roda as checagens e
encerra com sys.exit(0 ou 1). Isso e um bom formato de prova e um formato
invalido de teste, porque o exit no import aborta a coleta inteira do pytest e
derruba junto os 210 testes que estao em ordem.

Regra aqui: arquivo que encerra no import nao e coletado como teste. Ele continua
sendo executado como script por `python scripts/rodar_provas.py`, que roda no CI.
Nada deixa de ser verificado: muda o executor, nao a exigencia.
"""
from __future__ import annotations

import ast
import pathlib


def encerra_no_import(caminho: pathlib.Path) -> bool:
    try:
        arvore = ast.parse(caminho.read_text(encoding="utf-8", errors="ignore"))
    except SyntaxError:
        return False
    for no in arvore.body:
        for sub in ast.walk(no):
            if isinstance(sub, ast.Call) and getattr(sub.func, "attr", getattr(sub.func, "id", "")) in ("exit", "_exit"):
                if getattr(sub.func, "value", None) is not None or getattr(sub.func, "id", "") == "exit":
                    return True
    return False


def pytest_ignore_collect(collection_path, config):  # noqa: ARG001
    caminho = pathlib.Path(str(collection_path))
    if caminho.suffix != ".py" or not caminho.name.startswith("test_"):
        return None
    return True if encerra_no_import(caminho) else None

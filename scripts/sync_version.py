#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Serena Quantum Solutions
"""Sincroniza README e CHANGELOG com a versao do pyproject.toml.

O `pyproject.toml` e a fonte unica. Este script remove a possibilidade de divergencia
manual: ele le a versao, atualiza o badge do README e garante que o CHANGELOG abra na
mesma versao.

    python scripts/sync_version.py            # aplica
    python scripts/sync_version.py --check    # so verifica, sai 1 se divergir
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PYPROJECT = RAIZ / "pyproject.toml"
README = RAIZ / "README.md"
CHANGELOG = RAIZ / "CHANGELOG.md"
OPENAPI = RAIZ / "docs" / "openapi.json"
SERVIDOR = RAIZ / "api" / "server.py"


def versao() -> str:
    texto = PYPROJECT.read_text(encoding="utf-8")
    achado = re.search(r'^version\s*=\s*"([^"]+)"', texto, re.MULTILINE)
    if not achado:
        raise SystemExit("pyproject.toml sem campo version")
    return achado.group(1)


def sincronizar(v: str, aplicar: bool = True) -> list[str]:
    mudancas: list[str] = []

    readme = README.read_text(encoding="utf-8")
    novo = re.sub(r"badge/version-\d+\.\d+\.\d+", f"badge/version-{v}", readme)
    if novo != readme:
        mudancas.append(f"README: badge -> {v}")
        if aplicar:
            README.write_text(novo, encoding="utf-8")

    changelog = CHANGELOG.read_text(encoding="utf-8")
    achado = re.search(r"^##\s*\[(\d+\.\d+\.\d+)\]", changelog, re.MULTILINE)
    if not achado or achado.group(1) != v:
        atual = achado.group(1) if achado else "nenhuma"
        mudancas.append(f"CHANGELOG: abre em {atual}, pyproject diz {v}")
        if aplicar and not achado:
            CHANGELOG.write_text(f"## [{v}] - pendente de notas\n\n" + changelog, encoding="utf-8")

    # O guard tools/check_compliance.py confere estas duas fontes alem do badge.
    # Deixa-las de fora foi o que manteve o main vermelho depois do release 2.5.9.
    if OPENAPI.exists():
        openapi = OPENAPI.read_text(encoding="utf-8")
        novo = re.sub(r'("version"\s*:\s*")\d+\.\d+\.\d+(")',
                      rf"\g<1>{v}\g<2>", openapi, count=1)
        if novo != openapi:
            mudancas.append(f"docs/openapi.json: info.version -> {v}")
            if aplicar:
                OPENAPI.write_text(novo, encoding="utf-8")

    if SERVIDOR.exists():
        servidor = SERVIDOR.read_text(encoding="utf-8")
        novo = re.sub(r'^APP_VERSION\s*=\s*"\d+\.\d+\.\d+"',
                      f'APP_VERSION = "{v}"', servidor, count=1, flags=re.MULTILINE)
        if novo != servidor:
            mudancas.append(f"api/server.py: APP_VERSION -> {v}")
            if aplicar:
                SERVIDOR.write_text(novo, encoding="utf-8")

    return mudancas


def main(argv: list[str]) -> int:
    v = versao()
    aplicar = "--check" not in argv
    mudancas = sincronizar(v, aplicar)
    if not mudancas:
        print(f"versao {v} consistente em pyproject, README, CHANGELOG, openapi e APP_VERSION")
        return 0
    for m in mudancas:
        print(("- " if aplicar else "DIVERGENTE: ") + m)
    if not aplicar:
        print("rode sem --check para corrigir")
        return 1
    print(f"versao {v} propagada")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

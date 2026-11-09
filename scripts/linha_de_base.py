#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Linha de base mensuravel do projeto: escreve docs/LINHA_DE_BASE.md.

Mede o que existe hoje, sem prometer adocao. Fontes publicas, nenhuma credencial:
GitHub (estrelas, forks, issues abertas, observadores) e pypistats (downloads).

Uso:
    python3 scripts/linha_de_base.py            # mede e grava
    python3 scripts/linha_de_base.py --ler      # mostra o ultimo registro
"""
from __future__ import annotations

import datetime
import json
import pathlib
import sys
import urllib.request

RAIZ = pathlib.Path(__file__).resolve().parents[1]
ARQ = RAIZ / "docs/LINHA_DE_BASE.md"
REPO = "SerenaSolutions/zephirum-lang"
PACOTE = "zephirum"


def _ler_json(url: str) -> dict:
    pedido = urllib.request.Request(url, headers={"User-Agent": "zephirum-baseline"})
    with urllib.request.urlopen(pedido, timeout=25) as r:
        return json.loads(r.read())


def medir() -> dict:
    repo = _ler_json(f"https://api.github.com/repos/{REPO}")
    try:
        dl = _ler_json(f"https://pypistats.org/api/packages/{PACOTE}/recent")["data"]
    except Exception:  # noqa: BLE001 o servico cai sem avisar
        dl = {"last_day": None, "last_week": None, "last_month": None}
    return {
        "data": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d"),
        "estrelas": repo.get("stargazers_count"),
        "forks": repo.get("forks_count"),
        "observadores": repo.get("subscribers_count"),
        "issues_abertas": repo.get("open_issues_count"),
        "downloads_dia": dl.get("last_day"),
        "downloads_semana": dl.get("last_week"),
        "downloads_mes": dl.get("last_month"),
    }


def gravar(m: dict) -> None:
    linha = (f"| {m['data']} | {m['estrelas']} | {m['forks']} | {m['observadores']} | "
             f"{m['issues_abertas']} | {m['downloads_dia']} | {m['downloads_semana']} | "
             f"{m['downloads_mes']} |")
    if ARQ.exists():
        texto = ARQ.read_text(encoding="utf-8")
        texto = texto.rstrip() + "\n" + linha + "\n"
    else:
        texto = (
            "# Linha de base do ZEPHIRUM\n\n"
            "Medição factual do que existe hoje. Não é meta, não é projeção e não promete\n"
            "adoção: é o ponto de partida para que qualquer conversa sobre crescimento\n"
            "comece de um número que se pode conferir.\n\n"
            "| Data | Estrelas | Forks | Observadores | Issues | Downloads/dia | Downloads/semana | Downloads/mês |\n"
            "|---|---|---|---|---|---|---|---|\n" + linha + "\n"
        )
    ARQ.write_text(texto, encoding="utf-8")
    print(linha)


def main(argv: list[str]) -> int:
    if "--ler" in argv:
        print(ARQ.read_text(encoding="utf-8") if ARQ.exists() else "sem registro ainda")
        return 0
    gravar(medir())
    print(f"gravado em {ARQ.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

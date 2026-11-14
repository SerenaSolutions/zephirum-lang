#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Confere se todos os links da entrada de membro no Qiskit/ecosystem respondem.

A entrada e a nossa vitrine: se um link dela quebra, quem chega pelo catalogo
encontra um beco. Roda no guard de metadado e pode ser chamado a mao.
"""
from __future__ import annotations

import re
import sys
import urllib.request

ENTRADA = ("https://raw.githubusercontent.com/Qiskit/ecosystem/main/"
           "resources/members/zephirum_b2b5fe46.toml")


def checar(url: str) -> int:
    pedido = urllib.request.Request(url, method="HEAD",
                                    headers={"User-Agent": "zephirum-link-check"})
    try:
        with urllib.request.urlopen(pedido, timeout=25) as r:
            return r.status
    except Exception:  # noqa: BLE001 alguns servidores recusam HEAD
        try:
            with urllib.request.urlopen(url, timeout=25) as r:
                return r.status
        except Exception as e:  # noqa: BLE001
            print(f"  FALHA  {url}  ({e})")
            return 0


def main() -> int:
    with urllib.request.urlopen(ENTRADA, timeout=25) as r:
        texto = r.read().decode("utf-8")
    urls = sorted(set(re.findall(r"https?://[^\"'\s]+", texto)))
    ruins = 0
    for url in urls:
        status = checar(url)
        marca = "ok    " if 200 <= status < 400 else "QUEBRADO"
        if not 200 <= status < 400:
            ruins += 1
        print(f"  {marca} {status:3d}  {url}")
    print(f"{len(urls)} links, {ruins} quebrado(s)")
    return 1 if ruins else 0


if __name__ == "__main__":
    raise SystemExit(main())

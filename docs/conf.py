# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Serena Quantum Solutions
"""Configuracao do site de documentacao (Sphinx + tema oficial do ecossistema).

Decisao de arquitetura: o acervo em Markdown continua sendo a fonte unica.
O Sphinx le esses mesmos arquivos com MyST, sem duplicar conteudo e sem
reescrever um unico paragrafo. O que muda e a apresentacao, nao o texto.

Construir localmente:
    pip install -e ".[docs]"
    sphinx-build -b html docs _build/html
"""

import pathlib
import re

AQUI = pathlib.Path(__file__).parent
RAIZ = AQUI.parent

# Versao lida da fonte unica (arquivo VERSION), nunca duplicada aqui.
VERSION = (RAIZ / "VERSION").read_text(encoding="utf-8").strip()

project = "ZEPHIRUM / ZYQL"
author = "Serena Quantum Solutions"
copyright = "2026, Serena Quantum Solutions"
release = VERSION
version = ".".join(VERSION.split(".")[:2])

extensions = [
    "myst_parser",
    "sphinx_copybutton",
]

# Markdown sem frontmatter YAML obrigatorio, com tabelas e blocos de codigo.
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "fieldlist",
    "attrs_inline",
    "substitution",
]
myst_heading_anchors = 3
suppress_warnings = ["myst.header", "myst.xref_missing", "docutils"]

source_suffix = {".md": "markdown", ".rst": "restructuredtext"}
root_doc = "index"
exclude_patterns = ["_build", "**.ipynb_checkpoints", "openapi.json"]
language = "pt_BR"

# Tema oficial do ecossistema: mesma estrutura de barra lateral e navegacao.
html_theme = "qiskit-ecosystem"
html_title = f"ZEPHIRUM / ZYQL {release}"
html_short_title = "ZEPHIRUM"
html_static_path = []
html_show_sphinx = False

# O tema do ecossistema lista apenas a folha propria; a folha base do Furo
# precisa ser declarada aqui, senao a pagina chega sem layout.
html_css_files = ["styles/furo.css", "styles/qiskit-sphinx-theme.css"]

html_theme_options = {
    "sidebar_qiskit_text": "Projeto do ecossistema",
    "topbar_right_links": [
        {"label": "Repositorio", "url": "https://github.com/SerenaSolutions/zephirum-lang"},
        {"label": "Pacote", "url": "https://pypi.org/project/zephirum/"},
    ],
    "footer_structured_links": False,
}

html_context = {"theme_dev_mode": False}

# Links externos: nao falhar a construcao por 404 remoto.
linkcheck_ignore = [r"https://pypi\.org/.*", r"https://github\.com/.*", r"https://.*localhost.*"]

# Nao travar por aviso de documento nao incluido na arvore: o acervo e grande
# e cresce por fora desta arvore, por decisao de engenharia.
nitpicky = False

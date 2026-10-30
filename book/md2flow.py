#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""md2flow.py — conversor markdown -> flowables reportlab para a edição 2.

Suporta: títulos, parágrafos com **negrito**, *itálico*, `código`, citações [n],
listas com marcador e numeradas, tabelas de barra vertical, figuras com legenda,
equações centralizadas (linhas iniciadas por $$), blocos de citação e código.
"""
import os
import re

from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (Paragraph, Spacer, Table, TableStyle, Image as RLImage,
                                Preformatted, KeepTogether)

NAVY = colors.HexColor("#0a1030")
GOLD = colors.HexColor("#b8860b")
INK = colors.HexColor("#1a1a1a")
MUT = colors.HexColor("#555555")
LIGHT = colors.HexColor("#f5f2e8")
RULE = colors.HexColor("#c9c4b4")

_TAB_W = None


def _esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _inline(t):
    """Markdown inline mínimo -> mini-HTML do reportlab."""
    t = _esc(t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"(?<!\*)\*([^*]+?)\*(?!\*)", r"<i>\1</i>", t)
    t = re.sub(r"`([^`]+?)`", r'<font face="DVM" size="9.5">\1</font>', t)
    return t


def _styles(st):
    """Deriva os estilos que faltavam a partir dos estilos base do livro."""
    body = st["body"]
    return {
        "h3": ParagraphStyle("h3", parent=body, fontName="DVSB", fontSize=10.5, leading=14,
                             textColor=NAVY, spaceBefore=9, spaceAfter=3),
        "cap": ParagraphStyle("cap", parent=body, fontName="DVSO", fontSize=8.8, leading=11.6,
                              textColor=MUT, spaceBefore=3, spaceAfter=12, alignment=4),
        "eq": ParagraphStyle("eq", parent=body, fontName="DVS", fontSize=11, leading=17,
                             alignment=1, spaceBefore=7, spaceAfter=9, textColor=NAVY),
        "cell": ParagraphStyle("cell", parent=body, fontSize=8.4, leading=11.2, spaceAfter=0),
        "cellh": ParagraphStyle("cellh", parent=body, fontName="DVSB", fontSize=8.4, leading=11.2,
                                textColor=colors.white, spaceAfter=0),
        "bul": ParagraphStyle("bul", parent=body, leftIndent=14, firstLineIndent=-9, spaceAfter=3),
        "quote": ParagraphStyle("quote", parent=body, fontName="DVSO", fontSize=10, leading=15,
                                textColor=INK, leftIndent=16, rightIndent=10, spaceBefore=6,
                                spaceAfter=10, borderPadding=6),
    }


def _table(rows, st, width):
    body = rows[0]
    ncol = max(len(r) for r in rows)
    rows = [r + [""] * (ncol - len(r)) for r in rows]
    dados = [[Paragraph(_inline(c), st["cellh"]) for c in rows[0]]]
    for r in rows[1:]:
        dados.append([Paragraph(_inline(c), st["cell"]) for c in r])
    t = Table(dados, colWidths=[width / ncol] * ncol, repeatRows=1, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.4, RULE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#faf8f2")]),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


def _figura(caminho, legenda, st, width):
    if not os.path.exists(caminho):
        return []
    try:
        from PIL import Image as PILImage
        iw, ih = PILImage.open(caminho).size
    except Exception:
        iw, ih = 3, 2
    w = min(width, 15.4 * cm)
    img = RLImage(caminho, width=w, height=w * ih / iw)
    cap = Paragraph(_inline(legenda), st["cap"])
    return [Spacer(1, 6), KeepTogether([img, cap])]


def converter(md, st, toc=None, body_width=16.2 * cm, fig_base=None):
    """Converte markdown em lista de flowables."""
    S = _styles(st)
    fl, buf = [], []
    in_code = False
    code_buf = []
    tabela = []

    def descarrega():
        if not buf:
            return
        txt = " ".join(x.strip() for x in buf).strip()
        buf.clear()
        if txt:
            fl.append(Paragraph(_inline(txt), st["body"]))

    def fecha_tabela():
        if tabela:
            fl.append(Spacer(1, 5))
            fl.append(_table(list(tabela), S, body_width))
            fl.append(Spacer(1, 10))
            tabela.clear()

    for ln in md.split("\n"):
        s = ln.strip()

        if s.startswith("```"):
            descarrega()
            fecha_tabela()
            if in_code:
                fl.append(Preformatted("\n".join(code_buf), st["code"]))
                fl.append(Spacer(1, 8))
                code_buf = []
            in_code = not in_code
            continue
        if in_code:
            code_buf.append(ln)
            continue

        if s.startswith("|") and s.count("|") >= 3:
            descarrega()
            if re.fullmatch(r"\|[\s:|-]+\|", s):
                continue
            tabela.append([c.strip() for c in s.strip("|").split("|")])
            continue
        fecha_tabela()

        if not s:
            descarrega()
            continue

        m = re.match(r"^!\[(.*?)\]\((.*?)\)$", s)
        if m:
            descarrega()
            leg, path = m.group(1), m.group(2)
            if fig_base and not os.path.isabs(path):
                path = os.path.normpath(os.path.join(fig_base, path))
            fl.extend(_figura(path, leg, S, body_width))
            continue

        if s.startswith("# "):
            descarrega()
            titulo = s[2:]
            fl.append(Paragraph(_inline(titulo), st["h1"]))
            if toc is not None:
                toc.append(titulo)
            continue
        if s.startswith("### "):
            descarrega()
            fl.append(Paragraph(_inline(s[4:]), S["h3"]))
            continue
        if s.startswith("## "):
            descarrega()
            fl.append(Paragraph(_inline(s[3:]), st["h2"]))
            continue

        if s.startswith("$$") and s.endswith("$$") and len(s) > 4:
            descarrega()
            fl.append(Paragraph(_inline(s[2:-2].strip()), S["eq"]))
            continue

        if s.startswith("> "):
            descarrega()
            fl.append(Paragraph(_inline(s[2:]), S["quote"]))
            continue

        if re.match(r"^[-•]\s+", s):
            descarrega()
            fl.append(Paragraph("•&nbsp;&nbsp;" + _inline(re.sub(r"^[-•]\s+", "", s)), S["bul"]))
            continue
        m = re.match(r"^(\d+)\.\s+(.*)$", s)
        if m:
            descarrega()
            fl.append(Paragraph(f"{m.group(1)}.&nbsp;&nbsp;" + _inline(m.group(2)), S["bul"]))
            continue

        if s.startswith("*") and s.endswith("*") and not s.startswith("**"):
            descarrega()
            fl.append(Paragraph(_inline(s.strip("*")), st["it"]))
            continue

        buf.append(s)

    descarrega()
    fecha_tabela()
    if in_code and code_buf:
        fl.append(Preformatted("\n".join(code_buf), st["code"]))
    return fl

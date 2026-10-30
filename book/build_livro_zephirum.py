#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_livro_zephirum.py — monta a edição íntegra do livro ZEPHIRUM/ZYQL."""
import os, re, random, math
from PIL import Image, ImageDraw
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas as pdfcanvas
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph,
                                Spacer, PageBreak, Image as RLImage, Preformatted,
                                NextPageTemplate, KeepTogether)
from reportlab.platypus.tableofcontents import TableOfContents
from matplotlib import font_manager

BASE = "/app/conversations/6ab6a81d7f5a92622980cebc"
R = f"{BASE}/dexia/zephirum"
BOOK = f"{R}/book"
TMP = f"{BOOK}/build_final"
os.makedirs(TMP, exist_ok=True)

# ---------- fontes ----------
FP = os.path.join(os.path.dirname(font_manager.__file__), "mpl-data/fonts/ttf/DejaVuSans.ttf")
FPB = os.path.join(os.path.dirname(font_manager.__file__), "mpl-data/fonts/ttf/DejaVuSans-Bold.ttf")
FPO = os.path.join(os.path.dirname(font_manager.__file__), "mpl-data/fonts/ttf/DejaVuSans-Oblique.ttf")
FPM = os.path.join(os.path.dirname(font_manager.__file__), "mpl-data/fonts/ttf/DejaVuSansMono.ttf")

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
pdfmetrics.registerFont(TTFont("DVS", FP))
pdfmetrics.registerFont(TTFont("DVSB", FPB))
pdfmetrics.registerFont(TTFont("DVSO", FPO))
pdfmetrics.registerFont(TTFont("DVM", FPM))

NAVY = HexColor("#0a1030"); GOLD = HexColor("#b8860b"); INK = HexColor("#1a1a1a")
MUT = HexColor("#555555"); LIGHT = HexColor("#f5f2e8")

# ---------- artes de capítulo (geradas, únicas, sem custo de API) ----------
def cap_art(n, path):
    rng = random.Random(1000 + n)
    W, H = 1240, 1600
    img = Image.new("RGB", (W, H), (10, 16, 48))
    d = ImageDraw.Draw(img, "RGBA")
    # gradiente navy
    for y in range(H):
        t = y / H
        c = (int(8 + 14 * t), int(14 + 20 * t), int(40 + 30 * t))
        d.line([(0, y), (W, y)], fill=c)
    cx, cy = W // 2, H // 2
    # constelação de qubits: anéis + nós + fases
    for ring in range(4 + n % 5, 12 + n % 7):
        rr = 90 + ring * 52 + n * 7
        col = (212, 175, 55, rng.randint(28, 90)) if ring % 2 == 0 else (94, 234, 212, rng.randint(20, 70))
        d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), outline=col, width=2)
    nodes = []
    for k in range(14 + n * 3):
        ang = rng.uniform(0, 2 * math.pi)
        rad = rng.uniform(60, 560)
        x, y = cx + rad * math.cos(ang), cy + rad * 0.8 * math.sin(ang)
        nodes.append((x, y))
        sz = rng.randint(3, 9)
        d.ellipse((x - sz, y - sz, x + sz, y + sz), fill=(212, 175, 55, rng.randint(90, 220)))
    for i in range(len(nodes) - 1):
        x0, y0 = nodes[i]; x1, y1 = nodes[i + 1]
        d.line([(x0, y0), (x1, y1)], fill=(94, 234, 212, rng.randint(18, 55)), width=1)
    # marcas de fase e numerais únicos por capítulo
    d.ellipse((cx - 70, cy - 70, cx + 70, cy + 70), fill=(8, 16, 38, 200), outline=(212, 175, 55, 255), width=3)
    d.text((cx, cy - 26), f"CAP. {n:02d}", fill=(212, 175, 55), anchor="mm")
    d.text((cx, cy + 30), "ZEPHIRUM", fill=(94, 234, 212), anchor="mm")
    # moldura
    d.rectangle((14, 14, W - 14, H - 14), outline=(212, 175, 55, 120), width=3)
    img.save(path)

ARTS = []
ARTS2 = []
for n in range(1, 19):
    p = f"{TMP}/art_cap{n:02d}.png"
    cap_art(n, p)
    ARTS.append(p)
    p2 = f"{TMP}/art2_cap{n:02d}.png"
    cap_art(n + 200, p2)
    ARTS2.append(p2)

# ---------- estilos ----------
S_body = ParagraphStyle("body", fontName="DVS", fontSize=11, leading=19.7, spaceAfter=9, textColor=INK)
S_h1 = ParagraphStyle("h1", fontName="DVSB", fontSize=17, leading=21, textColor=NAVY, spaceBefore=6, spaceAfter=8)
S_h2 = ParagraphStyle("h2", fontName="DVSB", fontSize=12.5, leading=16, textColor=GOLD, spaceBefore=12, spaceAfter=6)
S_it = ParagraphStyle("it", fontName="DVSO", fontSize=10.5, leading=15, textColor=MUT, spaceAfter=10)
S_code = ParagraphStyle("code", fontName="DVM", fontSize=8.5, leading=12.5, textColor=NAVY, backColor=LIGHT)
S_part = ParagraphStyle("part", fontName="DVSB", fontSize=24, leading=30, textColor=NAVY)
S_partsub = ParagraphStyle("partsub", fontName="DVS", fontSize=12, leading=16, textColor=GOLD)

import sys as _sys
if BOOK not in _sys.path:
    _sys.path.insert(0, BOOK)
import md2flow as _md2flow

_STYLES = {"body": S_body, "h1": S_h1, "h2": S_h2, "it": S_it, "code": S_code,
           "part": S_part, "partsub": S_partsub}


def md_flowables(md, toc=None, level=0):
    """Conversor markdown->flowables (edicao 2: tabelas, figuras, listas, equacoes)."""
    return _md2flow.converter(md, _STYLES, toc=toc,
                              body_width=A4[0] - 4.8 * cm, fig_base=os.path.join(BOOK, "capitulos"))

# ---------- doc template com rodapé + TOC ----------
class Livro(BaseDocTemplate):
    def __init__(self, fn, **kw):
        super().__init__(fn, **kw)
        f = Frame(2.4 * cm, 2.2 * cm, A4[0] - 4.8 * cm, A4[1] - 4.4 * cm, id="f")
        Z = dict(leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
        ff = Frame(0, 0, A4[0], A4[1], id="ff", **Z)
        fc = Frame(0, 0, A4[0], A4[1], id="fc", **Z)
        # a capa precisa ser o PRIMEIRO template: o PDF tem de abrir na capa,
        # nao numa pagina em branco (defeito da 1a diagramacao).
        self.addPageTemplates([
            PageTemplate(id="capa", frames=[fc], onPage=self.pag_capa),
            PageTemplate(id="normal", frames=[f], onPage=self.rodape),
            PageTemplate(id="arte", frames=[ff], onPage=self.pag_arte),
        ])
        self.toc = []
        self.toc_pages = []

    def rodape(self, c, doc):
        c.saveState()
        c.setFont("DVS", 8); c.setFillColor(MUT)
        c.drawCentredString(A4[0] / 2, 1.1 * cm, "ZEPHIRUM — A Computação Antes da Execução")
        c.drawRightString(A4[0] - 2.4 * cm, 1.1 * cm, str(c.getPageNumber()))
        c.setFillColor(GOLD)
        c.rect(2.4 * cm, 1.55 * cm, A4[0] - 4.8 * cm, 0.5, fill=1, stroke=0)
        c.restoreState()

    def pag_capa(self, c, doc):
        """Capa: arte oficial do peixe beta em pagina cheia, sem painel que cubra a arte."""
        from PIL import Image, ImageDraw
        ART = f"{BASE}/dexia/zephirum/assets/brand/logo_zyql_betta_oficial_11out2026.jpg"
        DPI = 200
        W, H = int(A4[0] / 72 * DPI), int(A4[1] / 72 * DPI)
        art = Image.open(ART).convert("RGB")
        aw, ah = art.size
        # cor de fundo amostrada nos quatro cantos, para emendar a arte no papel
        amostras = [art.getpixel((3, 3)), art.getpixel((aw - 4, 3)),
                    art.getpixel((3, ah - 4)), art.getpixel((aw - 4, ah - 4))]
        bg = tuple(sum(v[i] for v in amostras) // 4 for i in range(3))
        tela = Image.new("RGB", (W, H), bg)
        a2 = art.resize((W, int(ah * W / aw)), Image.LANCZOS)
        tela.paste(a2, (0, 0))
        # transicao suave entre a arte e o papel, para nao cortar o peixe com uma tarja
        alt = a2.size[1]
        gh = min(int(0.16 * alt), max(0, H - alt))
        if gh > 0:
            borda = a2.crop((0, alt - 1, W, alt)).resize((1, 1)).getpixel((0, 0))
            grad = Image.new("RGB", (W, gh))
            gd = ImageDraw.Draw(grad)
            for y in range(gh):
                t = y / max(1, gh - 1)
                gd.line([(0, y), (W, y)], fill=tuple(int(borda[i] * (1 - t) + bg[i] * t) for i in range(3)))
            tela.paste(grad, (0, alt - 1))
        p = f"{TMP}/_capa_bg.png"
        tela.save(p)
        c.drawImage(p, 0, 0, width=A4[0], height=A4[1])
        c.setTitle("ZEPHIRUM: A Computação Antes da Execução (2ª edição)")
        c.setAuthor("Serena Quantum Solutions")
        c.setSubject("ZYQL — a linguagem quântica | the quantum language")
        c.setCreator("MGN Science Editions")
        # bloco de titulo sobre o papel escuro, abaixo da arte
        c.setFillColor(HexColor("#d4af37"))
        c.setFont("DVSB", 27)
        c.drawCentredString(A4[0] / 2, 7.0 * cm, "ZEPHIRUM")
        c.setFillColor(HexColor("#ffffff"))
        c.setFont("DVS", 13.5)
        c.drawCentredString(A4[0] / 2, 5.9 * cm, "A Computação Antes da Execução")
        c.setFillColor(HexColor("#5eead4"))
        c.setFont("DVS", 10)
        c.drawCentredString(A4[0] / 2, 5.1 * cm, "ZYQL — a linguagem quântica | the quantum language")
        c.setStrokeColor(HexColor("#d4af37"))
        c.setLineWidth(0.8)
        c.line(5.2 * cm, 4.3 * cm, A4[0] - 5.2 * cm, 4.3 * cm)
        c.setFillColor(HexColor("#ffffff"))
        c.setFont("DVSB", 12)
        c.drawCentredString(A4[0] / 2, 3.4 * cm, "SERENA QUANTUM SOLUTIONS")
        c.setFillColor(HexColor("#b8b8c8"))
        c.setFont("DVS", 9.5)
        c.drawCentredString(A4[0] / 2, 2.6 * cm, "MGN Science Editions · 2ª edição · 2026")

    def pag_arte(self, c, doc):
        pass  # imagem desenhada como flowable full-page no template

def arte_page(story, path):
    story.append(NextPageTemplate("arte"))
    story.append(PageBreak())
    story.append(RLImage(path, width=A4[0] - 2.0 * cm, height=(A4[0] - 2.0 * cm) * 1600 / 1240))
    story.append(NextPageTemplate("normal"))
    story.append(PageBreak())

# ---------- montagem ----------
story = []
# pagina 1 ja nasce com o template "capa" (primeiro da lista).

# folha de rosto
story.append(NextPageTemplate("normal"))
story.append(PageBreak())
story.append(Spacer(1, 6 * cm))
story.append(Paragraph("ZEPHIRUM", ParagraphStyle("t1", fontName="DVSB", fontSize=34, leading=40, textColor=NAVY)))
story.append(Paragraph("A Computação Antes da Execução", ParagraphStyle("t2", fontName="DVS", fontSize=16, leading=22, textColor=GOLD)))
story.append(Spacer(1, 14))
story.append(Paragraph("ZYQL — a linguagem quântica | the quantum language", S_it))
story.append(Spacer(1, 3 * cm))
story.append(Paragraph("SERENA QUANTUM SOLUTIONS", ParagraphStyle("t3", fontName="DVSB", fontSize=15, leading=20, textColor=INK)))
story.append(Paragraph("MGN Science Editions — 1ª edição, outubro de 2026", S_it))
story.append(PageBreak())

story.append(PageBreak())
story.append(Spacer(1, 8 * cm))
story.append(Paragraph("Dedicatória", S_h2))
story.append(Paragraph("A todos que já olharam para uma máquina caríssima rodando e perguntaram, "
    "baixinho: <i>será que precisava?</i> Este livro é a resposta formal à sua intuição.", S_it))

# ficha + prefácio
story.append(Paragraph("Ficha Catalográfica", S_h1))
story.append(Paragraph("SERENA QUANTUM SOLUTIONS. <b>Zephirum: a computação antes da execução / "
    "Serena Quantum Solutions. — 2ª ed. rev. e ampl. — MGN Science Editions, 2026.</b><br/>"
    "Inclui bibliografia e glossário trilíngue PT/EN/AR.<br/>"
    "1. Linguagens de programação quântica. 2. Verificação formal. 3. Computação sob contrato. "
    "I. Título.", S_body))
story.append(Spacer(1, 18))
story.append(Paragraph("Prefácio", S_h1))
story.append(Paragraph(
    "Este livro nasceu de uma pergunta que deveria vir antes de todas as outras: será que precisamos "
    "executar esta computação? A linguagem Zephyrum (ZYQL) é a nossa resposta — um contrato de necessidade "
    "com cinco cláusulas, um numeral honesto, uma escada de dez degraus e um livro-razão que qualquer "
    "pessoa confere. Provas em hardware quântico real da IBM registram os vereditos com recibos "
    "criptográficos; os resultados negativos recebem o mesmo carimbo dos positivos. Aqui não há promessa "
    "de velocidade — há um método para decidir quando o gasto vale a pena.", S_body))
story.append(Spacer(1, 10))
story.append(Paragraph("— R.G., outubro de 2026", S_it))
story.append(PageBreak())
story.append(Paragraph("Como ler este livro", S_h1))
story.append(Paragraph("Cada capítulo abre no <b>Nível 1 — para qualquer leitor</b>, desenvolve no <b>Nível 2 — "
    "para o cientista e o engenheiro</b> e fecha no <b>Nível 3 — para a ciência da computação</b>. As transições "
    "estão sempre marcadas: leia o Nível 1 de tudo e o resto do que for do seu ofício — o livro foi desenhado para "
    "ser atravessado em três profundidades diferentes, sem trair o rigor.", S_body))
story.append(Paragraph("Ao final de cada capítulo há <b>exercícios</b> e um <b>laboratório real</b>: um programa ZYQL "
    "compilado pelo kernel verdadeiro, com o OpenQASM 3.0 gerado transcrito tal como sai do compilador — inclusive "
    "os erros, que são didática. Os apêndices trazem a gramática completa, o código-fonte do kernel, os recibos do "
    "livro-razão, as transcrições das baterias de teste e o glossário trilíngue PT/EN/AR.", S_body))
story.append(Paragraph("A obra é bilíngue: a edição integral em português (capítulos 1 a 18) seguida da "
    "<b>International Section</b> com os capítulos em inglês, e seleções em alemão e árabe — a jornada do zero "
    "que dá nome à linguagem também fala essas línguas.", S_body))
story.append(PageBreak())

# sumário
story.append(Paragraph("Sumário", S_h1))
toc = TableOfContents()
toc.levelStyles = [
    ParagraphStyle("toc0", fontName="DVSB", fontSize=10.5, leading=16, textColor=NAVY),
    ParagraphStyle("toc1", fontName="DVS", fontSize=9.5, leading=13, leftIndent=16, textColor=INK),
]
story.append(toc)
story.append(PageBreak())

PARTS = {
    1: ("PARTE I — A PERGUNTA", "Capítulos 1 a 4", f"{BASE}/mapamundi/arte_qubit.png"),
    2: ("PARTE II — O TRIBUNAL DA CIÊNCIA", "Capítulos 5 a 7", f"{BASE}/mapamundi/arte_codigo.png"),
    3: ("PARTE III — A ARQUITETURA", "Capítulos 8 a 13", f"{BASE}/mapamundi/arte_dexia_hub.png"),
    4: ("PARTE IV — O TESTE", "Capítulos 14 a 16", f"{BASE}/mapamundi/arte_veredito.png"),
    5: ("PARTE V — O HORIZONTE", "Capítulos 17 a 18 + apêndices", f"{TMP}/art_cap17.png"),
}
TITULOS = {
    1: ("Capítulo 1 — O mundo executa antes de perguntar", 1),
    2: ("Capítulo 2 — Observação: computações que ninguém precisava fazer", 1),
    3: ("Capítulo 3 — Hipótese: precisamos computar isto?", 1),
    4: ("Capítulo 4 — A jornada do zero: śūnya → ṣifr → zephirum", 1),
    5: ("Capítulo 5 — Anterioridade: as vinte linhas que já existiam", 2),
    6: ("Capítulo 6 — Falsificação: os certificados que tentaram nos enganar", 2),
    7: ("Capítulo 7 — O que sobrou: a composição como contribuição", 2),
    8: ("Capítulo 8 — Formalização: pergunta, contrato, tolerância e orçamento", 3),
    9: ("Capítulo 9 — A linguagem Zephyrum: ASK, CONTRACT, MODEL, BUDGET, REQUIRE", 3),
    10: ("Capítulo 10 — O numeral Zephyrum: 0, 1 e Z", 3),
    11: ("Capítulo 11 — O algoritmo ZCA: a escada", 3),
    12: ("Capítulo 12 — Certificados e ledger: gerador e verificador separados", 3),
    13: ("Capítulo 13 — Os quatro pilares: Language, Compiler, Simulator, Runtime", 3),
    14: ("Capítulo 14 — Experimentos: resultados honestos, inclusive os que doem", 4),
    15: ("Capítulo 15 — Limitações: onde a escada não compensa", 4),
    16: ("Capítulo 16 — Resultados: o que os números dizem (e o que ainda não)", 4),
    17: ("Capítulo 17 — Futuro: o quântico como consequência, e o horizonte nano", 5),
    18: ("Capítulo 18 — Encerramento: a pergunta antes da máquina", 5),
}


# --- titulos e nota da edicao 2 ---
TITULOS[1] = ("Capítulo 1 — O mundo executa antes de perguntar", 1)
TITULOS[2] = ("Capítulo 2 — Observação: computações que ninguém precisava fazer", 1)
TITULOS[3] = ("Capítulo 3 — Hipótese: precisamos computar isto?", 1)
TITULOS[4] = ("Capítulo 4 — A jornada do zero: śūnya, ṣifr, zephirum", 1)
TITULOS[5] = ("Capítulo 5 — Anterioridade: as vinte linhas que já existiam", 2)
TITULOS[6] = ("Capítulo 6 — Falsificação: tentar fazer o sistema errar", 2)
TITULOS[7] = ("Capítulo 7 — O que sobrou: a composição como contribuição", 2)
TITULOS[8] = ("Capítulo 8 — Formalização: pergunta, contrato, tolerância e orçamento", 3)
TITULOS[9] = ("Capítulo 9 — A linguagem: ASK, CONTRACT, MODEL, BUDGET, REQUIRE", 3)
TITULOS[10] = ("Capítulo 10 — O terceiro valor: 0, 1 e REFUSED", 3)
TITULOS[11] = ("Capítulo 11 — O algoritmo ZCA: a escada", 3)
TITULOS[12] = ("Capítulo 12 — Certificados e recibo: gerador e verificador separados", 3)
TITULOS[13] = ("Capítulo 13 — Os quatro pilares e o inventário real do sistema", 3)
TITULOS[14] = ("Capítulo 14 — Experimentos: resultados honestos, inclusive os que doem", 4)
TITULOS[15] = ("Capítulo 15 — Limitações: onde a escada não compensa", 4)
TITULOS[16] = ("Capítulo 16 — Resultados: o que os números dizem, e o que ainda não dizem", 4)
TITULOS[17] = ("Capítulo 17 — Futuro: neutralidade tecnológica como método", 5)
TITULOS[18] = ("Capítulo 18 — Encerramento: a pergunta antes da máquina", 5)

NOTA_ED2 = """
## Nota a esta edição

Esta é a segunda edição do livro, revista e ampliada. Três mudanças de fundo a distinguem da primeira.

**Primeira: a camada de prova foi reescrita.** A primeira edição descrevia o recibo apenas como hash SHA3-256. Desde então o mecanismo recebeu assinatura pós-quântica ML-DSA-44, encadeamento por elo e uma suíte adversarial que ataca o próprio registro. O capítulo 12 foi reescrito por inteiro, e o capítulo 6 ganhou a seção de ataques.

**Segunda: um erro estatístico foi corrigido em público.** A regra de decisão original certificava em 12% das repetições quando o dispositivo estava exatamente sobre a banda. A regra foi trocada por intervalar, e o capítulo 14 documenta o defeito, a correção e a consequência — inclusive o fato de que um dos experimentos deixou de ser certificado.

**Terceira: toda alegação passou a ser classificada.** O capítulo 15 separa o que é sustentado por evidência do que é hipótese, e o capítulo 16 faz a síntese. Nenhum número aparece sem intervalo, e nenhum resultado negativo foi omitido.

As figuras foram refeitas a partir dos dados dos recibos, em escala adequada a leitura em papel e em tela. As referências foram organizadas por ordem de citação, com criterio de honestidade: onde o identificador não pôde ser conferido, consta apenas autor, veículo e ano.

Permanece o que a primeira edição já declarava: nenhuma peça isolada desta arquitetura é inédita; a contribuição é a composição contratual, e ela é falsificável.
"""

story.append(PageBreak())
story.extend(md_flowables(NOTA_ED2))

current_part = 0
for n in range(1, 19):
    parte = TITULOS[n][1]
    if parte != current_part:
        current_part = parte
        titulo, sub, art = PARTS[parte]
        story.append(NextPageTemplate("arte"))
        story.append(PageBreak())
        # divisor de parte com arte de fundo + tarja
        story.append(RLImage(art, width=A4[0], height=A4[0] * 1600 / 1240 * (1240 / 1600) * (A4[1] / A4[0]) * (1240 / 1600)))
        story.append(NextPageTemplate("normal"))
        story.append(PageBreak())
        story.append(Spacer(1, 7 * cm))
        story.append(Paragraph(titulo, S_part))
        story.append(Paragraph(sub, S_partsub))
        story.append(PageBreak())
    arte_page(story, ARTS[n - 1])
    md = open(f"{BOOK}/capitulos/cap{n:02d}_pt.md", encoding="utf-8").read()
    # registra no TOC
    story.append(Paragraph(TITULOS[n][0], ParagraphStyle(f"h1c{n}", parent=S_h1, fontSize=15)))
    fl = md_flowables("\n".join(md.split("\n")[2:]))  # pula título (já impresso)
    story.extend(fl)
    labp = f"{BOOK}/labs/lab{n:02d}.md"
    if os.path.exists(labp):
        story.extend(md_flowables(open(labp, encoding="utf-8").read()))
    arte_page(story, ARTS2[n - 1])
    story.append(PageBreak())

# seção internacional (inglês)
story.append(NextPageTemplate("arte"))
story.append(PageBreak())
story.append(RLImage(ARTS[0], width=A4[0] - 2 * cm, height=(A4[0] - 2 * cm) * 1600 / 1240))
story.append(NextPageTemplate("normal"))
story.append(PageBreak())
story.extend(md_flowables(open(f"{BOOK}/capitulos/referencias.md", encoding="utf-8").read()))
story.append(PageBreak())
story.append(Spacer(1, 6 * cm))
story.append(Paragraph("INTERNATIONAL SECTION", S_part))
story.append(Paragraph("The Quantum Language — selected English chapters", S_partsub))
story.append(PageBreak())
for n in range(1, 19):
    p = f"{BOOK}/capitulos/cap{n:02d}_en.md"
    if os.path.exists(p):
        md = open(p, encoding="utf-8").read()
        story.extend(md_flowables(md))
        story.append(PageBreak())

story.append(Spacer(1, 5 * cm))
story.append(Paragraph("AUSWAHL AUF DEUTSCH", S_part))
story.append(Paragraph("Ausgewählte Kapitel — deutsche Ausgabe", S_partsub))
story.append(PageBreak())
for n in range(1, 8):
    p = f"{BOOK}/capitulos/cap{n:02d}_de.md"
    if os.path.exists(p):
        md = open(p, encoding="utf-8").read()
        story.extend(md_flowables(md))
        story.append(PageBreak())

story.append(Spacer(1, 5 * cm))
story.append(Paragraph("Arabic edition \u2014 selected chapters", S_part))
story.append(Paragraph("Selected chapters — Arabic edition", S_partsub))
story.append(PageBreak())
for n in (1, 4, 6):
    p = f"{BOOK}/capitulos/cap{n:02d}_ar.md"
    if os.path.exists(p):
        md = open(p, encoding="utf-8").read()
        story.extend(md_flowables(md))
        story.append(PageBreak())

# apêndice A — gramática
story.append(Paragraph("Apêndice A — Especificação Zephirum: a gramática completa", S_h1))
story.append(Paragraph("A gramática formal da linguagem (Lark), arquivo <i>grammar/zyql_v13.lark</i>, "
    "na versão 1.4 do kernel — com operandos multi-qubit e as cláusulas do contrato:", S_body))
gram = open(f"{R}/grammar/zyql_v13.lark", encoding="utf-8").read()
story.append(Preformatted(gram, S_code))
story.append(PageBreak())

# apêndice B — código do kernel
story.append(Paragraph("Apêndice B — O código do kernel (listagens integrais)", S_h1))
for f, desc in [
    ("exec/C2_zyqlc/zyqlc.py", "Compilador ZYQL → OpenQASM 3.0 (codegen com recibos)."),
    ("exec/C2_zyqlc/zyql_verify.py", "Verificador formal de circuitos (equivalência até fase global e preservação semântica na transpilação)."),
    ("exec/C2_zyqlc/zyql_sdk.py", "SDK de integração universal: compile / from_qasm3 / to_qiskit / receipt e o plug para LLMs."),
    ("exec/C2_zyqlc/zyql_qasm_import.py", "Importador OpenQASM 3.0 → ZYQL (interoperabilidade bidirecional)."),
]:
    story.append(Paragraph(os.path.basename(f), S_h2))
    story.append(Paragraph(desc, S_it))
    try:
        code = open(f"{R}/{f}", encoding="utf-8").read()
        story.append(Preformatted(code, S_code))
    except Exception as e:
        story.append(Paragraph(f"(listagem indisponível: {e})", S_it))
    story.append(PageBreak())

# apêndice B2 — fontes das baterias + transcrições
story.append(Paragraph("Apêndice B2 — As baterias de teste: fontes e transcrições de execução", S_h1))
story.append(Paragraph("Execução real capturada em 2026-10-18, na máquina de construção desta edição. "
    "A falha pré-existente da paridade byte-a-byte do kernel C está transcrita com honestidade: "
    "está isolada do caminho Python e é o exemplo vivo do capítulo 16.", S_body))
story.append(Paragraph("Transcrição da execução", S_h2))
tr = open(f"{TMP}/transcriptas_baterias.txt", encoding="utf-8").read()
story.append(Preformatted(tr, S_code))
story.append(PageBreak())
story.append(Paragraph("Fonte: bateria v1.4 (test_v14.py)", S_h2))
story.append(Preformatted(open(f"{R}/exec/C2_zyqlc/test_v14.py", encoding="utf-8").read(), S_code))
story.append(PageBreak())
story.append(Paragraph("Fonte: verificador formal (test_verify.py)", S_h2))
story.append(Preformatted(open(f"{R}/exec/C2_zyqlc/test_verify.py", encoding="utf-8").read(), S_code))
story.append(PageBreak())
story.append(Paragraph("Fonte: bateria do compilador (test_compiler.py)", S_h2))
story.append(Preformatted(open(f"{R}/exec/C2_zyqlc/test_compiler.py", encoding="utf-8").read(), S_code))
story.append(PageBreak())

# apêndice G — figuras da tese
story.append(Paragraph("Apêndice G — Figuras técnicas do experimento CHSH", S_h1))
for fn, cap in [
    ("fig_chsh.png", "Figura 1 — Distribuição do parâmetro S do teste CHSH: hardware real (2,07 ± 0,12), simulação sem ruído (2,76) e os limites clássico (2,0) e de Tsirelson (2√2)."),
    ("fig_bell_controls.png", "Figura 2 — Controles do teste de Bell: as quatro bases de medição da desigualdade CHSH."),
    ("fig_ghz_ladder.png", "Figura 3 — Escada GHZ: preparação e verificação de estados emaranhados multipartite."),
    ("fig_h2_energy.png", "Figura 4 — Curva de energia da molécula H2 pelo método VQE: o otimizador clássico e o ansatz quântico em colaboração."),
]:
    fp = f"{R}/paper/thesis/figures/{fn}"
    if os.path.exists(fp):
        im = Image.open(fp)
        iw, ih = im.size
        w = A4[0] - 4 * cm
        story.append(RLImage(fp, width=w, height=w * ih / iw))
        story.append(Spacer(1, 8))
        story.append(Paragraph(cap, S_it))
        story.append(PageBreak())

# apêndice H — trechos do Livro II
story.append(Paragraph("Apêndice H — Trechos do Livro II: O Núcleo Híbrido", S_h1))
story.append(Paragraph("Antecipação da continuação da série Zephyrum, onde a honestidade vira arquitetura de "
    "um núcleo híbrido real. Transcritos na íntegra os três primeiros capítulos em produção.", S_body))
for n in (1, 2, 3):
    fp = f"{BOOK}/livro2/cap{n:02d}_hib_pt.md"
    if os.path.exists(fp):
        story.extend(md_flowables(open(fp, encoding="utf-8").read()))
        story.append(PageBreak())

# apêndice C — recibos
story.append(Paragraph("Apêndice C — Recibos do livro-razão (seleção)", S_h1))
story.append(Paragraph("Transcrição de recibos reais do ledger do ecossistema, incluindo o recibo #25 "
    "(CHSH no ibm_marrakesh, S = 2,07 ± 0,12, veredito Z) e o extrato da bateria v1.4 (12/12) e do "
    "verificador formal (4/4).", S_body))
import json as _json
if os.path.exists(f"{R}/dexia_receipts.jsonl"):
    _todos = [_json.loads(l) for l in open(f"{R}/dexia_receipts.jsonl", encoding="utf-8") if l.strip()]
    _n = len(_todos)
    story.append(Paragraph(
        f"O livro-razão do ecossistema continha {_n} recibos na data desta edição. "
        "Transcrevem-se aqui os marcos: os primeiros elos da cadeia, uma amostra distribuída da "
        "linha do tempo e os últimos elos, que demonstram a continuidade do encadeamento. "
        "A cadeia completa é verificável no repositório [R1], elo por elo.", S_body))
    _passo = max(1, (_n - 12) // 8)
    _idx = sorted(set(list(range(0, min(5, _n))) + list(range(5, max(6, _n - 5), _passo))[:8]
                      + list(range(max(0, _n - 5), _n))))
    for _i in _idx:
        o = _todos[_i]
        story.append(Paragraph(f"<b>Recibo {_i + 1} de {_n}</b>", S_it))
        story.append(Preformatted(_json.dumps(o, ensure_ascii=False, indent=2), S_code))
        story.append(Spacer(1, 6))
else:
    story.append(Paragraph("(ledger indisponível nesta edição)", S_it))
story.append(PageBreak())

# apêndice D — glossário trilíngue
story.append(Paragraph("Apêndice D — Glossário trilíngue PT / EN / AR", S_h1))
GLOSS = [
    ("Zephyrum", "Zephyrum", "زفيرم", "O numeral do desconhecido; o zero em trânsito histórico (śūnya→ṣifr→zefiro)."),
    ("Veredito Z", "Z verdict", "حُكم Z", "A resposta honesta 'indeterminado' — o kernel não chuta."),
    ("Contrato ε-B-M", "ε-B-M contract", "عقد ε-B-M", "Tolerância de erro, orçamento de custo e modelo de computação admitido."),
    ("Escada ZCA", "ZCA ladder", "سلّم ZCA", "Dez degraus do mais barato ao mais caro; para no primeiro que fecha o contrato."),
    ("PRASHNA", "PRASHNA block", "كتلة براشنا", "O bloco de pergunta da linguagem; homenagem ao sânscrito."),
    ("Recibo", "Receipt", "إيصال", "Registro criptográfico SHA3-256 de cada decisão; verificável por terceiros."),
    ("Ledger", "Ledger", "سجل", "Livro-razão append-only de recibos, em ordem temporal."),
    ("Kernel de decisão", "Decision kernel", "نواة القرار", "O operador que colapsa Z em 0, 1 ou o mantém, sob contrato."),
    ("Tipagem T1-T6", "T1-T6 typing", "التنميط T1-T6", "Tipos semânticos: qubit colapsado não evolui; dupla medição não compila."),
    ("OpenQASM 3.0", "OpenQASM 3.0", "أوبن كواسم 3.0", "Padrão mundial de intercâmbio de circuitos; a Zephyrum importa e exporta."),
    ("Plug LLM", "LLM plug", "قابس LLM", "Manifesto de function-calling e invocação determinística com recibo."),
    ("Verificador formal", "Formal verifier", "المُتحقق الصوري", "Prova de equivalência de circuitos até fase global."),
    ("CHSH", "CHSH", "CHSH", "Desigualdade de Bell; a prova canônica de não-classicidade."),
    ("Nano quântico", "Nano-quantum", "النانو الكمّي", "Fronteira de sensores e dispositivos quânticos em escala nanométrica."),
    ("Computação sob contrato", "Contract computing", "الحوسبة التعاقدية", "Executar apenas o que o contrato de necessidade autoriza."),
]
g_rows = "".join(f"<tr><td><b>{a}</b></td><td>{b}</td><td>{c}</td><td>{d}</td></tr>" for a, b, c, d in GLOSS)
story.append(Paragraph(
    "<table bordercolor='#b8860b' width='100%%' cellspacing='4'><tr><td><b>PT</b></td><td><b>EN</b></td><td><b>AR</b></td><td><b>Definição</b></td></tr>" +
    g_rows + "</table>", ParagraphStyle("tbl", parent=S_body, fontSize=9.5, leading=14)))
story.append(PageBreak())

# apêndice E — referências
story.append(Paragraph("Apêndice E — Referências e anterioridade", S_h1))
REFS = [
    "Bell, J. S. (1964). On the Einstein Podolsky Rosen paradox. Physics, 1(3), 195-200.",
    "Clauser, J. F.; Horne, M. A.; Shimony, A.; Holt, R. A. (1969). Proposed experiment to test local hidden-variable theories. Physical Review Letters, 23(15), 880.",
    "Kleene, S. C. (1952). Introduction to Metamathematics. Van Nostrand.",
    "Necula, G. C.; Lee, P. (1996). Proof-carrying code. POPL '96.",
    "Leroy, X. (2009). Formal verification of a realistic compiler. Communications of the ACM, 52(7), 107-115.",
    "Turing, A. M. (1936). On computable numbers. Proceedings of the London Mathematical Society.",
    "Rice, H. G. (1953). Classes of recursively enumerable sets and their decision problems. Transactions of the AMS.",
    "OpenQASM 3.0 Specification (2021-2024). OpenQASM Technical Steering Committee.",
    "IBM Quantum (2026). Quantum World Congress 2026 — keynote de Scott Crowder: métricas de sistema e computação útil por dólar.",
    "Cross, A. et al. (2022). Open Quantum Assembly Language for Extended Quantum Programs. ACM TQC.",
    "Ifrah, G. (2000). The Universal History of Numbers. Wiley (jornada do śūnya ao zero).",
    "Farhi, E.; Goldstone, J.; Gutmann, S. (2014). A Quantum Approximate Optimization Algorithm. arXiv:1411.4028.",
    "Peruzzo, A. et al. (2014). A variational eigenvalue solver on a photonic quantum processor. Nature Communications, 5, 4213.",
]
for r in REFS:
    story.append(Paragraph(r, ParagraphStyle("ref", parent=S_body, fontSize=9.5, leading=14, leftIndent=14, firstLineIndent=-14)))
story.append(PageBreak())
story.append(Paragraph("Índice Remissivo", S_h1))
IDX = [
    ("algoritmo ZCA", "cap. 11"), ("anterioridade", "cap. 5"), ("aproximação certificada", "cap. 11"),
    ("ASK/CONTRACT/MODEL/BUDGET/REQUIRE", "caps. 8, 9"), ("auditoria", "caps. 12, 14"),
    ("certificado forjado", "cap. 6"), ("CHSH", "caps. 10, 14"), ("contrato ε-B-M", "caps. 8, 15"),
    ("custo da análise", "cap. 15"), ("decisão epistêmica", "caps. 9, 10"), ("escada, regra de custo", "caps. 11, 15"),
    ("fator 11.147 (laço híbrido)", "caps. 2, 14"), ("falsa eliminação, taxa", "cap. 14"),
    ("formalização", "cap. 8"), ("gramática (Lark)", "apêndice A"), ("honestidade operacional", "caps. 10, 14, 16"),
    ("indecidibilidade", "caps. 3, 15"), ("kernel de decisão", "caps. 10, 13"), ("ledger", "cap. 12"),
    ("limites (lower bounds)", "cap. 15"), ("NetBenefit", "caps. 14, 16"), ("NEXA-IR", "cap. 13"),
    ("nota PRASHNA", "cap. 9"), ("numeral Z", "caps. 4, 10"), ("OpenQASM 3.0", "caps. 9, 13"),
    ("pilares (quatro)", "cap. 13"), ("plug LLM", "caps. 9, 16"), ("problema da parada", "caps. 3, 8, 15"),
    ("recibo SHA3-256", "caps. 12, 14"), ("recibo #25", "caps. 10, 12"), ("regressão do kernel", "cap. 14"),
    ("šūnya / ṣifr / zefiro", "cap. 4"), ("tolerância ε", "cap. 8"), ("tipagem T1-T6", "caps. 9, 13"),
    ("veredito Z (CHSH real)", "caps. 10, 14"), ("verificador formal de circuitos", "caps. 13, 14, apêndice B"),
    ("violação de Bell", "caps. 10, 14"), ("zero, jornada do", "cap. 4"), ("nano quântico", "cap. 17"),
]
idx_rows = "".join(f"<td valign='top' width='33%'>{a} — <b>{b}</b></td>" + ("</tr><tr>" if (i % 3 == 2) else "")
                   for i, (a, b) in enumerate(IDX))
story.append(Paragraph("<table width='100%'><tr>" + idx_rows + "</tr></table>",
               ParagraphStyle("idxt", parent=S_body, fontSize=10, leading=17)))
story.append(PageBreak())
story.append(Paragraph("Agradecimentos", S_h1))
story.append(Paragraph("À comunidade IBM Quantum, pelo plano aberto que permite a um laboratório independente "
    "provar linguagem própria em hardware físico. Ao ecossistema multiagente Dexia Hub — Planner, Prover, "
    "Executor, Verifier, Auditor e Orchestrator — pela disciplina de engenharia que sustenta cada recibo. "
    "E ao leitor que chegou até aqui fazendo a pergunta certa: será que precisava?", S_body))
story.append(Spacer(1, 24))
story.append(Paragraph("Colofão", S_h2))
story.append(Paragraph("Edição íntegra composta em A4 pelo kernel Zephyrum v1.4 e publicada pela "
    "MGN Science Editions. Provas em hardware quântico real executadas no plano aberto da IBM Quantum "
    "(ibm_marrakesh) pelo ecossistema multiagente Dexia Hub. Todos os vereditos, honestos.", S_body))

story.append(NextPageTemplate("capa"))
story.append(PageBreak())
story.append(Spacer(1, 9 * cm))
story.append(Paragraph("ZEPHIRUM", ParagraphStyle("bc1", fontName="DVSB", fontSize=30, leading=36, textColor=NAVY, alignment=1)))
story.append(Paragraph("A Computação Antes da Execução", ParagraphStyle("bc2", fontName="DVS", fontSize=14, leading=20, textColor=GOLD, alignment=1)))
story.append(Spacer(1, 20))
story.append(Paragraph('"O veredito mais honesto que um sistema pode dar é: ainda não sei — e aqui está o recibo."', ParagraphStyle("bc3", fontName="DVSO", fontSize=11.5, leading=17, textColor=MUT, alignment=1)))
story.append(Spacer(1, 26))
story.append(Paragraph("SERENA QUANTUM SOLUTIONS · MGN Science Editions", ParagraphStyle("bc4", fontName="DVS", fontSize=11, leading=16, textColor=INK, alignment=1)))
story.append(Paragraph("ZYQL — a linguagem quântica | the quantum language", ParagraphStyle("bc5", fontName="DVS", fontSize=9.5, leading=14, textColor=MUT, alignment=1)))

doc = Livro(f"{TMP}/livro_zephirum_integral.pdf", pagesize=A4,
            leftMargin=2.4 * cm, rightMargin=2.4 * cm, topMargin=2.2 * cm, bottomMargin=2.2 * cm)

# TOC via multiBuild
def after_flow(self, fl):
    from reportlab.platypus.flowables import Flowable
    if isinstance(fl, Paragraph) and fl.style.name.startswith("h1c"):
        txt = fl.getPlainText()
        self.notify("TOCEntry", (0, txt, self.page))
        key = f"h1c-{self.page}-{txt[:12]}"
        self.canv.bookmarkPage(key)
        self.canv.addOutlineEntry(txt, key, level=0, closed=False)
    elif isinstance(fl, Paragraph) and fl.style.name in ("h1",):
        txt = fl.getPlainText()
        if txt.startswith("Apêndice") or txt in ("Sumário", "Ficha Catalográfica", "Prefácio"):
            self.notify("TOCEntry", (1, txt, self.page))
BaseDocTemplate.afterFlowable = after_flow

doc.multiBuild(story)
print("PÁGINAS FINAIS:", doc.page)

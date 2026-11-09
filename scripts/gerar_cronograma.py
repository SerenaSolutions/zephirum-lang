#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Gera o cronograma em HTML (Vercel), PPTX, CSV e Markdown a partir de um YAML.

Fonte unica: docs/cronograma/zephirum_60d.yaml
Saidas:
  site/cronograma/index.html      -> publicado em zephirum.vercel.app/cronograma
  docs/cronograma/cronograma.pptx -> deck para apresentacao
  docs/cronograma/cronograma.csv  -> dados para planilha
  docs/cronograma/cronograma.md   -> leitura rapida no GitHub
"""
from __future__ import annotations

import csv
import datetime as dt
import html
import pathlib

import yaml

RAIZ = pathlib.Path(__file__).resolve().parents[1]
FONTE = RAIZ / "docs/cronograma/zephirum_60d.yaml"

CORES = {
    "Fechamento": "#7c6a4f",
    "Consolidacao": "#2f5d50",
    "Integracao": "#1f4e79",
    "Verificacao": "#6b3f69",
    "Produto": "#8a5a1e",
    "Ciencia": "#3f3f63",
}


def carregar() -> dict:
    return yaml.safe_load(FONTE.read_text(encoding="utf-8"))


def d(valor: str) -> dt.date:
    return dt.date.fromisoformat(valor)


def gantt(dados: dict) -> str:
    zero, fim = d(dados["dia_zero"]), d(dados["fim"])
    total = (fim - zero).days + 1
    linhas = []
    for m in dados["marcos"]:
        ini, f = d(m["ini"]), d(m["fim"])
        esq = (ini - zero).days / total * 100
        larg = max((f - ini).days + 1, 1) / total * 100
        cor = CORES.get(m["fase"], "#555")
        feito = m.get("estado") == "feito"
        rotulo = f'{m["id"]:02d}'
        linhas.append(
            f'<div class="g-linha" title="{html.escape(m["marco"])} · {m["ini"]} a {m["fim"]}">'
            f'<span class="g-id">{rotulo}</span>'
            f'<div class="g-trilho"><div class="g-barra{" feito" if feito else ""}" '
            f'style="left:{esq:.2f}%;width:{larg:.2f}%;background:{cor}">'
            f'{html.escape(m["fase"])}</div></div></div>'
        )
    marcas = []
    for mes in (dt.date(2026, 11, 16), dt.date(2026, 12, 1), dt.date(2026, 12, 16),
                dt.date(2027, 1, 1), dt.date(2027, 1, 9)):
        pos = (mes - zero).days / total * 100
        marcas.append(f'<div class="g-mes" style="left:{pos:.2f}%">'
                      f'{mes.strftime("%d/%m")}</div>')
    return f'<div class="gantt"><div class="g-eixo">{"".join(marcas)}</div>{"".join(linhas)}</div>'


def tabela(dados: dict) -> str:
    linhas = []
    for m in dados["marcos"]:
        feito = m.get("estado") == "feito"
        gate = f'<span class="gate">{m["gate"]}</span>' if m.get("gate") else ""
        linhas.append(
            f'<tr class="{"feito" if feito else ""}">'
            f'<td class="num">{m["id"]:02d}</td>'
            f'<td class="data">{d(m["ini"]).strftime("%d/%m")}<br><span>{d(m["fim"]).strftime("%d/%m")}</span></td>'
            f'<td><span class="fase" style="--c:{CORES.get(m["fase"], "#555")}">{html.escape(m["fase"])}</span></td>'
            f'<td class="marco">{html.escape(m["marco"])} {gate}</td>'
            f'<td>{html.escape(m["entregavel"])}</td>'
            f'<td class="aceite">{html.escape(m["aceite"])}</td></tr>'
        )
    return "".join(linhas)


def pagina(dados: dict) -> str:
    gates = "".join(
        f'<div class="card"><div class="card-h">{g["id"]}</div>'
        f'<p>{html.escape(g["pergunta"])}</p>'
        f'<p class="sub">Se reprovar: {html.escape(g["se_reprovar"])}</p></div>'
        for g in dados["gates"])
    deps = "".join(
        f'<tr><td>{html.escape(x["item"])}</td><td>{html.escape(x["de"])}</td>'
        f'<td>{html.escape(x["efeito"])}</td></tr>' for x in dados["dependencias"])
    total = sum(1 for m in dados["marcos"] if m.get("estado") == "feito")
    return f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Cronograma ZEPHIRUM ZYQL · 60 dias</title>
<style>
:root{{--bg:#0f1216;--surf:#161a20;--lin:#252b33;--fg:#e8e6e1;--dim:#9aa3ad;--acc:#d97757}}
@media (prefers-color-scheme:light){{:root{{--bg:#f7f5f1;--surf:#fff;--lin:#e2ddd4;--fg:#1a1a1a;--dim:#5f6672;--acc:#b5563a}}}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--fg);
font:16px/1.55 ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}}
.wrap{{max-width:1180px;margin:0 auto;padding:48px 20px 80px}}
header{{border-bottom:1px solid var(--lin);padding-bottom:28px;margin-bottom:36px}}
.kicker{{font-size:12px;letter-spacing:.16em;text-transform:uppercase;color:var(--acc);font-weight:700}}
h1{{font-size:clamp(28px,4.4vw,46px);line-height:1.08;margin:12px 0 10px;letter-spacing:-.02em}}
.lead{{color:var(--dim);max-width:70ch;margin:0}}
.marca{{display:flex;gap:28px;flex-wrap:wrap;margin-top:22px;font-size:14px;color:var(--dim)}}
.marca b{{display:block;color:var(--fg);font-size:22px;font-variant-numeric:tabular-nums}}
h2{{font-size:13px;letter-spacing:.14em;text-transform:uppercase;color:var(--dim);
margin:52px 0 16px;font-weight:700}}
.gantt{{background:var(--surf);border:1px solid var(--lin);border-radius:14px;padding:20px 20px 14px}}
.g-eixo{{position:relative;height:18px;margin-bottom:6px}}
.g-mes{{position:absolute;font-size:11px;color:var(--dim);transform:translateX(-50%)}}
.g-linha{{display:flex;align-items:center;gap:10px;margin:3px 0}}
.g-id{{width:22px;font-size:11px;color:var(--dim);font-variant-numeric:tabular-nums}}
.g-trilho{{position:relative;flex:1;height:22px;background:
linear-gradient(90deg,var(--lin) 1px,transparent 1px) 0 0/8.33% 100%}}
.g-barra{{position:absolute;top:3px;height:16px;border-radius:4px;font-size:10px;
color:#fff;padding:0 6px;white-space:nowrap;overflow:hidden;opacity:.92;
display:flex;align-items:center}}
.g-barra.feito{{outline:2px solid var(--acc);outline-offset:1px}}
table{{width:100%;border-collapse:collapse;background:var(--surf);
border:1px solid var(--lin);border-radius:14px;overflow:hidden;font-size:14px}}
th{{text-align:left;font-size:11px;letter-spacing:.1em;text-transform:uppercase;
color:var(--dim);padding:12px 14px;border-bottom:1px solid var(--lin);font-weight:600}}
td{{padding:12px 14px;border-bottom:1px solid var(--lin);vertical-align:top}}
tr:last-child td{{border-bottom:none}}
tr.feito{{background:rgba(217,119,87,.08)}}
.num{{color:var(--dim);font-variant-numeric:tabular-nums;width:34px}}
.data{{white-space:nowrap;font-variant-numeric:tabular-nums;width:76px}}
.data span{{color:var(--dim);font-size:12px}}
.fase{{font-size:11px;padding:3px 8px;border-radius:999px;white-space:nowrap;
border:1px solid var(--c);color:var(--c)}}
.marco{{font-weight:600}}
.gate{{font-size:10px;padding:2px 6px;border-radius:4px;background:var(--acc);
color:#fff;margin-left:6px;vertical-align:middle}}
.aceite,.sub{{color:var(--dim)}}
.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:14px}}
.card{{background:var(--surf);border:1px solid var(--lin);border-radius:12px;padding:16px}}
.card-h{{font-weight:800;color:var(--acc);font-size:13px;letter-spacing:.1em}}
.card p{{margin:8px 0 0;font-size:14px}}
footer{{margin-top:60px;padding-top:20px;border-top:1px solid var(--lin);
color:var(--dim);font-size:13px}}
@media (max-width:720px){{.tabela-wrap{{overflow-x:auto}}table{{min-width:760px}}}}
</style></head><body><div class="wrap">
<header>
<div class="kicker">Serena Quantum Solutions · plano de execução</div>
<h1>Cronograma ZEPHIRUM ZYQL<br>60 dias após o merge</h1>
<p class="lead">Marco zero em 09/11/2026, 13:00 BRT, quando o PR #1433 entrou na
<code>main</code> do Qiskit/ecosystem. O que foi aceito é um metadado de membro, não a
validação científica da linguagem. Este cronograma separa as duas coisas.</p>
<div class="marca">
<div><b>{len(dados["marcos"])}</b>marcos técnicos</div>
<div><b>{len(dados["gates"])}</b>gates de decisão</div>
<div><b>{total}</b>concluído</div>
<div><b>09/01/2027</b>fim previsto</div>
</div></header>

<h2>Linha do tempo</h2>
{gantt(dados)}

<h2>Marcos, entregáveis e critério de aceite</h2>
<div class="tabela-wrap"><table>
<thead><tr><th>#</th><th>Janela</th><th>Fase</th><th>Marco técnico</th>
<th>Entregável verificável</th><th>Critério de aceite</th></tr></thead>
<tbody>{tabela(dados)}</tbody></table></div>

<h2>Gates: o que impede avançar</h2>
<div class="cards">{gates}</div>

<h2>Dependências fora do nosso controle</h2>
<div class="tabela-wrap"><table>
<thead><tr><th>Item</th><th>Depende de</th><th>Efeito se atrasar</th></tr></thead>
<tbody>{deps}</tbody></table></div>

<footer>Gerado automaticamente de <code>docs/cronograma/zephirum_60d.yaml</code>.
Nenhuma data deste documento é promessa científica: são janelas de trabalho com
critério de aceite declarado.</footer>
</div></body></html>"""


def deck(dados: dict) -> pathlib.Path:
    from pptx import Presentation
    from pptx.dml.color import RGBColor
    from pptx.util import Emu, Pt

    prs = Presentation()
    prs.slide_width, prs.slide_height = Emu(12192000), Emu(6858000)
    escuro = RGBColor(0x0F, 0x12, 0x16)
    claro = RGBColor(0xE8, 0xE6, 0xE1)
    dim = RGBColor(0x9A, 0xA3, 0xAD)
    acc = RGBColor(0xD9, 0x77, 0x57)

    def novo(titulo: str, sub: str = ""):
        s = prs.slides.add_slide(prs.slide_layouts[6])
        f = s.background.fill
        f.solid()
        f.fore_color.rgb = escuro
        tb = s.shapes.add_textbox(Emu(640080), Emu(457200), Emu(10972800), Emu(1005840))
        p = tb.text_frame.paragraphs[0]
        p.text = titulo
        p.font.size, p.font.bold, p.font.color.rgb = Pt(30), True, claro
        if sub:
            tb2 = s.shapes.add_textbox(Emu(640080), Emu(1143000), Emu(10972800), Emu(460000))
            p2 = tb2.text_frame.paragraphs[0]
            p2.text = sub
            p2.font.size, p2.font.color.rgb = Pt(13), dim
        return s

    s = prs.slides.add_slide(prs.slide_layouts[6])
    f = s.background.fill; f.solid(); f.fore_color.rgb = escuro
    tb = s.shapes.add_textbox(Emu(914400), Emu(2011680), Emu(10363200), Emu(2000000))
    tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.text = "ZEPHIRUM ZYQL"
    p.font.size, p.font.bold, p.font.color.rgb = Pt(54), True, claro
    p2 = tf.add_paragraph(); p2.text = "Cronograma de 60 dias após o merge no Qiskit/ecosystem"
    p2.font.size, p2.font.color.rgb = Pt(20), dim
    p3 = tf.add_paragraph(); p3.text = "Marco zero: 09/11/2026, 13:00 BRT · PR #1433"
    p3.font.size, p3.font.color.rgb = Pt(13), acc

    s = novo("O que o merge significa", "Aceitação de metadado não é validação científica")
    caixas = [
        ("Foi aceito", "Uma entrada em resources/members: licença, versão, links, uso de Qiskit"),
        ("Não foi aceito", "A semântica trivalente, o recibo assinado, os benchmarks"),
        ("Consequência", "O bot do ecossistema sincroniza versão e licença a partir do PyPI"),
    ]
    for i, (t, c) in enumerate(caixas):
        tb = s.shapes.add_textbox(Emu(640080 + i * 3700000), Emu(2400000), Emu(3400000), Emu(1800000))
        tf = tb.text_frame; tf.word_wrap = True
        p = tf.paragraphs[0]; p.text = t
        p.font.size, p.font.bold, p.font.color.rgb = Pt(17), True, acc
        p2 = tf.add_paragraph(); p2.text = c
        p2.font.size, p2.font.color.rgb = Pt(13), claro

    fases = ["Consolidacao", "Integracao", "Verificacao", "Produto", "Ciencia"]
    for fase in fases:
        ms = [m for m in dados["marcos"] if m["fase"] == fase]
        s = novo(f"Fase · {fase}", f"{ms[0]['ini']} a {ms[-1]['fim']} · {len(ms)} marcos")
        linhas = []
        for m in ms:
            gate = f" [{m['gate']}]" if m.get("gate") else ""
            linhas.append(f"{m['id']:02d} · {m['ini'][5:]} a {m['fim'][5:]} · {m['marco']}{gate}")
        tb = s.shapes.add_textbox(Emu(640080), Emu(1700000), Emu(10972800), Emu(4200000))
        tf = tb.text_frame; tf.word_wrap = True
        for i, l in enumerate(linhas):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.text = l
            p.font.size, p.font.color.rgb = Pt(14), claro
            p.space_after = Pt(10)

    s = novo("Gates de decisão", "Sem estes, o marco seguinte não abre")
    tb = s.shapes.add_textbox(Emu(640080), Emu(1700000), Emu(10972800), Emu(4200000))
    tf = tb.text_frame; tf.word_wrap = True
    for i, g in enumerate(dados["gates"]):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        r = p.add_run(); r.text = f"{g['id']}  "
        r.font.bold, r.font.color.rgb = True, acc
        r2 = p.add_run(); r2.text = g["pergunta"]
        r2.font.color.rgb = claro
        r3 = p.add_run(); r3.text = f"   → se reprovar: {g['se_reprovar']}"
        r3.font.color.rgb = dim
        p.font.size = Pt(14); p.space_after = Pt(14)

    s = novo("Dependências fora do nosso controle", "O que atrasa por decisão de terceiro")
    tb = s.shapes.add_textbox(Emu(640080), Emu(1700000), Emu(10972800), Emu(4200000))
    tf = tb.text_frame; tf.word_wrap = True
    for i, x in enumerate(dados["dependencias"]):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = f"{x['item']} · depende de {x['de']} · {x['efeito']}"
        p.font.size, p.font.color.rgb = Pt(13), claro
        p.space_after = Pt(12)

    s = novo("Próximos 7 dias", "O que eu faria primeiro, em ordem")
    acoes = [
        "1. Guard de metadado no CI: impede que o bot do ecossistema receba versão ou licença divergente",
        "2. Circuitos equivalentes nos três caminhos: ZYQL puro, Qiskit puro, ZYQL via Qiskit",
        "3. Decisão de custódia da chave ML-DSA-44: sem ela, todo recibo é anônimo",
        "4. Rodar o job pesado do harness e ter docling e embeddings com evidência real",
    ]
    tb = s.shapes.add_textbox(Emu(640080), Emu(1700000), Emu(10972800), Emu(4200000))
    tf = tb.text_frame; tf.word_wrap = True
    for i, a in enumerate(acoes):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = a
        p.font.size, p.font.color.rgb = Pt(15), claro
        p.space_after = Pt(16)

    saida = RAIZ / "docs/cronograma/cronograma.pptx"
    prs.save(saida)
    return saida


def csv_(dados: dict) -> pathlib.Path:
    saida = RAIZ / "docs/cronograma/cronograma.csv"
    with saida.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "inicio", "fim", "fase", "marco", "entregavel", "aceite", "gate"])
        for m in dados["marcos"]:
            w.writerow([m["id"], m["ini"], m["fim"], m["fase"], m["marco"],
                        m["entregavel"], m["aceite"], m.get("gate", "")])
    return saida


def md(dados: dict) -> pathlib.Path:
    linhas = ["# Cronograma ZEPHIRUM ZYQL · 60 dias", "",
              "Marco zero: 09/11/2026, 13:00 BRT (PR #1433 na `main` do Qiskit/ecosystem).", "",
              "| # | Janela | Fase | Marco | Aceite | Gate |", "|---|---|---|---|---|---|"]
    for m in dados["marcos"]:
        linhas.append(f"| {m['id']:02d} | {m['ini']} a {m['fim']} | {m['fase']} | "
                      f"{m['marco']} | {m['aceite']} | {m.get('gate', '')} |")
    linhas += ["", "## Gates", ""]
    linhas += [f"- **{g['id']}** {g['pergunta']} (se reprovar: {g['se_reprovar']})"
               for g in dados["gates"]]
    linhas += ["", "## Dependências", ""]
    linhas += [f"- {x['item']}: depende de {x['de']}; {x['efeito']}" for x in dados["dependencias"]]
    saida = RAIZ / "docs/cronograma/cronograma.md"
    saida.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    return saida


def main() -> int:
    dados = carregar()
    (RAIZ / "site/cronograma").mkdir(parents=True, exist_ok=True)
    pagina_html = RAIZ / "site/cronograma/index.html"
    pagina_html.write_text(pagina(dados), encoding="utf-8")
    for caminho in (pagina_html, deck(dados), csv_(dados), md(dados)):
        print(f"{caminho.relative_to(RAIZ)} · {caminho.stat().st_size} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

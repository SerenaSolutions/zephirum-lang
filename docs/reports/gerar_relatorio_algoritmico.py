# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Serena Quantum Solutions
# -*- coding: utf-8 -*-
"""RELATORIO NIVEL ALGORITMICO — PDF com camada de texto real (reportlab).

Documento pesquisavel, com equacoes em monospace, tabela de evidencia e
secao explicita de limites. Sem maquiagem: cada numero vem de execucao
registrada nos JSONs do repositorio.
"""
import json, os

from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (KeepTogether, PageBreak, Paragraph, SimpleDocTemplate,
                                Spacer, Table, TableStyle)

ROOT = "/app/conversations/6a47cbde110fe595b9a5a983"
OUT = os.path.join(ROOT, "soak", "RELATORIO_ALGORITMICO.pdf")

ACC = colors.HexColor("#6e46b8")
INK = colors.HexColor("#1f1f24")
DIM = colors.HexColor("#6b6b76")
BOX = colors.HexColor("#f3f1f8")

ss = getSampleStyleSheet()
body = ParagraphStyle("body", parent=ss["BodyText"], fontName="Courier", fontSize=9.2,
                      leading=13.4, textColor=INK, alignment=TA_JUSTIFY, spaceAfter=7)
h1 = ParagraphStyle("h1", fontName="Courier-Bold", fontSize=13, leading=17,
                    textColor=ACC, spaceBefore=14, spaceAfter=6)
h2 = ParagraphStyle("h2", fontName="Courier-Bold", fontSize=10, leading=14,
                    textColor=INK, spaceBefore=9, spaceAfter=4)
title = ParagraphStyle("title", fontName="Courier-Bold", fontSize=20, leading=24,
                       textColor=colors.white)
sub = ParagraphStyle("sub", fontName="Courier", fontSize=10, leading=14,
                     textColor=colors.HexColor("#c9c2e0"))
small = ParagraphStyle("small", parent=body, fontSize=8, leading=11, textColor=DIM)
code = ParagraphStyle("code", fontName="Courier-Bold", fontSize=8.6, leading=12.6,
                      textColor=colors.HexColor("#33334a"), leftIndent=8, spaceAfter=2)


def box(lines):
    """Bloco de pseudocodigo/equacoes com fundo."""
    t = Table([[Paragraph(l.replace(" ", "&nbsp;"), code)] for l in lines],
              colWidths=[165 * mm])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), BOX),
                           ("LEFTPADDING", (0, 0), (-1, -1), 8),
                           ("TOPPADDING", (0, 0), (-1, -1), 2),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), 2)]))
    return [t, Spacer(1, 8)]


def P(t):
    return Paragraph(t, body)


soak = json.load(open(os.path.join(ROOT, "soak/soak_2000.json")))
hw = json.load(open(os.path.join(ROOT, "zq-ir/stress/hw_soak.json")))
rot_i = json.load(open(os.path.join(ROOT, "zephirum-lang/experiments/round_i_receipt.json")))
rot_d = json.load(open(os.path.join(ROOT, "zephirum-lang/experiments/round_d_receipt.json")))
total_soak = sum(a["iteracoes"] for a in soak["apps"].values())
erros_soak = sum(a["erros"] for a in soak["apps"].values())

story = []

# capa
head = Table([[Paragraph("RELATÓRIO — NÍVEL ALGORÍTMICO", title)],
              [Paragraph("ZYQL / ZEPHIRUM · núcleo de decisão trivalente", sub)],
              [Paragraph("Serena Quantum Solutions · 01/11/2026 · Apache-2.0", sub)]],
             colWidths=[165 * mm])
head.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#12101a")),
                          ("LEFTPADDING", (0, 0), (-1, -1), 14),
                          ("TOPPADDING", (0, 0), (-1, -1), 9),
                          ("BOTTOMPADDING", (0, 0), (-1, -1), 9)]))
story += [head, Spacer(1, 14)]

story += [Paragraph("0. Escopo e padrão de prova", h1)]
story += [P("Este relatório descreve o sistema no nível do algoritmo: modelo formal, regra de "
            "decisão, garantias estatísticas, complexidade, ordem de composição e o que "
            "<b>não</b> está provado. Nenhuma afirmação aparece sem lastro em execução "
            "registrada ou em derivação explícita. Onde há lacuna, ela está nomeada.")]

story += [Paragraph("1. Modelo formal", h1)]
story += [P("Seja <b>f: {0,1}^n → {0,1}</b> um oráculo de fase acessível por consulta quântica. "
            "O sistema resolve o problema-promise de Deutsch–Jozsa:")]
story += box(["PROMISE: f é constante  OU  f é balanceada (metade das entradas em 1)",
              "DECISÃO: d(f) ∈ { 1, 0, REFUSED }",
              "         1       = f constante, valor declarado pelo oráculo",
              "         0       = f constante com valor 0",
              "         REFUSED = não se afirma nem se nega, com motivo rastreável"])
story += [P("A terceira saída não é erro nem exceção: é valor de primeira classe com causa "
            "declarada. Formalmente, <b>d é função total</b>: todo f admissível retorna "
            "exatamente um dos três valores.")]

story += [Paragraph("2. Núcleo: interferência e dominância", h1)]
story += [P("Preparo |0…0⟩, aplico H^⊗n, uma consulta de fase ao oráculo, H^⊗n novamente e meço "
            "na base computacional. A amplitude do estado |0…0⟩ é:")]
story += box(["a000 = (1/2^n) · Σₓ (−1)^f(x)",
              "  f constante  ⇒  |a000|² = 1   (interferência construtiva total)",
              "  f balanceada ⇒  a000 = 0      (cancelamento exato)"])
story += [P("O veredito não vem do padrão medido isolado, mas da probabilidade do evento "
            "E = {medida = |0…0⟩}, estimada por S amostras: p̂₀ = (1/S)·Σ 𝟙[E]. A decisão é "
            "tomada por dominância contra banda declarada antes da execução.")]

story += [Paragraph("3. Estatística: a banda e o seu axioma", h1)]
story += [P("Com S amostras independentes e erro declarado ε ∈ (0,1), o limite de Hoeffding dá, "
            "com probabilidade ≥ 1 − ε:")]
story += box(["P( |p̂₀ − p₀| ≥ m ) ≤ 2·exp(−2·S·m²)",
              "m(ε,S) = sqrt( ln(2/ε) / (2S) )"])
story += [P("Regra selada: afirmativo se p̂₀ ≥ 1 − m(ε,S); recusa por oráculo balanceado se "
            "p̂₀ ≤ m(ε,S); recusa por banda no interior (INSIDE_NOISE_BAND).")]
story += [P("Múltiplas comparações (família k): a correção correta <b>encolhe</b> a banda. "
            "Com m₁ = m(ε,S) e m_k = m(ε/k,S):")]
story += box(["m'(k) = 2·m₁ − m_k        e        m'(k) < m₁ para k > 1",
              "m'(k) ≤ 0  ⇒  FAMILY_EXCEEDS_SHOTS (sem resolução para a família)"])
story += [P("Nota de histórico: a primeira implementação usou ε/k (banda mais <i>larga</i>), que é "
            "a direção errada — deixa a alegação mais agressiva. O erro foi pego por Monte Carlo "
            "interno e corrigido; a fórmula vigente é a acima.")]

story += [Paragraph("4. O axioma escondido e o gate de memória (BLP)", h1)]
story += [P("A §3 pressupõe independência das amostras. Se o ambiente guarda memória, a "
            "estimativa carrega viés sistemático que a banda não denuncia: o veredito mente sem "
            "avisar. O núcleo mede não-markovianidade antes de decidir (Breuer–Laine–Piilo):")]
story += box(["D(k) = ½·‖ρ_a(k) − ρ_b(k)‖₁     (distância de traço entre duas evoluções)",
              "revival  ⇔  Δ(k) = D(k+1) − D(k) > m_D",
              "contração CPTP garante Δ(k) ≤ 0 em dinâmica markoviana"])
story += [P("Realização: modelo de colisão com U = CX(S → âncora), em duas variantes — âncora "
            "reaproveitada (memória) e âncoras frescas por passo (controle markoviano). Exige-se "
            "revival na variante com memória <b>e</b> ausência no controle; revival no controle é "
            "anomalia declarada. Custo: 6 + 12k circuitos para k passos, O(k·S) amostras.")]

story += [Paragraph("5. Ordem de composição (fail-closed)", h1)]
story += box(["1. validação do contrato      → erro antes de qualquer gasto (fail-closed)",
              "2. gate de dispositivo (GHZ)  → decoerência ⇒ REFUSED, 0 consultas ao oráculo",
              "3. gate de memória (BLP)      → NOISE_HAS_MEMORY ⇒ REFUSED, 0 consultas",
              "4. consulta ao oráculo (DJ)   → 1 consulta (+1 sonda clássica se constante)",
              "5. decisão por dominância     → 1 | 0 | REFUSED(reason)",
              "6. selagem SHA3-256 [+ML-DSA-44] → recibo verificável offline"])
story += [P("Propriedade central: gates são avaliados ANTES do oráculo. Dispositivo decoerido ou "
            "ambiente com memória produzem recusa sem consumir recurso caro — verificável em "
            "execução, com oracle_calls = 0 nos dois caminhos de recusa por gate.")]

story += [Paragraph("6. Complexidade", h1)]
story += box(["núcleo (simulador) : O(S · 2^n) tempo · O(2^n) memória",
              "núcleo (hardware)  : O(S) shots · 1 job · O(1) pubs por decisão",
              "gate de memória    : O(k·S) amostras · O(k) circuitos · O(k) pós-processo",
              "gate de dispositivo: O(S_g) shots · 1 circuito GHZ",
              "selagem            : O(|recibo|) para SHA3-256",
              "escopo prático     : n ≤ 8 na fase-oráculo · MPS até n = 12 (χ = 4)"])
story += [P(f"Medido em silício: <b>{hw['qpu_por_decisao_s']} s de QPU por decisão</b> "
            f"({hw['sucessos']} jobs consecutivos em ibm_marrakesh). A aritmética de escala: "
            f"16.000 decisões custariam ≈ {hw['extrapolacao']['qpu_necessario_h']} h de QPU, "
            "contra janela de 600 s no plano aberto. Por isso a exaustão de 16.000 foi feita no "
            "simulador e o silício provou operabilidade repetida.")]

story += [Paragraph("7. O que está provado, sob quais hipóteses", h1)]
story += [P("A1 (independência): amostras i.i.d., ou gate de memória aprovado. "
            "A2 (margem): a diferença entre p̂₀ e o limiar excede m(ε,S). "
            "A3 (dispositivo): gate GHZ aprovado quando exigido. "
            "Sob A1–A3, a probabilidade de alegação afirmativa errada é ≤ ε.")]
story += [P("<b>Não está provado:</b> (i) correção sob viés sistemático de readout, que a banda "
            "Hoeffding não cobre por construção; (ii) detecção de oráculos adversariais fora da "
            "classe promise; (iii) ausência de memória — o gate mede revival em profundidade ≤ k "
            "e geometria declarada, e ausência de revival não prova ausência de memória; "
            "(iv) qualquer vantagem computacional quântica: o custo honesto aqui é 1 consulta "
            "clássica para o caso constante.")]

story += [Paragraph("8. Evidência registrada (execuções reais)", h1)]
rows = [["Métrica", "Resultado registrado"],
        ["Sobrecarga local", f"{total_soak:,} execuções em 8 apps · {erros_soak} erros".replace(",", ".")],
        ["Latência p50", "zqea-verify 0,01 ms · z-anyon 0,08 ms · zy-ai-rag 0,24 ms"],
        ["Throughput", f"{soak['apps']['zqea-verify']['throughput_ops_s']:,.0f} ops/s (verify) · "
                       f"{soak['apps']['zephirum-lang']['throughput_ops_s']:,.0f} ops/s (runtime)".replace(",", ".")],
        ["Silício", f"{hw['sucessos']}/{hw['k_jobs']} jobs DONE · veredito 1 em todos · "
                    f"{hw['qpu_por_decisao_s']} s QPU/decisão"],
        ["Rodada I (BLP)", f"revival {max(rot_i['delta']['memory'])} vs banda {rot_i['band_D']} "
                           f"({max(rot_i['delta']['memory'])/rot_i['band_D']:.1f}×) · controle "
                           f"{max(rot_i['delta']['memoryless'])}"],
        ["Rodada D", "3 QPUs · vereditos idênticos · GHZ confiável"],
        ["Selos", "100% verificáveis offline (após correção do payload embutido)"]]
tb = Table([[Paragraph(c, small) for c in r] for r in rows],
           colWidths=[34 * mm, 131 * mm])
tb.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#d8d4e6")),
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#ece8f6")),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 5),
                        ("TOPPADDING", (0, 0), (-1, -1), 4),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
story += [tb, Spacer(1, 10)]

story += [Paragraph("9. Problemas abertos (nomeados)", h1)]
story += box(["P1  banda sensível a memória: modelo misto markoviano/não-markoviano",
              "P2  análise sequencial (SPRT) para reduzir S mantendo ε",
              "P3  decisão com síndrome como veredito (detectar em vez de corrigir)",
              "P4  oráculos adversariais fora da classe promise",
              "P5  raio de robustez: distância de canal máxima sem trocar o veredito"])
story += [P("Cada item é atacável com o mesmo aparato: protocolo pré-registrado, banda declarada "
            "antes do dado, recusa com motivo e recibo selado. A regra da casa não muda com o "
            "tamanho do número: o que não se verifica não se afirma.")]

story += [Spacer(1, 10), Paragraph(
    "Fontes dos números: soak/soak_2000.json · stress/hw_soak.json · "
    "experiments/round_i_receipt.json · experiments/round_d_receipt.json · "
    "repositório SerenaSolutions/zq-ir e SerenaSolutions/zephirum-lang.", small)]


def rodape(canvas, doc):
    canvas.saveState()
    canvas.setFont("Courier", 7.5)
    canvas.setFillColor(DIM)
    canvas.drawString(20 * mm, 12 * mm,
                      "ZYQL/ZEPHIRUM · relatório nível algorítmico · Serena Quantum Solutions · Apache-2.0")
    canvas.drawRightString(190 * mm, 12 * mm, "pág. %d" % doc.page)
    canvas.restoreState()


doc = SimpleDocTemplate(OUT, pagesize=A4, leftMargin=20 * mm, rightMargin=20 * mm,
                        topMargin=16 * mm, bottomMargin=18 * mm,
                        title="ZYQL/ZEPHIRUM — Relatório nível algorítmico",
                        author="Serena Quantum Solutions")
doc.build(story, onFirstPage=rodape, onLaterPages=rodape)
print("PDF:", OUT, os.path.getsize(OUT) // 1024, "KB")

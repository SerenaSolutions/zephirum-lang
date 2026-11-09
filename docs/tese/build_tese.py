from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                PageBreak, KeepTogether)

NAVY = colors.HexColor("#0F2A53"); ACCENT = colors.HexColor("#1F6FB2"); CINZA = colors.HexColor("#444444")
ss = getSampleStyleSheet()
def st(n, **k):
    base = dict(fontName="Times-Roman", fontSize=10.5, leading=15, spaceAfter=7, alignment=4)
    base.update(k); return ParagraphStyle(n, parent=ss["BodyText"], **base)
TITULO = st("t", fontName="Times-Bold", fontSize=19, leading=24, alignment=1, textColor=NAVY)
SUBT   = st("s", fontName="Times-Italic", fontSize=12.5, leading=17, alignment=1, textColor=CINZA)
AUTOR  = st("a", fontSize=12, alignment=1, leading=16)
H1     = st("h1", fontName="Times-Bold", fontSize=13.5, leading=18, spaceBefore=14, spaceAfter=6,
            alignment=0, textColor=NAVY)
H2     = st("h2", fontName="Times-Bold", fontSize=11.5, leading=15, spaceBefore=9, spaceAfter=4, alignment=0)
CORPO  = st("c")
ITEM   = st("i", leftIndent=14, spaceAfter=4)
LEGENDA= st("l", fontSize=9, leading=12, alignment=1, textColor=CINZA, spaceAfter=12)
CAIXA  = st("cx", fontSize=9.5, leading=13.5, leftIndent=10, rightIndent=10, backColor=colors.HexColor("#F2F5FA"),
            borderPadding=8, spaceBefore=8, spaceAfter=10)

def rodape(c, d):
    c.saveState(); c.setFont("Times-Roman", 8.5); c.setFillColor(CINZA)
    c.drawString(2.2*cm, 1.3*cm, "ZEPHIRUM(TM) · ZYQL(TM) · Serena Solutions")
    c.drawRightString(A4[0]-2.2*cm, 1.3*cm, f"{d.page}")
    c.setStrokeColor(colors.HexColor("#D5DCE6")); c.setLineWidth(0.5)
    c.line(2.2*cm, 1.65*cm, A4[0]-2.2*cm, 1.65*cm); c.restoreState()

doc = SimpleDocTemplate("TESE_ZEPHIRUM_DECISAO_VERIFICAVEL.pdf", pagesize=A4,
                        leftMargin=2.2*cm, rightMargin=2.2*cm, topMargin=2.0*cm, bottomMargin=2.2*cm,
                        title="Decisão verificável em hardware quântico ruidoso",
                        author="Reginaldo Pinezi Uhlmann")
E = []
# ---------------- CAPA ----------------
E += [Spacer(1, 3.2*cm),
      Paragraph("Decisão verificável em hardware quântico ruidoso", TITULO),
      Spacer(1, .35*cm),
      Paragraph("semântica de cinco estados e recibos criptograficamente assinados<br/>na linguagem ZYQL", SUBT),
      Spacer(1, 2.6*cm),
      Paragraph("Reginaldo Pinezi Uhlmann", AUTOR),
      Paragraph("ORCID 0009-0005-3212-5179", st("o", fontSize=10, alignment=1)),
      Spacer(1, .6*cm),
      Paragraph("Trabalho de conclusão de curso — Bacharelado em<br/>Inteligência Artificial e Ciência de Dados", AUTOR),
      Spacer(1, 2.4*cm),
      Paragraph("Serena Solutions · ZEPHIRUM(TM) / ZYQL(TM)", st("r", fontSize=10.5, alignment=1, textColor=CINZA)),
      Paragraph("Versão 1.0 · 9 de novembro de 2026", st("r2", fontSize=10, alignment=1, textColor=CINZA)),
      PageBreak()]

# ---------------- RESUMO ----------------
E += [Paragraph("Resumo", H1),
      Paragraph("Este trabalho formaliza e mede um protocolo em que toda decisão produzida por um programa "
      "quântico é reproduzível localmente, delimitada por incerteza declarada e atribuível a um emissor por "
      "assinatura criptográfica. A linguagem ZYQL trata a decisão como função parcial de cinco estados — 1, 0, "
      "REFUSED, INCONCLUSIVE e ERROR — e obriga o registro de um recibo assinado em Ed25519. Foram executados "
      "circuitos de Deutsch-Jozsa e de Bell em hardware supercondutor real, confrontados com referência exata "
      "calculada por aritmética inteira. Os vereditos coincidiram com a verdade matemática em todas as execuções, "
      "com p(000) de 0,9727 e 0,9644 no oráculo constante e 0,0000 no balanceado, e fidelidade de correlação de "
      "0,9404 no par emaranhado. A verificação é possível por terceiro que não se comunica com o emissor. "
      "Conclui-se que a verificabilidade é obtida sem vantagem quântica e sem correção de erro materializada em "
      "hardware — duas hipóteses que permanecem abertas.", CORPO),
      Paragraph("<b>Palavras-chave:</b> computação quântica; verificação de resultados; linguagem formal; "
      "semântica trivalente; recibos assinados.", CORPO)]

# ---------------- 1 ----------------
E += [Paragraph("1. Objetivo e problema", H1),
      Paragraph("Resultado de computador quântico chega ao usuário como número que ele não pode conferir. Três "
      "perguntas ficam sem resposta: o número veio do hardware que se afirma? foi alterado depois? a decisão "
      "declarada decorre da evidência bruta ou de um limiar arbitrário?", CORPO),
      Paragraph("O objetivo é construir um protocolo em que essas três perguntas tenham resposta verificável por "
      "terceiro, e medir o comportamento desse protocolo em hardware real sob ruído.", CORPO),
      Paragraph("<b>Pergunta de pesquisa.</b> Uma linguagem com semântica de decisão explícita e recibo assinado "
      "preserva a correção do veredito sob ruído real de hardware, e permite que a verificação ocorra sem acesso "
      "ao emissor?", CORPO)]

# ---------------- 2 ----------------
E += [Paragraph("2. Referencial mínimo", H1),
      Paragraph("A decisão estatística a partir de contagens usa a desigualdade de Hoeffding, que dá limite "
      "superior de desvio entre proporção observada e probabilidade real, válido para variáveis independentes e "
      "limitadas.", CORPO),
      Paragraph("A avaliação de algoritmos quânticos é tratada por Deutsch e Jozsa, cujo problema separa função "
      "constante de balanceada com uma consulta ao oráculo — a referência usada aqui. A simulação molecular por "
      "estimativa de fase segue a formulação usada na literatura de química quântica. A correção de erro é "
      "tratada pelo código de Steane e pela família de códigos de superfície. A síntese de portas com precisão "
      "arbitrária é tratada pelo algoritmo de Solovay-Kitaev. A assinatura usa Ed25519, e a sintaxe formal usa a "
      "notação ISO/IEC 14977.", CORPO)]

# ---------------- 3 ----------------
E += [Paragraph("3. Arquitetura do protocolo", H1),
      Paragraph("3.1 Semântica de cinco estados", H2),
      Paragraph("Tratar recusa como zero é erro de projeto: esconde a diferença entre 'a evidência sustenta o "
      "falso' e 'a política não permitiu decidir'. Por isso a linguagem separa: 1 e 0 para decisão sustentada, "
      "REFUSED para impedimento de política ou condição obrigatória, INCONCLUSIVE para evidência insuficiente, "
      "ERROR para falha técnica.", CORPO),
      Paragraph("3.2 Recibo e cadeia", H2),
      Paragraph("Cada execução emite recibo com blocos de identidade, execução, evidência e autenticidade. O "
      "recibo é assinado em Ed25519 sobre o hash SHA3-256 do corpo canônico, e encadeia o hash do recibo "
      "anterior. Assinatura é imposta pelo compilador, não opcional.", CORPO),
      Paragraph("3.3 Quatro níveis de evidência, distintos", H2),
      Paragraph("Integridade (o conteúdo não mudou), autenticidade (o emissor é quem diz), reprodutibilidade (a "
      "evidência bruta reproduz o número) e correção (a regra aplicada sobre a evidência dá aquele veredito). "
      "Nenhum nível implica o outro — confundir isso é a falha mais comum em alegação quântica.", CORPO)]

# ---------------- 4 ----------------
E += [Paragraph("4. Método", H1),
      Paragraph("4.1 Referência exata como verdade", H2),
      Paragraph("Antes de qualquer hardware, a resposta é calculada localmente por aritmética exata, sem "
      "amostragem. Isso permite comparar hardware contra verdade, não contra expectativa.", CORPO),
      Paragraph("4.2 Execução física", H2),
      Paragraph("Circuitos de Deutsch-Jozsa (constante e balanceado) e de Bell foram transpilados e executados em "
      "processador supercondutor de 156 qubits, em plano aberto, com 512, 1024 e 2048 tiros conforme o lote.", CORPO),
      Paragraph("4.3 Regra de decisão", H2),
      Paragraph("Com proporção observada p, tiros n e delta fixado, o limite é ε = sqrt(ln(2/δ)/2n). Decide-se 1 "
      "se p−ε>0,5; 0 se p+ε<0,5; caso contrário, INCONCLUSIVE. A regra é versionada e registrada no recibo.", CORPO),
      Paragraph("4.4 Auditoria cega", H2),
      Paragraph("Os artefatos foram entregues a agente independente, sem acesso às conclusões do autor, com a "
      "instrução de recalcular tudo, adulterar o recibo e tentar derrubar as garantias.", CORPO)]

# ---------------- 5 ----------------
E += [Paragraph("5. Resultados", H1)]
dados = [["Execução", "Circuito", "Tiros", "Observado", "ε (δ=0,05)", "Veredito", "Verdade"],
 ["H1, 2026-11-07", "DJ constante", "512", "p(000)=0,9727", "0,0600", "1", "1"],
 ["H1, 2026-11-07", "DJ balanceado", "512", "p(000)=0,0000", "0,0600", "0", "0"],
 ["Lote 2026-11-09", "DJ constante", "2048", "p(000)=0,9644", "0,0300", "1", "1"],
 ["Lote 2026-11-09", "DJ balanceado", "2048", "p(000)=0,0000", "0,0300", "0", "0"],
 ["Lote 2026-11-09", "Bell", "1024", "correlação 0,9404", "—", "—", "1,0000"]]
tb = Table(dados, colWidths=[3.0*cm, 2.9*cm, 1.4*cm, 3.4*cm, 2.2*cm, 1.7*cm, 1.6*cm], repeatRows=1)
tb.setStyle(TableStyle([
 ("BACKGROUND",(0,0),(-1,0),NAVY), ("TEXTCOLOR",(0,0),(-1,0),colors.white),
 ("FONTNAME",(0,0),(-1,0),"Times-Bold"), ("FONTSIZE",(0,0),(-1,-1),8.6),
 ("FONTNAME",(0,1),(-1,-1),"Times-Roman"),
 ("GRID",(0,0),(-1,-1),0.4,colors.HexColor("#C7D2E0")),
 ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white, colors.HexColor("#F4F7FB")]),
 ("ALIGN",(2,0),(-1,-1),"CENTER"), ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
 ("TOPPADDING",(0,0),(-1,-1),4), ("BOTTOMPADDING",(0,0),(-1,-1),4)]))
E += [tb, Paragraph("Tabela 1 — Execuções físicas e confronto com a verdade exata.", LEGENDA),
      Paragraph("Em todas as execuções o veredito coincidiu com a verdade matemática. A diferença entre 1,0000 e "
      "0,9644 no oráculo constante é ruído de hardware, delimitado por ε e declarado no recibo — não erro lógico.", CORPO),
      Paragraph("5.1 Provas exatas que sustentam o método", H2),
      Paragraph("Código de Steane [[7,1,3]]: 42/42 recuperações exatas de peso um por enumeração completa dos "
      "padrões de erro, com probabilidade lógica 1,578e-3 em taxa física de 1%. Código de superfície d=3: "
      "distância provada por enumeração e probabilidade lógica 1,423e-3, supressão de 7,03 vezes. Fatoração de "
      "Shor: decisão inteira exata para 15, 21 e 35, com partição completa do espaço de resultados. Estimativa de "
      "fase para H2: energia fundamental de −1,851199 Ha por forma fechada, desvio numérico de 6,56e-4, abaixo da "
      "resolução teórica de 2,05e-3.", CORPO)]

# ---------------- 6 ----------------
E += [Paragraph("6. Validação", H1),
      Paragraph("1. Assinatura Ed25519 verificada com chave pública: sete casos, incluindo adulteração de "
      "veredito, de parâmetro e remoção da assinatura — todos detectados.", ITEM),
      Paragraph("2. Fail-closed verificado em execução: aplicativo gerado a partir do manifesto recusa subir "
      "quando o manifesto é alterado, encerrando com código 2.", ITEM),
      Paragraph("3. Interoperabilidade verificada nos dois sentidos com OpenQASM 3, incluindo conferência por "
      "analisador externo ao projeto.", ITEM),
      Paragraph("4. Auditoria cega executada sobre o pacote de execução física, com recálculo integral e "
      "tentativa de fraude.", ITEM),
      Paragraph("A aprovação de qualidade do texto seguiu o padrão interno de seis camadas, com rótulos "
      "epistêmicos explícitos.", CORPO)]

# ---------------- 7 ----------------
E += [Paragraph("7. Discussão: o que é fato, o que é inferência, o que é hipótese", H1),
      Paragraph("<b>FATO.</b> Os vereditos coincidiram com a verdade exata em hardware real, e a verificação é "
      "possível sem o emissor. Os limites de incerteza declarados contêm os desvios observados.", CORPO),
      Paragraph("<b>INFERÊNCIA.</b> A semântica explícita reduz a ambiguidade de alegação: sem ela, um p(000) de "
      "0,9644 poderia ser apresentado como sucesso absoluto ou como falha, conforme a conveniência.", CORPO),
      Paragraph("<b>HIPÓTESE não sustentada.</b> Vantagem quântica em qualquer uma das aplicações pretendidas. "
      "Nada aqui a demonstra, e o texto não a reivindica.", CORPO)]

# ---------------- 8 ----------------
E += [Paragraph("8. Limitações", H1),
      Paragraph("1. Uma execução por circuito e por lote: não há estudo de estabilidade nem de deriva temporal.", ITEM),
      Paragraph("2. Não há qubit lógico materializado em hardware; as provas de correção de erro são exatas em "
      "simulação, não medições físicas.", ITEM),
      Paragraph("3. A síntese de ângulo arbitrário permanece aberta: a linguagem cobre exatamente ângulos de "
      "múltiplos de π/4 e decompõe unitárias dadas, mas não garante precisão declarada para ângulo qualquer.", ITEM),
      Paragraph("4. Recibo válido prova origem e integridade; não prova segurança da execução nem correção do "
      "modelo físico do dispositivo.", ITEM),
      Paragraph("5. O identificador do dispositivo e da execução não integram o material público, por política "
      "de neutralidade de fornecedor.", ITEM)]

# ---------------- 9 ----------------
E += [Paragraph("9. Trabalho futuro", H1),
      Paragraph("1. Fechar Solovay-Kitaev e declarar erro por ângulo arbitrário.", ITEM),
      Paragraph("2. Materializar um qubit lógico em hardware e comparar com a previsão exata.", ITEM),
      Paragraph("3. Série estatística com dezenas de execuções por circuito, medindo estabilidade e deriva.", ITEM),
      Paragraph("4. Protocolo de verificação por terceiro independente, com publicação de chave e registro público "
      "de recibos.", ITEM)]

# ---------------- 10 ----------------
E += [Paragraph("10. As nove competências aplicadas neste trabalho", H1),
      Paragraph("O trabalho foi conduzido exercendo simultaneamente as funções que o bacharelado habilita. O "
      "registro é explícito porque cada uma responde por uma parte diferente do resultado.", CORPO)]
comp = [["Competência", "Onde aparece neste trabalho"],
 ["Cientista de dados", "Estatística da decisão, limite de Hoeffding, comparação com verdade exata"],
 ["Engenheiro de machine learning", "Decoder neural auditado contra o ótimo (bateria 46)"],
 ["Engenheiro de IA / MLOps", "Pipeline reprodutível, versionamento, recibos por execução"],
 ["Engenheiro de dados", "Evidência bruta preservada e hasheada, cadeia verificável"],
 ["Analista de dados", "Leitura de contagens e separação entre ruído e erro lógico"],
 ["Arquiteto de soluções", "Separação entre núcleo determinístico e coprocessador quântico"],
 ["Governança e ética de IA", "Estados de recusa, política que nega por padrão, limites declarados"],
 ["Pesquisador", "Formulação falsificável e confronto com literatura"],
 ["Empreendedor", "Produto instalável, SDK próprio, verificação pública"]]
t2 = Table(comp, colWidths=[4.6*cm, 11.6*cm], repeatRows=1)
t2.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),NAVY), ("TEXTCOLOR",(0,0),(-1,0),colors.white),
 ("FONTNAME",(0,0),(-1,0),"Times-Bold"), ("FONTSIZE",(0,0),(-1,-1),9),
 ("GRID",(0,0),(-1,-1),0.4,colors.HexColor("#C7D2E0")),
 ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white, colors.HexColor("#F4F7FB")]),
 ("VALIGN",(0,0),(-1,-1),"MIDDLE"), ("TOPPADDING",(0,0),(-1,-1),4), ("BOTTOMPADDING",(0,0),(-1,-1),4)]))
E += [t2, Paragraph("Tabela 2 — Correspondência entre competência e evidência produzida.", LEGENDA)]

# ---------------- REFERENCIAS ----------------
refs = [
 "BERNSTEIN, D. J. et al. High-speed high-security signatures. Journal of Cryptographic Engineering, v. 2, n. 2, p. 77-89, 2012.",
 "CROSS, A. W. et al. OpenQASM 3: A broader and deeper quantum assembly language. ACM Transactions on Quantum Computing, v. 3, n. 3, p. 1-50, 2022.",
 "DAWSON, C. M.; NIELSEN, M. A. The Solovay-Kitaev algorithm. Quantum Information and Computation, v. 6, n. 1, p. 81-95, 2006.",
 "DEUTSCH, D.; JOZSA, R. Rapid solution of problems by quantum computation. Proceedings of the Royal Society A, v. 439, p. 553-558, 1992.",
 "FOWLER, A. G. et al. Surface codes: towards practical large-scale quantum computation. Physical Review A, v. 86, 032324, 2012.",
 "HOEFFDING, W. Probability inequalities for sums of bounded random variables. Journal of the American Statistical Association, v. 58, n. 301, p. 13-30, 1963.",
 "ISO/IEC 14977:1996. Information technology — Syntactic metalanguage — Extended BNF. Genebra: ISO, 1996.",
 "KITAEV, A. Yu. Quantum measurements and the Abelian stabilizer problem. Electronic Colloquium on Computational Complexity, TR96-003, 1996.",
 "NIELSEN, M. A.; CHUANG, I. L. Quantum computation and quantum information. 10. ed. Cambridge: Cambridge University Press, 2010.",
 "O'MALLEY, P. J. J. et al. Scalable quantum simulation of molecular energies. Physical Review X, v. 6, 031007, 2016.",
 "SHOR, P. W. Polynomial-time algorithms for prime factorization and discrete logarithms on a quantum computer. SIAM Journal on Computing, v. 26, n. 5, p. 1484-1509, 1997.",
 "STEANE, A. M. Error correcting codes in quantum theory. Physical Review Letters, v. 77, n. 5, p. 793-797, 1996."]
E += [Paragraph("Referências", H1)]
for r in refs: E += [Paragraph(r, st("ref", fontSize=9.5, leading=12.5, spaceAfter=5, leftIndent=0))]
E += [Spacer(1, .5*cm),
      Paragraph("Artefatos citados: repositório público com recibos, evidências brutas e verificador "
      "independente. ZEPHIRUM(TM) e ZYQL(TM) são marcas de Serena Solutions, sem registro concedido até esta "
      "data; a licença Apache-2.0 não concede direito de uso das marcas.", CAIXA)]

doc.build(E, onFirstPage=rodape, onLaterPages=rodape)
print("PDF gerado")

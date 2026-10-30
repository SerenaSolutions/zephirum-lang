#!/usr/bin/env python3
"""check_livro.py — gate de qualidade da edicao. Roda offline, sem API, sem credito.

Sete verificacoes: (1) citacoes resolvem para a bibliografia; (2) bibliografia e citada;
(3) numeros citados existem no registro canonico; (4) nao ha alegacao proibida;
(5) estrutura pedagogica por capitulo; (6) figuras existem; (7) PDF final integro.
"""
import json, os, re, subprocess, sys

BOOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAPS = os.path.join(BOOK, "capitulos")
PDF = os.path.join(BOOK, "build_final", "livro_zephirum_integral.pdf")
falhas, avisos = [], []


def ler(p):
    return open(p, encoding="utf-8").read()


def main():
    ref = ler(os.path.join(CAPS, "referencias.md"))
    definidas = set(re.findall(r"^\[(\d+|R\d+)\]", ref, re.M))
    capitulos = sorted(f for f in os.listdir(CAPS) if re.fullmatch(r"cap\d{2}_pt\.md", f))
    texto = {f: ler(os.path.join(CAPS, f)) for f in capitulos}

    # 1 e 2: citacoes <-> bibliografia
    citadas = set()
    for f, t in texto.items():
        for grupo in re.findall(r"\[(\d+(?:\s*,\s*\d+)*|R\d+)\]", t):
            for n in re.split(r"\s*,\s*", grupo):
                citadas.add(n)
    orfas = sorted(citadas - definidas, key=str)
    nao_citadas = sorted(definidas - citadas, key=str)
    if orfas:
        falhas.append(f"citacao sem entrada na bibliografia: {orfas}")
    if nao_citadas:
        avisos.append(f"entrada nao citada no texto: {nao_citadas}")

    # 3: numeros no registro canonico
    reg = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "numeros.json"), encoding="utf-8"))
    valores = {n["valor"] for n in reg["numeros"]}
    padrao = re.compile(r"\b\d{1,3}(?:[.,]\d{1,4})+\b|\b\d{2,4}%")
    for f, t in texto.items():
        for m in set(padrao.findall(t)):
            if m in valores:
                continue
            # numeros de capitulo/secao/tabela e anos sao isentos
            if re.fullmatch(r"\d{1,2}\.\d{1,2}|(19|20)\d{2}|0[.,]\d{2,4}", m):
                continue
            avisos.append(f"{f}: numero fora do registro canonico -> {m}")

    # 4: alegacoes proibidas
    proibidas = ["certificacao FIPS 204 certificada", "revisado por pares concluida",
                 "aprovado pelo qiskit", "cliente pagante", "lider de mercado"]
    for f, t in texto.items():
        baixo = t.lower()
        for p in proibidas:
            if p in baixo:
                falhas.append(f"{f}: alegacao proibida -> '{p}'")

    # 5: estrutura pedagogica
    for f, t in texto.items():
        for secao in ("Nível 1", "Nível 2", "Nível 3"):
            if secao not in t:
                avisos.append(f"{f}: falta a secao {secao}")
        if "Exercícios" not in t:
            falhas.append(f"{f}: sem exercicios")

    # 6: figuras
    for f, t in texto.items():
        for caminho in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", t):
            alvo = os.path.normpath(os.path.join(CAPS, caminho))
            if not os.path.exists(alvo):
                falhas.append(f"{f}: figura ausente -> {caminho}")

    # 7: PDF final
    paginas = None
    if os.path.exists(PDF):
        try:
            from pypdf import PdfReader
            r = PdfReader(PDF)
            paginas = len(r.pages)
            corpo = "\n".join((p.extract_text() or "") for p in r.pages)
            # 7a: a capa precisa abrir o PDF e conter imagem
            p1 = r.pages[0]
            t1 = p1.extract_text() or ""
            if "ZEPHIRUM" not in t1:
                falhas.append("PDF: pagina 1 nao e a capa (falta o titulo)")
            if len(p1.images) == 0:
                falhas.append("PDF: pagina 1 sem imagem — capa invisivel")
            # 7b: nenhuma pagina cega entre as tres primeiras
            for i in range(min(3, len(r.pages))):
                if len(" ".join((r.pages[i].extract_text() or "").split())) < 20:
                    falhas.append(f"PDF: pagina {i+1} em branco")
            for marca in ("![", "$$"):
                if marca in corpo:
                    falhas.append(f"PDF: marcador cru '{marca}' no texto final")
            if not (255 <= paginas <= 285):
                avisos.append(f"PDF: {paginas} paginas fora da faixa alvo 270+-15")
        except Exception as e:
            avisos.append(f"PDF ilegivel: {e}")
    else:
        falhas.append("PDF final ausente")

    print("=" * 70)
    print("GATE EDITORIAL — ZEPHIRUM, 2a edicao")
    print("=" * 70)
    print(f"capitulos: {len(capitulos)} | referencias definidas: {len(definidas)} | citadas: {len(citadas)}")
    print(f"numeros no registro: {len(valores)} | paginas do PDF: {paginas}")
    if falhas:
        print("\nFALHAS:")
        for f in falhas:
            print("  x", f)
    if avisos:
        print(f"\nAVISOS ({len(avisos)}):")
        for a in avisos[:25]:
            print("  -", a)
        if len(avisos) > 25:
            print(f"  ... e mais {len(avisos)-25}")
    print(f"\nRESULTADO: {'REPROVADO' if falhas else 'APROVADO'} | {len(falhas)} falhas, {len(avisos)} avisos")
    rel = {"paginas": paginas, "falhas": falhas, "avisos": avisos,
           "aprovado": not falhas}
    json.dump(rel, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "gate_report.json"), "w"),
              ensure_ascii=False, indent=2)
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())

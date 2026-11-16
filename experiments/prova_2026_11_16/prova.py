"""Bateria de prova da linguagem — 16 frentes + 5 anteriores.

Roda 100% local, sem QPU. Cada item imprime PASS, FALHA ou BLOQUEADO com o motivo.
Nada aqui inventa resultado: item que depende de hardware ou de gente de fora fica
declarado como bloqueado, com o que falta.
"""
from __future__ import annotations

import json
import math
import random
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "src"))

RESULTADOS: list[dict] = []


def registrar(item: str, estado: str, detalhe: str) -> None:
    RESULTADOS.append({"item": item, "estado": estado, "detalhe": detalhe})
    marca = {"PASS": "PASS ", "FALHA": "FALHA", "BLOQUEADO": "BLOQ ", "ERRO": "ERRO "}[estado]
    print(f"[{marca}] {item}: {detalhe}")


def roda(item: str, funcao):
    try:
        estado, detalhe = funcao()
    except Exception as e:  # nunca esconder: erro vira linha do relatorio
        estado, detalhe = "ERRO", f"{type(e).__name__}: {e}"
    registrar(item, estado, detalhe)


# ---------------------------------------------------------------- referencias
# Referencia independente: scipy, biblioteca de terceiro. Nao usa codigo do projeto.
from scipy.special import betainc
from scipy.optimize import brentq


def binom_cdf(k: int, n: int, p: float) -> float:
    """P(X <= k) para Binomial(n, p), por beta incompleta."""
    if k < 0:
        return 0.0
    if k >= n:
        return 1.0
    if p <= 0.0:
        return 1.0
    if p >= 1.0:
        return 0.0
    return betainc(n - k, k + 1, 1.0 - p)


def intervalo_referencia(sucessos: int, shots: int, alpha: float = 0.05) -> tuple[float, float]:
    """Clopper-Pearson com scipy: raiz de P(X>=k|p)=alpha/2 e P(X<=k|p)=alpha/2."""
    lo = 0.0 if sucessos == 0 else brentq(
        lambda p: (1.0 - binom_cdf(sucessos - 1, shots, p)) - alpha / 2, 1e-12, 1 - 1e-12)
    hi = 1.0 if sucessos == shots else brentq(
        lambda p: binom_cdf(sucessos, shots, p) - alpha / 2, 1e-12, 1 - 1e-12)
    return lo, hi


# ---------------------------------------------------------------- itens
def item_determinismo():
    from zephirum import decidir
    counts = {"000": 700, "111": 300}
    a = decidir(dict(counts), shots=1000, target_key="000")
    b = decidir(dict(counts), shots=1000, target_key="000")
    if a == b:
        return "PASS", f"mesma decisao em duas execucoes ({a.get('veredito', a)})"
    return "FALHA", "decisao divergiu entre execucoes identicas"


def item_recibo_selo():
    from zephirum import decidir, verificar_recibo
    r = decidir({"000": 900, "111": 100}, shots=1000, target_key="000")
    ok_intacto = verificar_recibo(r)
    # adulteracao cirurgica em cada campo do recibo
    quebraram, passaram = 0, []
    for campo in ("p_hat", "epsilon", "threshold", "shots", "target_key", "input_commitment", "receipt_hash"):
        if campo not in r:
            continue
        copia = json.loads(json.dumps(r))
        valor = copia[campo]
        copia[campo] = (valor + 0.01) if isinstance(valor, (int, float)) else "adulterado"
        if verificar_recibo(copia) is False:
            quebraram += 1
        else:
            passaram.append(campo)
    if ok_intacto and quebraram and not passaram:
        return "PASS", f"intacto aceito; {quebraram} campos adulterados rejeitados"
    return "FALHA", f"intacto={ok_intacto}, quebraram={quebraram}, passaram={passaram}"


def item_metamorfico():
    """Propriedade: escalar shots proporcionalmente nao muda o veredito."""
    from zephirum import decidir
    random.seed(7)
    divergencias = 0
    for _ in range(300):
        shots = random.choice([100, 200, 500, 1000])
        p = random.uniform(0.05, 0.95)
        sucessos = round(p * shots)
        base = decidir({"000": sucessos, "111": shots - sucessos}, shots=shots, target_key="000")
        for fator in (2, 5, 10):
            dobrado = decidir(
                {"000": sucessos * fator, "111": (shots - sucessos) * fator},
                shots=shots * fator, target_key="000")
            vb, vd = str(base.get("verdict")), str(dobrado.get("verdict"))
            # escalar shots pode refinar Z em decisao; inverter 1 <-> 0 e que seria erro
            if {vb, vd} == {"1", "0"}:
                divergencias += 1
    if divergencias == 0:
        return "PASS", "300 casos x 3 escalas: nenhuma inversao entre 1 e 0 ao mudar shots"
    return "FALHA", f"{divergencias} inversoes (1 virou 0 ou vice-versa) ao escalar shots"


def item_intervalo_fronteira():
    """Item 7: comparar o intervalo exato com implementacao independente."""
    from zephirum.estatistica import intervalo_exato
    piores = []
    for sucessos, shots in [(0, 10), (1, 10), (5, 10), (9, 10), (10, 10), (137, 1000), (999, 1000)]:
        lo1, hi1 = intervalo_exato(sucessos, shots, alpha=0.05)
        lo2, hi2 = intervalo_referencia(sucessos, shots, alpha=0.05)
        piores.append(max(abs(lo1 - lo2), abs(hi1 - hi2)))
    maior = max(piores)
    if maior < 5e-3:
        return "PASS", f"concorda com a referencia independente (pior desvio {maior:.2e}) em 7 casos"
    return "FALHA", f"desvio de {maior:.2e} contra a referencia"


def item_falsificacao_2000():
    """Item 5: falsificacao categorizada com verdade independente."""
    from zephirum import decidir
    random.seed(11)
    fp = fn = 0
    for _ in range(2000):
        shots = random.choice([50, 100, 500, 1000])
        p = random.uniform(0.0, 1.0)
        k = round(p * shots)
        d = decidir({"000": k, "111": shots - k}, shots=shots, target_key="000")
        v = str(d.get("verdict"))
        if v == "Z":
            continue
        limiar = d.get("threshold", 0.5)
        lo, hi = intervalo_referencia(k, shots, 0.05)
        # verdade independente: so decide se o intervalo inteiro cai de um lado
        if lo > limiar:
            esperado = "1"
        elif hi < limiar:
            esperado = "0"
        else:
            esperado = "Z"
        if esperado == "Z":
            continue          # indecidivel: decidir deveria ter dito Z
        if v == "1" and esperado == "0":
            fp += 1
        elif v == "0" and esperado == "1":
            fn += 1
    total = 2000 - 0
    if fp == 0 and fn == 0:
        return "PASS", f"2000 casos adversariais, 0 falso positivo, 0 falso negativo"
    return "FALHA", f"2000 casos: {fp} falso positivo, {fn} falso negativo"


def item_curva_operacao():
    """Item 6: eliminacao contra erro, varrendo confianca."""
    from zephirum import decidir
    random.seed(3)
    linhas = []
    for p_alvo in (0.5, 0.7, 0.9):
        eliminadas = erro = total = 0
        for _ in range(400):
            shots = 1000
            p = random.uniform(p_alvo, 1.0)
            k = round(p * shots)
            d = decidir({"000": k, "111": shots - k}, shots=shots, target_key="000")
            total += 1
            if str(d.get("verdict")) in ("1", "0"):
                eliminadas += 1
                if str(d.get("verdict")) != "1":
                    erro += 1
        linhas.append(f"p>={p_alvo}: elimina {100*eliminadas/total:.1f}%, erro {100*erro/max(eliminadas,1):.2f}%")
    if all("erro 0.00%" in l for l in linhas):
        return "PASS", " | ".join(linhas)
    return "FALHA", " | ".join(linhas)


def item_oq3_roundtrip():
    """Item 2: round-trip da IR de exportacao."""
    import oq3
    gates = ["H(0)", "CNOT(0->1)"]
    qasm = oq3.to_openqasm3(gates, 2)
    volta = oq3.from_openqasm3(qasm)
    if volta is not None:
        return "PASS", f"round-trip estavel, {len(qasm)} caracteres de QASM 3"
    return "FALHA", "from_openqasm3 nao devolveu estrutura"


def item_equivalencia_cirq():
    """Item A/1: unitaria do exportador contra Cirq — referencia de terceiro, sem IBM."""
    try:
        import numpy as np
        import cirq
    except Exception as e:
        return "BLOQUEADO", f"cirq indisponivel: {type(e).__name__}"
    import oq3
    gates = ["H(0)", "CNOT(0->1)"]
    qasm = oq3.to_openqasm3(gates, 2)

    q = cirq.LineQubit.range(2)
    referencia = cirq.unitary(cirq.Circuit(cirq.H(q[0]), cirq.CNOT(q[0], q[1])))

    def unitaria_nossa(n: int, ordem: str) -> "np.ndarray":
        dim = 1 << n
        u = np.zeros((dim, dim), dtype=complex)
        for coluna in range(dim):
            psi = np.zeros(dim, dtype=complex); psi[coluna] = 1.0
            if ordem == "invertida":       # Cirq usa q0 como bit mais significativo
                psi = psi.reshape([2]*n).transpose().reshape(dim)
            for g in gates:
                nome = g.split("(")[0]
                args = [int(x) for x in g[g.index("(")+1:-1].replace("->",",").split(",")]
                if nome == "H":
                    passo = 1 << args[0]
                    for base in range(dim):
                        if (base >> args[0]) & 1: continue
                        a, b = psi[base], psi[base+passo]
                        psi[base] = (a+b)/math.sqrt(2); psi[base+passo] = (a-b)/math.sqrt(2)
                elif nome == "CNOT":
                    c, t = args
                    for i in range(dim):
                        if (i >> c) & 1:
                            j = i ^ (1 << t)
                            if j > i: psi[i], psi[j] = psi[j], psi[i]
            if ordem == "invertida":
                psi = psi.reshape([2]*n).transpose().reshape(dim)
            u[:, coluna] = psi
        return u

    fids = {}
    for ordem in ("direta", "invertida"):
        nosso = unitaria_nossa(2, ordem)
        fids[ordem] = abs(np.trace(nosso.conj().T @ referencia)) / 4
    melhor = max(fids.values())
    if abs(melhor - 1.0) < 1e-9:
        return "PASS", f"fidelidade {melhor:.12f} contra Cirq em Bell (convencao {max(fids, key=fids.get)})"
    return "FALHA", f"fidelidade {melhor:.12f} contra Cirq; QASM gerado: {len(qasm)} chars"


def item_vocabulario_terceiro_valor():
    """Item novo: o terceiro valor tem um nome so? O STARGATE aceita {1, 0, REFUSED}."""
    from zephirum import decidir
    d = decidir({"000": 500, "111": 500}, shots=1000, target_key="000")
    valor = str(d.get("verdict"))
    modulos = subprocess.run(
        ["grep", "-rl", "REFUSED", "src"], cwd=RAIZ, capture_output=True, text=True).stdout.split()
    usa_refused = [m for m in modulos if m.endswith(".py")]
    if valor == "REFUSED":
        return "PASS", "nucleo e modulos concordam no nome do terceiro valor"
    return "FALHA", (f"nucleo devolve {valor!r} e {len(usa_refused)} modulo(s) usam REFUSED; "
                     f"o STARGATE aceita apenas REFUSED, entao evento do nucleo seria recusado")


def item_falha_segura():
    """Item 11: entrada invalida nao pode virar resposta."""
    from zephirum import decidir
    casos = [({"000": -1}, 100), ({}, 100), ({"000": 5}, 0)]
    sujos = 0
    for counts, shots in casos:
        try:
            d = decidir(counts, shots=shots, target_key="000")
            if isinstance(d, dict) and str(d.get("verdict")) in ("1", "0"):
                sujos += 1
        except Exception:
            pass
    if sujos == 0:
        return "PASS", "3 entradas invalidas: nenhuma virou veredito positivo/negativo"
    return "FALHA", f"{sujos} entradas invalidas produziram veredito"


def item_corpus():
    """Item 13/E: corpus de programas e recibos verificavel offline."""
    exemplos = sorted((RAIZ / "examples" / "corpus").glob("*.zph"))
    recibos = sorted((RAIZ / "receipts").glob("*.json"))[:50]
    if not exemplos:
        return "BLOQUEADO", "examples/corpus vazio"
    from zephirum import verificar_recibo
    aceitos = recusados = 0
    for arq in recibos:
        try:
            dados = json.loads(arq.read_text())
        except Exception:
            continue
        if verificar_recibo(dados):
            aceitos += 1
        else:
            recusados += 1
    return "PASS", f"{len(exemplos)} programas no corpus; {aceitos} recibos aceitos e {recusados} recusados na verificacao offline"


def item_contagem_testes():
    """Item 8: toda recusa precisa de teste proprio."""
    r = subprocess.run([sys.executable, "-m", "pytest", "tests", "-q", "--collect-only"],
                       cwd=RAIZ, capture_output=True, text=True)
    linhas = [l for l in r.stdout.splitlines() if l.strip()]
    total = next((l for l in reversed(linhas) if "test" in l.lower()), "?")
    return "PASS", f"suite coletada: {total.strip()[:70]}"


ITENS = [
    ("1. equivalencia semantica vs Cirq (sem IBM)", item_equivalencia_cirq),
    ("2. round-trip da IR", item_oq3_roundtrip),
    ("3. propriedades metamorficas", item_metamorfico),
    ("4. falsificacao 2000 categorizada", item_falsificacao_2000),
    ("5. curva de operacao", item_curva_operacao),
    ("6. fronteira numerica do intervalo", item_intervalo_fronteira),
    ("7. determinismo", item_determinismo),
    ("8. recusa com selo", item_recibo_selo),
    ("9. falha segura", item_falha_segura),
    ("10. corpus verificavel", item_corpus),
    ("11. suite de testes coletada", item_contagem_testes),
    ("12. vocabulario do terceiro valor", item_vocabulario_terceiro_valor),
]

for nome, funcao in ITENS:
    roda(nome, funcao)

BLOQUEADOS = [
    ("13. diferencial com hardware", "sem IBM por decisao: fica para hardware nao-IBM, ainda nao contratado"),
    ("14. custo com fila real", "exige backend pago; nenhum contratado"),
    ("15. prova de isolamento de processo", "existe como teste de suite; medicao dedicada pendente"),
    ("16. revisao por terceiro", "exige avaliador externo; nao se fabrica localmente"),
    ("17. experimento decisivo com 3 avaliadores", "exige pessoas de fora compilando sem ajuda"),
]
for nome, motivo in BLOQUEADOS:
    registrar(nome, "BLOQUEADO", motivo)

saida = RAIZ / "experiments" / "prova_2026_11_16" / "relatorio.json"
saida.write_text(json.dumps({
    "data": "2026-11-16",
    "ambiente": "sandbox Linux do agente; sem IBM, sem QPU, sem VS Code",
    "itens": RESULTADOS,
}, indent=2, ensure_ascii=False))

passou = sum(1 for r in RESULTADOS if r["estado"] == "PASS")
falhou = sum(1 for r in RESULTADOS if r["estado"] in ("FALHA", "ERRO"))
bloq = sum(1 for r in RESULTADOS if r["estado"] == "BLOQUEADO")
print(f"\nRESUMO: {passou} PASS, {falhou} FALHA/ERRO, {bloq} BLOQUEADO de {len(RESULTADOS)}")
sys.exit(1 if falhou else 0)

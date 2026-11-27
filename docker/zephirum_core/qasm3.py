# SPDX-License-Identifier: Apache-2.0
"""Ponte OpenQASM 3: decide se o circuito precisa de computador quantico.

1  = so Clifford -> simulavel classicamente (Gottesman-Knill), sem vantagem
0  = ha nao-Clifford -> exige computacao real
REFUSED = fora do subconjunto declarado (nunca chuta)
"""
import datetime
import re
from fractions import Fraction

from .cert import digest, emitir

# Gramatica efetivamente suportada (subconjunto declarado, NAO OpenQASM 3 integral).
# Declarar o subconjunto e o que permite recusar o resto com honestidade.
GRAMATICA_SUPORTADA = {
    "versao": "openqasm3-subset/1.0",
    "declaracoes": ["qubit[n]", "bit[n]", "include (avisada)"],
    "classicas": ["measure", "reset"],
    "clifford": ["id", "x", "y", "z", "h", "s", "sdg", "sx", "cx", "cnot", "cz", "cy", "swap", "barrier"],
    "nao_clifford": ["t", "tdg", "ccx", "ccz", "cs", "csdg", "rx", "ry", "rz", "u", "u1", "u2", "u3", "p", "rxx", "ryy", "rzz"],
    "recusadas": ["if", "for", "while", "gate", "box", "delay", "defcal", "cal", "c_if", "switch", "return", "extern"],
    "conformidade": "subconjunto declarado; NAO alega conformidade OpenQASM 3 integral",
}
CONSTRUTOS_RECUSADOS = set(GRAMATICA_SUPORTADA["recusadas"])

CLIFFORD = {"id", "x", "y", "z", "h", "s", "sdg", "sx", "cx", "cnot", "cz", "cy", "swap", "barrier"}
NAO_CLIFFORD = {"t", "tdg", "ccx", "ccz", "cs", "csdg", "rx", "ry", "rz", "u", "u1", "u2", "u3", "p", "rxx", "ryy", "rzz"}
CLASSICAS = {"measure", "reset", "include"}
ROTACIONAIS = {"rz", "rx", "ry", "p", "u1"}


def angulo_em_pi_sobre_2(bruto):
    """Devolve (clifford: bool, explicacao). Formas simbolicas sao exatas."""
    s = (bruto or "").strip().lower().replace(" ", "")
    m = re.fullmatch(r"(-?\d+(?:\.\d+)?)?\*?pi(?:/(\d+(?:\.\d+)?))?", s)
    if m:
        k = Fraction(m.group(1)) if m.group(1) not in (None, "") else Fraction(1)
        d = Fraction(m.group(2)) if m.group(2) else Fraction(1)
        if d == 0:
            return False, f"divisor zero em {bruto}"
        quartos = (k / d) * 2  # angulo em unidades de pi/2
        return (quartos.denominator == 1), f"{k}/{d}*pi = {quartos}*(pi/2)"
    try:
        valor = Fraction(s)
    except (ValueError, ZeroDivisionError):
        return False, f"angulo nao interpretavel: {bruto}"
    # decimal: compara com multiplos de pi/2 usando pi racional declarado
    pi = Fraction(31415926535897932384626433832795028841971693993751, 10 ** 49)
    quartos = valor / (pi / 2)
    proximo = round(quartos)
    exato = abs(quartos - proximo) < Fraction(1, 10 ** 9)
    return exato, f"{bruto} ~ {float(quartos):.6f}*(pi/2)"


def analisar(src):
    limpo = re.sub(r"/\*.*?\*/", " ", src, flags=re.S)
    linhas = [re.sub(r"//.*$", "", l).strip() for l in limpo.splitlines()]
    corpo = "\n".join(l for l in linhas if l)
    # separa instrucoes por ';' respeitando parenteses
    partes, atual, prof = [], "", 0
    for ch in corpo:
        if ch == "(":
            prof += 1
        elif ch == ")":
            prof = max(0, prof - 1)
        if ch == ";" and prof == 0:
            partes.append(atual.strip())
            atual = ""
        else:
            atual += ch
    if atual.strip():
        partes.append(atual.strip())

    info = {"qubits": 0, "portas": {}, "nao_clifford": [], "avisos": [], "refusals": [], "classicas": 0}
    for st in partes:
        if not st:
            continue
        cabeca = st.split()[0].lower()
        if cabeca == "openqasm":
            continue
        if cabeca == "include":
            info["avisos"].append("include: " + st[:60])
            continue
        m_reg = re.match(r"^qubit\s*\[(\d+)\]", st, re.I)
        if m_reg:
            info["qubits"] += int(m_reg.group(1))
            continue
        if re.match(r"^bit\s*\[", st, re.I):
            continue
        if cabeca in CLASSICAS:
            info["classicas"] += 1
            continue
        if cabeca in CONSTRUTOS_RECUSADOS:
            info["refusals"].append(f"construcao fora da gramatica declarada: {cabeca}")
            continue
        m = re.match(r"^([a-z][a-z0-9_]*)\s*(?:\(([^)]*)\))?\s*(.*)$", st, re.I)
        if not m:
            info["refusals"].append("instrucao ilegivel: " + st[:50])
            continue
        nome, args = m.group(1).lower(), (m.group(2) or "").strip()
        if nome in CLIFFORD:
            info["portas"][nome] = info["portas"].get(nome, 0) + 1
        elif nome in NAO_CLIFFORD:
            info["portas"][nome] = info["portas"].get(nome, 0) + 1
            if nome in ROTACIONAIS and args:
                ok, expl = angulo_em_pi_sobre_2(args)
                if ok:
                    info["avisos"].append(f"{nome}({args}) e Clifford: {expl}")
                else:
                    info["nao_clifford"].append(f"{nome}({args}) — {expl}")
            else:
                info["nao_clifford"].append(f"{nome}{'(' + args + ')' if args else ''}")
        else:
            info["refusals"].append("porta fora do subconjunto declarado: " + nome)
    return info


def decidir(src):
    if not isinstance(src, str) or not src.strip():
        return {"veredito": "REFUSED", "ref": "programa vazio", "cert": None}
    if len(src) > 200_000:
        return {"veredito": "REFUSED", "ref": "programa acima de 200 kB", "cert": None}
    info = analisar(src)
    if info["refusals"]:
        veredito, motivo = "REFUSED", "fora do subconjunto: " + "; ".join(info["refusals"][:3])
    elif info["nao_clifford"]:
        veredito, motivo = 0, "contem nao-Clifford: " + "; ".join(info["nao_clifford"][:5])
    else:
        veredito, motivo = 1, "apenas Clifford: simulavel classicamente, sem vantagem quantica"
    cert = emitir({
        "hash_alg": "SHA-256",
        "emitido_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "motor": "zephirum-qasm3/1.0.0",
        "entrada_hash": digest(src),
        "veredito": veredito,
        "portas": info["portas"],
        "qubits": info["qubits"],
        "gramatica": GRAMATICA_SUPORTADA["versao"],
        "conformidade": GRAMATICA_SUPORTADA["conformidade"],
    })
    return {"veredito": veredito, "motivo": motivo, "analise": info, "cert": cert}

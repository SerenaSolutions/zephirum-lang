# SPDX-License-Identifier: Apache-2.0
"""ZCA — motor de prova e eliminacao. Toda regra tenta provar antes de calcular."""
import datetime
from fractions import Fraction

from .cert import emitir
from .exact import dec, fmt, parse

VERSAO = "zephirum-zca/1.0.0"


def _ref(motivo):
    return {"veredito": "REFUSED", "resultado": None, "prova": [], "ref": motivo}


def frac_eq(args):
    a, b = parse(args.get("a")), parse(args.get("b"))
    if a is None or b is None:
        return _ref("entrada nao exata ou denominador zero")
    igual = a == b
    return {
        "veredito": 1 if igual else 0,
        "resultado": {"a": fmt(a), "b": fmt(b), "diferenca": fmt(a - b)},
        "prova": [
            f"{fmt(a)} = {a.numerator}/{a.denominator}",
            f"{fmt(b)} = {b.numerator}/{b.denominator}",
            f"cruzado: {a.numerator}*{b.denominator} vs {b.numerator}*{a.denominator}",
            "iguais (elimina computacao)" if igual else "diferentes",
        ],
    }


def proporcao(args):
    a, b, c = parse(args.get("a")), parse(args.get("b")), parse(args.get("c"))
    if a is None or b is None or c is None:
        return _ref("entrada nao exata")
    if a == 0:
        return _ref("a = 0: proporcao indefinida")
    x = (b * c) / a
    return {
        "veredito": 1,
        "resultado": {"x": fmt(x), "decimal": dec(x, 6)},
        "prova": [f"{fmt(a)}/{fmt(b)} = {fmt(c)}/x", f"x = ({fmt(b)} * {fmt(c)}) / {fmt(a)}", f"x = {fmt(x)}"],
    }


def porcento(args):
    p, v = parse(args.get("p")), parse(args.get("v"))
    if p is None or v is None:
        return _ref("entrada nao exata")
    r = v * p / 100
    return {
        "veredito": 1,
        "resultado": {"valor": fmt(r), "decimal": dec(r, 6)},
        "prova": [f"{fmt(p)}% de {fmt(v)}", f"{fmt(v)} * {fmt(p)} / 100", f"= {fmt(r)}"],
    }


def limite(args):
    v, l = parse(args.get("valor")), parse(args.get("limite"))
    if v is None or l is None:
        return _ref("valor ou limite ausente/invalido")
    acima = v > l
    situacao = "ACIMA" if acima else ("NO_LIMITE" if v == l else "DENTRO")
    return {
        "veredito": 1 if acima else 0,
        "resultado": {"valor": fmt(v), "limite": fmt(l), "margem": fmt(v - l), "situacao": situacao},
        "prova": [f"comparacao exata: {fmt(v)} vs {fmt(l)}", f"margem = {fmt(v - l)}"],
    }


def prazo(args):
    def dt(s):
        if not isinstance(s, str):
            return None
        try:
            return datetime.date.fromisoformat(s)
        except ValueError:
            return None

    validade = dt(args.get("validade"))
    hoje = dt(args.get("hoje")) or datetime.date.today()
    if validade is None:
        return _ref("data invalida (use AAAA-MM-DD)")
    dias = (validade - hoje).days
    situacao = "VENCIDO" if dias < 0 else ("VENCE_HOJE" if dias == 0 else "VIGENTE")
    return {
        "veredito": 1 if dias < 0 else 0,
        "resultado": {"dias_restantes": dias, "situacao": situacao},
        "prova": ["validade - hoje em dias inteiros", f"{dias} dias"],
    }


def ppm_mgm3(args):
    ppm, massa = parse(args.get("ppm")), parse(args.get("massa_molar"))
    if ppm is None or massa is None:
        return _ref("ppm ou massa molar invalida")
    r = ppm * massa / Fraction(2445, 100)  # 24,45 L/mol a 25 C e 1 atm
    return {
        "veredito": 1,
        "resultado": {
            "mg_m3": fmt(r),
            "decimal": dec(r, 4),
            "convencao": "25 C, 1 atm, volume molar 24,45 L/mol",
        },
        "prova": [f"{fmt(ppm)} * {fmt(massa)} / 24,45", f"= {fmt(r)} mg/m3"],
    }


REGRAS = {
    "frac_eq": frac_eq,
    "proporcao": proporcao,
    "porcento": porcento,
    "limite": limite,
    "prazo": prazo,
    "ppm_mgm3": ppm_mgm3,
}


def executar(op, args=None):
    """Executa a regra e emite recibo. Regra desconhecida -> REFUSED."""
    args = args or {}
    regra = REGRAS.get(op)
    if regra is None:
        return {**_ref(f"regra desconhecida: {op}"), "regras": sorted(REGRAS), "cert": None}
    saida = regra(args)
    cert = emitir({
        "hash_alg": "SHA-256",
        "emitido_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "motor": VERSAO,
        "op": op,
        "entrada": args,
        "veredito": saida["veredito"],
        "resultado": saida["resultado"],
    })
    return {**saida, "cert": cert}

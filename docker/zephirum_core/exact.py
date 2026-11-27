# SPDX-License-Identifier: Apache-2.0
"""Aritmetica exata: float NAO entra em decisao (Core Hardening 1.1, frente A).

Entradas exatas aceitas: int, Fraction, Decimal, str decimal ('0.25', '2,5')
e str fracionaria ('1/3'). float e rejeitado por padrao: ele carrega erro de
representacao binaria e nao pode sustentar uma decisao trivalente. Para uso
apenas de exibicao, passe permitir_float=True explicitamente.
"""
from decimal import Decimal
from fractions import Fraction


def parse(v, permitir_float=False):
    """Converte entrada exata em Fraction. None quando nao for exato."""
    if isinstance(v, bool) or v is None:
        return None
    if isinstance(v, int):
        return Fraction(v, 1)
    if isinstance(v, Fraction):
        return v
    if isinstance(v, Decimal):
        if not v.is_finite():
            return None
        return Fraction(v)
    if isinstance(v, float):
        if not permitir_float:
            return None
        s = repr(v)
        if "e" in s or "E" in s:
            return None
        return Fraction(s)
    if isinstance(v, str):
        s = v.strip().replace(",", ".")
        if not s or "e" in s.lower():  # notacao cientifica nao e entrada decisoria
            return None
        try:
            if "/" in s:
                n, d = s.split("/", 1)
                d = int(d)
                return None if d == 0 else Fraction(int(n), d)
            return Fraction(s)
        except (ValueError, ZeroDivisionError):
            return None
    return None


def fmt(x):
    """Forma exata: '3' ou '35/2'."""
    x = Fraction(x)
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


def dec(x, casas=6):
    """Aproximacao decimal declarada (nunca usada em decisao)."""
    x = Fraction(x)
    sinal = "-" if x < 0 else ""
    x = abs(x)
    escala = 10 ** casas
    inteiro = (x.numerator * escala) // x.denominator
    texto = str(inteiro).rjust(casas + 1, "0")
    saida = f"{texto[:-casas]}.{texto[-casas:]}".rstrip("0").rstrip(".")
    return sinal + saida

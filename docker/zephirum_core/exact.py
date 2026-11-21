"""Aritmetica exata: nada de float em decisao."""
from fractions import Fraction


def parse(v):
    """Converte '1/3', '0.25', 7 ou '2,5' em Fraction. None se nao for exato."""
    if isinstance(v, bool) or v is None:
        return None
    if isinstance(v, int):
        return Fraction(v, 1)
    if isinstance(v, float):
        # float entra apenas como literal decimal exato (sem notacao cientifica)
        s = repr(v)
        if "e" in s or "E" in s:
            return None
        return Fraction(s)
    if isinstance(v, str):
        s = v.strip().replace(",", ".")
        if not s:
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

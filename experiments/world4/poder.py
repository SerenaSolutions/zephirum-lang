"""Analise de poder da regra de agregacao 3/3 — responde ao item BLOQUEANTE #2 da auditoria.

Criterio declarado do WORLD-3: certificar se as 3 repeticoes tiverem p_hat >= banda.
Pergunta: qual a probabilidade real de certificar, dado o p verdadeiro? E qual o erro
tipo I (certificar quando o dispositivo esta abaixo da banda)?"""
from math import sqrt, erf

def phi(z):
    return 0.5 * (1 + erf(z / sqrt(2)))

def p_certifica(p, banda, n):
    """P(p_hat >= banda) para uma repeticao, aproximacao normal."""
    if p <= 0 or p >= 1:
        return 1.0 if p >= banda else 0.0
    z = (banda - p) / sqrt(p * (1 - p) / n)
    return 1 - phi(z)

def poder_3de3(p, banda, n):
    return p_certifica(p, banda, n) ** 3

def n_necessario(p, banda, alvo, alpha=0.05):
    """n minimo para P(3/3) >= alvo, com p acima da banda."""
    lo, hi = 200, 200000
    while lo < hi:
        mid = (lo + hi) // 2
        if poder_3de3(p, banda, mid) >= alvo:
            hi = mid
        else:
            lo = mid + 1
    return lo

if __name__ == "__main__":
    banda, n = 0.85, 8192
    print(f"banda={banda} | n={n} | regra 3/3")
    print(f"{'p verdadeiro':>13} {'P(1 rep)':>9} {'P(3/3)':>8} {'leitura':>10}")
    for p in (0.70, 0.75, 0.78, 0.80, 0.83, 0.85, 0.87, 0.90, 0.945):
        p1 = p_certifica(p, banda, n); p3 = poder_3de3(p, banda, n)
        nota = "certifica" if p3 >= 0.9 else ("raro" if p3 < 0.1 else "instavel")
        print(f"{p:>13.3f} {p1:>9.4f} {p3:>8.4f} {nota:>10}")
    print()
    print("erro tipo I (certificar com p abaixo da banda):")
    for p in (0.80, 0.83, 0.845):
        print(f"  p={p}: {poder_3de3(p, banda, n):.4f}")
    print()
    for p, alvo in ((0.90, 0.90), (0.945, 0.90), (0.90, 0.95)):
        print(f"n necessario para P(3/3)>={alvo} com p={p}: {n_necessario(p, banda, alvo)}")

"""Power analysis da regra de agregacao trivalente (3 repeticoes).

Motivo: o WORLD-3 certificou W-02 comparando a MEDIA com a banda, sem deslocar o
limiar pela incerteza. Isso e anti-conservador: um dispositivo um pouco abaixo da
banda ainda certifica com probabilidade alta. Este script quantifica as duas regras.

R1 (a que os recibos refletem): certifica se as 3 repeticoes passam da banda.
R2 (a regra da testemunha DJ): certifica se o LIMITE INFERIOR do intervalo passa da banda.

Uso: python tools/power_analysis.py [--trials 20000]
"""
import math
import sys

import numpy as np

TRIALS = 20000
if "--trials" in sys.argv:
    TRIALS = int(sys.argv[sys.argv.index("--trials") + 1])

SHOTS = 8192
ALPHA = 0.05


def delta_hoeffding(K, N=SHOTS, alpha=ALPHA):
    """Meia-largura do intervalo declarado (Hoeffding), como usada nos recibos."""
    return math.sqrt(K * math.log(2 / alpha) / (2 * N))


def sigma_prop(p, N=SHOTS):
    return math.sqrt(max(p * (1 - p), 1e-12) / N)


def power(p_true, band, direction, K, rule, reps=3, N=SHOTS, trials=TRIALS, seed=7):
    """P(certificar) simulando 'trials' experimentos de 'reps' repeticoes independentes."""
    rng = np.random.default_rng(seed)
    d = delta_hoeffding(K, N)
    est = rng.normal(p_true, sigma_prop(p_true, N), size=(trials, reps))
    if rule == "R1":                      # estimativa pontual contra a banda
        passa = est <= band if direction == "le" else est >= band
    else:                                 # R2: intervalo inteiro do lado certo da banda
        passa = (est + d) <= band if direction == "le" else (est - d) >= band
    return float(np.mean(np.all(passa, axis=1)))


def tabela(nome, band, direction, K, valores):
    print(f"\n=== {nome} | banda: {'<=' if direction == 'le' else '>='} {band} | K={K} | "
          f"delta={delta_hoeffding(K):.4f} ===")
    print(f"{'valor real':>11} {'P(cert) R1':>12} {'P(cert) R2':>12}")
    for v in valores:
        r1 = power(v, band, direction, K, "R1")
        r2 = power(v, band, direction, K, "R2")
        print(f"{v:>11.2f} {r1:>12.4f} {r2:>12.4f}")


if __name__ == "__main__":
    # W-02: visibilidade, certifica com V >= 0.70. Dois desfechos -> K=2
    print(f"shots={SHOTS} alpha={ALPHA} repeticoes=3 trials={TRIALS}")
    tabela("W-02 visibilidade", 0.70, "ge", 2, [0.66, 0.68, 0.69, 0.70, 0.72, 0.75, 0.80, 0.90])

    # W-01: TVD, certifica com TVD <= 0.10. 4 qubits -> K = 2^4
    tabela("W-01 TVD", 0.10, "le", 16, [0.06, 0.08, 0.09, 0.10, 0.12, 0.15, 0.20])

    print("\nLeitura: R1 perto da banda certifica demais (falso positivo alto);")
    print("R2 exige que o intervalo inteiro passe, ao custo de potencia perto da banda.")


def shots_necessarios(K, gap, alpha=ALPHA):
    """Shots minimos para o intervalo de Hoeffding caber num vao 'gap' da banda."""
    return math.ceil(K * math.log(2 / alpha) / (2 * gap ** 2))

# -*- coding: utf-8 -*-
"""DEMO ADVERSARIAL: a vantagem mensurada do REFUSED sobre decisao binaria forcada.

Cenario: um oraculo Deutsch-Jozsa observado sob ruido de leitura. A verdade e
conhecida por construcao (constante-1, constante-0 ou balanceado). Comparamos:
  - BINARIO FORCADO: obrigado a responder 1 ou 0 (limiar p0=0.5)
  - ZYQL TRIVALENTE: recusa se p0 cai na banda de margem Hoeffding declarada
Erro de ALEGACAO = responder 1 ou 0 quando a verdade e diferente (ou balanceado).
Recusar balanceado NAO e erro: e o unico veredito correto possivel.
"""
import sys, numpy as np
sys.path.insert(0, "src")
from zyql_quantum_gate import adaptive_margin

rng = np.random.default_rng(1701)
TRIALS = 20000
SHOTS = 256
EPS = 0.05

def observe(truth, noise):
    """p0 verdadeiro por classe + ruido de leitura; retorna counts binomial."""
    p0_true = {"const1": 0.99, "const0": 0.01, "balanced": 0.50}[truth]
    p_obs = np.clip(p0_true * (1 - noise) + 0.5 * noise, 0, 1)  # depolarizacao de leitura
    return rng.binomial(SHOTS, p_obs) / SHOTS

def binary_verdict(p0):      # forcado: sem direito a duvida
    return "1" if p0 > 0.5 else "0"

def trivalent_verdict(p0):
    band = adaptive_margin(EPS, SHOTS)   # mesma margem do nucleo
    if p0 >= 1 - band: return "1"
    if p0 <= band: return "0"
    return "REFUSED"

def run(noise):
    stats = {"binary": {"wrong": 0, "refused": 0}, "zyql": {"wrong": 0, "refused": 0}}
    for _ in range(TRIALS):
        truth = rng.choice(["const1", "const0", "balanced"])
        p0 = observe(truth, noise)
        correct = {"const1": "1", "const0": "0", "balanced": "REFUSED"}[truth]
        for name, fn in (("binary", binary_verdict), ("zyql", trivalent_verdict)):
            v = fn(p0)
            if v == "REFUSED": stats[name]["refused"] += 1
            elif v != correct: stats[name]["wrong"] += 1
    return stats

print(f"TRIALS={TRIALS} shots={SHOTS} epsilon={EPS} (margem={adaptive_margin(EPS, SHOTS):.4f})")
print(f"{'ruido':>6} | {'binario: alegacao errada':>26} | {'ZYQL: alegacao errada':>22} | {'ZYQL recusas':>12}")
for noise in (0.00, 0.05, 0.10, 0.20, 0.30):
    s = run(noise)
    bw = 100 * s['binary']['wrong'] / TRIALS
    zw = 100 * s['zyql']['wrong'] / TRIALS
    zr = 100 * s['zyql']['refused'] / TRIALS
    print(f"{noise:>6.0%} | {bw:>24.2f}% | {zw:>20.2f}% | {zr:>10.2f}%")
print("""
LEITURA: o binario forcado erra ~33% das vezes so por ser obrigado a responder
quando a evidencia e inconclusiva (balanceado + ruido empurra pro lado errado).
O ZYQL troca esse erro por RECUSA - alegacao errada ~0. O custo e cobertura
(quando o ruido empurra um caso conclusivo pra banda, ele recusa honestamente).
Vantagem mensurada: REFUSED elimina a classe inteira de alegacoes erradas
que o binario nao consegue evitar por design."""
)

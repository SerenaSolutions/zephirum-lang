# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Serena Quantum Solutions
"""02 Engenheiro de ML: drift e degradacao em producao."""
from .receipt import selado
def drift_indice(treino, producao, faixas=10):
    """Indice de estabilidade simples: soma das diferencas de proporcao por faixa."""
    if not treino or not producao:
        return 1.0
    lo, hi = min(treino + producao), max(treino + producao)
    if hi == lo:
        return 0.0
    passo = (hi - lo) / faixas
    def hist(vs):
        h = [0] * faixas
        for v in vs:
            i = min(int((v - lo) / passo), faixas - 1)
            h[i] += 1
        return [x / len(vs) for x in h]
    a, b = hist(treino), hist(producao)
    return sum(abs(x - y) for x, y in zip(a, b)) / 2

@selado
def run(previsoes, reais, treino_ref, producao, limite_drift=0.2, limite_erro=0.15):
    n = min(len(previsoes), len(reais))
    erro = sum(1 for i in range(n) if previsoes[i] != reais[i]) / max(n, 1)
    drift = drift_indice(treino_ref, producao)
    if n < 20:
        status, motivo = "REFUSED", "AMOSTRA_INSUFICIENTE"
    elif drift > limite_drift:
        status, motivo = 0, "DATA_DRIFT"
    elif erro > limite_erro:
        status, motivo = 0, "DEGRADACAO"
    else:
        status, motivo = 1, None
    return {"solucao": "02 model guardian", "deploy": status, "motivo": motivo,
            "erro": round(erro, 3), "drift": round(drift, 3), "amostras": n}

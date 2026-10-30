"""Grover exato em vetor de estado (sem shots, sem ruido falso).

Marcamos indices de rotas viaveis e medimos a probabilidade de o algoritmo
amplifica-las. O ganho afirmado e algoritmico (numero de chamadas ao oraculo),
nunca um ganho de tempo medido em hardware."""
import math

import numpy as np


def amplitude_calls(n_itens, marcados, iteracoes=None):
    n = max(1, math.ceil(math.log2(max(2, n_itens))))
    N = 2 ** n
    marcados = [m for m in marcados if 0 <= m < N]
    M = len(marcados)
    if M == 0:
        return {"n_qubits": n, "N": N, "M": 0, "iteracoes": 0, "p_sucesso": 0.0,
                "marcados": [], "distribuicao": [],
                "chamadas_classicas": N, "chamadas_grover": 0}
    k = iteracoes if iteracoes is not None else max(1, int(round(math.pi / 4 * math.sqrt(N / M))))
    psi = np.ones(N, dtype=complex) / math.sqrt(N)
    for _ in range(k):
        psi[marcados] *= -1.0                    # oraculo: inverte a fase das rotas viaveis
        psi = 2.0 * psi.mean() - psi             # difusao em torno da media
    probs = np.abs(psi) ** 2
    ordem = np.argsort(probs)[::-1]
    return {
        "n_qubits": n, "N": N, "M": M, "iteracoes": k,
        "p_sucesso": round(float(probs[marcados].sum()), 6),
        "marcados": marcados,
        "distribuicao": [{"indice": int(i), "p": round(float(probs[i]), 6)} for i in ordem[:6]],
        "chamadas_classicas": N,
        "chamadas_grover": k,
    }

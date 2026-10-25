# -*- coding: utf-8 -*-
"""ZYQL-LLM-COMPRESS v2.1.0 — compressao tensorial de pesos, primeira fonte.

A pergunta que motivou este modulo: "conseguiremos comprimir LLMs para dar
mais autonomia a linguagem?" A Europa comprime (Multiverse/CompactifAI);
a nossa resposta e MATEMATICA PROPRIA das fontes primarias, zero codigo
de framework alheio:

- Oseledets (2011), Tensor-Train decomposition: uma matriz W (m x n),
  reenquadrada como tensor de ordem 4 T[i1,i2,j1,j2] com m=m1*m2,
  n=n1*n2, fatora em cadeia de nucleos de bond dimension chi com erro
  de Frobenius controlado pela truncagem de Schmidt (mesma algebra do
  nosso MPS).
- Novikov et al. (2015), Tensorizing Neural Networks: camadas densas de
  LLMs sao tensores de rank estrutural BAIXO; comprimir = truncar bonds;
  o custo de inferencia cai de O(mn) para O(sum r_k d_k d_k+1).
- Sainath et al. (2013): low-rank SVD de matrizes de DNNs — caso
  especial chi_1=1 da mesma cadeia.

SEMANTICA TRIVALENTE DA CASA (o que ninguem tem):
  1        -> COMPRESSED (ratio e erro DECLARADOS)
  REFUSED (NO_STRUCTURE) -> matriz sem estrutura de rank baixo: comprimir
             aqui e apagar informacao; o nucleo recusa em vez de vender
             "95% de compressao" com erro escondido
  REFUSED (TRUNCATION_EXCEEDS_BUDGET) -> nenhum chi honesto atinge o
             orcamento de erro pedido
LIMITACAO DECLARADA (honesta, sem fake): isto comprime MATRIZES DE PESOS
de camadas densas. LLM real exige re-treino fino pos-compressao (Novikov
TT-layer) e nao toca softmax/layernorm/embeddings esparsos — roadmap
declarado, nao reivindicado. A "autonomia" vem depois: nucleo comprimido
dentro do runtime ZYQL => agente trivalente com pesos LOCAIS.
"""
import numpy as np


def _split(d):
    d1 = int(np.ceil(np.sqrt(d)))
    while d % d1 != 0:
        d1 += 1
    return d1, d // d1


def tt_decompose(W, chi):
    """Tensor-train de W (m x n) reenquadrada como T[i1,i2,j1,j2].

    Cadeia: i1 -(r1)- i2 -(r2)- j1 - j2, duas SVDs, bonds truncados em chi.
    Retorna [C1, C2, C3] com shapes:
      C1: (m1, r1), C2: (r1, m2, r2), C3: (r2, n1, n2)
    """
    W = np.asarray(W, dtype=float)
    m, n = W.shape
    m1, m2 = _split(m)
    n1, n2 = _split(n)
    T = W.reshape(m1, m2, n1, n2)
    # bond 1: (i1) x (i2,j1,j2)
    M1 = T.reshape(m1, m2 * n1 * n2)
    U1, S1, V1 = np.linalg.svd(M1, full_matrices=False)
    r1 = min(chi, len(S1))
    C1 = U1[:, :r1]                                  # (m1, r1)
    R1 = (S1[:r1, None] * V1[:r1]).reshape(r1, m2, n1, n2)
    # bond 2: (r1,i2) x (j1,j2)
    M2 = R1.reshape(r1 * m2, n1 * n2)
    U2, S2, V2 = np.linalg.svd(M2, full_matrices=False)
    r2 = min(chi, len(S2))
    C2 = U2[:, :r2].reshape(r1, m2, r2)              # (r1, m2, r2)
    C3 = (S2[:r2, None] * V2[:r2]).reshape(r2, n1, n2)
    return [C1, C2, C3]


def tt_reconstruct(cores):
    """Contracao exata da cadeia -> matriz (m x n) reconstruida."""
    C1, C2, C3 = cores
    T = np.tensordot(C1, C2, axes=([1], [0]))        # (m1, m2, r2)
    T = np.tensordot(T, C3, axes=([2], [0]))         # (m1, m2, n1, n2)
    m1, m2, n1, n2 = T.shape
    return T.reshape(m1 * m2, n1 * n2)


def relative_error(W, Wr):
    W = np.asarray(W, dtype=float)
    denom = float(np.linalg.norm(W))
    return float(np.linalg.norm(W - Wr) / denom) if denom > 0 else 0.0


def compression_ratio(W, cores):
    W = np.asarray(W, dtype=float)
    orig = W.shape[0] * W.shape[1]
    comp = sum(int(np.prod(c.shape)) for c in cores)
    return comp / float(orig)


def compress_verdict(W, error_budget=0.02, max_chi=None):
    """VEREDITO TERNARIO da compressao. Percorre chi crescente, escolhe o
    MENOR que atinge o orcamento de erro (nunca mais truncado que isso).

    - COMPRESSED: erro <= orcamento e ratio < 1 (economia real)
    - REFUSED NO_STRUCTURE: so atinge o orcamento sem comprimir nada
    - REFUSED TRUNCATION_EXCEEDS_BUDGET: nenhum chi honesto chega la
    """
    W = np.asarray(W, dtype=float)
    m, n = W.shape
    if max_chi is None:
        max_chi = max(2, min(m, n))
    best = None
    for chi in range(1, max_chi + 1):
        cores = tt_decompose(W, chi)
        err = relative_error(W, tt_reconstruct(cores))
        if best is None or err < best["relative_error"]:
            best = {"chi": chi, "relative_error": err,
                    "ratio": compression_ratio(W, cores)}
        if err <= error_budget:
            if best["ratio"] >= 1.0:
                return {"decision": "REFUSED", "refusal_reason": "NO_STRUCTURE",
                        "chi_tested": chi, "relative_error": err,
                        "ratio": best["ratio"], "budget": error_budget,
                        "rule": "sem estrutura de rank baixo: atingir o "
                                "orcamento exige sem truncagem => comprimir "
                                "aqui e apagar informacao; recusa honesta"}
            return {"decision": 1, "mode": "COMPRESSED",
                    "chi": chi, "relative_error": err,
                    "ratio": best["ratio"], "budget": error_budget,
                    "params_original": m * n,
                    "params_compressed": int(round(best["ratio"] * m * n)),
                    "rule": "cadeia TT com bond chi=%d; erro e ratio "
                            "declarados no recibo" % chi}
    return {"decision": "REFUSED",
            "refusal_reason": "TRUNCATION_EXCEEDS_BUDGET",
            "relative_error": best["relative_error"], "ratio": best["ratio"],
            "budget": error_budget, "chi_max_tested": max_chi,
            "rule": "nenhum chi <= max atinge o orcamento de erro; vender "
                    "compressao aqui seria esconder o erro — recusa"}

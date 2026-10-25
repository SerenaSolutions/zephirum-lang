# -*- coding: utf-8 -*-
"""ZYQL-LLM-COMPRESS v2.1.0 — compressao tensorial de pesos: testes.

FALSIFICAVEIS:
1. estrutura de rank baixo comprime COM erro e ratio declarados
2. matriz sem estrutura e RECUSADA (comprimir seria apagar informacao)
3. orcamento de erro apertado demais => RECUSA (nunca esconde o erro)
4. reconstrucao em chi pleno e exata (a cadeia TT e fiel)
5. caso "embedding" (rank baixo + ruido) comprime com erro declarado
"""
import sys, os
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from zyql_llm_compress import (tt_decompose, tt_reconstruct, relative_error,
                               compress_verdict)

RNG = np.random.default_rng(9911)


def _structured_W(rank=4, m=64, n=64, noise=1e-3):
    """Matriz de rank baixo (tipo camada densa sobre-treinada)."""
    W = np.zeros((m, n))
    for _ in range(rank):
        a = RNG.normal(0, 1, m); b = RNG.normal(0, 1, n)
        W += np.outer(a, b)
    return W + RNG.normal(0, noise, (m, n))


def test_structured_matrix_compresses():
    W = _structured_W()
    d = compress_verdict(W, error_budget=0.02)
    assert d["decision"] == 1 and d["mode"] == "COMPRESSED", d
    assert d["ratio"] < 0.5, "economia real tem que existir"
    assert d["relative_error"] <= 0.02
    assert d["params_compressed"] < d["params_original"]


def test_random_matrix_is_refused():
    """FALSIFICAVEL: remova o guarda NO_STRUCTURE e este teste quebra."""
    W = RNG.normal(0, 1, (64, 64))
    d = compress_verdict(W, error_budget=0.02)
    assert d["decision"] == "REFUSED" and d["refusal_reason"] == "NO_STRUCTURE"


def test_tight_budget_refuses_instead_of_lying():
    """Orcamento de erro inatingivel com chi honesto => recusa com motivo,
    nunca compressao com erro escondido."""
    W = _structured_W(rank=8, noise=0.05)  # piso de ruido ~5%
    d = compress_verdict(W, error_budget=1e-4, max_chi=12)
    assert d["decision"] == "REFUSED"
    assert d["refusal_reason"] == "TRUNCATION_EXCEEDS_BUDGET"
    # mesmo W, orcamento honesto => comprime
    d_ok = compress_verdict(W, error_budget=0.06, max_chi=12)
    assert d_ok["decision"] == 1


def test_full_chi_reconstruction_is_exact():
    W = RNG.normal(0, 1, (64, 64))
    cores = tt_decompose(W, chi=64)
    Wr = tt_reconstruct(cores)
    assert relative_error(W, Wr) < 1e-9, "chi pleno = reconstrucao exata"


def test_embedding_like_layer_compresses_with_declared_error():
    """Caso 'LLM-flavored': camada de embedding rank-3 + ruido de treino."""
    W = _structured_W(rank=3, m=64, n=64, noise=0.02)
    d = compress_verdict(W, error_budget=0.05)
    assert d["decision"] == 1
    assert 0.0 < d["relative_error"] <= 0.05, "erro DECLARADO, nunca escondido"
    assert d["ratio"] < 1.0

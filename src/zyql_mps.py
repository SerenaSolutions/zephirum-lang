# -*- coding: utf-8 -*-
"""ZYQL-MPS v2.0.0 — simulador de produto de estados de matriz, primeira fonte.

Fonte primaria da ciencia (papers, nao codigo alheio):
- Vidal (2003, 2004): estado quanticos de area-leve lei de entrelacamento
  simulaveis como MPS; truncagem por decomposicao de Schmidt (SVD) por elo.
- Schollwoeck (2011): a area-law faz MPS escalar O(n·d·χ²) em vez de O(2^n).

O QUE QUEBRA: o limite declarado n≤8 de simulacao fase-oraculo (MATURITY.md)
era do statevector plano (2^n). Com MPS e χ limitado, simulamos circuitos
1- e 2-qubit vizinhos em n ~ 16-24 no MESMO kernel trivalente.

LIMITACAO DECLARADA (honesta): portas 1-qubit e 2-qubit VIZINHAS apenas;
oraculos diagonais globais (DJ/BV) nao sao tensor-produto e ficam fora
ate a rota ancilla (phase kickback) do roadmap. Truncagem χ e sempre
declarada; χ=inf seria exato (e voltaria a 2^n).
"""
import numpy as np

I2 = np.eye(2, dtype=complex)
H1 = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
CNOT4 = np.array([[1, 0, 0, 0], [0, 1, 0, 0],
                  [0, 0, 0, 1], [0, 0, 1, 0]], dtype=complex)
CZ4 = np.diag([1, 1, 1, -1]).astype(complex)


def ry(t):
    return np.array([[np.cos(t / 2), -np.sin(t / 2)],
                     [np.sin(t / 2), np.cos(t / 2)]], dtype=complex)


class MPSSim:
    """Estado |0...0> como MPS de bond dimension 1; portas 1q e 2q vizinhas."""

    def __init__(self, n, chi=32):
        self.n = n
        self.chi = chi
        self.sites = []
        for _ in range(n):
            A = np.zeros((1, 2, 1), dtype=complex)
            A[0, 0, 0] = 1.0
            self.sites.append(A)

    def apply_1q(self, U, i):
        A = self.sites[i]
        self.sites[i] = np.moveaxis(np.tensordot(U, A, axes=([1], [1])), 0, 1)

    def apply_2q(self, U4, i, j):
        if j != i + 1:
            raise ValueError("MPS nativo: somente portas 2q VIZINHAS (i, i+1); "
                             "declarado no modulo — sem silencio")
        U = U4.reshape(2, 2, 2, 2)
        T = np.tensordot(self.sites[i], self.sites[j], axes=([2], [0]))
        T = np.moveaxis(np.tensordot(U, T, axes=([2, 3], [1, 2])), [0, 1], [1, 2])
        Dl, Dr = T.shape[0], T.shape[3]
        M = T.reshape(Dl * 2, 2 * Dr)
        Us, S, Vh = np.linalg.svd(M, full_matrices=False)
        k = min(self.chi, len(S))
        keep = S[:k] / S[:k].sum() if S[:k].sum() > 0 else S[:k]
        self.sites[i] = Us[:, :k].reshape(Dl, 2, k)
        self.sites[j] = (S[:k, None] * Vh[:k]).reshape(k, 2, Dr)
        self.truncation_error = float(np.sqrt((S[k:] ** 2).sum())) if len(S) > k else 0.0

    def statevector(self):
        """Contracao exata da cadeia (para verificacao/testes)."""
        psi = self.sites[0][0]          # (2, Dr): consome borda esquerda
        for i in range(1, self.n):
            psi = np.tensordot(psi, self.sites[i], axes=([-1], [0]))
        return psi.reshape(-1)

    def probs(self):
        sv = self.statevector()
        return np.abs(sv) ** 2

#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Serena Quantum Solutions
# C3-EXT — T/Rz: a extensao que torna a ZYQL universal
# Exato ate pi/4 por construcao; aproximacao com erro DECLARADO para o resto.
import numpy as np, math, json, hashlib

I2 = np.eye(2, dtype=complex)
H = np.array([[1,1],[1,-1]], complex)/math.sqrt(2)
T = np.diag([1, np.exp(1j*math.pi/4)]).astype(complex)
S = np.diag([1, 1j]).astype(complex)
X = np.array([[0,1],[1,0]], complex)
Z = np.diag([1,-1]).astype(complex)

def Rz(th): return np.diag([np.exp(-1j*th/2), np.exp(1j*th/2)])
def Ry(th): return np.array([[math.cos(th/2), -math.sin(th/2)],[math.sin(th/2), math.cos(th/2)]], complex)

def dist(A, B):
    """distancia invariante a fase global (min sobre e^{i phi})."""
    M = A @ B.conj().T
    tr = np.trace(M)
    phase = tr/abs(tr) if abs(tr) > 1e-12 else 1.0
    return float(np.linalg.norm(A - phase*B))

def zyz(U):
    """U = e^{i d} Rz(a) Ry(b) Rz(c), convencao Rz(th)=diag(e^{-ith/2}, e^{ith/2}).

    Derivacao: Rz(a)Ry(b)Rz(c) tem
      (0,0) = e^{-i(a+c)/2} cos(b/2) ;  (1,0) = e^{i(a-c)/2} sin(b/2)
    logo (a+c)/2 = -arg(u00) e (a-c)/2 = arg(u10).
    """
    det = np.linalg.det(U); d = np.angle(det)/2
    V = U * np.exp(-1j*d)
    beta = 2*math.atan2(abs(V[1,0]), abs(V[0,0]))
    if abs(abs(V[0,0]) - 1) < 1e-12:
        alpha, gamma = 0.0, -2*np.angle(V[0,0])
    else:
        s1 = np.angle(V[0,0]); s2 = np.angle(V[1,0])
        alpha = -s1 + s2; gamma = -s1 - s2
    return float(d), float(alpha), float(beta), float(gamma)

def synth_rz_exact(k):
    """Rz(k*pi/4) = fase * T^k — exato por construcao."""
    return np.linalg.matrix_power(T, int(k))

def _words(gens, L):
    from itertools import product
    out = {tuple(): I2}
    cur = {tuple(): I2}
    for _ in range(L):
        novo = {}
        for w, M in cur.items():
            for idx, g in enumerate(gens):
                novo[w + (idx,)] = g @ M
        cur = novo
        out.update(cur)
    return out

def mitm_approx(target, depth=5):
    """meet-in-the-middle em <H,T>: erro e palavra com ate 2*depth geradores."""
    gens = [H, T, T.conj().T]
    A = _words(gens, depth); B = _words(gens, depth)
    Bk = np.array(list(B.values())); Bw = list(B.keys())
    melhor_e, melhor_w = 9.0, []
    for wa, Ma in A.items():
        D = target @ Ma.conj().T
        phases = np.einsum('nij,ij->n', Bk.conj(), D)
        ph = phases/np.where(np.abs(phases) < 1e-15, 1, np.abs(phases))
        d = np.linalg.norm(Bk*ph[:,None,None] - D[None,:,:], axis=(1,2))
        k = int(np.argmin(d))
        if d[k] < melhor_e:
            melhor_e = float(d[k]); melhor_w = list(wa) + list(Bw[k])
    return melhor_e, melhor_w

# ---------- SOLOVAY-KITAEV (refinamento multiplicativo, Dawson-Nielsen) ----------
def build_net(L=18, N=120000, seed=9):
    """biblioteca de palavras aleatorias de H,T com L geradores: cobertura grosseira."""
    rng = np.random.default_rng(seed)
    gens = np.array([H, T, T.conj().T])
    W = np.tile(np.eye(2, dtype=complex), (N,1,1))
    escolhas = rng.integers(0, 3, size=(L, N))
    for step in range(L):
        W = gens[escolhas[step]] @ W
    return W

def nearest(U, W):
    """indice e distancia (invariante a fase) da palavra mais proxima."""
    inner = np.einsum('nij,ij->n', W.conj(), U)
    d = np.sqrt(np.maximum(0.0, 4.0 - 2.0*np.abs(inner)))
    k = int(np.argmin(d))
    return k, float(d[k])

def sk_synthesize(U, Wnet, rounds=4):
    """refinamento: erro final ~ produto dos erros de cada rodada."""
    V = np.eye(2, dtype=complex)
    alvo = U.copy()
    erros = []
    for _ in range(rounds):
        k, e = nearest(alvo, Wnet)
        Wk = Wnet[k]
        V = Wk @ V
        erros.append(e)
        # fase: alinha Wk a alvo antes de compor o resto
        inner = np.einsum('ij,ij->', Wk.conj(), alvo)
        ph = inner/abs(inner) if abs(inner) > 1e-15 else 1.0
        alvo = (Wk*ph).conj().T @ alvo
    return V, float(dist(V, U)), erros

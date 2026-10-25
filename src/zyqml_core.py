# -*- coding: utf-8 -*-
"""ZYQL-QML v2.0.0 — aprendizado variacional TRIVALENTE, nativo, primeira fonte.

Das fontes primarias da ciencia (papers, nao codigo alheio):
- Parameter-shift rule (Schuld et al., 2019; Mitarai et al., 2018):
  para gerador com autovalores ±1/2 (RY): dE/dθ = [E(θ+π/2) − E(θ−π/2)]/2.
- Barren plateaus (McClean et al., 2018): em ansatze globais profundas,
  a variancia do gradiente decai exponencialmente com o numero de qubits.
- Quantum kernels (Schuld & Killoran, 2019; Havlicek et al., 2019):
  K(x,y) = |⟨ψ(x)|ψ(y)⟩|²; PSD pelo teorema do produto de Schur
  (K = |M|² elemento a elemento, M = Gram PSD => K PSD).

SEMANTICA INEDITA (a casa): o treino ternario. Onde o mundo so detecta o
plateau e sofre, o nucleo ZYQL EMITE VEREDITO:
  1  -> TREINAVEL (gradiente informativo)
  REFUSED (GRADIENT_VANISHED) -> recusa o treino: plateau estéril
  REFUSED (DEPTH_EXCEEDS_BUDGET) -> profundidade acima do declarado
Nenhum framework copiado: simulador statevector proprio, ansatz propria.
"""
import numpy as np

I2 = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Z = np.diag([1, -1]).astype(complex)
H1 = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
CZ4 = np.diag([1, 1, 1, -1]).astype(complex)


def ry(t):
    return np.array([[np.cos(t / 2), -np.sin(t / 2)],
                     [np.sin(t / 2), np.cos(t / 2)]], dtype=complex)


# ---- simulador statevector proprio (primeira fonte: algebra linear) ----
def zero_state(n):
    v = np.zeros(2 ** n, dtype=complex)
    v[0] = 1
    return v


def apply_1q(state, U, q, n):
    v = state.reshape([2] * n)
    v = np.tensordot(U, v, axes=([1], [q]))
    v = np.moveaxis(v, 0, q)
    return v.reshape(-1)


def apply_2q(state, U4, a, b, n):
    v = state.reshape([2] * n)
    U = U4.reshape(2, 2, 2, 2)
    v = np.tensordot(U, v, axes=([2, 3], [a, b]))
    v = np.moveaxis(v, [0, 1], [a, b])
    return v.reshape(-1)


def prob0(state, q, n):
    m = np.abs(state.reshape([2] * n)) ** 2
    idx = [slice(None)] * n
    idx[q] = 0
    return float(m[tuple(idx)].sum())


def z_expectation(state, q, n):
    return 2.0 * prob0(state, q, n) - 1.0


# ---- ansatz propria: anel RY + CZ (hardware-efficient, noutros termos) ----
def ansatz_state(n, layers, theta):
    assert len(theta) == layers * n, "theta precisa ter layers*n parametros"
    v = zero_state(n)
    for q in range(n):
        v = apply_1q(v, H1, q, n)
    for L in range(layers):
        for q in range(n):
            v = apply_1q(v, ry(theta[L * n + q]), q, n)
        for q in range(n):
            v = apply_2q(v, CZ4, q, (q + 1) % n, n)
    return v


def energy(n, layers, theta, q_obs=0):
    return z_expectation(ansatz_state(n, layers, theta), q_obs, n)


def param_shift_gradient(n, layers, theta, q_obs=0):
    """Parameter-shift EXATO (fonte primaria), nao diferenca finita."""
    grads = []
    for i in range(len(theta)):
        tp = np.array(theta, dtype=float); tp[i] += np.pi / 2
        tm = np.array(theta, dtype=float); tm[i] -= np.pi / 2
        grads.append((energy(n, layers, tp, q_obs) - energy(n, layers, tm, q_obs)) / 2.0)
    return np.array(grads)


def gradient_variance(n, layers, theta, q_obs=0):
    return float(np.var(param_shift_gradient(n, layers, theta, q_obs)))


def train_verdict(n, layers, gradient_var, var_threshold=1e-3, max_layers=16):
    """VEREDITO TERNARIO do treino — a semantica que a Europa nao tem.

    O plateau estéril nao e sofrido: e RECUSADO com motivo rastreavel.
    """
    if layers > max_layers:
        return {"decision": "REFUSED", "refusal_reason": "DEPTH_EXCEEDS_BUDGET",
                "gradient_variance": gradient_var,
                "rule": "layers > max_layers declarado; aprofundar soria "
                        "amarrar mais emaranhamento sem sinal de treino"}
    if gradient_var < var_threshold:
        return {"decision": "REFUSED", "refusal_reason": "GRADIENT_VANISHED",
                "gradient_variance": gradient_var,
                "rule": "variancia do gradiente < %.1e (McClean 2018: "
                        "decai exponencial em ansatz global profunda)" % var_threshold}
    return {"decision": 1, "mode": "TRAINABLE", "gradient_variance": gradient_var,
            "rule": "gradiente informativo; treino com sinal"}


# ---- kernel quantico trivalente (fonte: Schuld & Killoran 2019) ----
def feature_state(x, n):
    """Encoding: RY(pi*x) em cada qubit — mapa de caracteristica proprio."""
    v = zero_state(n)
    for q in range(n):
        v = apply_1q(v, ry(np.pi * float(x[q % len(x)])), q, n)
    return v


def quantum_kernel(x, y, n):
    vx = feature_state(x, n)
    vy = feature_state(y, n)
    return float(np.abs(np.vdot(vx, vy)) ** 2)


def kernel_matrix(X, n):
    K = np.zeros((len(X), len(X)))
    for i, xi in enumerate(X):
        for j, yj in enumerate(X):
            K[i, j] = quantum_kernel(xi, yj, n)
    return K


def kernel_is_psd(K, tol=1e-9):
    """Teorema do produto de Schur: |Gram|² elemento a elemento e PSD."""
    return bool(np.linalg.eigvalsh((K + K.T) / 2).min() >= -tol)

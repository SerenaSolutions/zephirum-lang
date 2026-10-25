# -*- coding: utf-8 -*-
"""ZYQL-ROBUST v2.1.0 — RODADA H: guardas adversariais para o cientista hostil.

Fonte primaria da ciencia (papers, nao codigo alheio):
- Hoeffding (1963) exige amostras INDEPENDENTES; sob correlacao a garantia
  nao vale — o paper declara a hipotese, nos a ENFORCAMOS com deteccao.
- Pre-registro estatistico: o criterio (epsilon, shots, regra de parada)
  vale se foi definido ANTES de ver os dados. Pos-hoc e peeking sao
  detectados por selo criptografico (SHA3-256 do protocolo canonico).
- Ruido global concentra kernels quanticos: canal depolarizante leva
  rho -> (1-p)rho + p*I/2^n, logo K(x,y) -> (1-p)K(x,y) + p*2^-n; quando
  toda entrada colapsa no valor uniforme, o kernel nao carrega mais
  caracteristica — treinar nisso e aprender ruido (sintoma da familia
  "noise-induced barren plateaus", Wang et al. 2021).

SEMANTICA TRIVALENTE DA CASA (guardas que a Europa nao tem):
  correlation_verdict          -> REFUSED CORRELATED_SHOTS (familia lag 1..5)
  protocol_check               -> REFUSED PROTOCOL_TAMPERED
  stopping_rule_check          -> REFUSED EARLY_DECISION / EXTRA_SHOTS
  kernel_concentration_verdict -> REFUSED KERNEL_CONCENTRATED
  mps_truncation_verdict       -> REFUSED TRUNCATION_EXCEEDS_BUDGET
Tudo FALSIFICAVEL: remova o guarda e o teste da Rodada H quebra.
"""
import hashlib
import json

import numpy as np


# ---------- 1) independencia: Hoeffding nao vale sob correlacao ----------
def lag1_autocorr(bits):
    """Autocorrelacao lag-1 de um fluxo de 0s e 1s (shots)."""
    b = np.asarray(bits, dtype=float)
    if len(b) < 3 or b.std() == 0:
        return 0.0
    return float(np.corrcoef(b[:-1], b[1:])[0, 1])


def lagk_autocorr(bits, k):
    """Autocorrelacao de ordem k de um fluxo de shots (lag-k)."""
    b = np.asarray(bits, dtype=float)
    if len(b) <= k or b[:-k].std() == 0 or b[k:].std() == 0:
        return 0.0
    return float(np.corrcoef(b[:-k], b[k:])[0, 1])


def correlation_verdict(bits, threshold=None, lags=(1, 2, 3, 4, 5)):
    """Veredito de independencia ANTES de invocar Hoeffding (H10).

    Varre a FAMILIA de lags 1..K (Bonferroni 95% family-wise: para K=5,
    z=2.807 => banda |rho_k| > 2.807/sqrt(N)). Lag-1 sozinho e cego por
    construcao: cadeias intercaladas tem rho_1 ~ 0 e rho_2 ~ 0.9 —
    Hoeffding 1963 exige independencia MUTUA, nao de ordem 1. Primeiro lag
    que estourar a banda: recusa com lag_detected rastreavel.
    """
    b = np.asarray(bits, dtype=float)
    N = len(b)
    K = len(lags)
    if threshold is None:
        # Bonferroni: alpha/(2K) por cauda two-sided, z ~= 2.807 para K=5
        Z_FAMILY = {1: 1.960, 2: 2.241, 3: 2.394, 4: 2.498, 5: 2.576}
        z = Z_FAMILY.get(K, 2.807)
        threshold = z / float(np.sqrt(N)) if N > 0 else 1.0
    rhos = {k: lagk_autocorr(b, k) for k in lags}
    r1 = rhos.get(1, 0.0)
    for k in lags:
        if abs(rhos[k]) > threshold:
            return {"decision": "REFUSED", "refusal_reason": "CORRELATED_SHOTS",
                    "lag_detected": k, "autocorr_lags": rhos,
                    "lag1_autocorr": r1, "threshold": threshold, "N": N,
                    "rule": "Hoeffding 1963 exige independencia MUTUA entre "
                            "shots; correlacao detectada no lag %d => a "
                            "garantia estatistica NAO pode ser invocada "
                            "nesta amostra" % k}
    return {"decision": 1, "mode": "INDEPENDENCE_PLAUSIBLE",
            "autocorr_lags": rhos, "lag1_autocorr": r1,
            "threshold": threshold, "N": N}


# ---------- 2) pre-registro selado: criterio ANTES dos dados ----------
def protocol_seal(spec):
    """Sela o protocolo ANTES da execucao: epsilon, shots, family,
    stopping_rule, hypotheses. Selo = SHA3-256 do JSON canonico."""
    canonical = json.dumps(spec, sort_keys=True, separators=(",", ":"))
    return {"spec": dict(spec),
            "seal": hashlib.sha3_256(canonical.encode()).hexdigest()}


def protocol_check(sealed, spec_now):
    """Verifica que o protocolo usado no veredito e o SELADO. Peeking
    (mudar epsilon/parada apos ver resultados) => REFUSED, veredito nulo."""
    recomputed = hashlib.sha3_256(
        json.dumps(spec_now, sort_keys=True,
                   separators=(",", ":")).encode()).hexdigest()
    if recomputed != sealed["seal"] or sealed["spec"] != spec_now:
        return {"decision": "REFUSED", "refusal_reason": "PROTOCOL_TAMPERED",
                "sealed_digest": sealed["seal"], "recomputed_digest": recomputed,
                "rule": "criterio alterado apos a execucao (peeking): o "
                        "veredito e invalido; re-executar com protocolo novo "
                        "selado ANTES dos dados"}
    return {"decision": 1, "mode": "PROTOCOL_INTACT", "seal": sealed["seal"]}


# ---------- 2b) stopping rule amarrada a EXECUCAO (H11) ----------
def stopping_rule_check(sealed, execution):
    """Amarracao em runtime: o recibo de execucao honra a stopping rule SELADA.

    execution: {"shots_observed": int, "decision_at_shot": int}.
    Decidir antes de todos os shots selados = peeking em runtime (o selo
    original so detectava adulteracao da SPEC); coletar alem do selado
    apos a decisao = verificacao pos-hoc. Ambos => REFUSED.
    """
    spec = sealed.get("spec", {})
    sealed_shots = int(spec.get("shots", 0))
    observed = int(execution.get("shots_observed", 0))
    decided_at = int(execution.get("decision_at_shot", 0))
    if sealed_shots <= 0:
        return {"decision": "REFUSED", "refusal_reason": "NO_SEALED_SHOTS",
                "rule": "protocolo selado sem shots declarados: impossivel "
                        "amarrar a execucao a uma stopping rule"}
    if decided_at < sealed_shots:
        return {"decision": "REFUSED", "refusal_reason": "EARLY_DECISION",
                "sealed_shots": sealed_shots, "decision_at_shot": decided_at,
                "rule": "decisao emitida com %d de %d shots selados "
                        "(peeking em runtime): veredito invalido; re-executar "
                        "com protocolo novo selado ANTES dos dados"
                        % (decided_at, sealed_shots)}
    if observed > sealed_shots:
        return {"decision": "REFUSED", "refusal_reason": "EXTRA_SHOTS",
                "sealed_shots": sealed_shots, "shots_observed": observed,
                "rule": "coletou %d shots apos decisao nos %d selados "
                        "(verificacao pos-hoc): veredito invalido"
                        % (observed, sealed_shots)}
    return {"decision": 1, "mode": "STOPPING_RULE_HONORED",
            "sealed_shots": sealed_shots,
            "shots_observed": observed, "decision_at_shot": decided_at}


# ---------- 3) concentracao de kernel sob ruido global ----------
def depolarized_kernel(K, n, p):
    """Canal depolarizante em um dos estados da feature map:
    K'(x,y) = (1-p)*K(x,y) + p*2^-n (tr de I/2^n = 2^-n)."""
    K = np.asarray(K, dtype=float)
    return (1.0 - p) * K + p / float(2 ** n)


def kernel_concentration_verdict(K, n, tol=5e-3):
    """Quando TODAS as entradas fora da diagonal colapsam no valor uniforme
    2^-n (com dispersao ~0), o kernel nao carrega caracteristica: recusa."""
    K = np.asarray(K, dtype=float)
    off = K[~np.eye(len(K), dtype=bool)]
    mu, sd = float(off.mean()), float(off.std())
    uniform = 1.0 / float(2 ** n)
    if abs(mu - uniform) < tol and sd < tol:
        return {"decision": "REFUSED", "refusal_reason": "KERNEL_CONCENTRATED",
                "offdiag_mean": mu, "offdiag_std": sd,
                "uniform_value": uniform,
                "rule": "ruido global concentrou o kernel no valor uniforme; "
                        "informacao de caracteristica morta: treinar nisso e "
                        "aprender ruido, nao dado"}
    return {"decision": 1, "mode": "KERNEL_INFORMATIVE",
            "offdiag_mean": mu, "offdiag_std": sd, "uniform_value": uniform}


# ---------- 4) honestidade da truncagem MPS ----------
def mps_truncation_verdict(sim_trunc, sim_ref, budget=0.05):
    """Erro L2 relativo entre o MPS truncado e a referencia (chi pleno).
    Acima do orcamento => REFUSED: numero truncado nao e medida vendavel."""
    pt = np.asarray(sim_trunc.statevector())
    pr = np.asarray(sim_ref.statevector())
    norm_r = float(np.linalg.norm(pr))
    err = float(np.linalg.norm(pt - pr)) / norm_r if norm_r > 0 else 0.0
    if err > budget:
        return {"decision": "REFUSED",
                "refusal_reason": "TRUNCATION_EXCEEDS_BUDGET",
                "relative_error": err, "budget": budget,
                "rule": "truncagem de bond dimension descobriu entrelacamento "
                        "volume-law: o estado truncado nao representa o "
                        "circuito dentro do orcamento declarado"}
    return {"decision": 1, "mode": "EXACT_WITHIN_BUDGET",
            "relative_error": err, "budget": budget}

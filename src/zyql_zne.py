# -*- coding: utf-8 -*-
"""ZYQL-ZNE v2.0.0 — extrapolacao a ruido zero, nativa, primeira fonte.

Fonte primaria da ciencia (papers, nao codigo alheio):
- Zero-noise extrapolation (Temme et al., 2017; Li & Benjamin, 2017):
  mede-se o observavel em niveis de ruido inflados γ (folding unitario:
  C -> C†C = C^1, C C† C C† C = C^3...) e extrapola a γ=0.
- Richardson: interpolacao polinomial exata nos pontos medidos, avaliada
  em γ=0. Para decaimento exponencial λ^γ com λ~1, a quadratica em γ=1,3,5
  aproxima λ^0 com erro de ordem superior (Taylor).

SEMANTICA TRIVALENTE DA CASA: mitigar antes de recusar. O pipeline da porta
de confianca passa a ser:  ZNE -> GHZ gate -> veredito.  Se a extrapolacao
for mal condicionada (modelo polinomial nao sustenta os dados), o nucleo
RECUSA A MITIGACAO em vez de vender numero embalado:
  1       -> MITIGATED (estimativa com residuo honesto)
  REFUSED (EXTRAPOLATION_ILL_CONDITIONED) -> guard leave-one-out falhou
O guard: ajuste linear nos primeiros k−1 pontos preve o ultimo; erro
relativo > 0.5 => o decaimento nao e polinomiallocal => extrapolacao nao
e confiavel => REFUSED. FALSIFICAVEL: remova o guard e o teste quebra.
"""
import numpy as np


def fold_expectation(ideal, gamma, depol):
    """Modelo proprio de canal depolarizante por fator de folding γ:
    E(γ) = ideal * depol^γ (ruido cresce com o circuito dobrado).
    Usado nos testes como gerador de sintomas realistas; a mitigacao em
    silicio usa as contagens REAIS em cada γ (ver experiments/)."""
    return ideal * (depol ** gamma)


def richardson_at_zero(gammas, values):
    """Interpolacao de Richardson: polinomio exato pelos pontos, γ=0."""
    gammas = np.asarray(gammas, dtype=float)
    values = np.asarray(values, dtype=float)
    out = 0.0
    for i in range(len(gammas)):
        w = 1.0
        for j in range(len(gammas)):
            if j != i:
                w *= (0.0 - gammas[j]) / (gammas[i] - gammas[j])
        out += values[i] * w
    return float(out)


def _linear_predict_last(gammas, values):
    g = np.asarray(gammas, dtype=float)
    v = np.asarray(values, dtype=float)
    A = np.vstack([g[:-1], np.ones(len(g) - 1)]).T
    slope, inter = np.linalg.lstsq(A, v[:-1], rcond=None)[0]
    return float(slope * g[-1] + inter)


def zne_verdict(gammas, values, guard_tol=0.5):
    """Veredito ternario da mitigacao. gammas crescentes, valores medidos."""
    v = np.asarray(values, dtype=float)
    est = richardson_at_zero(gammas, values)
    pred_last = _linear_predict_last(gammas, values)
    rel_err = abs(pred_last - v[-1]) / max(abs(v[-1]), 1e-12)
    if rel_err > guard_tol:
        return {"decision": "REFUSED",
                "refusal_reason": "EXTRAPOLATION_ILL_CONDITIONED",
                "estimate": est, "guard_relative_error": rel_err,
                "rule": "leave-one-out: decaimento nao e polinomial local; "
                        "extrapolar aqui e vender chute com manto de formula"}
    residual = abs(est - v[0])  # honesto: quanto a mitigacao moveu o numero
    return {"decision": 1, "mode": "MITIGATED", "estimate": est,
            "noisy_value": float(v[0]), "guard_relative_error": rel_err,
            "disclaimer": "estimativa assume ruido ~polinomial em γ ate γ=0; "
                          "recibo deve citar gammas e contagens de cada ponto"}

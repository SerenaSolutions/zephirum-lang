# -*- coding: utf-8 -*-
"""SHOT AUDITOR — controlador trivalente de continuacao de campanhas quanticas.

Decide CONTINUE / STOP / REFUSED apos cada profundidade de uma campanha,
com banda declarada (IC 95% do gradiente) e regra de parada selada ANTES
dos dados. Peeking em runtime => REFUSED (binding via stopping_rule_check).
"""
import math

Z95 = 1.959963985  # quantil 95% (declarado, selado junto com a regra)

def gradiente_band(p_obs_counts, shots):
    """Banda de ruido do gradiente a partir das contagens das DUAS energias.

    p_obs_counts: (counts_mais, counts_menos) — histogramas de E(theta+pi/2)
    e E(theta-pi/2). E = <Z0> + <Z1Z2> medido dos counts (bitstring q3q2q1q0).
    Retorna (gradiente, sigma_g, banda_g): banda_g = Z95 * sigma_g.
    """
    def energia(counts):
        tot = sum(counts.values())
        e = 0.0
        for bs, c in counts.items():
            b = bs.replace(" ", "")
            z0 = 1 - 2 * int(b[-1])           # Z0 (bit menos significativo)
            z1 = 1 - 2 * int(b[-2])           # Z1
            z2 = 1 - 2 * int(b[-3])           # Z2
            e += c * (z0 + z1 * z2)
        return e / tot

    def var_energia(counts):
        tot = sum(counts.values())
        v = 0.0
        for bs, c in counts.items():
            b = bs.replace(" ", "")
            z0 = 1 - 2 * int(b[-1])
            z1 = 1 - 2 * int(b[-2])
            z2 = 1 - 2 * int(b[-3])
            v += c * (z0 + z1 * z2) ** 2
        m = energia(counts)
        return (v / tot - m * m) / tot

    e_m, e_n = energia(p_obs_counts[0]), energia(p_obs_counts[1])
    v_m, v_n = var_energia(p_obs_counts[0]), var_energia(p_obs_counts[1])
    g = (e_m - e_n) / 2.0
    sigma_g = math.sqrt(v_m + v_n) / 2.0
    return g, sigma_g, Z95 * sigma_g

def audit_step(g, banda_g, shots_da_profundidade, selo):
    """Decisao trivalente da profundidade atual. Regra SELADA antes dos dados:
    |g| <= banda_g  => STOP (gradiente indistinguivel de zero no IC 95%)
    |g| >  banda_g  => CONTINUE (sinal acima da banda)
    Incoerencia com o protocolo selado => REFUSED.
    """
    chk = stopping_rule_check(selo, {"shots_observed": shots_da_profundidade,
                                     "decision_at_shot": shots_da_profundidade})
    if chk["decision"] == "REFUSED":
        return {"decisao": "REFUSED", "motivo": chk.get("refusal_reason", "?"),
                "regra": chk.get("rule", ""), "g": g, "banda": banda_g}
    if abs(g) <= banda_g:
        return {"decisao": "STOP", "motivo": "GRADIENTE_DENTRO_DA_BANDA",
                "regra": "IC 95% do gradiente contem zero: pagar mais shots "
                         "e estatistica de mais para um sinal que ja e ruido",
                "g": g, "banda": banda_g}
    return {"decisao": "CONTINUE", "motivo": "GRADIENTE_ACIMA_DA_BANDA",
            "g": g, "banda": banda_g}

from zyql_robust import stopping_rule_check  # noqa: E402  (selo/runtime binding)

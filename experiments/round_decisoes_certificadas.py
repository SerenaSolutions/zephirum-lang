# -*- coding: utf-8 -*-
"""RODADA DECISÕES CERTIFICADAS — o produto inteiro funcionando de ponta a ponta.

Enxurrada de decisoes automaticas sobre EVIDENCIA REAL (contagens medidas em
silicio, recebidas da rodada REPRO) -> cada decisao sai trivalente (1/0/REFUSED)
com banda declarada -> cada decisao selada em cadeia -> e a BATERIA DE ATAQUES:
5 tentativas de fraude contra o historico. Criterio refutavel: se QUALQUER
ataque passar sem deteccao, a rodada FALHA publicamente.
"""
import json, os, sys, hashlib, datetime
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src"))

def h(s):
    return hashlib.sha3_256(s.encode()).hexdigest()

# ---------- ETAPA 1: decisoes sobre evidencia real ----------
# Evidencia: p0 medido em silicio (rodada REPRO, recibos d4e2033c): r1=0.9106, r2=0.9131
P0_MEDIDO = [0.9106, 0.9131]
N_SHOTS = 2048
N_DECISOES = 50
BANDA_CONFIANCA = 0.97  # limiar de decisao da casa (recibos H-2/REPRO)

from zyql_quantum_gate import adaptive_margin_family

def decisao(i, rng):
    """Uma decisao trivalente sobre uma reamostragem da evidencia medida."""
    p_medido = float(rng.choice(P0_MEDIDO))
    # reamostragem binomial da CONTAGEM REAL medida (2048 shots)
    uns = int(rng.binomial(N_SHOTS, p_medido))
    p_obs = uns / N_SHOTS
    margem = adaptive_margin_family(0.05, N_SHOTS, family=2)
    if p_obs >= BANDA_CONFIANCA - margem:
        v = "1"
    elif p_obs <= 0.5 + margem:
        v = "0"
    else:
        v = "REFUSED"
    return {"id": i, "evidencia_p0": round(p_obs, 4), "banda_margem": round(margem, 4),
            "veredito": v, "limiar": BANDA_CONFIANCA,
            "fonte": "reamostragem das contagens REPRO (silicio, recibo d4e2033c)"}

def construir_log(decisoes):
    log = []
    prev = "GENESIS-DC"
    for d in decisoes:
        d2 = dict(d); d2["prev"] = prev
        d2["selo"] = h(json.dumps(d2, sort_keys=True, ensure_ascii=True))
        log.append(d2); prev = d2["selo"]
    return log

def verificar_log(log):
    """True se TODO o historico verifica: selos e encadeamento."""
    prev = "GENESIS-DC"
    for d in log:
        payload = {k: v for k, v in d.items() if k != "selo"}
        if d["prev"] != prev or d["selo"] != h(json.dumps(payload, sort_keys=True, ensure_ascii=True)):
            return False
        prev = d["selo"]
    return True

def executar_bateria(log_original):
    """5 ataques; cada um tem que ser DETECTADO. Retorna lista (ataque, detectado)."""
    res = []
    # A1: edicao retroativa de uma decisao
    log = json.loads(json.dumps(log_original)); log[17]["veredito"] = "1"
    res.append(("A1_edicao_retroativa", not verificar_log(log)))
    # A2: reordenacao da cadeia
    log = json.loads(json.dumps(log_original)); log[5], log[6] = log[6], log[5]
    res.append(("A2_reordenacao_cadeia", not verificar_log(log)))
    # A3: recibo forjado (selo copiado de outro)
    log = json.loads(json.dumps(log_original)); log[9]["selo"] = log[8]["selo"]
    res.append(("A3_recibo_forjado", not verificar_log(log)))
    # A4: decisao fabricada apos o fato, inserida sem selo coerente
    log = json.loads(json.dumps(log_original))
    log.insert(20, {"id": 999, "evidencia_p0": 0.9999, "banda_margem": 0.02,
                    "veredito": "1", "limiar": 0.97, "prev": log[0]["selo"],
                    "selo": h(json.dumps({"fake": True}))})
    res.append(("A4_insercao_fabricada", not verificar_log(log)))
    # A5: remocao silenciosa de um recibo (romper encadeamento)
    log = json.loads(json.dumps(log_original)); del log[30]
    res.append(("A5_remocao_silenciosa", not verificar_log(log)))
    return res

if __name__ == "__main__":
    rng = np.random.default_rng(1701)
    decs = [decisao(i, rng) for i in range(N_DECISOES)]
    log = construir_log(decs)
    n1 = sum(1 for d in log if d["veredito"] == "1")
    n0 = sum(1 for d in log if d["veredito"] == "0")
    nr = sum(1 for d in log if d["veredito"] == "REFUSED")
    integro = verificar_log(log)
    ataques = executar_bateria(log)
    todos_detectados = all(d for _, d in ataques)
    json.dump(log, open(os.path.join(HERE, "decisions_log.json"), "w"), indent=1)
    raiz = h("".join(d["selo"] for d in log))
    rec = {
        "spec": "Z-QEA/2.2", "modulo": "RODADA DECISOES CERTIFICADAS",
        "data": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "protocolo": ("50 decisoes automaticas sobre reamostragens das contagens medidas no silicio "
                      "(REPRO, recibo d4e2033c), cada decisao trivalente com banda declarada e selada "
                      "em cadeia; bateria de 5 ataques ao historico; criterio refutavel: qualquer "
                      "ataque nao detectado => rodada FALHA"),
        "evidencia_fonte": "REPRO r1=0.9106 r2=0.9131 (silicio, recibos encadeados)",
        "decisoes": {"total": N_DECISOES, "confiadas": n1, "negadas": n0, "recusadas": nr},
        "raiz_log": raiz,
        "integridade_verificada": integro,
        "ataques": [{"ataque": a, "detectado": d} for a, d in ataques],
        "ataques_detectados": sum(1 for _, d in ataques if d),
        "veredito_global": ("CERTIFICADO: pipeline integra, 5/5 ataques detectados"
                            if integro and todos_detectados else "FALHOU: ver editais"),
        "previous_seal": json.load(open(os.path.join(HERE, "round_repro_receipt.json")))["selo_sha3_256"],
        "receipt_id": "decisoes-cert-" + raiz[:8],
    }
    rec["selo_sha3_256"] = hashlib.sha3_256(json.dumps({k: v for k, v in rec.items()}, sort_keys=True, ensure_ascii=True, default=str).encode()).hexdigest()
    json.dump(rec, open(os.path.join(HERE, "round_dc_receipt.json"), "w"), ensure_ascii=True, indent=1)
    print("decisoes: %d (1=%d, 0=%d, REFUSED=%d)" % (N_DECISOES, n1, n0, nr))
    print("integridade do log:", "INTEGRA" if integro else "ROMPIDA")
    for a, d in ataques:
        print("ataque %-22s -> %s" % (a, "DETECTADO" if d else "*** PASSOU ***"))
    print("veredito:", rec["veredito_global"])
    print("selo:", rec["selo_sha3_256"][:16], "| encadeado em", rec["previous_seal"][:12])

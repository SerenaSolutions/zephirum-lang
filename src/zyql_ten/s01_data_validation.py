# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Serena Quantum Solutions
"""01 Cientista de dados: qualidade do dado antes do treino."""
import statistics

def check_integrity(rows):
    return sum(1 for r in rows if r) / max(len(rows), 1)

def check_missing(rows, campos):
    total = len(rows) * max(len(campos), 1)
    faltando = sum(1 for r in rows for c in campos if r.get(c) in (None, ""))
    return faltando / max(total, 1)

def check_duplicates(rows):
    vistos, dup = set(), 0
    for r in rows:
        chave = tuple(sorted(r.items()))
        if chave in vistos:
            dup += 1
        vistos.add(chave)
    return dup / max(len(rows), 1)

def check_bias(rows, campo, corte=0.7):
    """Maior fatia de uma categoria acima de `corte` sinaliza enviesamento."""
    contagem = {}
    for r in rows:
        contagem[r.get(campo)] = contagem.get(r.get(campo), 0) + 1
    if not contagem:
        return 1.0
    return max(contagem.values()) / len(rows)

def run(rows, campos, campo_bias="segmento", limites=None):
    limites = limites or {"missing": 0.05, "duplicates": 0.02, "bias": 0.7}
    metricas = {
        "integridade": check_integrity(rows),
        "ausentes": check_missing(rows, campos),
        "duplicados": check_duplicates(rows),
        "vies": check_bias(rows, campo_bias),
    }
    if not rows:
        return {"solucao": "01 data validation", "qualidade": "REFUSED",
                "motivo": "SEM_DADO", "metricas": metricas}
    ok = (metricas["ausentes"] <= limites["missing"]
          and metricas["duplicados"] <= limites["duplicates"]
          and metricas["vies"] <= limites["bias"])
    fiabilidade = 1 - max(metricas["ausentes"], metricas["duplicados"])
    if len(rows) < 30:
        return {"solucao": "01 data validation", "qualidade": "REFUSED",
                "motivo": "AMOSTRA_INSUFICIENTE", "metricas": metricas}
    return {"solucao": "01 data validation",
            "qualidade": 1 if ok else 0,
            "confiabilidade": round(fiabilidade, 3),
            "metricas": {k: round(v, 3) for k, v in metricas.items()}}

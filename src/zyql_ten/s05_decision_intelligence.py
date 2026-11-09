# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Serena Quantum Solutions
"""05 Analista de dados: variacao, anomalia e suficiencia de evidencia."""
from .receipt import selado
import statistics

def variacao(atual, anterior):
    if not anterior:
        return None
    return (atual - anterior) / anterior

def anomalia(serie, limite_z=2.5):
    if len(serie) < 5:
        return None
    media = statistics.fmean(serie)
    desvio = statistics.pstdev(serie) or 1e-9
    return [(i, round((v - media) / desvio, 2)) for i, v in enumerate(serie)
            if abs((v - media) / desvio) > limite_z]

@selado
def run(serie, atual, anterior, fontes):
    var = variacao(atual, anterior)
    anom = anomalia(serie) or []
    if var is None or len(serie) < 5:
        evidencia, motivo = "REFUSED", "SERIE_CURTA"
    elif not fontes:
        evidencia, motivo = "REFUSED", "SEM_FONTE"
    elif anom:
        evidencia, motivo = 1, None
    else:
        evidencia, motivo = 0, "SEM_ANOMALIA"
    return {"solucao": "05 decision intelligence", "recomendacao": evidencia,
            "motivo": motivo, "variacao": None if var is None else round(var, 4),
            "anomalias": anom, "fontes": len(fontes)}

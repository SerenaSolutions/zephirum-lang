# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Serena Quantum Solutions
"""07 Governanca: proveniencia, versao, politica e controles de vies."""
from .receipt import selado
@selado
def run(origem_dado, versao_modelo, versao_aprovada, politica, vies_medido,
        limite_vies=0.7):
    falhas = []
    if not origem_dado:
        falhas.append("PROVENIENCIA_AUSENTE")
    if versao_modelo != versao_aprovada:
        falhas.append("VERSAO_NAO_APROVADA")
    if not politica or not politica.get("revisao_humana"):
        falhas.append("POLITICA_SEM_REVISAO_HUMANA")
    if vies_medido > limite_vies:
        falhas.append("VIES_ACIMA_DO_LIMITE")
    if "PROVENIENCIA_AUSENTE" in falhas:
        status = "REFUSED"
    else:
        status = 0 if falhas else 1
    return {"solucao": "07 ai governance", "compliance": status,
            "motivo": (falhas[0] if falhas else None),
            "falhas": falhas, "origem": origem_dado,
            "versao": versao_modelo}

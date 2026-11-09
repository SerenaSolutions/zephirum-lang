# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Serena Quantum Solutions
"""09 Consultor setorial: mesma camada, regras por setor."""
SETORES = {
    "agro": {"metrica": "consumo_agua", "limite": 1.2, "unidade": "m3/ha"},
    "saude": {"metrica": "exames_inconsistentes", "limite": 0.05, "unidade": "fracao"},
    "financas": {"metrica": "transacoes_suspeitas", "limite": 0.02, "unidade": "fracao"},
    "energia": {"metrica": "perda_distribuicao", "limite": 0.08, "unidade": "fracao"},
    "juridico": {"metrica": "documentos_conflitantes", "limite": 0.03, "unidade": "fracao"},
}

def run(setor, valor, referencia=None):
    if setor not in SETORES:
        return {"solucao": "09 industrial intelligence", "recomendacao": "REFUSED",
                "motivo": "SETOR_DESCONHECIDO", "setor": setor}
    cfg = SETORES[setor]
    base = referencia if referencia is not None else cfg["limite"]
    if valor is None:
        estado, motivo = "REFUSED", "SEM_MEDICAO"
    elif valor > base:
        estado, motivo = 1, None
    else:
        estado, motivo = 0, "DENTRO_DO_LIMITE"
    return {"solucao": "09 industrial intelligence", "recomendacao": estado,
            "motivo": motivo, "setor": setor, "metrica": cfg["metrica"],
            "valor": valor, "referencia": base, "unidade": cfg["unidade"]}

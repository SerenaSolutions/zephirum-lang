# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Serena Quantum Solutions
"""03 Engenheiro de IA/MLOps: controle de execucao do pipeline."""
from .receipt import selado
import hashlib, pathlib

def hash_arquivos(caminhos):
    h = hashlib.sha3_256()
    for c in sorted(caminhos):
        p = pathlib.Path(c)
        if p.exists():
            h.update(p.read_bytes())
        else:
            h.update(b"<ausente>")
    return h.hexdigest()

def custo_estimado(etapas):
    pesos = {"treino": 1.0, "inferencia": 0.3, "avaliacao": 0.2, "publicacao": 0.1}
    return round(sum(pesos.get(e, 0.5) for e in etapas), 2)

@selado
def run(caminhos, etapas, versao_modelo, versao_exigida, custo_teto=2.0):
    digest = hash_arquivos(caminhos)
    custo = custo_estimado(etapas)
    versao_ok = versao_modelo == versao_exigida
    if not caminhos:
        estado, motivo = "REFUSED", "SEM_ARTEFATO"
    elif not versao_ok:
        estado, motivo = 0, "VERSAO_DIVERGENTE"
    elif custo > custo_teto:
        estado, motivo = 0, "CUSTO_ACIMA_DO_TETO"
    else:
        estado, motivo = 1, None
    return {"solucao": "03 pipeline control", "execucao": estado, "motivo": motivo,
            "integridade": digest[:16], "custo": custo,
            "etapas": list(etapas), "versao": versao_modelo}

# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Serena Quantum Solutions
"""10 Empreendedor: prova tecnica com metrica economica."""
def run(benchmarks, custo_por_operacao, custo_concorrente, diferencial_tecnico):
    if not benchmarks:
        return {"solucao": "10 technology proof", "prontidao": "REFUSED",
                "motivo": "SEM_BENCHMARK"}
    reproduzivel = all(b.get("reproduzivel") for b in benchmarks)
    vantagem = (custo_concorrente - custo_por_operacao) / custo_concorrente
    if not reproduzivel:
        estado, motivo = "REFUSED", "BENCHMARK_NAO_REPRODUZIVEL"
    elif not diferencial_tecnico:
        estado, motivo = 0, "SEM_DIFERENCIAL"
    elif vantagem <= 0:
        estado, motivo = 0, "SEM_VANTAGEM_ECONOMICA"
    else:
        estado, motivo = 1, None
    return {"solucao": "10 technology proof", "prontidao": estado, "motivo": motivo,
            "vantagem_custo": round(vantagem, 3),
            "custo_operacao": custo_por_operacao,
            "benchmarks": len(benchmarks)}

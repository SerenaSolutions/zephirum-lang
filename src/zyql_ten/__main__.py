# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Serena Quantum Solutions
"""Roda as dez solucoes com dados de exemplo e imprime o quadro."""
import json
from . import SOLUCOES
from . import (s01_data_validation as s01, s02_model_guardian as s02,
               s03_pipeline_control as s03, s04_data_router as s04,
               s05_decision_intelligence as s05, s06_compute_router as s06,
               s07_ai_governance as s07, s08_scientific_verification as s08,
               s09_industrial_intelligence as s09, s10_technology_proof as s10)

def executar():
    linhas = [
        s01.run([{"id": i, "valor": i * 2, "segmento": "a" if i % 2 else "b"}
                 for i in range(60)], ["id", "valor", "segmento"]),
        s02.run([1, 0, 1, 1, 0, 1, 0, 1] * 4, [1, 0, 1, 1, 0, 1, 0, 1] * 4,
                [10, 11, 12, 13, 14], [10, 11, 12, 13, 15]),
        s03.run(["pyproject.toml"], ["avaliacao", "publicacao"], "1.5.0", "1.5.0"),
        s04.run([{"id": 1}, {"id": 2}, {"id": 1}, {"x": 9}], ["id"]),
        s05.run([10, 12, 11, 13, 12, 40, 11, 12], 12, 10, ["erp"]),
        s06.run(n_qubits=6, tem_solucao_classica=False, problema_estrutural=True),
        s07.run("catalogo/2026-11", "1.5.0", "1.5.0",
                {"revisao_humana": True}, 0.42),
        s08.run(),
        s09.run("agro", 1.7),
        s10.run([{"reproduzivel": True}, {"reproduzivel": True}], 0.4, 1.0, True),
    ]
    return linhas

def main():
    for r in executar():
        print(json.dumps(r, ensure_ascii=False))
    decisao = [r.get("qualidade", r.get("deploy", r.get("execucao", r.get("rota",
               r.get("recomendacao", r.get("compliance", r.get("evidencia",
               r.get("prontidao")))))))) for r in executar()]
    import sys
    print("solucoes executadas: 10", file=sys.stderr)

if __name__ == "__main__":
    main()

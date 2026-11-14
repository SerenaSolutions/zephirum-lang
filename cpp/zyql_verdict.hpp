// SPDX-License-Identifier: Apache-2.0
// Copyright (c) 2026 Serena Quantum Solutions
#pragma once
#ifdef __cplusplus
extern "C" {
#endif

/* Codigos de rota: 1 classico, 2 quantico, 0 recusado. */
int zyql_rota(int tem_solucao_classica, int problema_estrutural,
              int profundidade, int orcamento);

/* Veredito trivalente: 1 autoriza, 0 nega, 2 recusa por falta de evidencia. */
int zyql_veredito(double p0, double epsilon);

#ifdef __cplusplus
}
#endif

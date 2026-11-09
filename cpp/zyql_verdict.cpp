// SPDX-License-Identifier: Apache-2.0
// Copyright (c) 2026 Serena Quantum Solutions
// Nucleo numerico em C++ do ZYQL: rota de execucao e veredito trivalente.
// A implementacao Python equivalente fica em src/zyql_ten/ e as duas sao
// confrontadas por teste de concordância, para que divergência apareça.
#include "zyql_verdict.hpp"

extern "C" int zyql_rota(int tem_solucao_classica, int problema_estrutural,
                         int profundidade, int orcamento) {
    if (tem_solucao_classica) return 1;
    if (!problema_estrutural) return 1;
    if (profundidade <= 0) return 0;
    if (profundidade > orcamento) return 0;
    return 2;
}

extern "C" int zyql_veredito(double p0, double epsilon) {
    if (epsilon < 0.0 || epsilon >= 0.5) return 2;
    if (p0 >= 1.0 - epsilon) return 1;
    if (p0 <= epsilon) return 0;
    return 2;
}

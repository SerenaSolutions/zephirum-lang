# Adaptador QASM 3 <-> ZYQL

Prova de interoperabilidade sem dependencia de fornecedor: o nucleo ZYQL exporta
e importa o padrao aberto OpenQASM 3 usando apenas biblioteca padrao + numpy.

Escopo declarado: h, x, y, z, s, sdg, t, tdg, cx, rz, measure.
Fora do escopo: QasmRefused com motivo — nunca ignorado em silencio (fail-closed).

Resultados (test_adapter.py): 10/10 PASS
- ida e volta identica em Bell, GHZ-3, DJ constante, DJ balanceado, rotacao T, medida
- 4 recusas corretas (porta desconhecida, sem cabecalho, indice fora, sem declaracao)

Conferencia externa: um analisador independente do padrao leu nosso QASM
(3 qubits, 4 operacoes) e o texto devolvido por ele foi reabsorvido pelo nosso
adaptador com estado identico (tolerancia 1e-14). O adaptador NAO importa SDK de
fornecedor; a conferencia foi feita fora do produto.

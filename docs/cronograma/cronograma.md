# Cronograma ZEPHIRUM ZYQL · 60 dias

Marco zero: 09/11/2026, 13:00 BRT (PR #1433 na `main` do Qiskit/ecosystem).

| # | Janela | Fase | Marco | Aceite | Gate |
|---|---|---|---|---|---|
| 00 | 2026-11-09 a 2026-11-09 | Fechamento | Merge aceito e propagado | Concluido |  |
| 01 | 2026-11-10 a 2026-11-12 | Consolidacao | Guard de metadado no CI | PR de teste falha de proposito | G1 |
| 02 | 2026-11-10 a 2026-11-14 | Consolidacao | Circuitos equivalentes nos 3 caminhos | Mesmo circuito canonico ou diferenca explicada linha por linha | G1 |
| 03 | 2026-11-10 a 2026-11-19 | Consolidacao | Custodia de chave ML-DSA-44 (RF-06) | Verificacao por terceiro com a chave publica |  |
| 04 | 2026-11-10 a 2026-11-19 | Consolidacao | Suite reproduzivel em 3.10 | 193+ testes aprovados sem xfail novo |  |
| 05 | 2026-11-20 a 2026-11-23 | Integracao | Matriz de compatibilidade SDK 2.x | Piso e teto declarados e testados |  |
| 06 | 2026-11-20 a 2026-11-25 | Integracao | OpenQASM 3 round-trip | Equivalencia semantica comprovada |  |
| 07 | 2026-11-22 a 2026-11-26 | Integracao | Transpiler em niveis 0 a 3 | Tabela publicada sem alegacao de superioridade |  |
| 08 | 2026-11-24 a 2026-11-28 | Integracao | Aer contra kernel proprio | TVD declarada, nao apenas resultado final |  |
| 09 | 2026-11-27 a 2026-11-29 | Integracao | Primitives V2 (Sampler e Estimator) | Decisao registrada em ADR |  |
| 10 | 2026-11-30 a 2026-12-07 | Verificacao | Reproducao em QPU com protocolo selado | Qubits, profundidade e throughput declarados | G2 |
| 11 | 2026-11-30 a 2026-12-09 | Verificacao | Auditoria de recibo | O que SHA3 prova e nao prova, escrito | G3 |
| 12 | 2026-12-03 a 2026-12-11 | Verificacao | Ruido e taxa de REFUSED | Recusa tratada como informacao, nao falha |  |
| 13 | 2026-12-07 a 2026-12-14 | Verificacao | Benchmarks com referencia justa | Mesmas shots, mesmo backend e mesmo transpile |  |
| 14 | 2026-12-12 a 2026-12-14 | Verificacao | Limitacoes conhecidas | Lista honesta, sem eufemismo |  |
| 15 | 2026-12-15 a 2026-12-19 | Produto | ZYQL Decision Engine independente | Instalavel e testado fora do repositorio |  |
| 16 | 2026-12-17 a 2026-12-21 | Produto | Exemplos de integracao executaveis | Verde no CI, nao notebook morto |  |
| 17 | 2026-12-19 a 2026-12-22 | Produto | Documentacao de dev e politica de suporte | Requisito do ecossistema atendido |  |
| 18 | 2026-12-22 a 2026-12-24 | Produto | Demonstracao funcional | Recibo conferido por quem assiste |  |
| 19 | 2026-12-25 a 2026-12-31 | Ciencia | Artigo v1 com DOI | Texto com limitacoes e reprodutibilidade |  |
| 20 | 2026-12-29 a 2027-01-03 | Ciencia | Benchmarks publicados | Terceiro reproduz sem falar conosco |  |
| 21 | 2027-01-01 a 2027-01-06 | Ciencia | Pedido formal de reproducao | Resposta registrada por escrito | G4 |
| 22 | 2027-01-05 a 2027-01-09 | Ciencia | Dossie de manutencao | Sustentavel por 12 meses |  |

## Gates

- **G1** A especificacao do teste de 3 caminhos esta escrita e selada? (se reprovar: Nao executa benchmark)
- **G2** Passou local e em Aer com recibo? (se reprovar: Nao vai para QPU)
- **G3** Protocolo selado antes do submit e tres metricas declaradas? (se reprovar: Job invalido como evidencia)
- **G4** Terceiro reproduziu com identidade propria? (se reprovar: Sem alegacao cientifica)

## Dependências

- Custodia da chave ML-DSA-44: depende de Decisao do supervisor; Todo recibo segue anonimo; marcos 11 e 19 travam
- Revisores externos: depende de Terceiros; Marco 21 nao fecha e o artigo fica sem validacao
- Creditos de infraestrutura: depende de Renovacao mensal; Job pesado do harness para de rodar
- Edital CIQUANTA 2 sem 2026: depende de MCTI; Fomento nao entra no ciclo de 60 dias

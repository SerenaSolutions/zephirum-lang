# Auditoria: `src/zyql_ten/` contra `docs/REQUISITOS_ARQUITETURA_ZYQL.md`

Reauditoria de 09/11/2026 apos as correcoes. Evidencia medida nesta sessao.

| Req | Item | Status | Evidencia |
|---|---|---|---|
| RF-01 | Nucleo de decisao congelado | **ATENDE** | decide() so em zyql_runtime; 0 definicoes proprias nos 10 modulos |
| RF-02 | Provedores de evidencia | **ATENDE** | 10/10 com run() proprio; 15 testes nos modulos de setor |
| RF-03 | Reprovado != sem evidencia | **ATENDE** | 10/10 declaram motivo; s07 e s08 corrigidos |
| RF-04 | Roteador de execucao | **ATENDE** | C++ e Python concordam na grade completa de casos |
| RF-05 | Recibo auditavel por operacao | **ATENDE** | 10/10 com recibo SHA3 schema 1.0.0; verificar() = True |
| RF-06 | Assinatura fora do CI | **PARCIAL** | recibo declara assinatura ausente; ML-DSA nao assina os 10 ainda |
| RF-07 | Adaptador + 3 metricas | **ATENDE** | qubits, profundidade e throughput com origem declarada; Qiskit 2.6.0 |
| RF-08 | Governanca declarada | **ATENDE** | falhas por codigo e motivo explicito (VERSAO_NAO_APROVADA) |
| RF-09 | Demonstracao setorial unica | **ATENDE** | 10 linhas JSON; resumo em stderr |
| RF-10 | Verificacao por terceiro | **NAO ATENDE** | verificador independente inexistente; depende de terceiro |
| RNF-01 | Piso Python 3.11 | **ATENDE** | pyproject >=3.11; lock >=3.11 |
| RNF-02 | Lockfile | **ATENDE** | uv.lock coerente com o piso: 90 pacotes |
| RNF-03 | Latencia < 1 s | **ATENDE** | decide() em milissegundos; roteador paga a transpilacao |
| RNF-04 | Custo por operacao | **PARCIAL** | profundidade e throughput locais; segundos de QPU nao medidos |
| RNF-05 | Suite verde | **ATENDE** | 208 testes passando |
| RNF-06 | Portao de conformidade | **ATENDE** | 19/19 itens verdes |
| RNF-07 | Versionamento separado | **ATENDE** | gramatica 1.5.0 e schema de recibo 1.0.0 independentes |

**Resumo: 14 atendem, 2 parciais, 1 nao atendem.**

Antes: 8 atendiam, 4 parciais, 5 nao atendiam. Resta um requisito nao atendido, RF-10, que depende
de terceiro, e dois parciais conscientes: assinatura ML-DSA e custo em segundos de QPU.

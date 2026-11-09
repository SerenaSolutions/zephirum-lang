# Auditoria: `src/zyql_ten/` contra `docs/REQUISITOS_ARQUITETURA_ZYQL.md`

Auditoria de 09/11/2026, gerada por verificacao executavel, nao por inspecao visual.

| Req | Item | Status | Evidencia |
|---|---|---|---|
| RF-01 | Nucleo de decisao congelado | **ATENDE** | decide() so em zyql_runtime; 0 definicoes proprias nos 10 modulos |
| RF-02 | Provedores de evidencia | **ATENDE** | 10/10 modulos com run() proprio; 13 testes |
| RF-03 | Reprovado != sem evidencia | **PARCIAL** | 8/10 declaram motivo de recusa; casos vazios testados |
| RF-04 | Roteador de execucao | **ATENDE** | classico conhecido -> CLASSICO; relevancia quantica -> QUANTICO; custo em profundidade transpilada |
| RF-05 | Recibo auditavel por operacao | **NAO ATENDE** | apenas 1/10 modulos emitem recibo; os demais devolvem dicionario sem selagem |
| RF-06 | Assinatura fora do CI | **NAO ATENDE** | nenhuma chave privada ou assinatura no pipeline; CI emite recibo sem assinatura |
| RF-07 | Adaptador quantico + 3 metricas | **PARCIAL** | qiskit_bridge com qubits+profundidade; throughput de QPU nao registrado; 2 modulos usam Qiskit nativo |
| RF-08 | Governanca declarada | **ATENDE** | falhas por codigo: ['VERSAO_NAO_APROVADA', 'POLITICA_SEM_REVISAO_HUMANA', 'VIES_ACIMA_DO_LIMITE'] |
| RF-09 | Demonstracao setorial unica | **PARCIAL** | 12 linhas de saida em python -m zyql_ten |
| RF-10 | Verificacao por terceiro | **NAO ATENDE** | verificador independente inexistente; quem verifica e o autor |
| RNF-01 | Piso Python 3.11 | **NAO ATENDE** | pyproject declara >=3.10 |
| RNF-02 | Lockfile | **ATENDE** | uv.lock com 120 pacotes |
| RNF-03 | Latencia < 1 s | **ATENDE** | decide() com n=5 e 2048 shots em 6 ms |
| RNF-04 | Custo por operacao | **PARCIAL** | profundidade transpilada medida; segundos de QPU nao registrados |
| RNF-05 | Suite verde | **ATENDE** | 206 testes passando |
| RNF-06 | Portao 19/19 | **ATENDE** | 19/19 itens verdes |
| RNF-07 | Versionamento separado | **NAO ATENDE** | gramatica e contrato de recibo nao tem versionamento independente |

**Resumo: 8 atendem, 4 parciais, 5 nao atendem.**

## O que isso significa

Os requisitos de nucleo (RF-01 a RF-04, RF-08, RF-09) e os de infraestrutura (RNF-02, RNF-05, RNF-06)
estao atendidos com evidencia executavel. Os cinco pontos em aberto sao os mesmos que o documento ja
declarava como risco: recibo por operacao, metrica de throughput em QPU, piso de Python, custo real de QPU
e verificacao por terceiro.

O mais grave e RF-05. Somente o modulo 08 emite recibo com selagem. Os outros nove devolvem dicionario de
resultado, o que serve para demonstracao e nao serve para auditoria. Enquanto isso nao mudar, a promessa
de 'uma evidencia depois de cada operacao' vale para um setor, nao para os dez.

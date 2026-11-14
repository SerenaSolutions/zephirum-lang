# Os dez modulos de setor do ZYQL — documentacao tecnica

Versao 1.0, 09/11/2026. Codigo em `src/zyql_ten/`, testes em `tests/test_zyql_ten.py`.
Medido em Python 3.11.16 com Qiskit nativo.

## Contrato comum

Cada modulo expoe `run(...)` que devolve as metricas do setor e uma chave de veredito.
Nao ha excecao silenciosa: entrada insuficiente resulta em `REFUSED` com motivo
declarado, conforme RF-03 do documento de requisitos.

## Modulos

### `s01_data_validation` — Cientista de dados

**Objetivo:** 01 Cientista de dados: qualidade do dado antes do treino.

**Assinatura:** `run(rows, campos, campo_bias='segmento', limites=None)`

**Veredito:** `qualidade` = `REFUSED` | **tempo:** 0.03 ms

**Saida:** `solucao`, `motivo`, `metricas`

### `s02_model_guardian` — Engenheiro de ML

**Objetivo:** 02 Engenheiro de ML: drift e degradacao em producao.

**Assinatura:** `run(previsoes, reais, treino_ref, producao, limite_drift=0.2, limite_erro=0.15)`

**Veredito:** `deploy` = `REFUSED` | **tempo:** 0.04 ms

**Saida:** `solucao`, `motivo`, `erro`, `drift`, `amostras`

### `s03_pipeline_control` — Engenheiro de IA/MLOps

**Objetivo:** 03 Engenheiro de IA/MLOps: controle de execucao do pipeline.

**Assinatura:** `run(caminhos, etapas, versao_modelo, versao_exigida, custo_teto=2.0)`

**Veredito:** `execucao` = `1` | **tempo:** 0.37 ms

**Saida:** `solucao`, `motivo`, `integridade`, `custo`, `etapas`

### `s04_data_router` — Engenheiro de dados

**Objetivo:** 04 Engenheiro de dados: roteamento e deduplicacao.

**Assinatura:** `run(registros, esquema, ja_processados=None)`

**Veredito:** `rota` = `1` | **tempo:** 0.03 ms

**Saida:** `solucao`, `motivo`, `recebidos`, `novos`, `evitados`

### `s05_decision_intelligence` — Analista de dados

**Objetivo:** 05 Analista de dados: variacao, anomalia e suficiencia de evidencia.

**Assinatura:** `run(serie, atual, anterior, fontes)`

**Veredito:** `recomendacao` = `0` | **tempo:** 0.11 ms

**Saida:** `solucao`, `motivo`, `variacao`, `anomalias`, `fontes`

### `s06_compute_router` — Arquiteto de solucao

**Objetivo:** 06 Arquiteto: roteador de execucao classico, ML ou quantico (Qiskit).

**Assinatura:** `run(n_qubits, tem_solucao_classica, problema_estrutural, orcamento=40)`

**Veredito:** `rota` = `QUANTICO` | **tempo:** 1239.59 ms

**Saida:** `solucao`, `motivo`, `custo_quantico`, `qubits`, `orcamento`

### `s07_ai_governance` — Governanca e etica

**Objetivo:** 07 Governanca: proveniencia, versao, politica e controles de vies.

**Assinatura:** `run(origem_dado, versao_modelo, versao_aprovada, politica, vies_medido, limite_vies=0.7)`

**Veredito:** `compliance` = `1` | **tempo:** 0.0 ms

**Saida:** `solucao`, `falhas`, `origem`, `versao`

### `s08_scientific_verification` — Pesquisador de IA

**Objetivo:** 08 Pesquisador: base classica (Statevector) contra o runtime ZYQL.

**Assinatura:** `run(n=3, shots=2048, seed=1701)`

**Veredito:** `evidencia` = `1` | **tempo:** 13.68 ms

**Saida:** `solucao`, `p0_constante`, `p0_balanceado`, `veredito_zyql`, `reproduzivel`

### `s09_industrial_intelligence` — Consultor setorial

**Objetivo:** 09 Consultor setorial: mesma camada, regras por setor.

**Assinatura:** `run(setor, valor, referencia=None)`

**Veredito:** `recomendacao` = `1` | **tempo:** 0.0 ms

**Saida:** `solucao`, `motivo`, `setor`, `metrica`, `valor`

### `s10_technology_proof` — Empreendedor

**Objetivo:** 10 Empreendedor: prova tecnica com metrica economica.

**Assinatura:** `run(benchmarks, custo_por_operacao, custo_concorrente, diferencial_tecnico)`

**Veredito:** `prontidao` = `REFUSED` | **tempo:** 0.01 ms

**Saida:** `solucao`, `motivo`, `vantagem_custo`, `custo_operacao`, `benchmarks`

## Ponte com Qiskit

`src/zyql_ten/qiskit_bridge.py` mantem a mesma funcao em duas representacoes: callable puro
para o nucleo ZYQL e circuito nativo (`QuantumCircuit`, `Statevector`, `transpile`).
`cross_check(n,tipo)` roda as duas e devolve se concordam; divergencia reprova o teste.


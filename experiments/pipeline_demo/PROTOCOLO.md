# PRÉ-REGISTRO — DEMONSTRAÇÃO REPRODUZÍVEL ZYQL DE PONTA A PONTA (ENTREGÁVEL 7)

**Data do pré-registro:** 2026-11-07
**Status:** REGISTRADO ANTES DA EXECUÇÃO (pre-registered)
**Ambiente:** Python 3.11 (`/tmp/zyvenv/bin/python`), Qiskit 2.6.1, Qiskit-Aer 0.18.2 (sem QPU, sem credenciais IBM)

---

## 1. Hipótese Testável em Uma Frase

O pipeline ZYQL reproduzível de 9 etapas executa a identificação de oráculo booleano linear com 1 consulta quântica simulada, valida o resultado por verificação clássica independente e recusa estritamente qualquer divergência ou violação de promessa com zero falsos positivos, emitindo recibos encadeados com integridade SHA3-256 verificável offline.

---

## 2. Critérios Objetivos de Sucesso e Falha

Todos os critérios são estritamente quantitativos e numéricos, sem adjetivação subjetiva.

### Critérios de Sucesso (cumprimento conjunto obrigatório):
1. **Identificação Exata da Máscara:** $\hat{s} == s_{alvo}$ com probabilidade observada na medição $p(\hat{s}) \ge 0.9900$ (amostragem ideal com 2048 shots).
2. **Economia Algorítmica de Consultas:** exatamente 1 consulta quântica ao oráculo ($Q_{quantum} = 1$), contra $n$ consultas determinísticas exigidas no caminho clássico ($Q_{classico} = n$).
3. **Decisão de Rota Trivalente:** roteamento estrito importado do repositório:
   - Rota `simulacao` quando o orçamento clássico for insuficiente ($B_{classico} < n$) e a promessa do oráculo for válida;
   - Rota `classico` quando $B_{classico} \ge n$;
   - Rota `recusa` (`REFUSED`) quando a promessa for violada (`audit_promise == NO_PROMISE`) ou a configuração estiver fora dos limites suportados ($n \notin [1, 8]$).
4. **Verificação Independente:** 0 discrepâncias ($D = 0$) na checagem ortogonal direta $f(e_i) == (\hat{s} \gg i) \& 1$ para todos os $i \in \{0, \dots, n-1\}$.
5. **Comportamento Refutável perante Divergência:** se $D \ge 1$ (divergência induzida ou real), o pipeline emite obrigatoriamente veredito `REFUSED` com razão `INDEPENDENT_VERIFICATION_MISMATCH` (taxa de aprovação espúria = 0%).
6. **Integridade do Recibo:** 100% de correspondência no selo SHA3-256 recalculado canonicamente sobre o payload: `recomputed == declared`.
7. **Encadeamento Criptográfico:** para qualquer recibo com predecessor $k > 1$, `payload.prev == cadeia[k-1].selo_sha3_256`; para o primeiro recibo, `payload.prev == "GENESIS"`.
8. **Não-Regressão da Base Existente:** execução de `pytest tests -q` mantém rigorosamente os 147 testes aprovados (0 quebras).

### Critérios de Falha (qualquer ocorrência reprova a demonstração):
1. Máscara recuperada divergente da real ($\hat{s} \neq s_{alvo}$) sob promessa válida sem que haja emissão de `REFUSED`.
2. Probabilidade medida $p(\hat{s}) < 0.9500$ sem justificativa ou recusa estatística por banda de ruído.
3. Número de consultas quânticas $> 1$ para resolver Bernstein-Vazirani.
4. Qualquer aprovação (veredito $\neq$ `REFUSED`) quando a verificação independente reportar $D > 0$.
5. Recibo com selo SHA3-256 violado (`recomputed != declared`) ou campo `prev` descontinuado na cadeia.
6. Qualquer requisição a hardware real (QPU) ou tentativa de leitura de credenciais externas IBM.
7. Modificação de arquivos fora de `experiments/pipeline_demo/` ou queda dos 147 testes do pytest.

---

## 3. O Que a Demonstração NÃO Prova (Limites Declarados)

Para manter a honestidade científica do repositório Zephirum, delimitamos com rigor o que este experimento **não** reivindica:
1. **Não prova vantagem computacional de tempo prático:** Para dimensões pequenas ($n \le 8$), qualquer CPU convencional executa $n$ consultas em menos de 1 milissegundo. A demonstração comprova vantagem informacional de consultas ($1$ vs $n$), não superioridade de relógio de parede frente a supercomputadores clássicos.
2. **Não prova robustez em hardware ruidoso real:** O pipeline roda em simulação local (`qiskit_aer.AerSimulator` / vetor de estado determinístico), sem efeitos físicos de decoerência ($T_1, T_2$), crosstalk entre cúbits vizinhos ou assimetria de leitura (SPAM). Não substitui rodadas certificadas com IDs de job de hardware emitidos por laboratórios quânticos.
3. **Não prova resolução universal para funções arbitrárias:** A identificação com 1 consulta depende estritamente da estrutura do oráculo (promessa Bernstein-Vazirani / linearidade sobre GF(2)). Funções não-lineares gerais não gozam dessa garantia e são recusadas na auditoria de promessa.
4. **Não altera infraestrutura do sistema:** O experimento é uma prova autocontida de reprodutibilidade em `experiments/pipeline_demo/`, sem impacto nas APIs ou módulos estáveis de `src/`.

---

## 4. Tabela das 9 Etapas do Pipeline

| Etapa | Nome da Etapa | Entrada | Ação / Algoritmo | Saída / Artefato | Módulo Existente Utilizado | Critério Refutável |
|---|---|---|---|---|---|---|
| 1 | Entrada em ZYQL | Problema formulado (tipo, $n$, máscara $s$ ou tabela $f$, orçamento $B_{classico}$, shots) | Validação estrutural pré-oráculo | Objeto de problema ZYQL validado | `src/zyql_runtime.py` (`_validate`) | $n \in [1, 8]$, shots $\in [16, 100000]$ |
| 2 | Decisão clássica suficiente | Problema ZYQL, orçamento clássico $B_{classico}$ | Auditoria da promessa do oráculo e contagem de consultas clássicas determinísticas | Relatório de viabilidade e promessa | `src/zyql_oracle_id.py` (`audit_promise`), `src/zyql_quantum_gate.py` (`classical_deterministic`) | `audit_promise` $\in$ {`PROMISE_OK`, `NO_PROMISE`}; custo determinístico $= n$ |
| 3 | Decisão de rota | Relatório clássico e restrições | Aplicação da lógica trivalente da casa: `simulacao` (vantagem necessária), `classico` (se $B_{classico} \ge n$), ou `recusa` (promessa rompida/erro) | Veredito de rota (`classico` / `simulacao` / `recusa`) | Lógica trivalente de `src/zyql_runtime.py` (`Verdict`) | Rota $\in$ {`classico`, `simulacao`, `recusa`} sem exceção silenciosa |
| 4 | Conversão Qiskit | Rota `simulacao`, parâmetros $n$ e $s$ | Montagem do circuito quântico de Bernstein-Vazirani com Hadamard e oráculo de inversão de fase via CNOTs | Objeto `QuantumCircuit` | Padrão Qiskit compatível com `src/zyql_oracle_id.py` (`reveal_linear`) | $n+1$ qubits (entrada + âncilla), $n$ bits de medida |
| 5 | Transpilação | `QuantumCircuit`, backend alvo | Transpilação e otimização para conjunto nativo do backend simulador com semente determinística | Circuito transpilado + métricas de profundidade | `qiskit.transpile` com `seed_transpiler=1701` | Profundidade pós-transpilação registrada, portas mapeadas |
| 6 | Execução | Circuito transpilado, shots | Disparo da simulação em backend local com semente fixa (sem QPU, sem rede) | Objeto `Result` com contagens cruas de medição | `qiskit_aer.AerSimulator` (`seed_simulator=1701`) | $\sum \text{counts} == \text{shots}$ |
| 7 | Coleta | Histograma de contagens | Extração do estado medido dominante e cálculo da probabilidade experimental $p_{obs}$ | Hipótese candidata $\hat{s}$ e probabilidade $p_{obs}$ | Padrão `_marginal_input` / `_top` de `src/zyql_oracle_id.py` | Estado dominante com $p_{obs} \ge 0.9900$ |
| 8 | Verificação independente | Hipótese $\hat{s}$, função oráculo $f$ | Avaliação determinística clássica independente nas $n$ bases unitárias $f(e_i) == (\hat{s} \gg i) \& 1$. Se divergir, veredito $\to$ `REFUSED` | Relatório de divergências ($D = 0$ ou $D > 0$) e veredito final | Avaliação direta independente contra $f$ | $D == 0 \implies 1$; $D > 0 \implies REFUSED$ |
| 9 | Recibo selado | Veredito final, métricas, estado de cadeia | Serialização canônica do payload, vinculação ao recibo anterior (`prev`), cálculo do selo SHA3-256 e persistência | Recibo JSON selado e inserção em `cadeia.json` | `src/battery_ci.py` (`canon`), `src/qroute/receipt.py` | Selo SHA3-256 íntegro e encadeamento em `cadeia.json` verificado |

---

## 5. Selo Criptográfico de Pré-Registro

Declaração de integridade do pré-registro calculada em SHA3-256 sobre a totalidade do corpo deste documento (excluindo estritamente a linha a seguir contendo o selo):
**SHA3-256:** `0d8bf6a3f8b7238fd14fe72b308e192aff2a8624d4dc38324e39a4d18b9278cd`

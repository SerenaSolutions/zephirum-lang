# Relatório de Auditoria Técnica — ZYQL / Zephirum (2026-11-07)

## 1. Reprodução da Suíte de Testes
- **Comando**: `PYTHONPATH=src:api /tmp/zyvenv/bin/python -m pytest tests -q`
- **Resultado exato**: 147 aprovados, 0 falhas, 1 aviso (`StarletteDeprecationWarning`) em 31.24s.
- **Falhas**: Nenhuma falha identificada na suíte completa de testes.

## 2. Mapeamento da Arquitetura

### Módulos em `src/`
| Módulo | Função |
|---|---|
| `battery_ci.py` | Bateria de CI para verificação canônica da decisão trivalente e recibos. |
| `oq3.py` | Transpilação e exportação de circuitos para a especificação OpenQASM 3. |
| `quantum_safe_readiness.py` | Avaliação de prontidão pós-quântica (QSR) aplicando Desigualdade de Mosca. |
| `quantum_types.py` | Tipos quânticos de primeira classe (`QBit`, `QReg`) com checagem de no-cloning. |
| `shot_auditor.py` | Controlador sequencial trivalente de parada de amostragem sem peeking. |
| `zephirum.h` | Declaração de cabeçalho C da API do núcleo (sem implementação .c no repositório). |
| `zkernel.py` | Núcleo de simulação com tabela de processos, scheduler e registro de backends. |
| `zqea_kem.py` | Encapsulamento de chaves pós-quântico (ML-KEM-768) para envelopes confidenciais. |
| `zqea_sig.py` | Assinatura pós-quântica (ML-DSA-44) e validação de cadeia de recibos. |
| `zquantum.py` | Simulador quântico de vetor de estado em amplitude complexa float64. |
| `zyql_auditkit.py` | Certificação estatística de entropia quântica (CPA-01) com selo de recibo. |
| `zyql_cirq.py` | Ponte de interoperabilidade e paridade semântica com Google Cirq. |
| `zyql_lisp.py` | Parser Lark e interpretador S-expressions da linguagem ZYQL v2 (.zph). |
| `zyql_llm_compress.py` | Compressão tensorial (Tensor-Train / SVD) de pesos com controle de erro. |
| `zyql_mps.py` | Simulador em Matrix Product States (MPS) para contração de circuitos. |
| `zyql_oracle_id.py` | Identificação de oráculos (Deutsch-Jozsa, Bernstein-Vazirani) e promessas. |
| `zyql_protocols.py` | Protocolos P-08 (ZNE) e P-10 (fronteira clássica vs hardware) com Qiskit. |
| `zyql_quantum_gate.py` | Porta de interferência Deutsch-Jozsa com banda analítica e bounds de Hoeffding. |
| `zyql_rag_layer.py` | Recuperação densa/esparsa via BM25 e aterramento técnico de regras neurais. |
| `zyql_robust.py` | Guardas adversariais e testes de estresse estatístico para validação de veredito. |
| `zyql_runtime.py` | Runtime de produção com interface `decide()`, gates prévios e selo SHA3. |
| `zyql_selfverified.py` | Verificação com circuito espelho C† no mesmo job para validação de fidelidade. |
| `zyql_witness.py` | Testemunha de recusa fundamentada por TVD com intervalo de Hoeffding. |
| `zyql_world3.py` | Protocolos e verificação de hardware para o benchmark WORLD-3. |
| `zyql_worldscale.py` | Protocolos W-01 a W-03 para teste algorítmico e análogo fotônico em escala. |
| `zyql_zne.py` | Extrapolação a ruído zero (Zero-Noise Extrapolation) nativa para mitigação de erro. |
| `zyqml_core.py` | Classificação variacional quântica (QML) com banda trivalente de confiança. |
| `qroute/` | Roteamento com Grover e veredito trivalente (core, graph, grover, hardware, receipt). |
| `zqgate/` | Interface CLI legada para decisão trivalente prévia à execução. |

### Superfície da API
- **API do Núcleo (`api/server.py` montada em `/v1/core`)**: `GET /health`, `GET /limits`, `POST /bound` (álgebra de Hoeffding), `POST /decide` (decisão 1/0/REFUSED + recibo SHA3-256), `POST /verify` (checagem de integridade), `POST /oracle/reveal` (Bernstein-Vazirani), `POST /oracle/promise` (auditoria de promessa).
- **Gateway Unificado (`api/gateway.py`)**: `GET /health`, `GET /v1/catalog`, `GET /v1/limits`, `POST /v1/qsr/assess` (critério de Mosca), `POST /v1/lang/run` (sandbox `.zph`). Autenticação via `X-API-Key` com escopos (`read`, `decide`, `qsr`, `lang`) e rate limit de 120 req/min.
- **Faturamento (`api/billing.py` em `/v1/billing`)**: `GET /planos`, `POST /checkout` (Stripe), `POST /webhook` (idempotente assinado), `GET /saldo`, `POST /verificar` (débito de cotas).

### Trilho Trivalente (1 / 0 / REFUSED)
Implementado em `src/zyql_quantum_gate.py` (`_trivalent`) e orquestrado por `src/zyql_runtime.py` (`decide`):
1. **Circuito de Interferência**: Prepara $|+^{\otimes n}\rangle$, aplica oráculo de fase $U_f |x\rangle = (-1)^{f(x)}|x\rangle$ (1 chamada quântica), reaplica Hadamards e mede a probabilidade $p_0$ de $|0^{\otimes n}\rangle$.
2. **Bandas e Limites**: Margem fixa de $\pm 0.15$ ou adaptativa $\sqrt{\ln(2/\epsilon)/(2N)}$ (Hoeffding inverso com correção Bonferroni para famílias).
3. **Regra de Decisão**:
   - $p_0 \ge 1 - \text{margin}$: Oráculo constante. Executa 1 sonda clássica $f(0)$ para definir `1` (se $f(0)=1$) ou `0` (se $f(0)=0$).
   - $p_0 \le \text{margin}$: Oráculo balanceado dependente da entrada $\implies$ `REFUSED` (`BALANCED_ORACLE`).
   - $\text{margin} < p_0 < 1 - \text{margin}$: Zona de indecisão por ruído $\implies$ `REFUSED` (`INSIDE_NOISE_BAND`).
4. **Filtros Pré-Oráculo (0 chamadas de oráculo)**: `ghz_integrity` recusa se fidelidade GHZ < 0.80 (`REFUSED_DEVICE_DECOHERED`); `memory_revival_gate` recusa se detectar ruído não Markoviano (`NOISE_HAS_MEMORY`).

### Integração Qiskit e Encadeamento de Recibos
- **Qiskit**: Presente em `src/qroute/hardware.py` (circuitos Grover, transpilação e submissão via `SamplerV2`, `AerSimulator`, `FakeMarrakesh`); `src/zyql_protocols.py` (P-08/P-10); `src/zyql_selfverified.py` (espelho C†); `src/zyql_witness.py` (TVD e `Statevector`); `src/zyql_auditkit.py`; `src/zyql_oracle_id.py`; `src/zyql_world3.py` e `src/zyql_worldscale.py`.
- **Encadeamento de Recibos**:
   - `src/zyql_runtime.py`: `previous_seal` injetado no payload do recibo e selado em SHA3-256; verificado por `verify_chain()`.
   - `src/zqea_sig.py`: `prev_sha3` assinado pós-quanticamente com ML-DSA-44 via `cadeia()` e `verificar_cadeia()`.
   - `src/qroute/receipt.py`: parâmetro `hash_anterior` propagado nos recibos de rota.
   - `api/server.py`: encadeamento sequencial persistido em arquivo `.chain.json` via `_correntear()`.

## 3. Inconsistências Identificadas (Documentação vs Código)

1. **Quantidade de suítes de teste**: `README.md:166` cita "13 test suites (tests/)". O diretório `tests/` contém 33 arquivos `test_*.py` executando 147 testes.
2. **Status da assinatura ML-DSA-44**: `docs/MATURITY.md:10`, `CITATION.cff:14` e `src/zephirum.h:6` classificam assinatura ML-DSA-44 como "PRODUÇÃO" e padrão do ZYQL. Porém, `src/zyql_runtime.py:107,151` e `api/server.py:108,225` usam apenas SHA3-256. `README.md:42` e `docs/receipts.md:6` admitem ser "DECLARED ROADMAP".
3. **Rate limit por IP declarado vs implementado**: `api/gateway.py:213` (em `/v1/limits`) declara que "gateway nao faz autenticacao de usuario final nem rate limit por IP". Contudo, `api/gateway.py:178` define `quem = chave or (request.client.host if request.client else "anon")`, aplicando rate limit por IP quando não há chave.
4. **Divergência de versionamento**: `pyproject.toml:7` e `README.md:23` indicam `2.5.7`. `VERSION:1`, `api/server.py:42` e `docs/openapi.json:5` trazem `2.5.6`. `src/zyql_runtime.py:1,105` cita `v1.8.0` e `zyql-runtime-2.3.0`, e `docs/MATURITY.md:8` indica `v2.3.2`.
5. **C API declarada sem implementação C**: `src/zephirum.h:1-52` declara uma C API nativa com `ZYQL_REFUSED (-1)`. O repositório não tem arquivos `.c` e a recusa no runtime Python é a string `"REFUSED"` (`src/zyql_runtime.py:26`).
6. **Alvo de teste no Makefile desatualizado**: `Makefile:5-11` executa apenas 6 arquivos no comando `make test`, omitindo 27 das 33 suítes existentes.

## 4. Verificação de Afirmações da Documentação

| Afirmação Documentada | Fonte | Veredito | Evidência / Justificativa |
|---|---|---|---|
| "13 test suites (tests/)" | `README.md:166` | **FALSA** | Execução do pytest e contagem no diretório revelam 33 arquivos `test_*.py` e 147 testes unitários/integrados. |
| "Física declarada: simulação exata... o pedido com hardware=true é recusado explicitamente" | `api/server.py:18-22` | **VERDADEIRA** | Em `api/server.py:200-205`, `req.hardware == True` gera `HTTPException(422)` imediato com mensagem de recusa sem simulação silenciosa. |
| Medições de fidelidade e bateria 3/3 PASS em QPU supercondutora IBM em produção | `README.md:115-116, 125-128` | **NÃO VERIFICÁVEL AQUI** | O ambiente local não tem credenciais ativas da IBM e o envio de jobs a QPUs é proibido pela auditoria. Recibos brutos existem em `experiments/`, mas a execução no chip físico não pode ser re-executada localmente. |

## 5. Divisão de Responsabilidades
- **Agente Coordenador (Usuário)**: Direcionamento estratégico, regras de negócio e prioridades; interlocução externa, aprovação de releases e autorização formal para envio de jobs pagos a QPUs.
- **Engenharia (AI Agent)**: Manutenção, refatoração e implementação em `src/`, `api/` e `tests/`; resolução de inconsistências entre código e documentação; sustentação da suíte de testes e automação de CI.
- **Verificador Independente (Terceiro)**: Auditoria estatística e matemática externa dos limites de erro (Hoeffding/TVD); testes adversariais de penetração na API e validação independente de evidências de hardware.

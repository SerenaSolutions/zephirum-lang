# GEN1_BASELINE — fotografia técnica inicial

**Projeto:** ZEPHIRUM / ZYQL  
**Repositório:** `SerenaSolutions/zephirum-lang`  
**Base inspecionada:** `main` em `880d567f42542c2a8c4114aec013f751940126c3`  
**Branch de trabalho:** `feat/gen1-scientific-kernel-baseline`  
**Status:** baseline documental inicial; não é certificação nem auditoria independente.

## Escopo e método

A leitura direta cobriu `README.md`, `AGENTS.md`, `pyproject.toml`, `Makefile`, `VERSION`, documentação normativa e de maturidade, componentes centrais de execução, adaptadores representativos, testes relacionados e workflow de CI. As referências abaixo permitem reproduzir a inspeção. Esta fotografia não afirma inspeção linha a linha de cada arquivo do repositório, de cada workflow, de cada recibo experimental ou execução local da suíte.

O repositório declara como regra de contribuição em `AGENTS.md`: `python3 -m pytest -q`, respeito a `.github/copilot-instructions.md`, branch isolada e verificação independente. A CI (`.github/workflows/ci.yml`) executa uma matriz Python 3.10–3.12 e testes/conformidade adicionais; `Makefile` define `make test` apontando para `/tmp/zyvenv/bin/python`, caminho específico do ambiente e não garantido em clone limpo.

## Estado encontrado

| Área | Estado observado | Evidência principal | Classe inicial |
|---|---|---|---|
| Semântica trivalente | `Verdict.PERMIT=1`, `DENY=0`, `REFUSED`; testes para oráculos constantes e balanceados | `src/zyql_runtime.py` (`Verdict`, `decide`); `tests/test_runtime.py::test_matrix` | IMPLEMENTED_AND_TESTED (escopo dos testes citados) |
| Gate/interferência | Implementação Deutsch–Jozsa, sonda clássica `f(0)`, banda e recusa explicitadas | `src/zyql_quantum_gate.py::ZYQLQuantumGate`, `_trivalent`, `run_quantum` | IMPLEMENTED_AND_TESTED parcialmente; garantias estatísticas requerem revisão própria |
| Runtime clássico/quântico local | `decide()` usa `ZYQLQuantumGate`, que usa o simulador de vetor de estado local | `src/zyql_runtime.py`; `src/zyql_quantum_gate.py`; `src/zquantum.py::QCircuit` | IMPLEMENTED_AND_TESTED para caminhos cobertos, não é orquestração científica genérica |
| Simulação Qiskit | Adaptador constrói e executa em `AerSimulator`, seed e contagens validadas; explicitamente local | `src/zephirum/adapters/qiskit_backend.py::executar` | IMPLEMENTED; testes de adaptador listados em `tests/test_adaptador_qiskit.py`; execução integral não feita neste baseline |
| Adaptadores externos | Adaptadores separados para Qiskit, qBraid e CUDA-Q, com recusas por SDK/capacidade/falha | `src/zephirum/adapters/{qiskit_backend,qbraid_backend,cudaq_backend}.py` | PARTIALLY_IMPLEMENTED; caminhos não equivalem a validação de hardware real |
| Seleção/orquestração | Q-ROUTE possui pipeline de avaliação clássica, Grover e opção de hardware; `zkernel.Kernel` tem registry simples | `src/qroute/core.py::decide/ executa`; `src/zkernel.py::Kernel` | PARTIALLY_IMPLEMENTED; não foi demonstrado um roteador universal por adequação/custo/precisão |
| Formalização/validação | Contrato de circuito Qiskit valida qubits, portas, argumentos e parâmetros; não há contrato científico geral demonstrado na inspeção | `src/zephirum/adapters/qiskit_backend.py::validar` | PARTIALLY_IMPLEMENTED |
| Linguagem | Interpretador Lisp de programas `.zph`; gramática citada em `docs/grammar/zyql.ebnf` | `src/zyql_lisp.py`; `README.md`; `docs/FACTS.md` | IMPLEMENTED, protótipo/experimental segundo limites documentados |
| Recibos e integridade | Há mais de uma trilha/formato; verificador canônico aceita campos/regras legadas; runtime, qroute e adaptador emitem estruturas próprias | `src/zqea_canon.py`; `src/zyql_runtime.py`; `src/qroute/receipt.py`; `docs/SPEC_Z-QEA_v1.0.md` | IMPLEMENTED, compatibilidade e convergência precisam auditoria |
| Assinatura/autoria | ML-DSA-44 implementada opcionalmente via `pqcrypto`; documentação canônica nega certificação e aplicação universal às publicações | `src/zqea_sig.py`; `docs/FACTS.md`; `docs/MATURITY.md` | IMPLEMENTED_NOT_FULLY_TESTED / BETA, sem certificação FIPS/CAVP/CMVP |
| Prova formal científica | Não demonstrada pela inspeção como provador geral; checks de tipos, contratos, estatística e conformidade não são intercambiáveis com prova matemática | módulos acima; `docs/SPEC_Z-QEA_v1.0.md` (fora de escopo: correção algorítmica/fidelidade experimental) | NOT_IMPLEMENTED como sistema geral |
| Experiência QPU | Documentação relata evidência, mas este baseline não submeteu jobs nem validou recibos experimentais em provedor | `README.md`; adaptadores; `docs/FACTS.md` | UNKNOWN quanto à reprodução independente; NÃO declarar validado por esta tarefa |

## Contradições e limites documentais a reconciliar

1. `README.md` abre chamando o projeto experimental e muito inicial, mas contém seções e alegações de maturidade elevada. `docs/MATURITY.md` marca alguns componentes como *PRODUÇÃO*, enquanto declara outros como *BETA* e *EXPERIMENTAL*. A classificação deve ser componente a componente e ligada a critérios/testes atuais, não inferida do rótulo global.
2. `docs/receipts.md` descreve ML-DSA como roadmap; `docs/FACTS.md`, `docs/MATURITY.md` e `src/zqea_sig.py` dizem que a camada está implementada, mas não aplicada a todos os recibos e sem validação/certificação de módulo. A afirmação compatível é a mais restrita: código disponível no extra, adoção e validação limitadas.
3. Há caminhos de recibo diferentes: `src/zyql_runtime.py` (`payload` + `selo_sha3_256`), `src/zqea_canon.py` (compatibilidade de selos históricos), `src/zqea_sig.py` (especificação assinada), `src/qroute/receipt.py` e adaptador. Não afirmar formato único antes de mapear fixtures e consumidores.
4. `src/zyql_quantum_gate.py` implementa margem familiar adaptativa e `docs/MATURITY.md` registra revisão matemática pendente de `adaptive_margin_family`; não anunciar sua garantia familiar como estabelecida.
5. A especificação Z-QEA delimita explicitamente que integridade, assinatura e cadeia não provam correção matemática, fidelidade do hardware nem veracidade das medições.

## Execução e testes

**Testes executados neste ciclo:** nenhum. As ferramentas disponíveis permitiram leitura e gravação no GitHub, mas não executar shell/Python nem consultar resultados atuais de CI. Portanto, não há resultados de passagem/falha afirmados neste baseline.

Comando documentado pelo repositório para a suíte: `python3 -m pytest -q` (`AGENTS.md`). A CI também roda `python -m pytest tests -q --no-header`, `tools/conformance_zqea.py`, `tools/check_compliance.py` e scripts adicionais (`.github/workflows/ci.yml`). O `Makefile` padrão depende de `/tmp/zyvenv/bin/python`.

## Decisão técnica inicial

**REQUIRES_FOUNDER_DECISION** para qualquer alteração de semântica pública, política estatística, formato de recibo ou alegações de maturidade. **READY_FOR_CONTRACTS** pode ser reconsiderado depois do inventário integral de recibos/APIs e da verificação de CI; nenhum código de runtime foi alterado neste ciclo.

O próximo incremento seguro é completar a matriz de contratos contra as interfaces existentes e adicionar testes de compatibilidade em branch, sem renomear nem substituir APIs legadas.

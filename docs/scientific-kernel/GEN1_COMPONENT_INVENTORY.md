# GEN1_COMPONENT_INVENTORY — inventário inicial baseado em código

**Base:** `main` em `880d567f42542c2a8c4114aec013f751940126c3`.  
**Nota:** inventário arquitetural inicial dos componentes relevantes à Gen 1, não catálogo de todos os arquivos do repositório.

| Responsabilidade desejada | Implementação localizada | Interfaces/símbolos observados | Classificação e lacunas |
|---|---|---|---|
| Interface científica | Lisp `.zph`; API Python de decisão por contagens; CLI `zyql-decide`; Q-ROUTE | `src/zyql_lisp.py::run`; `src/zephirum/__init__.py::decidir`; `src/zyql_runtime.py::main`; `src/qroute/cli.py` | Componentes de entrada existem para casos distintos. Não há contrato único de problema científico identificado. |
| Formalização | Gramática e parser Lisp; validação de circuito e de parâmetros | `docs/grammar/zyql.ebnf`; `src/zyql_lisp.py::tokenize/parse`; `src/zephirum/adapters/qiskit_backend.py::validar`; `src/zyql_runtime.py::_validate` | Validação específica existe; hipóteses, domínio matemático, requisitos de evidência e execução não formam um objeto canônico demonstrado. |
| Decisão/VERITAS | Gate trivalente e verificações de entrada antes do cálculo | `src/zyql_runtime.py::Verdict/Decision/_validate/decide`; `src/zyql_quantum_gate.py::_trivalent`; `src/qroute/core.py::decide` | Há gates locais e domínio-específicos, não um verificador geral de provas. Diferenciar checks de contrato de prova formal. |
| Estratégia/orquestração | Q-ROUTE avalia grafo/classicamente e calcula amplificação de Grover; flags `hardware`/`dry`; `zkernel` mantém backends nomeados | `src/qroute/core.py::decide/ executa`; `src/qroute/graph.py`; `src/qroute/grover.py`; `src/qroute/hardware.py`; `src/zkernel.py::Kernel.backends` | Roteamento é específico para rotas. `Kernel.backends` é registry simples com status; não prova despacho por adequação científica. Revisar fallback e dados declarados. |
| Motor de execução | `QCircuit` local; Qiskit/Aer simulator; adaptadores para qBraid e CUDA-Q | `src/zquantum.py::QCircuit`; `src/zephirum/adapters/qiskit_backend.py::{construir,executar}`; `qbraid_backend.py::executar`; `cudaq_backend.py::executar` | Vários caminhos com diferentes capacidades e dependências. O adaptador Qiskit local usa `AerSimulator`; adaptadores externos não significam hardware executado/testado neste ciclo. |
| Evidência e recibos | canonicalizador/verificador; runtime; Q-ROUTE; assinaturas e cadeia; recibos específicos de linguagens | `src/zqea_canon.py::{canon,verificar}`; `src/zyql_runtime.py::{decide,verify_receipt,verify_chain}`; `src/qroute/receipt.py::{sela,verifica_encadeamento}`; `src/zqea_sig.py::{assinar,verificar,verificar_cadeia,ancorar}` | Implementado por trilhas. Campo de hash, canonicalização, cadeia e assinatura diferem; migração/convergência exige corpus de compatibilidade. |
| Tipos quânticos | Protótipo de tipo `QType`, `CompileError`, mini DSL | `src/quantum_types.py::{QType,QuantumLang,CompileError}` | No-cloning é tratado no protótipo; o cabeçalho declara que a integração com interpretador ainda é trabalho futuro. Não assumir sistema de tipos completo da linguagem. |
| C++ | Núcleo pequeno de veredito, compilado como biblioteca compartilhada | `cpp/Makefile`; `cpp/zyql_verdict.cpp`, `cpp/zyql_verdict.hpp` (existência indicada pelo Makefile; requer leitura complementar) | Implementação presente no repositório, mas equivalência, API e cobertura precisam de verificação direta antes de classificação funcional. CI tem teste de concordância marcado `nativo`. |
| API/serviço | Serviço gerado por Zyclotron; APIs em pastas próprias | `src/zyclotron_service.py::emit_service`; `api/chat.py`; `api/zyql_chat.py`; `docker/README.md` descreve ainda outro core HTTP | Escopos e entrypoints distintos. Não os tratar automaticamente como Scientific Kernel API. API e segurança exigem auditoria específica. |
| Científico por domínio | pacote `zyql_science` com motor, áreas, bateria e recibo | `zyql_science/motor.py`, `areas.py`, `bateria.py`, `RECEIPT_SCIENCE.json` | Conteúdo não foi lido em profundidade neste ciclo; existência confirmada por listagem, capacidades e contratos permanecem UNKNOWN. |
| SDK | Cliente HTTP/SDK de serviço | `zysdk/client.py`, `test_zysdk.py`, recibo | Listagem confirma arquivos; implementação não auditada neste ciclo. UNKNOWN para integração com contratos Gen 1. |

## Contratos publicamente relevantes a preservar

- `zyql_runtime.Decision` e `Verdict` são apresentados como API estável em `src/zyql_runtime.py`; `tests/test_runtime.py` cobre resultados, determinismo, recibo, validação e cadeia.
- `zephirum.decidir(counts, shots, threshold, delta, target_key)` retorna estrutura serializada com `verdict`, `input_commitment` e `receipt_hash` (`src/zephirum/__init__.py`). Não é o mesmo protocolo de `zyql_runtime.decide`.
- O contrato Qiskit usa `{"qubits": ..., "gates": [...]}` e operações/forma normalizada em `src/zephirum/adapters/qiskit_backend.py::validar`.
- `docs/SPEC_Z-QEA_v1.0.md` define canonicalização Z-QEA e formatos, enquanto verificadores legados preservam regras anteriores (`src/zqea_canon.py`).

## Testes localizados (existência, não resultado)

- Runtime/recibo: `tests/test_runtime.py`, `tests/test_receipt_hardening.py`, `tests/test_zqea_verify.py`, `tests/test_zqea_sig.py`.
- Adaptadores: `tests/test_adaptador_qiskit.py`, `tests/test_adaptador_qbraid.py`, `tests/test_adaptador_cudaq.py`, `tests/test_capacidades_qbraid.py`.
- Linguagem/algebra: `tests/test_lisp_regression.py`, `tests/test_zyql_algebra.py`, `tests/test_zyql_ten.py`.
- CI: `.github/workflows/ci.yml`; requisitos e extensões: `pyproject.toml`.

## Trabalho de inventário ainda necessário

Ler e cruzar `src/qroute/{hardware,receipt,graph,grover}.py`, todos os adaptadores e respectivos testes, `zyql_science`, `zysdk`, `cpp/zyql_verdict.*`, `docs/CLAIMS.md`, `docs/AUDIT.md`, contratos da API e exemplos/recibos publicados. Para cada afirmação, capturar símbolo/teste e executar o comando correspondente antes de promover status para `IMPLEMENTED_AND_TESTED`.

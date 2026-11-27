# GEN1_COMPONENT_INVENTORY — Componentes Gen 1 vs código real

Classificação: IMPLEMENTED_AND_TESTED · IMPLEMENTED_NOT_FULLY_TESTED ·
PARTIALLY_IMPLEMENTED · DOCUMENTED_ONLY · NOT_IMPLEMENTED · UNKNOWN

| Componente Gen 1 | Estado | Evidência |
|---|---|---|
| Scientific Interface | PARTIALLY_IMPLEMENTED | `zephirum_lexer.py`, `zephirum.py`, `nexa_core.parse_nexa`; sem API HTTP ainda |
| Formalization Layer | IMPLEMENTED_AND_TESTED | ASK/CONTRACT/MODEL em `nexa_core.py`; contratos em `test_contracts.py` |
| VERITAS Verification Gate | IMPLEMENTED_AND_TESTED | escada do NCA + `_unknown` (§12) + `verify_certificate.py`; `test_trust.py` |
| Hybrid Computational Orchestrator | NOT_IMPLEMENTED (até este commit) | criado agora: `hybrid_orchestrator.py` + `test_hybrid_orchestrator.py` |
| Execution Engine | IMPLEMENTED_AND_TESTED | `zephirum_vm.py` (orçamento), `zephirum_runtime.py`, `zephirum_simulator.py` |
| Z-QEA Evidence Engine | PARTIALLY_IMPLEMENTED | recibos com CERT_HASH/INPUT_HASH (SHA-256); sem assinatura digital; sem recibo E1-E4 tipado |
| Isolamento | IMPLEMENTED_AND_TESTED | `zephirum_isolate.py`, `test_isolate.py` |
| Transpilação multi-alvo | IMPLEMENTED_AND_TESTED | `zephirum_transpiler_multi.py`, `test_transpiler_multi.py` |
| Backend quântico de hardware | NOT_IMPLEMENTED | nunca executado; nenhuma credencial configurada |
| Orquestração CPU/GPU | NOT_IMPLEMENTED | sem adaptador GPU; não confundir com ausência de evidência |

## Regra de leitura

Nenhum item acima é considerado existente sem o ficheiro citado. Documentação
sem código correspondente não conta como implementação.

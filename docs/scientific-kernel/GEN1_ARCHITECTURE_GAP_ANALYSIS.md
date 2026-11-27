# GEN1_ARCHITECTURE_GAP_ANALYSIS — O que falta para o Scientific Kernel Gen 1

## 1. Gaps por componente

| Componente | Gap real | Incremento mínimo |
|---|---|---|
| Scientific Interface | sem serviço HTTP; sem entrada JSON formalizada | `service.py` sobre `qsim_gateway.gateway()` |
| Formalization Layer | sem contrato de problema versionado (problem_id, assumptions, policy) | `execution_contract.py` com esquema declarado |
| VERITAS Gate | distinção epistémica (proved/supported/unknown) existe de facto mas não é tipada | wrapper `ScientificVerdict` sobre TRUE/FALSE/Z, sem alterar a API |
| Hybrid Orchestrator | **inexistente** — decisão de backend dispersa no gateway | `hybrid_orchestrator.py` (este commit) |
| Execution Engine | VM clássica completa; simulador quântico parcial (2 qubits puros) | famílias mistas; registo de backend por execução |
| Z-QEA Evidence | recibo sem classe de evidência (E1-E4); sem assinatura | recibo tipado com `evidence_class`, sem quebrar formato antigo |
| Hardware quântico | inexistente | adaptador só quando houver credenciais e política aprovada |

## 2. Tensão arquitectural identificada nos documentos colados

Os documentos propõem `ACCEPTED / REJECTED / INDETERMINATE` como semântica
canónica. O código real usa `TRUE / FALSE / Z`, com `Z` documentado como
UNKNOWN (§12). A recomendação correcta (a do próprio documento, secção 5) é
**não mudar a API pública agora**: primeiro formalizar a correspondência e
testá-la, depois decidir. Este incremento não altera nenhum veredicto.

## 3. Conflito de maturidade

Os documentos externos classificam o projeto como "produção" enquanto o
README real descreve estado experimental. Resolução: `docs/MATURITY` real não
existe; a classificação vigente é a do README e da conformidade v0.3
(executável, não estável).

## 4. Decisão técnica

READY_FOR_CONTRACTS — o orquestrador híbrido mínimo foi implementado e testado
neste ciclo; os contratos de problema/backend são o próximo incremento.

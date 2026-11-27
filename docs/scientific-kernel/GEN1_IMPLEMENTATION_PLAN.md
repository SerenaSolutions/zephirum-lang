# GEN1_IMPLEMENTATION_PLAN — Plano incremental (evidence before velocity)

Cada fase termina com evidência executável; nenhuma fase declara conclusão
sem teste verde no mesmo commit.

## Fase 0 — Baseline (CONCLUÍDA neste ciclo)
GEN1_BASELINE.md, GEN1_COMPONENT_INVENTORY.md, GEN1_ARCHITECTURE_GAP_ANALYSIS.md,
GEN1_RISK_REGISTER.md. Critério de saída: toda afirmação aponta para ficheiro.

## Fase 1 — Orquestrador híbrido (CONCLUÍDA neste ciclo)
`prototype/hybrid_orchestrator.py` + `prototype/test_hybrid_orchestrator.py`:
- contratos de capacidade por backend (operações declaradas, limites, precisão);
- seleção com política explícita (analytic → classical → simulator);
- fallback apenas se autorizado, sempre registado no recibo;
- hardware nunca substituído silenciosamente por simulação;
- recusa explícita (NOT ROUTED) com motivo.
Critério de saída: bateria PASS integrada na conformidade.

## Fase 2 — Contrato de problema versionado
`execution_contract.py`: problem_id, contract_version, assumptions, policy,
evidence_requirements. Compatibilidade: campos opcionais; nada quebra.
Critério: contrato inválido recusado com motivo; testes adversariais.

## Fase 3 — Recibo tipado Z-QEA
Acrescentar `evidence_class` (E1 integridade, E2 formal, E3 numérico,
E4 experimental) ao recibo existente, preservando campos antigos.
Critério: recibos antigos continuam a verificar; novos distinguem as classes.

## Fase 4 — Serviço HTTP
`service.py` sobre o gateway; entrada JSON = contrato da Fase 2.
Critério: mesma decisão e mesmo hash via CLI e via HTTP.

## Fase 5 — Hardware quântico (bloqueada por decisão do fundador)
Exige credenciais, política de custo e protocolo pré-declarado. Nenhum
adaptador será escrito antes da autorização.

## Fora de escopo (declarado)
Sistema operativo próprio, bootloader, correcção de erros quântica própria,
provas automáticas universais, vantagem quântica.

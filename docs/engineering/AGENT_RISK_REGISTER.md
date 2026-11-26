# Registro de riscos (AGENT_RISK_REGISTER)

| # | Risco | Severidade | Mitigacao | Estado |
|---|---|---|---|---|
| R1 | Agentes declarados "operacionais" sem reconhecimento real | ALTA | secao de verificacao em AGENT_CAPABILITIES.md | MITIGADO |
| R2 | Inflacao de alegacao (marketing > evidencia) | ALTA | CLAIMS.md + gate do book | MITIGADO |
| R3 | Confusao simulacao vs hardware | ALTA | rotulo de maturidade + Evidence | MITIGADO |
| R4 | Conflito de edicao concorrente | MEDIA | fronteiras de arquivo (AGENT_RESPONSIBILITIES) | MITIGADO |
| R5 | Cadeia de suprimentos (dependencias, MCP desconhecido) | MEDIA | security-engineer; nada instalado sem aprovacao | ABERTO |
| R6 | Exposicao de segredos em codigo/historico | ALTA | security-engineer + varredura; tokens fora do repo | MITIGADO |
| R7 | Merge direto contornando protecao | MEDIA | PR obrigatorio; registrar bypass como incidente | ABERTO |

# GEN1_RISK_REGISTER — Riscos técnicos e científicos

Escala: probabilidade (1-3) x impacto (1-3).

| # | Risco | P | I | Mitigação no código |
|---|---|---|---|---|
| R1 | Deriva semântica (TRUE/FALSE/Z tratado como booleano) | 2 | 3 | `Z` nunca coercido; `_unknown` explícito; testes de contrato |
| R2 | Backend declara capacidade que não tem | 2 | 3 | orquestrador só despacha operações declaradas; bateria adversarial |
| R3 | Fallback silencioso de hardware para simulação | 2 | 3 | fallback exige autorização explícita e fica no recibo |
| R4 | Simulação apresentada como hardware real | 1 | 3 | campo `kind` obrigatório; teste dedicado |
| R5 | Hash confundido com prova de verdade | 2 | 2 | documentação: hash = integridade (E1), não validade |
| R6 | Deriva documentação-código (já ocorreu nos documentos colados) | 3 | 2 | baseline com referências de ficheiro; revisão por commit |
| R7 | Replicação independente inexistente | 3 | 3 | verificar C cobre parte; revisão externa pendente |
| R8 | Dependência de mantenedor único | 2 | 3 | documentação executável; instalador testado; arXiv aberto |
| R9 | Alegação de vantagem quântica sem benchmark | 1 | 3 | proibida por política; nenhuma alegação existe hoje |
| R10 | Ambiente Copilot/agentes não verificável deste lado | 3 | 1 | perfis criados mas marcados como não testados |

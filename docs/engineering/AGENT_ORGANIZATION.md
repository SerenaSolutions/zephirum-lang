# Organizacao da equipe (AGENT_ORGANIZATION)

Founder-led: o fundador aprova fundamentos, contratos publicos, releases e merges.

```
FOUNDER / CHIEF ARCHITECT (aprovacao humana)
        |
AGENT 00 chief-architect  (coordenacao)
        |
+-------+-------+--------+--------+---------+---------+--------+
|       |       |        |        |         |         |        |
VERITAS QUANTUM HYBRID  CORE    RED TEAM  EVIDENCE  SECURITY  RESEARCH
  01      02     03      04       05        06        07        08
```

Regras de colaboracao:
- Nenhum agente presume que outro concluiu tarefa sem verificar o artefato.
- Toda tarefa tem escopo e arquivos de responsabilidade (sem edicao concorrente do mesmo arquivo).
- O auditor nao aprova a propria implementacao; Red Team testa de forma independente; Evidence confere antes de selar.
- Chief Architect consolida relatorios e conflitos.
- Sem suporte real a subagentes, executar sequencialmente. Nunca simular paralelismo.

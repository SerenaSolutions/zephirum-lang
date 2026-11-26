# Inventario real de capacidades (AGENT_CAPABILITIES)

Levantado em 2026-11-26 pelo supervisor da casa. Regra: nada declarado sem prova.

## O que ESTE ambiente (sandbox do supervisor) comprova

| Capacidade | Estado | Evidencia |
|---|---|---|
| Leitura/escrita no repositorio via git | TESTADO | clonagem e commits desta sessao |
| API GitHub (issues, discussions, PRs, actions) | TESTADO | issues #146-#151, comentario na Discussion #141 |
| Execucao de testes Python/CI local | TESTADO | pytest/baterias executadas |
| Sub-agentes de pesquisa em paralelo | TESTADO | missoes de varredura (7+4 frentes) |
| MCP configurados | NAO EXISTE | `.agents/mcps/config.json` = `{"mcpServers": {}}` |
| Reconhecimento de `.github/agents/` pelo Copilot | NAO VERIFICAVEL DAQUI | exige ambiente GitHub Copilot Agent; acao do fundador |

## O que NAO pode ser declarado
- Que os agentes estao "operacionais": os perfis existem como arquivos; o reconhecimento depende do ambiente Copilot (Agent/CLI/Cloud) e deve ser comprovado por ele.
- Que conectores Atlassian/Slack/Notion/Vercel estao conectados: nenhum esta configurado neste ambiente.
- Que existe execucao paralela real entre agentes do repositorio: delegacao paralela comprovada apenas entre sub-agentes do supervisor.

## Verificacao pendente (acao do fundador)
1. Abrir o Copilot em modo Agent no repositorio e listar os agentes reconhecidos.
2. Registrar a saida em `docs/engineering/AGENT_CAPABILITIES.md` (secao "verificado no Copilot").
3. Somente apos isso declarar a equipe OPERACIONAL.

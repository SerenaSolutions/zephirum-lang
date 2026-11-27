# AGENT_CAPABILITIES — inventário honesto

Data: 2026-11-27. Princípio: não declarar disponível o que não foi comprovado.

## O que foi criado neste ciclo

- `.github/agents/` — 9 perfis de agente (chief-architect, veritas, quantum,
  hybrid, language-runtime, red-team, evidence, security, documentation).
- `.github/copilot-instructions.md` — regras invariáveis do repositório.

## O que NÃO foi possível verificar daqui

- Se o GitHub Copilot reconhece os perfis: sem acesso ao ambiente Copilot
  deste lado, nenhuma delegação real foi testada.
- Servidores MCP configurados: desconhecido; não foram instalados.
- Integrações Atlassian/Slack/Notion/Vercel: não conectadas neste repositório.

## Correções ao plano externo (documentos de 27/11)

O plano colado descrevia outro projecto: `zephirum-lang`, linguagem ZYQL,
Lisp `.zph`, `docs/FACTS.md`, SHA3-256, ML-DSA-44, valores 1/0/REFUSED.
Nada disso existe aqui. O baseline real está em
`docs/scientific-kernel/GEN1_BASELINE.md` com referências de ficheiro.

## Regra de operação

Perfil criado ≠ agente operacional. Operacional exige: reconhecimento pelo
ambiente + uma delegação real executada + resultado verificado.

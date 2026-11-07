# Auditoria do GitHub — 07/11/2026

Escopo: 36 repositórios da conta `SerenaSolutions`, dos quais 30 próprios e 6 forks.
Método: API do GitHub, com medição por repositório. Forks de terceiros aparecem na
contagem mas não entram nas recomendações, porque a postura deles não é nossa.

**Limite declarado:** auditoria de configuração, feita com token de leitura. Os alertas
de secret scanning da conta exigem permissão de administrador e não puderam ser lidos.

## Achado crítico

### C1 — CRÍTICO — credencial de QPU em repositório público

`SerenaSolutions/AigroQuantumFintech` é **público** e versiona um arquivo `.env` com uma
variável `CHAVE_DE_NUVEM` de 46 caracteres, sem placeholder. Não é a mesma chave que
usamos hoje, mas é uma credencial de nuvem real, exposta desde que o arquivo entrou no
repositório.

Agravante: apagar o arquivo **não resolve**. Ele continua no histórico do Git, acessível
por qualquer clone. Remediação, nesta ordem:

1. Revogar a chave na o provedor de nuvem hoje. Rotação é a única ação que fecha o risco.
2. Remover o `.env` da árvore e adicionar `.env` ao `.gitignore`.
3. Purificar o histórico (`git filter-repo` ou BFG) e forçar push, ciente de que reescreve
   o histórico do repositório.
4. Se a chave foi usada em qualquer cobrança, revisar o consumo da conta.

## Achados por severidade

| ID | Severidade | Quantos | O que é |
|---|---|---|---|
| C1 | Crítico | 1 | chave de QPU em repositório público |
| G1 | Alta | 4 | checks obrigatórios configurados, mas pushes passam por bypass de administrador |
| G3 | Alta | 32 | branch principal sem proteção: qualquer push entra sem review e sem CI |
| G6 | Alta | 12 | sem licença detectada pelo GitHub |
| G5 | Média | 21 | sem workflow de CI |
| G2 | Média | 4 | branch protection sem `strict`: PR entra desatualizado |
| G8 | Baixa | 28 | sem topics: invisível em busca por assunto |

### G1 — o gate existe no papel

Quatro repositórios têm checks obrigatórios declarados: `zephirum-lang` (4 checks),
`zqea-verify` (2), `zqea-guardian` (1) e `zq-gate` (1). Em todos, os pushes recentes
passaram com a mensagem de violação contornada. Tradução: a proteção está configurada,
mas o token usado no push tem poder de administrador e atravessa. Esteira que nunca
reprova não é esteira, é enfeite.

Correção: usar identidade de máquina sem bypass, ou exigir PR para `main` e deixar o push
direto apenas para automação com escopo declarado.

### G3 — 32 repositórios sem proteção

Inclui os que importam: `zephirum-lang`, `serena-quantum-safe-readiness`, `qsr-crypto-gate`,
`zyql-quantum-vulnerability` e `zyql-audit-ui`. Um push errado em `main` derruba release.
Correção: exigir PR, checks obrigatórios e review próprio em cada um dos cinco.

### G6 — 12 sem licença

Entre eles `zyql-audit-ui`, que é interface pública consumindo a API. Sem licença, o
direito de uso é ambíguo, e isso pesa em conversa comercial. Correção: Apache-2.0 nos
repositórios de produto.

## Segmentação que muda a leitura

Dos 102 achados brutos, boa parte é ruído estrutural: 28 são ausência de topics em
repositórios de experimento, e 21 são ausência de CI em repositórios de uma tarde. O
número que importa não é 102, é **7**: um crítico, quatro altos nos repositórios de
produto e dois médios de esteira.

## O que fazer, em ordem

1. Revogar a chave exposta (C1). Nada mais importa antes disso.
2. Proteger `main` nos cinco repositórios de produto com PR obrigatório e checks (G1, G3).
3. Parar de usar token com bypass nos pushes de automação (G1).
4. Licença Apache-2.0 no `zyql-audit-ui` (G6).
5. CI mínimo nos cinco, rodando a suíte existente (G5).
6. Topics nos cinco de produto, que é o que faz busca por assunto encontrar (G8).

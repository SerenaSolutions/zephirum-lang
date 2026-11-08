# Recursos avançados do GitHub — o que entrou e o que depende do painel

**Data:** 08/11/2026 · **Regra respeitada:** nada que interfira na submissão do
Qiskit/ecosystem em revisão (PR #1433, mantenedor Luciano Bello).

## Entrou nesta rodada (arquivo novo, nada publicado)

| Recurso | Arquivo | Proteção contra ruído na submissão |
|---|---|---|
| Publicação no PyPI por Trusted Publishing (OIDC) | `publicar-pypi.yml` | **manual**, exige digitar `PUBLICAR`, ambiente `pypi-release` com aprovação, e recusa se a versão já existir |
| Dependency Review em PR | `dependency-review.yml` | só no nosso repositório |
| OpenSSF Scorecard (semanal) | `scorecard.yml` | só no nosso repositório |
| Release Drafter | `release-drafter.yml` + `.github/release-drafter.yml` | só no nosso repositório |
| Cache de pip e concurrency na CI | `ci.yml` | economia de minutos, sem mudança de comportamento |

## Por que a publicação é manual

O repositório Qiskit/ecosystem tem o workflow "Daily | Update member data", que relê os
dados da entrada de membro. Publicar versão nova pode fazê-lo atualizar a submissão
em revisão e gerar movimento onde não deve haver. A versão da entrada é 2.5.6 e o
pacote está em 2.5.7: qualquer publicação mexe nesse número. Por isso o gatilho é
`workflow_dispatch`, não tag.

## Depende do painel do GitHub (não é arquivo)

1. Settings → Code security → **secret scanning** e **push protection** ligados.
2. Rulesets → exigir **commits assinados** em `main`.
3. Environments → criar `pypi-release` com **required reviewers**.
4. PyPI → registrar o Trusted Publisher apontando para este repositório e o ambiente
   `pypi-release` (sem isso a publicação falha por OIDC).

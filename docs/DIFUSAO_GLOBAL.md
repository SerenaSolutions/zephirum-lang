# Protocolo de difusão global — ZYQL / ZEPHIRUM

Iniciado 03/11/2026 a pedido do dono. Regra que governa tudo: **canal onde só se vê o link
não é difusão; difusão é onde alguém pode reproduzir o resultado em 5 minutos.**

## Fase 0 — Sinais de maturidade (feito hoje, v2.5.1)

Revisor técnico decide em 30 segundos se um projeto é brinquedo ou ferramenta. Estes são os
marcadores que ele procura e que faltavam:

| marcador | antes | agora |
|---|---|---|
| `py.typed` (consumidor sabe que há tipos) | ausente | presente |
| `.pre-commit-config.yaml` (lint antes do commit) | ausente | presente |
| CI de cobertura com piso (não regride) | ausente | `.github/workflows/coverage.yml` |
| `docs/DEPRECATION.md` (semver e prazo de aviso) | ausente | presente |
| `GOVERNANCE.md` (como uma mudança entra) | ausente | presente |
| recipe conda-forge | ausente | `packaging/conda/meta.yaml` (pronto) |

## Fase 1 — 7 dias (execução nossa, sem depender de terceiro)

1. **Trusted Publishing no PyPI (OIDC)**: publicar sem token, por GitHub Actions. Elimina de vez
   a dor do `PYPI_TOKEN` e o risco de chave no chat.
2. **VSIX no CI**: build da extensão VS Code e anexo no release. Hoje existe só o scaffold.
3. **Tabela de benchmark contra Qiskit, Cirq e PennyLane**: latência de decisão e de verificação,
   com a metodologia declarada. Sem isso, "rápido" é adjetivo; com isso, é número.
4. **docs/index.html com busca**: a landing responde 200, mas não tem busca nem versão.

## Fase 2 — 30 dias (ecossistema)

1. **conda-forge**: abrir PR em `conda-forge/staged-recipes` com a recipe pronta. Qiskit e
   PennyLane estão lá; sem isso, o usuário científico não instala.
2. **arXiv**: preprint do núcleo trivalente (draft em `docs/preprint/`). DOI já existe via Zenodo.
3. **Notebooks Colab indexados** no README: do zero ao veredito sem instalar nada.
4. **Traduções** do README (PT/EN já; ES e ZH depois) — metade do público de quântica não lê inglês.

## Fase 3 — 90 dias (institucional)

1. **QUANTICS 2027**: submissão de paper até **25/03/2027**. Workflow de lembrete já ativo.
2. **Qiskit Ecosystem**: PR #1433, aguardando o mantenedor. Credencial de ecossistema alimenta
   editais (FAPESP PIPE) e procurement.
3. **Qiskit Fall Fest Brasil**: hospedar edição local (janela de pedido ~06/2027).
4. **Marketplace**: releases publicadas; falta o clique de Publish (dono).

## Canais e o que cada um exige (estado real, sem otimismo)

| canal | estado | bloqueio |
|---|---|---|
| PyPI | ✅ publicando (2.4.0) | trusted publishing ainda manual |
| GitHub topics/descrição | ✅ otimizado (17 topics) | — |
| conda-forge | 📝 recipe pronta | PR em staged-recipes |
| arXiv | 📝 draft pronto | conta arXiv (dono) |
| VS Code Marketplace | 📝 scaffold | token VSCE (dono) |
| LinkedIn | ❌ restrito | verificação Persona (dono) |
| X / Twitter | ⏸ OAuth pedido | clique de autorização (dono) |
| Hacker News / Reddit | ❌ | conta própria exigida |
| Slack/Discord de comunidades | ❌ | cadastro por e-mail |

## Critério de sucesso, declarado

Não é número de estrelas. É: **alguém que nunca falou conosco reproduz um veredito com recibo
verificável, sem pedir ajuda.** Quando isso acontecer três vezes em canais diferentes, a difusão
funcionou.

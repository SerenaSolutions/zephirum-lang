# Avaliação das 30 ferramentas sugeridas para o CI do ZEPHIRUM

Verificação feita na fonte em 09/11/2026, pela API do GitHub: existência do
repositório, arquivamento e data do último push. Veredito por ferramenta:
**Adotado** (entrou em workflow), **Já existe** (o repositório já faz),
**Adiar** (útil mas sem base agora), **Descartar** (não serve ao caso),
**Não existe** (a URL indicada não corresponde a repositório real).

| # | Ferramenta | Tipo | Veredito | Motivo |
|---|---|---|---|---|
| 1 | Snyk | App | Adiar | Exige token e duplica CodeQL + dependency-review. Só se houver apetite a fix automático de PR. |
| 2 | Whitesource Bolt | App | Descartar | Produto descontinuado, absorvido pela Mend.io. |
| 3 | Anchore scan-action | Action | Adiar | Só faz sentido com imagem Docker publicada. O projeto não publica imagem. |
| 4 | StackHawk | App | Adiar | DAST pago. A API FastAPI não está publicada em ambiente de teste. |
| 5 | OSS Review Toolkit | Action | Não existe | `oss-review-toolkit/ort-action` retorna 404. O ORT existe como CLI, não como action. |
| 6 | Trivy | Action | **Adotado** | `security-scan.yml`, semanal, não bloqueante: vulnerabilidade, segredo e má configuração. |
| 7 | py-actions/flake8 | Action | Descartar | Último push em 19/08/2024. Ruff faz o mesmo, mais rápido e mantido. |
| 8 | black-formatter-action | Action | Não existe | `cpcloud/black-formatter-action` retorna 404. |
| 9 | isort-action | Action | Não existe | `JamesIves/isort-action` retorna 404. |
| 10 | mypy-check | Action | **Adotado** | `quality.yml`, informativo. Código sem tipagem gera centenas de avisos; bloquear seria teatro. |
| 11 | Safety CI | Action | Não existe | `pyupio/safety-ci` retorna 404. |
| 12 | mkdocs-deploy-gh-pages | Action | Descartar | Último push em 19/07/2024, e o Pages já publica `site/`. |
| 13 | doctest-action | Action | Não existe | `peter-evans/doctest-action` retorna 404. |
| 14 | Read the Docs | App | Adiar | Segunda plataforma de docs. Pages já resolve. |
| 15 | PyPI Publish Action | Action | Já existe | `publicar-pypi.yml`, com OIDC e aprovação. |
| 16 | All Contributors | App | Adiar | Só faz sentido com comunidade externa ativa. |
| 17 | Stale | App | Adiar | Volume de issues ainda baixo. |
| 18 | Semantic Pull Requests | App | Adiar | Útil, mas exige disciplina de título que só vale com mais colaboradores. |
| 19 | WIP | App | Descartar | Draft PR do próprio GitHub já cumpre o papel. |
| 20 | CLA Assistant | App | Adiar | Depende de decisão jurídica sua, não técnica. |
| 21 | qutip-action | Action | Não existe | `qutip/qutip-action` retorna 404. |
| 22 | ibmq-runner | Action | Não existe | `qiskit-community/ibmq-runner` retorna 404. E QPU não se submete por CI: exige selo prévio. |
| 23 | pytest-benchmark | Action | Adiar | Sem linha de base estável, o número não significa nada. |
| 24 | actions/labeler | Action | **Adotado** | `labeler.yml` + `.github/labeler.yml`, rotula PR por caminho. |
| 25 | Auto Assign | App | Adiar | Time pequeno; atribuição manual custa menos. |
| 26 | setup-micromamba | Action | Descartar | O projeto instala por pip a partir do pyproject. Conda introduziria segundo resolvedor. |
| 27 | actions/cache | Action | Adiar | Ganho marginal; o gargalo real da CI é instalar qiskit, não cachear. |
| 28 | Release Drafter | App | Já existe | `release-drafter.yml` ativo. |
| 29 | danger-python | Action | Não existe | `danger/danger-python` retorna 404. |
| 30 | OWASP ZAP | Action | **Adotado** | `security-scan.yml`, baseline no site público, sem abrir issue e sem falhar o build. |

## O que isso muda

Antes: nenhuma checagem de lint ou de tipos em todo o repositório.
Agora: `quality.yml` bloqueia apenas erro real (sintaxe, nome indefinido,
import quebrado) e reporta o resto sem travar merge. `security-scan.yml`
roda semanal, fora do caminho de PR. `labeler.yml` organiza o histórico.

## O que foi recusado de propósito

Nada de segunda plataforma de teste dinâmico apontando para produção sem
ambiente de staging, nada de duplicar CodeQL, SBOM ou revisão de dependências,
e nada de automação que submeta job a QPU. Submissão quântica continua ato
manual e selado, conforme o gate spec, teste local, QPU.

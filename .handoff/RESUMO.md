# Handoff — Semana 1 gerada em sandbox (NÃO publicada)

**Data:** 07/11/2026 · **Origem:** agente coordenador · **Estado:** commit local, remoto intocado

## O que foi corrigido
| # | Inconsistência auditada | Correção | Prova |
|---|---|---|---|
| 1 | `docs/openapi.json` em 2.5.6 contra `pyproject` 2.5.7 | alinhado em 2.5.7 | `info.version` = 2.5.7 |
| 2 | README dizia 13 suítes; existem 33 | corrigido para 33 | contagem em `tests/test_*.py` |
| 3 | gateway negava rate limit por IP que ele aplica | texto do `/v1/limits` corrigido | `api/gateway.py` |
| 4 | `make test` rodava 6 de 33 arquivos | agora roda `pytest tests/` inteiro | 147 aprovados |

## O que NÃO foi feito, de propósito
- Nada foi enviado ao GitHub. `git status -sb` mostra `ahead 1`, remoto intacto.
- Nada foi publicado no PyPI.
- PR #54 não foi tocado.
- Job de QPU `dbnqhi8ou4as73b4vu00` segue na fila, cota de 460 s intacta.

## Como aplicar quando o responsável autorizar
```
git apply .handoff/0001-semana-1-em-sandbox-verdade-do-repositorio-NAO-publi.patch
# ou
git fetch .handoff/semana1-sandbox.bundle main:semana1
```

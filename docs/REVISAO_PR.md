# Operacao de PR: regras que nasceram de erros reais

Este documento existe porque eu errei, e os erros estao listados com data.
Cada regra abaixo responde a um erro concreto, nao a uma boa pratica abstrata.

## Erros cometidos (registro honesto)

| Data | Erro | Consequencia |
|---|---|---|
| 30/10 | Afirmei que o e-mail de resposta nao havia chegado ao PR | Estava errado: o comentario existia como resposta no thread de revisao (03:05). So consultei os comentarios gerais, nao os de revisao. |
| 30/10 | Publiquei comentario pelo token e o e-mail chegou depois | Texto duplicado no PR #1433, em dois lugares. Ruido para o mantenedor. |
| 30/10 | Tratei `submission_number = 1432` como inconsistencia | Era correto: issue de submissao #1432, PR resultante #1433. Quase reportei erro inexistente. |
| 30/10 | Repeti um diagnostico de auditoria externa sem ler o codigo | O auditor disse que o TVD nao era calculado em hardware; o codigo calcula nas duas rotas. Registrado como refutado em `AUDITORIA_REPO.md`. |

## Regras

1. **Dois endpoints, nao um.** Antes de dizer que algo nao chegou ou nao foi respondido,
   consultar `issues/{n}/comments` **e** `pulls/{n}/comments`. O segundo nao aparece no primeiro.
2. **Uma mensagem por assunto.** Se uma resposta ja foi postada, nao postar de novo por outro
   canal. Se o outro canal entregar depois, assumir a duplicata em vez de criar uma terceira.
3. **Numero so entra em relatorio depois de conferido por chamada real.** Ver
   `tools/verificar_publicacao.py`. Versao, DOI, contagem de assercao, job id: todos vem de
   leitura, nunca de memoria.
4. **Auditor externo nao e fonte primaria.** Toda afirmacao de auditor sobre o codigo e
   verificada no arquivo e na linha, e a refutacao e registrada com referencia.
5. **Antes de responder no PR, ler os checks.** `mergeable`, estado dos workflows e o ultimo
   commit do head. Resposta em cima de build vermelho e ruido.
6. **Formatacao e do dono do repositorio.** No `qiskit/ecosystem`, o toml de membro e gerado e
   formatado por eles; nosso papel e garantir que os DADOS estejam certos (versao, licenca,
   dependencia declarada, label) e nao reescrever o arquivo deles.

## Verificacao automatica

```bash
python tools/verificar_publicacao.py          # pyproject x PyPI x DOI x recibos x links
python tools/verificar_publicacao.py --offline  # so checagens locais
```

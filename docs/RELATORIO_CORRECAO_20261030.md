# Relatório de correção: publicação de 30/10/2026

Auditoria do que foi publicado no PyPI, GitHub e LinkedIn nesta data, com o que
foi corrigido, como foi verificado e o que permanece aberto.

## 1. PyPI: corrigido e verificado

Defeitos no 2.1.1, encontrados por instalação limpa em venv:

| # | Defeito | Evidência |
|---|---|---|
| 1 | `import zephirum` falhava | `ModuleNotFoundError` após `pip install zephirum==2.1.1` |
| 2 | Nenhum pacote `zephirum/` no wheel | `top_level.txt` com 25 nomes de topo, nenhum `zephirum` |
| 3 | Metadados vazios | `author`, `home_page`, `project_urls`, `license`, `keywords`, `classifiers` nulos |
| 4 | Licença não chegava ao índice | `pyproject` declarava MIT; build com setuptools antigo descartava |
| 5 | Contato pessoal exposto | `author_email` era um gmail particular |

Publicado 2.1.2. Verificação: `pip install zephirum==2.1.2` em venv limpa devolve
`__version__ == 2.1.2`, `License-Expression: MIT`, 6 project URLs e
`zephirum.zqgate is zqgate == True`.

## 2. Números das publicações: conferidos contra a fonte

| Alegação | Valor publicado | Fonte no repositório | Situação |
|---|---|---|---|
| W-02 visibilidade | 0,952 ± 0,001 | recibos e AUDITORIA_ULTRA | correto |
| W-01 TVD | 0,253 | AUDITORIA_ULTRA: 0,253 ± 0,048, IC [0,244; 0,263] | correto, faltava a incerteza |
| W-03 p(marcado) | 0,773 | AUDITORIA_ULTRA: 0,773 ± 0,011, IC [0,764; 0,782] | correto, faltava a incerteza |
| Taxa de certificação indevida | 12% | POWER_ANALYSIS: 0,1205 na banda | correto |

Nenhum valor foi inventado. A omissão é a incerteza, não o número.

## 3. Varredura adversarial (Nemotron 3 Ultra 550B)

Doze apontamentos. Nove refutados com evidência:

- "LICENSE ausente no artefato": falso. `dist-info/licenses/LICENSE` presente.
- "`zqgate` não encontrado no layout src": falso. O wheel contém `zqgate/`.
- "py-modules incompatível com src layout": falso. 24 módulos presentes no wheel.
- "shim cria wrapper e colide com o pacote real": falso. `zephirum.zqgate is zqgate`
  é verdadeiro; `sys.modules` registra `zqgate`, não um wrapper.
- "pickle do shim quebra": irrelevante. Módulos Python não são pickláveis por definição.

Três válidos, e nenhum introduzido pela correção:

- **Nomes de topo**: 25 pacotes de nível superior violam boas práticas e podem
  colidir. Exige mover para `zephirum.*`, o que é breaking change e versão maior.
- **Dupla fonte de versão**: `pyproject` e `importlib.metadata`. Prática comum; o
  risco é divergência silenciosa.
- **Classifiers de Qiskit**: ainda ausentes. Depende da decisão sobre ecossistema.

## 4. Pendências abertas

- LinkedIn: as três publicações mencionam revisão no Qiskit Ecosystem (a remover) e
  omitem a incerteza de W-01 e W-03. Bloqueado por créditos de integração esgotados.
- Carrossel revisado (`carrossel-zyql-v2.pdf`, 8 páginas, slide 8 sem menção a
  terceiros) pronto, aguardando o mesmo desbloqueio.
- Estrutura de pacote: migração para `zephirum.*` como versão maior, em PR próprio.

## 5. Escopo do que NÃO foi tocado

Resultados científicos, recibos, selos e alegacões do WORLD-3 permanecem exatamente
como estavam. Esta correção é de empacotamento e de metadados.

# MISSÃO — Álgebra de decisões trivalentes (ZYQL v2)

**Destinatário:** Antigravity CLI (executor de engenharia supervisionado)
**Supervisão:** Superagent · **Aprovação final:** responsável humano
**Data:** 08/11/2026 · **Repo:** `/tmp/zl` (SerenaSolutions/zephirum-lang)

## Objetivo

Fechar o intervalo entre decidir uma vez e decidir em sequência. Hoje cada decisão
carrega seu erro e ninguém soma o erro do conjunto; `k` da margem familiar é um
número digitado à mão. O objetivo é fazer `k` ser **contado do próprio programa** e
o erro familiar ser **propagado pela composição**.

## O que construir

Novo módulo `src/zyql_algebra.py`, sem tocar em semântica existente.

### 1. Tipo `Decisao`

Campos: `veredito` (1 | 0 | "REFUSED"), `epsilon` (erro tolerado daquela decisão),
`shots`, `refusal_reason` (quando recusada), `recibo_selo` (opcional).

Invariantes obrigatórias:
- `epsilon` em (0, 1); `shots` inteiro ≥ 1.
- `veredito == "REFUSED"` exige `refusal_reason` não vazio.
- Construir objeto inválido levanta `ValueError`.

### 2. Operadores

- `conjuncao(a, b)` — só é 1 se ambas forem 1. Se qualquer for 0, resultado 0.
  Se qualquer for REFUSED e nenhuma for 0, resultado REFUSED propagando o motivo.
- `disjuncao(a, b)` — dual da conjunção.
- `negacao(a)` — 1↔0; REFUSED permanece REFUSED com o mesmo motivo.
- `sequencia(*decisoes)` — todas devem ser 1 para o programa seguir; qualquer 0
  encerra com 0; qualquer REFUSED encerra com REFUSED.

### 3. Contagem e orçamento de erro (o núcleo da inovação)

- Cada operação conta quantos testes independentes consumiu. `n_testes(expr)`
  devolve esse número.
- O erro familiar do programa é `min(epsilon_familia(n_testes), min(epsilons))`,
  onde `epsilon_familia(k) = 1 - (1 - eps)^k` calculado com `eps` individual.
- A margem de decisão de cada folha deve poder ser recalculada com
  `adaptive_margin_family(eps, shots, family=n_testes(...), modo="rigorous")`.
- Se `n_testes` exceder o que `shots` sustenta (margem resultante ≤ 0), o resultado
  **é REFUSED** com motivo `FAMILY_EXCEEDS_SHOTS`. Nunca aprovar por falta de poder.

### 4. Recibo

`recibo_da_expressao(expr)` devolve dicionário com: `n_testes`, `epsilon_familia`,
`veredito`, `refusal_reason` (se houver), `forma` (árvore serializável) e
`selo_sha3_256` calculado com `zqea_sig.sha3_256` sobre a forma canônica.
O recibo deve ser verificável: mesma expressão → mesmo selo.

## Restrições duras

1. **Não alterar** `src/zyql_quantum_gate.py`, `src/zqea_sig.py` nem assinaturas
   existentes. Só adicionar o módulo novo e seus testes.
2. **Não mudar padrão de margem** (continua `conservative`).
3. Todo código novo leva cabeçalho SPDX Apache-2.0.
4. Escrever `tests/test_zyql_algebra.py` com: verdade das operações (tabela
   completa dos 9 pares), propagação de REFUSED, contagem de testes, selo
   determinístico, e recusa por `FAMILY_EXCEEDS_SHOTS`.
5. `PYTHONPATH=src:api:experiments python -m pytest tests -q` deve passar inteiro.
6. Não fazer commit. Deixar a árvore pronta para auditoria.

## Critério de aceite

Suíte inteira verde, módulo novo coberto, nenhum arquivo existente modificado
(conferível por `git status`), e demonstração em uma linha mostrando que uma
sequência de 7 decisões tem `n_testes == 7` e erro familiar declarado.

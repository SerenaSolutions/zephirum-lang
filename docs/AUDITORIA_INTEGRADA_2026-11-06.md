# Auditoria integrada — 06/11/2026

Escopo: segurança comercial, integridade dos recibos e interoperabilidade com o
Qiskit Ecosystem. Método: medição no código e nos serviços, não inspeção visual.
Cada achado traz a evidência que o sustenta e o comando que a reproduz.

**Limite declarado:** auditoria interna, feita pelo autor. Não substitui pentest
independente nem parecer de terceiro, e nenhum achado aqui deve ser lido como
atestado de conformidade.

## Veredito por eixo

| Eixo | Estado | Base |
|---|---|---|
| Segurança comercial | PARCIAL | 141 testes; HMAC e replay ok; falta limitação de taxa e CORS |
| Integridade dos recibos | PARCIAL | selo SHA3 em 11 módulos; encadeamento não é universal |
| Interoperabilidade Qiskit | PRONTO PARA REVISÃO | PR aberto e mergeável, cap declarado, versões alinhadas |

## Achados

### A1 — ALTA — ausência de limitação de taxa
`/v1/core/decide`, `/v1/qsr/assess` e `/v1/billing/verificar` aceitam requisições sem
limite. Evidência: `grep -ciE 'ratelimit|rate_limit|slowapi|limiter' api/*.py` → 0 em
todos os módulos. Risco: consumo de CPU por chamada e esgotamento de cota alheia.
Remediação: limite por chave e por IP, 429 com cabeçalho de retentativa.

### A2 — ALTA — CORS não configurado
Evidência: `grep -c CORSMiddleware api/*.py` → 0. Um front-end de outro domínio não
consegue consumir a API, e a correção apressada costuma ser `*`, que expõe a chave.
Remediação: lista explícita de origens, métodos e cabeçalhos permitidos.

### A3 — MÉDIA — encadeamento de recibos não é universal
O selo SHA3 existe em 11 módulos, mas `grep -rlE '"prev"|prev=' src/*.py` devolve 0:
o encadeamento está no Q-ROUTE e não nas rotas da API.
Consequência: prova-se que um recibo não foi alterado; não se prova que nenhum recibo
foi apagado ou reordenado.
Remediação: incluir `prev` em todo recibo emitido pela API.

### A4 — MÉDIA — modo degradado do webhook
Sem `STRIPE_WEBHOOK_SECRET`, o webhook aceita segredo compartilhado no corpo; sem
nenhum dos dois, recusa com 503, que é o comportamento correto. O modo intermediário é
aceitável em desenvolvimento e inadequado em produção.
Remediação: exigir assinatura quando `ZYQL_ENV=producao`.

### A5 — BAIXA — credencial mestra única
Uma chave mestra de ambiente, sem rotação automática. As chaves nomeadas já são
hasheadas e revogáveis.
Remediação: rotação trimestral documentada.

### A6 — BAIXA — ausência de autenticação de usuário final
Declarada em `/v1/limits`. Não é defeito se a API não for exposta diretamente ao
público.

## O que está provado

- Assinatura HMAC-SHA256 validada, com rejeição de HMAC errado, de corpo adulterado e de
  timestamp fora da tolerância de 300 s.
- Webhook idempotente: recebimento repetido não emite segunda chave.
- Chaves de compra guardadas como hash e comparação em tempo constante.
- Adulteração de um único campo muda o selo, verificado por cálculo direto.
- Teto `qiskit>=2.6,<3` declarado; repositório e PyPI em 2.5.6.

## O que NÃO está provado

- Ausência de vulnerabilidade. Nenhuma ferramenta de análise foi aplicada por terceiro.
- Resistência a ataque de rede real, sob carga ou com adversário ativo.
- Correção formal do protocolo de selagem sob modelo de ameaça definido.

## Próximas três ações, em ordem

1. Limitação de taxa e CORS restrito (A1, A2) — bloqueiam exposição pública.
2. `prev` em todo recibo da API (A3) — sustenta a alegação de trilha auditável.
3. Exigir assinatura em produção (A4) — fecha o modo degradado.

Depois disso, contratar auditoria externa com escopo escrito. Sem esse passo, o material
serve para parceiro técnico, não para instituição que exige parecer independente.

## Remediação aplicada (mesma data)

| Achado | Estado | Evidência |
|---|---|---|
| A1 rate limit | CORRIGIDO | janela deslizante de 60 s por chave em `api/gateway.py`, `ZYQL_RATE_LIMIT` (padrão 120/min), resposta 429 com `Retry-After` |
| A2 CORS | CORRIGIDO | `ZYQL_CORS_ORIGINS` restrito, sem curinga, métodos e cabeçalhos declarados |
| A3 encadeamento | CORRIGIDO | `prev` e `elo` em todo recibo da API via `_correntear`, estado em `ZYQL_CHAIN_FILE` |
| A4 webhook degradado | CORRIGIDO | com `ZYQL_ENV=production`, ausência de `STRIPE_WEBHOOK_SECRET` responde 503 |

Testes: `tests/test_auditoria.py` cobre elo seguinte apontando para o selo anterior, 429 na
terceira chamada com limite 2, e 503 em produção sem assinatura.

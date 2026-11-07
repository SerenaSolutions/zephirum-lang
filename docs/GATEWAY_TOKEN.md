# Um token para todo o ecossistema

O gateway expõe linguagem, algoritmos, oráculos e prontidão pós-quântica atrás de uma
única chave, no header `X-API-Key`.

## Fronts e escopos

| Front | Escopo | Rotas |
|---|---|---|
| read | `read` | `/v1/catalog`, `/v1/limits` |
| core | `decide` | `/v1/core/decide`, `/v1/core/bound`, `/v1/core/verify`, `/v1/core/oracle/*` |
| qsr | `qsr` | `/v1/qsr/assess` |
| lang | `lang` | `/v1/lang/run` |

`/health` é aberto para sondagem de disponibilidade. Todo o resto exige chave.

## Emitir, revogar, rodar

```bash
python -m api.gateway issue --name producao --scopes read,decide,qsr,lang
python -m api.gateway revoke <chave>
ZYQL_API_TOKEN=<chave> uvicorn api.gateway:app --host 0.0.0.0 --port 8000
```

O texto da chave aparece **uma única vez**. O que fica em disco, em `.tokens.json`, é
apenas o hash SHA3-256, junto com nome, escopos e data. Revogar marca o registro e a
chave para de valer no pedido seguinte.

## Duas formas de chave

1. **Chave mestra** em `ZYQL_API_TOKEN`, lida do ambiente. Serve para serviço a serviço e
   para o deploy. Comparada em tempo constante.
2. **Chaves nomeadas** emitidas pela CLI, com escopo limitado e revogação individual.
   São as que devem ir para pessoas e integrações.

## No Replit

`start.sh` instala `.[api,pq]` e sobe o `uvicorn`. A chave entra pelas variáveis do
Repl, nunca no código e nunca no repositório. `.tokens.json` e `.replit-env` estão no
`.gitignore`.

## O que o token não resolve

Não há autenticação de usuário final, rate limit por IP nem cota por chave. Para
exposição pública, essas camadas vão no Replit ou num gateway de borda. Está declarado
em `/v1/limits` para ninguém supor proteção que não existe.

## Estado atual da chave

A chave mestra vive como segredo de ambiente, `$ZYQL_API_TOKEN`, e não está no
repositório. As chaves nomeadas emitidas por CLI ficam em `.tokens.json` apenas como
hash SHA3. A chave de produção emitida antes da migração para o segredo foi **revogada**.

Comandos:

```bash
python -m api.gateway issue --name <nome> --scopes read,decide,qsr,lang
python -m api.gateway list
python -m api.gateway revoke <chave>
```

`list` mostra hash curto, nome, escopos, data e se está ativa ou revogada. Nunca
imprime a chave.

## Verificação de ponta a ponta (medida)

| Chamada | Resultado |
|---|---|
| `GET /health` sem chave | 200 |
| `GET /v1/catalog` sem chave | 401 |
| `GET /v1/catalog` com a chave | 200, quatro fronts |
| `POST /v1/qsr/assess` | veredito 0: um ativo precisa migrar, o outro está pronto |
| `POST /v1/lang/run` com `(hello zyql)` | saída `Hello, zyql! | decisao = 1` |
| `POST /v1/core/decide` com `const1` | veredito 1 com recibo selado |

## Verificação do webhook de pagamento

Duas camadas, e a primeira manda:

1. `STRIPE_WEBHOOK_SECRET` definido: exige o cabeçalho `Stripe-Signature` com HMAC-SHA256
   sobre `timestamp.corpo`, tolerância de 300 segundos. Assinatura ausente, inválida ou
   antiga é recusada com 401.
2. Só `ZYQL_WEBHOOK_SECRET`: valida segredo compartilhado no corpo. Funciona, mas não
   protege contra POST forjado com o segredo vazado.
3. Nenhum dos dois: o webhook responde 503. Nunca emite chave sem verificação.

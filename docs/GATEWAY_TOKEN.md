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

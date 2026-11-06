# Integrar Lovable e Replit ao ZYQL

Não existe conector nativo do Base44 para Lovable nem para Replit. A ponte é a mesma
para as duas: **contrato de API publicado + GitHub compartilhado**.

## Papéis

| Peça | O que faz | O que NÃO faz |
|---|---|---|
| API ZYQL (`api/server.py`) | expõe a matemática: decidir, limitar, verificar recibo, oráculo | não tem interface visual |
| Lovable | constrói a interface que consome a API | não substitui o cálculo, não guarda recibo |
| Replit | hospeda e publica o serviço | não reescreve a lógica de decisão |
| GitHub | é o barramento: todos sincronizam do mesmo repositório | não é transporte de dados de produção |

## Rotas publicadas

`GET /health`, `GET /limits`, `POST /bound`, `POST /decide`, `POST /verify`,
`POST /oracle/reveal`, `POST /oracle/promise`. Especificação completa em
[`openapi.json`](openapi.json) (OpenAPI 3.1, gerado do próprio servidor).

## Passo a passo no Lovable

1. No Lovable, criar o projeto apontando para um repositório GitHub dedicado à interface.
2. Importar `docs/openapi.json` como contrato, ou colar as rotas manualmente.
3. A interface chama a API; o veredito exibido é sempre o que a API devolveu, nunca
   calculado no navegador. Veredito calculado no cliente não é auditável.
4. Variável de ambiente com a URL base da API e, se houver, a chave.

## Passo a passo no Replit

1. Importar o repositório do GitHub como Repl Python.
2. Instalar o pacote: `pip install zephirum[api]`.
3. Subir o serviço: `uvicorn api.server:app --host 0.0.0.0 --port 8000`.
4. Publicar o Repl e usar a URL pública como base para o Lovable.

## Limite honesto

O ZYQL decide e selá o recibo. Ele não garante disponibilidade, autenticação de usuário
nem proteção de dados pessoais na ponta. Se a interface for pública, autenticação e
rate limit precisam ser resolvidos no Replit ou num gateway, não dentro do algoritmo.

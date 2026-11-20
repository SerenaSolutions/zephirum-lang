# Chat com IA no site ZEPHIRUM

Esta integração adiciona `https://SEU-DOMINIO/chat` (arquivo `site/chat.html`) e a função serverless `POST /api/chat` para Vercel. A chave OpenAI fica somente em variável de ambiente do servidor; nunca é enviada ao navegador.

## O que inclui

- Assistente de documentação com contexto canônico do projeto e links para fontes públicas.
- Conversa com histórico persistido **no `localStorage` do navegador**, não em banco/servidor. O usuário pode apagá-lo na tela.
- Ferramentas de cálculo opcionais `zyql_decide` e `zyql_bound`; só ficam disponíveis se `ZYQL_API_URL` estiver configurada. Chamadas são limitadas a essas duas rotas, validadas no backend e forçadas para simulação (`hardware=false`, `sign=false`). Não há submissão de QPU nem execução arbitrária de código.
- Limites de tamanho e frequência best-effort, respostas sem cache e logs da função sem prompts/IPs.

> O conteúdo enviado é processado pelo provedor OpenAI. Não envie dados pessoais, tokens, credenciais ou dados confidenciais. Resposta do modelo não é decisão nem validação científica. A integração não guarda histórico do lado do servidor; logs da plataforma/provedor estão sujeitos às respectivas políticas.

## Publicar na Vercel

1. Faça merge desta branch para o branch de deploy do repositório. O `vercel.json` da raiz publica `site/` como estático; o diretório `api/` é detectado como função serverless Python.
2. No projeto Vercel, abra **Settings → Environment Variables** e adicione `OPENAI_API_KEY` com uma chave da API OpenAI. Marque os ambientes (Production e/ou Preview) desejados. Não coloque a chave no GitHub, no HTML, em `NEXT_PUBLIC_*` nem no chat.
3. Opcional: defina `OPENAI_MODEL` (padrão `gpt-4.1-mini`).
4. Para habilitar cálculo, configure `ZYQL_API_URL` com a URL HTTPS base de uma implantação ZYQL compatível com `POST /decide` e `POST /bound`; se protegida, configure `ZYQL_API_KEY` (enviada como `X-API-Key`). Sem `ZYQL_API_URL`, o chat de documentação funciona sem as ferramentas de execução.
5. Opcionalmente configure `CHAT_ALLOWED_ORIGINS` com origens separadas por vírgula (por exemplo, `https://serenasolutions.github.io,https://seu-dominio.vercel.app`). Sem essa lista, a função aceita apenas a origem que corresponde ao host que recebeu a chamada.
6. Faça redeploy para carregar as variáveis. Acesse `https://SEU-DOMINIO/chat` (por exemplo, o domínio de produção configurado no projeto Vercel seguido de `/chat`). Não há um domínio público concreto informado por esta mudança.

## Desenvolvimento e testes

```bash
python -m unittest discover -s tests -p 'test_zyql_chat.py'
```

Para testar localmente, use Vercel CLI com as variáveis no ambiente; nunca com uma chave embutida no frontend. Se uma implantação do API ZYQL ainda não existe, a parte de cálculos fica desativada, e não deve ser simulada por respostas inventadas do modelo.

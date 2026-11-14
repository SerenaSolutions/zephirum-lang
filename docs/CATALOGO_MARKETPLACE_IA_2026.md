# Varredura do GitHub Marketplace: IA, agentes e nuvem

Termos consultados na busca do Marketplace em 09/11/2026, com o total que a
própria busca devolveu. Isso corrige a leitura anterior, que olhou apenas os
seis termos nomeados e não as categorias de IA.

| Termo | Actions | Apps | Leitura |
|---|---|---|---|
| claude | 217 | 28 | Mercado maduro de revisão de PR por IA. |
| openai | 214 | — | Idem, quase tudo revisor de PR de terceiro. |
| mcp | 268 | — | Em 2026 o volume é de auditoria de segurança de MCP e de medidor de custo de token de ferramenta. |
| gemini | 119 | — | Muitos revisores, poucos oficiais. |
| supabase | 40 | **0** | Só Actions. Não existe App Supabase no Marketplace. |
| quantum | 29 | **1** | Quase tudo é scanner de prontidão pós-quântica. |
| antigravity | 3 | — | Nenhuma da Google. |
| ibm quantum | **1** | — | A única é a `SerenaSolutions/ravi-quantuno`. |
| qiskit | **0** | — | Não existe action de Qiskit no Marketplace. |
| aws | 784 | — | Nuvem madura: credencial, ECS, Lambda, CloudFormation, S3. |
| azure | 320 | — | Inclui Azure AI Agent Evaluation e Artifact Signing. |
| ollama | 37 | — | Servidor de LLM local em runner, sem custo de API. |

## Fornecedores oficiais verificados na fonte

Repositório, licença, último push e última release, checados pela API do GitHub.

| Action | Repositório | Licença | Última release |
|---|---|---|---|
| Claude | `anthropics/claude-code-action` | MIT | v1 |
| Gemini CLI | `google-github-actions/run-gemini-cli` | Apache-2.0 | v0.1.22 (24/04/2026) |
| Codex | `openai/codex-action` | Apache-2.0 | sem release tagueada |
| AWS credenciais | `aws-actions/configure-aws-credentials` | MIT | v6.3.0 |
| Azure login | `azure/login` | MIT | v3.1.0 |
| Google auth | `google-github-actions/auth` | Apache-2.0 | v3 |
| Docker build | `docker/build-push-action` | Apache-2.0 | v7.4.0 |
| Terraform | `hashicorp/setup-terraform` | MPL-2.0 | v4.0.1 |
| Fly.io | `superfly/flyctl-actions` | Apache-2.0 | 1.5 |
| Supabase CLI | `supabase/setup-cli` | MIT | v3.2.0 |
| Ollama | `ollama/ollama` | MIT | v0.40.15 |
| Papermill | `nteract/papermill` | BSD-3-Clause | sem release tagueada |
| nbconvert | `jupyter/nbconvert` | BSD-3-Clause | v7.17.2 |
| Hugging Face Hub | `huggingface/huggingface_hub` | Apache-2.0 | v2.4.0 |
| uv | `astral-sh/setup-uv` | MIT | v10.3.3 |
| Cloudflare | `cloudflare/wrangler-action` | Apache-2.0 | v4.1.3 |
| kubectl | `azure/setup-kubectl` | MIT | v5.2.0 |
| Helm | `azure/setup-helm` | MIT | v5.0.1 |
| k8s deploy | `azure/k8s-deploy` | MIT | v7.0.1 |
| gcloud | `google-github-actions/setup-gcloud` | Apache-2.0 | v3.0.1 |
| ECR login | `aws-actions/amazon-ecr-login` | MIT | v2.1.7 |
| Codecov | `codecov/codecov-action` | MIT | v7.1.1 |
| QEMU | `docker/setup-qemu-action` | Apache-2.0 | v4.4.0 |

## O que foi ativado

`experiment-lab.yml`: executa um script de `experiments/` num ambiente
reproduzível, com as dependências do próprio `pyproject.toml`, e sela o
resultado em SHA3-256 amarrado ao commit e ao run. Não precisa de secret
nenhum. É a ferramenta de bancada que faltava para o dia a dia do algoritmo:
roda, registra e guarda artefato.

`ai-lab.yml`: Claude e Gemini acionados à mão, cada um só roda se a chave
existir. Dois secrets habilitam: `ANTHROPIC_API_KEY` e `GEMINI_API_KEY`.

## O que não vale instalar, apesar do número grande

Dos 214 resultados de "openai" e 217 de "claude", a esmagadora maioria é
revisor de PR de terceiro que pede a chave do seu modelo e ganha acesso ao
diff. Com CodeQL, Ruff, mypy e revisão humana já no repositório, é superfície
de risco sem ganho. O mesmo vale para os 268 de "mcp": são quase todos
scanners de segurança de agente, úteis apenas se você publicar servidor MCP.

## Servidor de LLM local: a única rota de IA que não gasta crédito

As 37 actions de Ollama existem porque o gargalo de 2026 é custo de token em CI.
Nenhuma é oficial: as mais mantidas são `ai-action/ollama-action` (34 estrelas,
push em junho) e `ai-action/setup-ollama` (17 estrelas, push em novembro). Rodam
modelo pequeno em CPU de runner, o que serve para resumir diff e rotular PR,
não para trabalho de fronteira. É a alternativa honesta ao bloqueio de cota.

## O ganho medido de hoje

O laboratório trocou `pip install` por `astral-sh/setup-uv` mais `uv pip install`.
Mesmo conjunto de dependências, incluindo qiskit, com cache de resolução.

## Tensão a resolver antes de adotar nuvem

O estatuto do Dexia proíbe dependência externa. Actions de CI não são
dependência do pacote, então tecnicamente convivem. Mas AWS, Azure, GCP e
Fly.io não têm uso hoje: não há serviço hospedado fora da Vercel. Instalar
credencial de nuvem sem serviço para operar é passivo, não capacidade.

## Varredura complementar (09/11/2026, segunda passada)

| termo | actions | apps | leitura |
|---|---|---|---|
| aws | 784 | — | dominio total de infraestrutura |
| kubernetes | 241 | — | so faz sentido com cluster real |
| cloudflare | 172 | — | workers, R2, pages |
| gcp | 54 | — | gcloud, GKE, Vertex AI |
| ollama | 37 | — | IA local sem custo de API (nada oficial) |
| hugging face | 11 | — | sync de modelo/dataset |
| cloudflare apps | - | 0 | nenhum |

Verificados nesta passada: cloudflare/wrangler-action v4.1.3, azure/k8s-deploy v7.0.1,
azure/setup-kubectl v5.2.0, azure/setup-helm v5.0.1, google-github-actions/setup-gcloud
v3.0.1, aws-actions/amazon-ecr-login v2.1.7, astral-sh/setup-uv v10.3.3,
codecov/codecov-action v7.1.1, docker/setup-qemu-action v4.4.0.

Adotado com medicao: astral-sh/setup-uv v10.3.3 no experiment-lab. Instalacao das
dependencias do projeto caiu de 13s para 1s; job inteiro de 26s para 13s (parte do
ganho vem de cache quente, o numero honesto e o passo de instalacao).

Ollama: nenhuma action oficial. ai-action/setup-ollama (push 06/11/2026) e
ai-action/ollama-action (push 24/06/2026) sao as mais mantidas, ambas de comunidade.

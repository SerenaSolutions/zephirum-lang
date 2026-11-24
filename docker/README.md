# ZEPHIRUM Core — infraestrutura em Docker

Motor ZCA, ponte OpenQASM 3, verificador de recibo e adaptador IBM Quantum, tudo
numa imagem. O núcleo não tem dependência externa; o QPU é opcional.

## Invariantes

1. Proof → Compute: prova antes de calcular.
2. Trivalente: `1`, `0`, `REFUSED`. Nunca `REFUSED` virando booleano.
3. Aritmética exata (`fractions.Fraction`). Float só em apresentação.
4. Recibo com hash canônico SHA-256 (o campo `hash_alg` declara o algoritmo).
5. Fail-closed: backend sem credencial recusa com código, nunca cai em silêncio.

## Rodar sem Docker (rápido, para testar)

```bash
python3 -m pytest -q tests        # 25 testes
python3 -m zephirum_core.server   # http://localhost:8080
```

## Rodar com Docker

```bash
cp .env.example .env              # preencha o token só se for usar QPU
docker compose up -d --build core # API sem QPU, porta 8080
curl -s localhost:8080/health
```

## Rodar no QPU da IBM (plano free)

```bash
# 1. pegue o token em quantum.ibm.com, aba Account
# 2. coloque em .env:  IBM_QUANTUM_TOKEN=seu_token
docker compose --profile qpu up -d --build core-qpu
# API com qiskit + qiskit-ibm-runtime na porta 8081
```

O plano free dá um número limitado de segundos de QPU por mês. Por isso existe o
**portão de cota**: antes de qualquer submissão, o programa passa pela análise
Clifford. Se for só Clifford, a resposta é `REFUSED` com código `IBM-422` e a
cota não é gasta, porque simulador clássico resolve o mesmo circuito.

### Rotas

| Rota | O que faz |
| --- | --- |
| `GET /health` | estado e versão |
| `GET /regras` | as 6 regras do ZCA com exemplos |
| `POST /zca` | `{op, args}` → veredito, prova e recibo |
| `POST /qasm3` | `{qasm}` → 1 (Clifford), 0 (não-Clifford), REFUSED |
| `POST /verify` | `{cert, hash}` → recibo íntegro ou adulterado |
| `POST /ensaio` | valida sem enviar: diz se o QPU aceitaria |
| `POST /submit` | submete ao QPU e devolve job_id, contagens e recibo |

### Exemplo: submissão com portão de cota

```bash
curl -s localhost:8081/ensaio -H 'content-type: application/json' \
  -d '{"qasm":"OPENQASM 3.0; qubit[2] q; h q[0]; cx q[0],q[1];"}'
# -> REFUSED, IBM-422: só Clifford, simulador resolve

curl -s localhost:8081/submit -H 'content-type: application/json' \
  -d '{"qasm":"OPENQASM 3.0; qubit[1] q; h q[0]; t q[0];","shots":1024}'
# -> veredito 1 com job_id, contagens e recibo
```

## Suíte do QuanSo OS no container

```bash
docker compose --profile quanso run --rm quanso-tests
```

Monta o repositório em modo leitura, instala pytest na imagem e roda a suíte.
Nenhum artefato do repositório é alterado.

## Códigos de recusa

| Código | Significado |
| --- | --- |
| `IBM-401` | token ausente no ambiente |
| `IBM-404` | backend inexistente ou indisponível |
| `IBM-422` | circuito Clifford: não gasta cota |
| `IBM-429` | limite de cota do plano atingido |
| `IBM-503` | biblioteca qiskit ausente na imagem |
| `IBM-500` | falha na execução |

## O que NÃO está coberto

- Nenhuma submissão real foi feita aqui: o sandbox não tem token nem rede para o QPU.
  Os caminhos testados são o portão de cota, o ensaio e a recusa fail-closed.
- Autenticação da API: ela não tem. Rode em rede privada ou coloque um proxy na frente
  antes de expor na internet.

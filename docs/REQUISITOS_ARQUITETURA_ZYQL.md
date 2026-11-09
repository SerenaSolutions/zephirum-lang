# Requisitos técnicos da arquitetura ZYQL — transição da ZEPHIRUM

Documento de requisitos, versão 1.0, 09/11/2026. Base: estado verificado do
repositório no commit da publicação deste arquivo, gramática v1.5.0, 31 módulos
em `src/`, 193 testes, portão de conformidade 19/19.

Cada requisito tem identificador, prioridade e critério de aceitação
verificável. Sem critério de aceitação, o item não é requisito, é intenção.

## 1. Premissa

A ZYQL não é um modelo de IA nem um produto setorial. É a camada que decide,
verifica e comprova antes de executar. A transição consiste em levar essa camada
do estado atual, que já decide e já emite recibo em pesquisa, para um estado de
operação com contrato estável, reprodutibilidade medida e verificação por
terceiro.

## 2. Requisitos funcionais

**RF-01 Núcleo de decisão congelado.** A função `decide()` é a única porta de
decisão trivalente do sistema. Assinatura publicada e versionada. Nenhum módulo
setorial implementa decisão própria.
Aceitação: alteração de assinatura exige incremento de versão maior e registro
em CHANGELOG; teste `test_zyql_ten.py` falha se o enum de veredito mudar.

**RF-02 Provedores de evidência.** Toda checagem de domínio (qualidade de dado,
drift, integridade de pipeline, proveniência, política) é um provedor que
entrega medição e veredito ao núcleo, nunca um verbo novo na linguagem.
Aceitação: `src/zyql_ten/` cobre as dez demonstrações do documento com `run()`
próprio e retorno medido; 11 testes verdes.

**RF-03 Distinção entre reprovado e sem evidência.** Reprovar sem conseguir
medir é proibido. Sem medição, a saída é REFUSED com motivo declarado.
Aceitação: todo `run()` devolve `motivo` quando o veredito é REFUSED; teste
cobre conjunto vazio, série curta e setor desconhecido.

**RF-04 Roteador de execução.** O sistema avalia rota clássica, quântica
simulada e quântica em hardware antes de executar, e escolhe a mais barata que
satisfaça o critério.
Aceitação: item 06 escolhe CLÁSSICO quando existe solução clássica conhecida e
QUÂNTICO quando a relevância é demonstrada, com custo em profundidade
transpilada comparado a orçamento declarado.

**RF-05 Recibo auditável por operação.** Toda decisão emite recibo com hash
SHA3-256 dos insumos, veredito, banda de erro, chamadas ao oráculo, shots,
latência e identificação do commit.
Aceitação: `verify_receipt()` valida recibo íntegro e rejeita adulteração;
cadeia de recibos verificável por `verify_chain()`.

**RF-06 Assinatura pós-quântica fora do CI.** Recibo é assinado com ML-DSA-44
em ambiente com chave custodiada. O pipeline de integração contínua nunca
recebe chave privada.
Aceitação: recibo gerado em CI declara explicitamente `assinatura: ausente`;
recibo assinado só é emitido por execução local autorizada.

**RF-07 Adaptador quântico por Qiskit.** Toda interação com backend quântico
passa pelo adaptador, com versão de SDK fixada e registro das três métricas de
sistema: qubits programáveis, profundidade transpilada e throughput.
Aceitação: nenhum módulo chama backend diretamente; recibo de QPU registra as
três métricas.

**RF-08 Governança declarada.** Rastreabilidade de origem, versão de modelo e
política de decisão com registro de falhas por item.
Aceitação: item 07 devolve lista `falhas` com o código de cada violação, nunca
um booleano solto.

**RF-09 Demonstração setorial.** As dez soluções do documento executam a partir
de um ponto de entrada único, com saída legível por máquina.
Aceitação: `python -m zyql_ten` executa as dez e imprime JSON por linha.

**RF-10 Verificação por terceiro.** Terceiro consegue verificar recibo sem
confiar no autor, usando apenas o verificador publicado e o material selado.
Aceitação: verificador independente reproduz o mesmo resultado a partir de
recibo e artefato selado. **Não atendido hoje.**

## 3. Requisitos não funcionais

**RNF-01 Piso de linguagem.** Python 3.11 como piso, porque o Qiskit 2.6 é a
última linha a suportar 3.10. O `pyproject.toml` declara `>=3.10` e o CI fixa
3.10. Divergência aberta.

**RNF-02 Reprodutibilidade de dependências.** Arquivo de lock com versões
resolvidas. Hoje as faixas são abertas e o Trivy varre zero alvos por isso.

**RNF-03 Latência de decisão.** Decisão local abaixo de 1 segundo para n até 8
qubits com shots dentro da banda suportada.

**RNF-04 Custo por operação.** Custo medido em profundidade transpilada e em
segundos de QPU, nunca estimado por intuição.

**RNF-05 Cobertura de teste.** Suíte completa verde em todas as versões
suportadas. Estado atual: 193 testes.

**RNF-06 Portão de conformidade.** Nenhuma entrega sem 19/19 no verificador,
incluindo SPDX em todo arquivo Python e licença coerente.

**RNF-07 Versionamento semântico.** Gramática e contrato de recibo versionados
de forma independente do pacote.

## 4. Contrato congelado

`decide(f, n=3, shots=2048, seed=1701, seal_path=None, epsilon=None,
require_device_trust=False, device_shots=2048, previous_seal=None, family=1,
require_memory_check=False, memory_steps=3)`

Veredito: `PERMIT = 1`, `DENY = 0`, `REFUSED`.

Decisão carrega: veredito, p0, modo, banda de erro, chamadas ao oráculo, shots,
n, latência, motivo de recusa, recibo.

## 5. Gates da transição

G0 Estado atual verificado: verde.
G1 Dependências resolvidas: lockfile, piso 3.11, Trivy com alvo real.
G2 Provedores de evidência com teste por setor: coberto por `zyql_ten`.
G3 Roteador com economia medida contra baseline.
G4 Verificação por terceiro com recibo reproduzível fora do autor.
G5 Operação com SLA e custo por operação declarados.

Nenhum gate se abre por decisão interna. Cada um exige artefato verificável.

## 6. Riscos declarados

Certificação formal não existe: sem FIPS, CAVP ou CMVP. Custódia de chave é
local. Verificação independente não foi feita. O piso de Python está defasado.
Não há lockfile. Esses cinco itens são a diferença entre pesquisa e produto.

## [Em desenvolvimento] - 2026-11-12

Trabalho em curso. Sem release, sem publicação no PyPI.

- Perfil de evidência para medida clássica (`MEASURE`): a incerteza declara o método
  (amostra ou expandida, com fator de cobertura `k`), e a obrigação declara quais
  tipos de evidência a quitam. O padrão segue fechado em apenas quântico.
- Três defesas ativas: obrigação quântica recusa medida clássica; `MEASURE` sem `k`
  é recusada; tipo de evidência desconhecido é recusa, nunca omissão.
- Bateria de metrologia: 20 casos com veredito previsto antes da execução, 19/20,
  com 5/5 nos casos de bancada clássica.

## [2.5.8] - 2026-11-07

### Segurança (auditoria integrada de 06/11)
- Rate limit por chave: janela deslizante de 60 s, `ZYQL_RATE_LIMIT` (padrão 120/min), 429 com `Retry-After`.
- CORS restrito por `ZYQL_CORS_ORIGINS`, sem curinga, com métodos e cabeçalhos declarados.
- Recibos encadeados: `prev` e `elo` em toda rota da API; corrente em `ZYQL_CHAIN_FILE`.
- Webhook Stripe com verificação de assinatura HMAC-SHA256 sobre `timestamp.corpo`, tolerância de 300 s.
- `ZYQL_ENV=production` exige `STRIPE_WEBHOOK_SECRET`: modo degradado recusado com 503.

### Comercial
- `api/billing.py`: checkout, emissão de chave com saldo, medição por verificação, idempotência e 402 no saldo esgotado.
- Gateway com token: fronts `read`, `decide`, `qsr`, `lang`; chaves alfanuméricas de 48 caracteres, guardadas em SHA3.

### Pacote
- `uvicorn` declarado no extra `api` (antes o `uvicorn` faltava e o servidor não subia).
## [2.5.6] - 2026-11-05
- `zyql_worldscale`: banda do W-03 unificada em 0.85, a mesma do protocolo
  pre-registrado. Antes o codigo certificava com 0.70 enquanto o protocolo recusava
  o mesmo resultado, o que tornava o recibo ambiguo.
- `rodada_mundial` passa a aceitar `bandas` explicito.

## [2.5.5] - 2026-11-05
- Modulo `quantum_safe_readiness` (QSR): inventario criptografico, criterio de Mosca,
  agilidade, interop ML-KEM-768/ML-DSA-44 e recibo SHA3 selado.
- `docs/QSR_FONTES.md` com a fundamentacao em FIPS 203/204/205, IR 8547 final,
  SP 800-57, CNSA 2.0 e SP 1800-38; chaves publicas conferem com o padrao.

## [2.5.4] - 2026-11-05
- `qroute.__version__` passa a ler o metadado do pacote em vez de repetir
  a versao escrita a mao; a 2.5.3 publicada reportava 2.4.0 internamente.
- Metadados do PyPI alinhados (licenca Apache-2.0, dependencia an industry-standard quantum SDK com teto).

## [2.5.3] - 2026-11-03

### Corrigido — conformidade v1.1.0 (cerca fechada)
1. `SPEC.md` §3 reescrita conforme o código: `p0 <= banda` recusa como
   `BALANCED_ORACLE` e **não** produz veredito `0`; veredito `0` só existe no
   ramo de interferência com `f(0) == 0`. A v1.0.0 declarava o contrário.
2. Canon único: `src/qroute/receipt.py` passou a importar `canon` de
   `src/battery_ci.py`. Os 7 recibos de `examples/recibos/` foram reselados sob
   a regra única, com o conteúdo intacto (mudou apenas o hash).
3. `run_conformance.py` reprova recibo sem selo em vez de pular, e varre
   `experiments/**/*_receipt.json`, `examples/recibos/*.json` e a raiz.
4. Cobertura de regra por `p0` sintético: zona cinzenta (`INSIDE_NOISE_BAND`),
   fronteiras exatas e `BALANCED_ORACLE` no limiar inferior, mais a porta de
   dispositivo exigindo `REFUSED` com zero chamadas de oráculo.
5. `src/battery_ci.py` passou a rodar sob `__main__`: importar o módulo para
   reusar `canon` não executa a bateria nem chama `sys.exit`.
Suíte: 57 verificações, CONFORMANTE local.

### Adicionado — suíte de conformidade ZYQL (spec 1.0.0)
`conformance/SPEC.md` fixa o contrato: banda Hoeffding, banda de família Bonferroni,
regra de decisão, taxonomia fechada de recusa, canonicalização do selo SHA3-256,
porta de dispositivo e exigência de OpenQASM 3 no produto quântico.
`conformance/run_conformance.py` testa o núcleo de referência contra os casos dourados
(`conformance/cases.json`), recomputa o selo de todos os recibos do repositório e
confere a presença de OpenQASM 3; sai 0 quando conformante e 1 quando não.
Workflow `conformance.yml` roda em push, em PR e semanalmente.
Estado local: 42/42 CONFORMANTE.

### Adicionado — prova de fogo no silício, executável por agente externo
`experiments/prova_de_fogo.py` + `experiments/verificar_prova_de_fogo.py` + `docs/PROVA_DE_FOGO.md`.
Duas medidas independentes no hardware (interferência decide a classe, leitura direta
decide o valor), porta de integridade GHZ vetando o dispositivo, e recusa declarada
dentro da banda de Hoeffding. Primeira execução em the provider_marrakesh, job internal,
1024 shots, eps=0.05: const-0 -> 0, const-1 -> 1, balanceado -> REFUSED(BALANCED_ORACLE),
GHZ fidelidade 0.9131, recibo selado e31b3295. O verificador recomputa o selo e reconfere
cada veredito pelos counts crus; recibo adulterado é reprovado.

### Corrigido — CI vermelho no HEAD (pytest ausente e alvo de cobertura invalido)
Duas falhas de pipeline que nao tinham relacao com o codigo do nucleo:

1. `CI` / `tests`: `tests/test_kem.py` importa `pytest` no topo, mas o job nunca instalava
   `pytest`. Alem disso o arquivo era executado direto (`python tests/test_kem.py`), o que
   nao roda nenhum teste. Agora o job instala `pytest` e chama `python -m pytest`.
2. `coverage` / `piso de cobertura`: `--cov=src/zyql_runtime.py` nao e alvo valido do coverage
   (resultado 0%, "module was never imported"). Trocado por `--cov=zyql_runtime` com
   `PYTHONPATH=src`; a cobertura real medida e 73%, acima do piso de 70%.
3. `tests/test_kem.py`: o skip de `pqcrypto` passou a usar `try/except ImportError` com
   `SystemExit(0)`, para pular a bateria mesmo quando o arquivo roda fora do pytest.
4. `VERSION` alinhado a 2.5.3 (estava em 2.5.1, divergindo de `pyproject.toml`, README e
   CHANGELOG).

Pendente e fora do alcance do codigo: `Verificacao de publicacao` continua vermelho enquanto
o PyPI estiver em 2.4.0. Publicar 2.5.3 exige `PYPI_TOKEN` do dono.


### Corrigido — `docs/ENTIRE.md` descrevia o mecanismo errado
A versão anterior mandava empurrar direto para `https://entire.com/et/<namespace>/<repo>.git`.
A documentação oficial diz outra coisa, e a diferença explica por que a tela de repositórios
aparece vazia: **o Entire GitHub App precisa ter acesso ao repositório antes de qualquer mirror
existir**. Sem o app instalado não há o que listar — não é interface incompleta.

O documento agora separa os dois modelos (mirror × hospedagem nativa), lista as regiões
disponíveis (incluindo São Paulo), registra o que muda e o que não muda, e declara o limite
conhecido: mirrors não suportam Git LFS.

## [2.5.2] - 2026-11-03

### Adicionado — espelhamento para o Entire
- `scripts/mirror_to_entire.sh`: espelha os 32 repositórios da conta para a forge do Entire,
  com `--dry-run`, token por header HTTP (nunca na URL) e contagem explícita de falhas.
- `docs/ENTIRE.md`: o que é o Entire (fundada por Thomas Dohmke, ex-CEO do GitHub), por que
  encaixa com a nossa tese de recibo de decisão, e o estado verificado: a página do namespace
  responde com **Login**, e `ENTIRE_TOKEN` não está no ambiente.

Correção de rota durante a implementação: a listagem usava `/orgs/`, que devolve erro para
conta pessoal; trocada por `/users/`, e erro de API agora falha alto em vez de virar lista
vazia silenciosa.

## [2.5.1] - 2026-11-03

### Adicionado — sinais de maturidade e protocolo de difusão global
Auditoria contra o padrão de an industry-standard quantum SDK, a differentiable quantum SDK, another quantum SDK e Q#: faltavam seis marcadores que
revisor técnico procura em 30 segundos.

- `src/py.typed` — consumidor Python sabe que há tipos declarados;
- `.pre-commit-config.yaml` — ruff e checagens de arquivo antes do commit;
- `.github/workflows/coverage.yml` — CI de cobertura com piso (não regride);
- `docs/DEPRECATION.md` — semver como contrato, aviso de 2 MINOR ou 90 dias, recibos nunca
  invalidados;
- `GOVERNANCE.md` — como uma mudança entra; recusa não pode virar alegação automática;
- `packaging/conda/meta.yaml` — recipe conda-forge pronta para `staged-recipes`;
- `docs/DIFUSAO_GLOBAL.md` — protocolo em 4 fases com estado real de cada canal e bloqueios.

Nada aqui alega vantagem técnica: é infraestrutura de credibilidade. Suite inalterada e verde.
**Nota de erro próprio:** a tag v2.5.1 chegou a ser criada antes do bump de versão no
`pyproject.toml`; o `test_meta.py` acusou a inconsistência e o bump foi feito em seguida.

## [2.5.0] - 2026-11-03

### Adicionado — API REST com a matemática exposta
`api/server.py` reescrito: antes era um wrapper que executava programa e devolvia
"executed". Agora devolve veredito trivalente com a conta junto.

- `POST /decide` — veredito 1 / 0 / REFUSED com `p0`, banda de Hoeffding usada, shots,
  epsilon, família e recibo SHA3-256 (assinatura ML-DSA-44 opcional com `sign=true`).
- `POST /bound` — a álgebra separada do veredito: banda para S shots **ou** shots
  necessários para uma banda-alvo (`S = ln(2/(ε/k)) / 2m²`).
- `POST /verify` — verificação offline: recomputa o selo, denuncia `SEAL_MISMATCH`.
- `POST /oracle/reveal` e `POST /oracle/promise` — modos v2.4.0 pela rede.
- `GET /limits` — o que o sistema **não** faz, declarado em produção.

### Duas honestidades embutidas (e testadas)
1. `hardware=true` devolve **409**, não uma simulação disfarçada. Execução em QPU exige
   job ID verificável e vive no script de hardware do repositório.
2. Família de testes maior **encolhe** a banda (Bonferroni na direção correta). Um teste
   verifica a monotonicidade em vez de assumi-la — foi exatamente aqui que a primeira
   implementação errou no passado.

### Corrigido durante a implementação
- A banda não aparecia no recibo porque o kernel devolve `error_bound` e não `margin`;
  o campo agora é derivado explicitamente de `adaptive_margin_family`.
- Um teste meu afirmava que família 500 com 64 shots seria "insolúvel" — falso pela
  fórmula. O teste foi corrigido para verificar a propriedade real (monotonicidade),
  não uma suposição.

Testes: `tests/test_api.py` — 18 verificações, incluindo banda conferida contra a conta
feita à mão (tolerância 1e-12).

## [2.4.0] - 2026-11-03

### Adicionado — modos de DESCOBERTA do oráculo
O núcleo já respondia "que classe é este oráculo?". Este módulo responde "qual é o oráculo?",
identificando a função escondida com a mesma semântica trivalente.

- `reveal_linear(mask, n)` — Bernstein–Vazirani: recupera a máscara s de f(x) = (s·x) mod 2 em
  **uma única consulta** (clássico: n consultas). Verificado para todas as máscaras de 2 e 3 bits.
- `find_period(table, n)` — Simon: recupera o período s escondido resolvendo o espaço nulo sobre
  GF(2) dos y medidos. Afirma s só quando a dimensão é 1; caso contrário REFUSED com candidatos.
  Função injetora devolve veredito 0 (sem período inventado).
- `identify_2bit(table)` — identifica os **16** booleanos de 2 variáveis, com flag de promessa.
- `audit_promise(table)` — a promessa de Deutsch–Jozsa (constante OU balanceado) raramente é
  testada: oráculo de peso 1 ou 3 parece "ruído" e some num REFUSED. Aqui ele é acusado como
  NO_PROMISE com **testemunha** (entradas que provam a violação).

### Bugs encontrados e corrigidos durante a implementação (registro honesto)
1. **Oráculo BV com CZ**: com âncilla em |−⟩ e porta CZ o âncilla NÃO se fatora e a
   interferência cai pela metade (p = 0,5 em vez de 1,0). Troca para CX produz o chute de fase
   correto.
2. **Ordem de leitura do registrador**: `probabilities_dict` lista o qubit mais alto primeiro;
   ler os primeiros n caracteres devolvia o âncilla e metade da entrada. A entrada são os
   **últimos** n caracteres.
3. **Oráculo de Simon controlando só os bits em 1**: o caso x=10 disparava também em x=11 e
   anulava o MCX de x=11, quebrando o período (só s=11, palíndromo, passava). Correção:
   inverter os zeros e controlar em TODOS os n qubits.

Testes: `tests/test_oracle_id.py` cobre 8 máscaras BV, 3 períodos Simon + caso injetor,
16 funções identificadas e 4 casos de auditoria de promessa. Todos falsificáveis.

## [2.3.2] - 2026-11-03

### Corrigido (check-up estático)
- **Bug latente em `qroute/hardware.py`**: a função `p_marcados` carregava a expressão
  morta `{...for m in marcados} if False else None`, que referenciava `n` indefinido
  (ruff F821) e alocava uma variável sem uso. Não quebrava em execução porque o ramo
  nunca era avaliado — mas código que mente sobre o que faz é dívida. Removida.
- Código morto removido em `zyql_quantum_gate` (`band_pending`) e em `zyql_mps`
  (cálculo de `keep` nunca lido: uma soma de array por passo a menos).
- `zyql_zne`: resíduo da extrapolação renomeado para `_residual`, preservando a
  intenção informativa sem enganar o lint.
- Ruff F821/F841/F811: de 6 ocorrências para 2 (ambas de variável de efeito colateral
  em `quantum_types`, declaradas como tal).

### Validado
- Bateria de 1000 execuções por app (8 apps, 8.000 no total): 0 erros.
- Rodada no silício (the provider_marrakesh, 256 shots, n=2): const-1 → 1, const-0 → 0,
  paridade → REFUSED. 3/3 conforme esperado, 6s de QPU.

## [2.3.1] - 2026-11-01

### Corrigido
- **Cap do an industry-standard quantum SDK declarado** (`an industry-standard quantum SDK>=2.6,<3`), atendendo ao checkup Q03 do an industry-standard quantum SDK
  Ecosystem (revisão do PR #1433). Extras de hardware também receberam teto
  (`an industry-standard quantum SDK-aer>=0.17,<0.19`). Sem teto, uma futura 3.x poderia quebrar o pacote
  sem que o metadata avisasse; o cap torna o limite explícito e auditável.

## [2.3.0] - 2026-11-01

### Adicionado
- **Gate de memoria do ruido no runtime** (`require_memory_check`). Antes de gastar
  oraculo, o runtime roda a medida BLP em modelo de colisao (ancora reaproveitada vs
  ancoras frescas). Revival de distancia de traco acima da banda => `REFUSED` com motivo
  `NOISE_HAS_MEMORY`, porque a independencia das amostras — axioma de toda banda
  Hoeffding da casa — deixou de valer. A recusa tambem sai selada (SHA3-256) e o recibo
  carrega o gate inteiro.
- `memory_revival_gate()` no nucleo (`zyql_quantum_gate`): D(k), deltas, banda,
  `noise_has_memory`, `control_anomaly` e validacao de instrumento por D(0).
- Protocolo de auditoria passa a declarar a hipotese de independencia como **testada**
  quando o gate roda, em vez de apenas assumida.
- `tests/test_memory_gate.py`: 6 testes falsificaveis (deteccao, determinismo por seed,
  recusa sem gasto de oraculo, compatibilidade com o comportamento antigo, recibo
  selado e declaracao no protocolo).

### Base empirica
Rodada I (the provider_marrakesh, job `internal`): revival 0.2382 contra banda 0.0520
(4.6x), controle sem revival (0.0209) — memoria detectada em silicio real.

## [2.2.1] - 2026-10-31

### Alterado
- **Relicenciamento para Apache-2.0.** O código passa de MIT para Apache-2.0, que concede
  licença explícita de patentes — requisito prático em computação quântica, onde circuitos
  e algoritmos são densos em patentes. A tese companheira permanece CC BY-NC-ND 4.0.
  Autoria preservada em `NOTICE`. Decisão do detentor do copyright (SerenaSolutions).

## [2.2.0] - 2026-10-31

### Adicionado
- `Q-ROUTE`: busca quantica de rotas dentro da linguagem, executada em QPU real
  (`the provider_kingston`, job `internal`) com recibo de hardware.
- `ZYQL Quantum Console`: interface do Q-ROUTE com execucao em QPU.

### Experimentos (rodadas seladas)
- Rodada D (matriz de reprodutibilidade em 3 QPUs): fechada, 6 jobs DONE
  (`the provider_fez` + `the provider_marrakesh`), vereditos identicos entre as QPUs.
- Rodada I (gate de memoria do ruido, medida BLP): protocolo pre-registrado antes
  do disparo; revival de distancia de traco na variante com memoria
  (0.2382 vs banda 0.0520, 4.6x a banda) e ausencia de revival no controle sem
  memoria (0.0209 <= banda). Veredito `1: MEMORIA DETECTADA` em `the provider_marrakesh`
  (job `internal`), com a consequencia declarada: a banda Hoeffding
  nao e automaticamente valida nessa profundidade de dispositivo.

### Corrigido
- Alinhamento de versao: `pyproject.toml` estava em 2.2.0 enquanto README e
  CHANGELOG seguiam em 2.1.1 (guard `test_meta` acusava CI vermelho no `main`).

## [2.1.1] - 2026-10-30

### Corrigido
- Empacotamento: `py-modules` no `pyproject.toml` listava 12 modulos e deixava de fora
  12 outros, incluindo `zyql_witness`, `zqea_sig`, `zqea_kem`, `zyql_worldscale`,
  `zyql_world3`, `zyql_auditkit`, `zyql_another quantum SDK` e `shot_auditor`. O wheel publicado como
  2.1.0 saiu incompleto; este release publica o conjunto correto (32 arquivos).
- Divergencia de versionamento: a tag `v2.1.0` (`37fbf74`) continha a lista antiga de
  modulos e nao estava no historico do `main`. Em vez de reescrever tag publicada,
  a versao 2.1.1 publica o estado correto e a tag passa a coincidir com o PyPI.
- `license` migrado para PEP 639 (`license = "MIT"` + `license-files`).
- `zyql_rag_layer.bm25_rank` aceita documentos como `str` ou `{"text": ...}` e levanta
  `ValueError` explicito, em vez de `TypeError` opaco.

### Adicionado
- `src/zqea_sig.py`: autoria pos-quantica de recibos (ML-DSA-44, FIPS 204) e cadeia
  `prev_sha3` com deteccao de elo alterado ou removido.
- `src/zyql_witness.witness_from_counts`: regra unica de abstencao (Hoeffding) para
  qualquer distribuicao, nao so a familia Deutsch-Jozsa.
- `tests/test_modulos_orfaos.py` (16 assercoes), `tests/test_qasm3.py` (24),
  `tests/test_zqea_sig.py` (8).
- `tools/verificar_publicacao.py` e workflow de verificacao de publicacao.
- `notebooks/world3-trivalent-verdicts.ipynb`: rodada WORLD-3 executavel, com
  verificacao de selo, intervalos de 95% e veredito trivalente.

## [2.1.0] - 2026-10-24

### Adicionado (RODADA H: bateria adversarial de alta complexidade, pensada
como o cientista hostil que submetera a linguagem; 15 testes falsificaveis)
- **zyql_robust.py — guardas adversariais nativos, primeira fonte**:
  H1 correlacao entre shots (Hoeffding 1963 exige independencia: recusa
  CORRELATED_SHOTS antes de invocar a margem); H2 pre-registro selado
  (SHA3-256 do protocolo canonico; peeking de epsilon pos-hoc =>
  REFUSED PROTOCOL_TAMPERED); H3 kernel concentrado pelo ruido global
  (depolarizante leva K ao valor uniforme 2^-n: PSD passa, informacao
  morreu — recusa KERNEL_CONCENTRATED); H4 honestidade da truncagem MPS
  (erro relativo acima do orcamento => REFUSED TRUNCATION_EXCEEDS_BUDGET,
  numero truncado nao e medida).
- **zyql_llm_compress.py — compressao tensorial de pesos (TT/SVD),
  fonte primaria (Oseledets 2011; Novikov 2015; Sainath 2013)**: veredito
  TERNARIO da compressao — COMPRESSED com erro e ratio declarados /
  REFUSED NO_STRUCTURE (sem rank baixo: comprimir e apagar informacao) /
  REFUSED TRUNCATION_EXCEEDS_BUDGET. Primeiro passo honesto rumo a
  compressao de LLMs dentro do runtime ZYQL (autonomia com pesos locais);
  re-treino pos-compressao e limites DECLARADOS como roadmap, sem fake.
- **tests/test_rodada_h.py + test_llm_compress.py**: 15 testes, cada um
  construido para FALHAR se a protecao sumir; curva de decaimento do
  gradiente medida (n=6/8/10 a L fixo, McClean 2018) com veredito
  consistente com o limiar em toda a grade.
- **experiments/rodada_h_spec.md**: especificacao dos jobs de QPU para o
  confronto da Rodada H em silicio the provider (pronta para execucao quando as
  credenciais estiverem ativas na sessao).

### Testes
- Suite: 65/65 verde (50 da v2.0.0 + 15 da Rodada H), zero dependencia
  externa nova (numpy + crypto stdlib apenas).

## [2.0.0] - 2026-10-24

### Adicionado (fronteiras da IA quantica europeia, implementadas NATIVAS,
da fonte primaria da ciencia — papers originais, zero codigo copiado)
- **zyqml_core.py — QML trivalente**: simulador statevector proprio, ansatz
  em anel RY+CZ, gradiente por parameter-shift EXATO (Schuld/Mitarai 2018-19),
  e o veredito TERNARIO do treino: 1=TRAINABLE / REFUSED(GRADIENT_VANISHED)
  quando a variancia do gradiente sinaliza barren plateau (McClean 2018) /
  REFUSED(DEPTH_EXCEEDS_BUDGET). Onde o mundo detecta o plateau e sofre,
  o nucleo RECUSA O TREINO com motivo rastreavel — semantica inedita.
  Kernels quanticos K(x,y)=|<psi(x)|psi(y)>|^2 com PSD provado pelo teorema
  do produto de Schur (Schuld & Killoran 2019).
- **zyql_zne.py — mitigacao de erro antes da recusa**: extrapolacao a ruido
  zero por interpolacao de Richardson (Temme 2017, Li & Benjamin 2017),
  nativa e framework-free. Veredito ternario: MITIGATED com residuo honesto
  OU REFUSED(EXTRAPOLATION_ILL_CONDITIONED) pelo guard leave-one-out —
  o chute embalado nunca e vendido como mitigacao. Pipeline da porta:
  ZNE -> GHZ gate -> veredito.
- **zyql_mps.py — simulador MPS quebra o limite n<=8 declarado**: produto de
  estados de matriz com truncagem Schmidt/SVD por elo (Vidal 2003-04,
  Schollwoeck 2011), escalando O(n·d·chi^2). GHZ n=12 exato com chi=4 no
  teste. LIMITACAO DECLARADA: portas 1q e 2q VIZINHAS; oraculos diagonais
  globais ficam fora ate a rota ancilla. Truncagem sempre declarada.
- **tests/test_frontiers.py — 9 testes falsificaveis**: parameter-shift vs
  finite difference; plateau profundo vs raso; kernel PSD (e detector pega
  matriz destruida); ZNE mitiga ruido moderado E RECUSA ruido severo; MPS
  exato em n=12, cross-validado contra o statevector independente, recusa
  porta nao-vizinha com erro declarado.

### Pendente (declarado, sem fake)
- QNLP (estilo lambeq) e modo analogico (estilo Pasqal): roadmap — exigem
  decisao de design da linguagem, nao ficou pronto hoje. Nao reivindicado.
- Decodificador QEC em tempo real (estilo Riverlane): a rota natural e o
  decode por sindrome ja validado na Rodada F-rev, elevado a streaming.

## [1.9.1] - 2026-10-24

### Adicionado (auditoria adversarial — resposta ao auditor externo e RFC #36)
- **Correcao de testes multiplos (Bonferroni, direcao correta)**:
  `adaptive_margin_family(epsilon, shots, family)` => banda
  m' = 2*m(eps) - m(eps/k); a banda ENCOLHE com a familia, protegendo
  a mesma zona do teste unico com erro de familia <= epsilon.
  `run_quantum(..., family=k)` e `decide(..., family=k)`.
  Familia grande demais para os shots => RECUSA TUDO
  (refusal_reason=FAMILY_EXCEEDS_SHOTS), nunca risco somado.
  ACHADO PUBLICO DA FALSIFICACAO: a primeira implementacao (alargar a
  banda com eps/k) foi pega pelo proprio teste de Monte Carlo
  (tests/test_multiple_testing.py) e revertida — alargar tornava a
  alegacao de constante MAIS agressiva, direcao errada.
- **Taxonomia de recusa**: toda RECUSA carrega refusal_reason
  (BALANCED_ORACLE | INSIDE_NOISE_BAND | FAMILY_EXCEEDS_SHOTS);
  runtime decide() propaga no Decision e no recibo selado.
- **Registro de protocolo** no recibo (auditoria: epsilon declarado
  ANTES da execucao, shots, regra de parada, comparacoes da familia,
  tratamento do inconclusivo, hipotese de independencia declarada).
- 7 testes falsificaveis novos (tests/test_multiple_testing.py):
  banda encolhe com familia, valores-guia, entrada adversarial,
  controle de risco de familia por Monte Carlo, taxonomia, familia
  no recibo, recusa honesta sob familia absurda.

# Changelog

All notable changes to the ZEPHIRUM language are documented here.

## [1.9.0] - 2026-10-23
### Added — upgrade do algoritmo + Rodada C no silício (semânticas inéditas)
- **Margem adaptativa (Hoeffding inverso)**: `decide(f, epsilon=0.05)` — a banda de confiança
  é DERIVADA do erro máximo declarado; com shots suficientes a banda estreita, sem shots
  o núcleo recusa em vez de mentir. `adaptive_margin(eps, shots)` é API pública.
- **Porta de integridade GHZ** (semântica inédita no GitHub): `decide(..., require_device_trust=True)`
  testa o PRÓPRIO QPU (GHZ_3, fidelidade |000>+|111>) antes de confiar no veredito;
  dispositivo decoerido => REFUSED SEM gastar oráculo, modo `REFUSED_DEVICE_DECOHERED`.
- **Cadeia de proveniência**: recibos do runtime selam o selo do anterior
  (`previous_seal`) + `verify_chain([...])`. Ledger tamper-evidente de rodadas.
- **RODADA C no a production superconducting QPU the provider_kingston** (jobs internal / internal,
  256 shots, epsilon=0.05): porta GHZ fidelidade **0.977 → dispositivo confiável**;
  DJ adaptativo **EXATO**: const-1 p0=0.9922→1, const-0 p0=1.0000→0, balanceado p0=0.0039→REFUSED.
  Recibo ML-DSA-44 **encadeado** no selo da Rodada B: experiments/round_c_receipt.json.
- Lição selada no silício: transpilar com optimization_level=2 no Heron (nível 1 mapeou
  a bateria em qubits ruidosos — primeira tentativa RECUSADA honestamente e refeita).
- 5 testes novos no runtime (11/11): banda adaptativa, vereditos adaptativos, porta GHZ,
  recusa sem oráculo, cadeia tamper-evidente.

## [1.8.0] - 2026-10-23
### Added — resposta à auditoria: "runtime de produção no algoritmo"
- `zyql_runtime`: runtime de PRODUÇÃO do núcleo ZYQL. API estável `decide()->Decision`,
  enum `Verdict` (PERMIT/DENY/REFUSED), validação pré-oráculo (ConfigError), determinismo
  por seed, recibo SHA3-256 opcional por decisão (verificável offline), thread-safe,
  zero prints no caminho da lib. Throughput local: ~3.4k decisões/s (n=3).
- CLI `zyql-decide` (console script) + `python -m zyql_runtime`.
- `docs/MATURITY.md`: declaração oficial de maturidade POR COMPONENTE (produção/beta/
  experimental/legacy) com limites explícitos — fim da ambiguidade "protótipo de pesquisa".
- `tests/test_runtime.py`: matriz de vereditos, determinismo, validação pré-oráculo,
  recibo selado→verificado→adulterado→recusado, honestidade do limite de erro, stress 200 decisões.

## [1.7.5] - 2026-10-23
### Fixed
- Badge de versão do README desatualizada (1.6.0) — agora 1.7.5, em sincronia com `pyproject.toml`.
- CI e Makefile agora executam TODOS os testes (`test_canonical.py` + `test_zqea_verify.py`), não apenas o canônico.

### Added
- `tests/test_meta.py`: meta-teste de consistência de versão (pyproject = badge README = CHANGELOG). O mismatch apontado em auditoria externa não pode mais voltar a acontecer despercebido.
- Packaging corrigido para distribuição PyPI: `package-dir = src` + `py-modules` com TODOS os módulos da linguagem (`zquantum`, `zkernel`, `quantum_types`, `zyql_lisp`, `zyql_quantum_gate`, `zyql_rag_layer`, `battery_ci`, `oq3`) + pacote `zqgate` (CLI). Antes, `pip install zephirum` entregaria apenas o CLI antigo, sem a linguagem.

## [1.7.4] - 2026-10-23
### Added
- **Rodada B executada — lacuna de shots baixos FECHADA**: bateria Deutsch-Jozsa n=3 trivalente no a production superconducting QPU `the provider_kingston` (conta independente, backend distinto da Rodada A) em 64, 128, 256 e 384 shots. Vereditos trivalentes (1/0/REFUSED) **EXATOS em todos os níveis**, inclusive 64 shots (abaixo da previsão teórica de 82). Protocolo Estatístico ZYQL agora validado em hardware no intervalo completo [64, 16384] shots. Recibo ML-DSA-44 + entropia quântica: `experiments/round_b_receipt.json` (veredito `RODADA_B_VERIFICADA_TRIVALENTE_EXATO`).
- Scripts da rodada no repositório: `experiments/round_b_battery.py` (submissão) e `experiments/round_b_analyze.py` (análise + selagem v2).
- Documentação atualizada: `docs/ZYQL_STATISTICAL_PROTOCOL.md` (seção Rodada B + proposta concluída), `docs/PROOFS.md` (índice de evidências com a lacuna fechada).

## [1.7.3] - 2026-10-22
### Added
- Validação do Protocolo Estatístico ZYQL em Hardware Real (a production superconducting QPU `the provider_fez`, Rodada A): sweep de 512 a 16384 shots no Deutsch-Jozsa $n=3$ trivalente com 100% de acerto (3/3 casos em todos os 6 níveis), zero recusa espúria e $p(000) \ge 0.9977$ para constantes / $\le 0.0024$ para balanceado. Veredicto **VALIDADO** no intervalo [512, 16384] com recibo selado SHA3-256 (`experiments/refusal_receipt.json`).
- Documentação da lacuna aberta abaixo de 512 shots em `docs/ZYQL_STATISTICAL_PROTOCOL.md` e proposta da Rodada B (sweep 16..256 shots).
- Atualização do índice de provas de conceito em `docs/PROOFS.md` (seção do problema com links para `docs/PROBLEM.md` e `experiments/refusal_receipt.json`).

## [1.7.2] - 2026-10-21
### Added
- Problem solved: minimum shots for reliable trivalent decisions measured on a production superconducting QPU the provider_fez (Rodada A, 18/18 correct at 512..16384, protocol VALIDADO) — docs/PROBLEM.md, docs/ZYQL_STATISTICAL_PROTOCOL.md §6, experiments/refusal_receipt.json (sealed)
- Hello World canônico da linguagem: forma `(hello)` no núcleo Lisp, exemplo `examples/hello_world.zph` selado (Z-QEA).

## [1.7.2] - 2026-10-21
### Added
- Rodada 6 — HARDWARE REAL (a production superconducting QPU the provider_marrakesh, job internal,
  512 shots, laboratório próprio): bateria ZYQL completa no silicio — DJ
  trivalente (1/0/REFUSED), palavras de tracado S3 (B_R B_S)^2 -> |01> vs
  (B_S B_R)^2 -> |10> — divergencia nao-abeliana medida no hardware — e Grover
  n=2. Todos os 6 circuitos dentro da banda de ruido declarada (desvio max 0.045).
  Recibo selado: experiments/round6_hardware_receipt.json (veredito HARDWARE_OK).
- Produto zy-ai-rag (SerenaSolutions/zy-ai-rag, v1.0.0): decisao trivalente de IA
  para CI — BM25 + tradutor LLM opcional (Gemini) + portao quantico ZYQL, recibo
  Z-QEA. Modos declarados: LLM ou OFFLINE.

## [1.7.1] - 2026-10-21
### Added
- ZYQL Lisp interpreter (src/zyql_lisp.py) + photonic layer: programs written
  IN the language (.zph) execute against an exact photonic Fock simulator
  (numpy/scipy, cutoff 10, no shots, no hardware, declared honestly).
- Round 5 photonic lab (experiments/round5_photonic_receipt.json, sealed):
  HOM bunching p(1,1)=0 exact; Mach-Zehnder deterministic exit with port
  switching at phase pi; ZYQL trivalent decision ON photonic dual-rail qubits
  (const-0 => 0, const-1 => 1, balanced => REFUSED, 1 oracle call); SU(2)
  beam-splitter rotations: order matters (photonic analog of the braid
  signature). Photonic Hadamard verified exact: BS50 . phase(pi/2) . BS50
  = e^{-i pi/4} H.

## [1.7.0] - 2026-10-21
### Changed
- ZYQL v2 syntax: Lisp-style s-expressions replace the Python-style surface
  (owner decision 2026-10-21). Core is the ZeptonQL trivalent decision —
  declared NOT quantum; quantum execution is an optional explicit layer.
  Spec: docs/ZYQL_LISP_SPEC.md; examples: examples/*_lisp.zph;
  .zph now highlights as Lisp on GitHub (.gitattributes, linguist-language=Lisp,
  mapping to be dropped once Linguist registers ZEPHIRUM natively).
- VS Code grammar updated to the v2 s-expression syntax.

### Added
- Rodada 4 (noiseless, statevector, sealed): experiments/round4_derived.py +
  round4_derived_receipt.json — C11 Grover n=3 (matches theory to 9 decimals),
  C12 DJ n=6 trivalent (1/0/REFUSED exact), C13 GHZ-5 parity, C14 QFT-3
  roundtrip, C15 receipt registry sweep (6 receipts INTEGRAL), C16 Z-ANYON LAB:
  non-Abelian braid battery (commutator L1 = 6, |11> veto exact, period-3 echo
  verified) — NAO_ABELIANO_VERIFICADO.
- Marketplace product line (derived, all ZeptonQL/Z-QEA based):
  zqea-verify (live), z-anyon-lab, zq-gate, zqea-seal — see docs/MARKETPLACE.md.

## [1.6.0] - 2026-10-21
### Added
- docs/PROBLEM.md: dossier da expedição científica sobre a confiabilidade da decisão trivalente ZYQL em hardware quântico real (shots mínimos empíricos, calibração do REFUSED e hipóteses H1/H2).
- S3 qutrit miniature (experiments/): braiding non-commutativity and 3-channel
  fusion space (qutrit-in-qubits), noiseless with exact-zero deviation vs theory
  (canonical rational arithmetic) and verified on real hardware: a production superconducting QPU
  the provider_fez, jobs internal and internal; full ZYQL
  trivalent battery 3/3 PASS on hardware (receipt sealed in
  experiments/s3_qutrit_full_receipt.json). Scientific sweep of 26 circuits
  (job internal) submitted; harvest pending.
- Packaging: pyproject.toml — `pip install -e .` exposes zkernel, zquantum,
  zyql_quantum_gate, quantum_types, zyql_rag_layer, oq3 as installable modules.
- docs/AUDIT.md: external audit record (GitHub Copilot audit, 2026-10-21) with
  our validation, findings and remediation status.
- docs/ROADMAP.md: public roadmap (compiler, type layer, benchmarks, FIPS 204).
- docs/PARTNERSHIP.md: GitHub partnership dossier.
- GitHub Pages deployment via GitHub Actions (site/).

- a differentiable quantum SDK cross-check (experiments/chemistry/a differentiable quantum SDK_crosscheck.py):
  H2 VQE reproduces the battery FCI reference -1.13730604 Ha with error
  4.2e-09 (convention documented: a differentiable quantum SDK default unit is bohr; battery
  geometry is angstrom). Receipt sealed.
- New .zph examples: s3_qutrit.zph (fusion-space miniature), chemistry_h2.zph.
- .gitattributes: honest Linguist stats (receipts generated, assets vendored).
- docs/PROOFS.md: public index of proofs of concept (S3 non-Abelian
  miniature front and center) + proofs section on the Pages site.
- Scientific sweep harvested (job internal, 26 circuits): braid
  angle sweep 10/10 dominant channels correct, non-Abelian window measured at
  theta/pi in [0.3,0.7]; braid-word period 6/6; Pauli error map exact.
  chi-square (4096 shots) fails in all points due to sub-1% uncalibrated
  readout bias — declared honestly; TV <= 4.5%. Master receipt re-sealed
  (C7). Data figure updated with all 10 measured points.
- Z-QEA Receipt Verifier (GitHub Action, Marketplace candidate):
  `.github/actions/zqea-verify` — recomputes the SHA3-256 seal of any receipt
  JSON; INTEGRAL passes the job, a broken seal fails it. Tested both ways
  (tests/test_zqea_verify.py).
- Seal rule upgrade: master receipt re-sealed with the clean canonical rule
  (seal = SHA3-256 over the receipt with the seal field removed —
  self-contained verification, no history chaining). Documented in the
  receipt itself (field selo_regra). New master seal: a4419246...
- docs/MARKETPLACE.md: GitHub Marketplace listing plan (free verifier,
  hosted tier later). Site: sponsor page with declared tiers.
- Sponsor button live: .github/FUNDING.yml (GitHub "Sponsor" on the repo
  points to the tier page); Stripe products/prices created for the three
  tiers ($5/$25/$100 monthly), checkout flow validated in test mode.
- Scientific sweep v2 HARVESTED (job internal, 30 circuits with
  readout calibration): mitigated chi-square passes 18/20 (raw v1: 0/10),
  dominant channels 20/20, measured readout fidelity 94.6-97.6%. Hypothesis
  CONFIRMED: the v1 chi-square failure was readout bias (instrument), not
  physics. Receipt sealed (scientific_sweep2_receipt.json).
### Fixed
- Broken README quickstart: `from src.zyql_quantum_gate import ...` failed
  (sys.path.insert pointed at repo root, not src/). Modules now use a
  deterministic in-tree fallback and work installed or from source.
- Topics: removed typo tag `betta`.

## [1.5.0] - 2026-10-20
### Added
- Chemistry battery (experiments/chemistry): H2, LiH, H2O, NH3 — Jordan-Wigner
  mapping reproduces PySCF FCI exactly in all four molecules (error 0 / < 1e-10),
  battery receipt 85c20bc9. Nature-derived molecules through the full pipeline.
- Formal statistical protocol (docs/ZYQL_STATISTICAL_PROTOCOL.md): noise band
  d=0.15, binomial error bounds, minimum-shots formula, drift validity window.
- REFUSED formal spec (docs/ZYQL_REFUSED_SPEC.md): six triggers (R1-R6),
  bounded cost model (never consumes QPU), anti-DoS analysis, own receipt type.
- External audit response (docs/AUDIT_RESPONSE_2026-10-19.md): secrets scan
  clean over full history, dependencies locked (requirements-lock.txt).
### Changed
- Receipts documentation: SHA3-256 integrity seal is the implemented label;
  ML-DSA-44 (FIPS 204) signatures are a declared roadmap item (honest labeling).

## [1.4.3] - 2026-10-12
### Added
- `qif` quantum conditional (controlled-X decomposition, no collapse) - verified: Bell 1/2+1/2.
- First-class quantum types (`qbit`/`zyqbit`) with static no-cloning rejection.
- Native neural statement `zyql_rag`: docs -> BM25 -> translator -> interference gate -> receipt.
- Hardware confrontation vs textbook an industry-standard quantum SDK (job internal, the provider_fez): depth 2 / 0 two-qubit gates vs depth 10 / 3 CZ, both decide correctly.

## [1.0.0] - 2026-10-11
### Added
- Trivalent Deutsch-Jozsa decision gate with declared noise band (+-0.15).
- Z-QEA certificates with canonical rational arithmetic.
- ML-DSA-44 (FIPS 204) receipt sealing.
- a production superconducting QPU lab bridge (verified ingestion: job internal).

## [0.3.0] - 2026-10-10
### Added
- Hybrid Stack (5 layers), RX/RY/RZ/SWAP/Toffoli, Pauli Monte Carlo noise.
- OpenQASM 3 round-trip import/export verified against the reference parser.

## [0.2.0] - 2026-10-09
### Added
- Zephyron -> OpenQASM 3 transpiler; state-vector kernel [re,im] float64.

## [0.1.0] "Ausra Bridge" - 2026-10-07
### Added
- State-vector kernel, parser (12 gates), Bell/GHZ/Grover/QFT verified.

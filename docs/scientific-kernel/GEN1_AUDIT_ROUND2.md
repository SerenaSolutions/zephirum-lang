# Auditoria Gen 1 — rodada 2 (somente leitura)

**Repositório:** `SerenaSolutions/zephirum-lang`  
**Branch solicitada:** `feat/gen1-scientific-kernel-baseline`  
**Revisão efetivamente resolvida pelos leitores de arquivo:** `642074c33de2f6a065a9a30098fcacc48d07c020`  
**Data declarada pelo commit:** 2026-11-25 15:04:25 UTC  
**Escopo:** inspeção estática e proposta de RFC. Nenhum código, teste, contrato público ou formato de recibo foi modificado nesta rodada.

## 0. Integridade e proveniência da auditoria

### VERIFICADO

- A API de arquivo, ao receber `ref=feat/gen1-scientific-kernel-baseline`, resolveu os arquivos consultados para o commit `642074c33de2f6a065a9a30098fcacc48d07c020`. Exemplos: `src/zyql_runtime.py`, `src/qroute/hardware.py`, `src/zephirum/adapters/qiskit_backend.py` e `api/chat.py` retornaram esse `CommitOID`.
- O endpoint de commit do GitHub confirma o commit `642074c33de2f6a065a9a30098fcacc48d07c020`, cuja mensagem é `docs: configure Gen 1 agent workstreams and governance`, e cujo pai é `2f08acd80670a382d1cde5c607e404e68d2d5b8b`.
- O pai `2f08acd80670a382d1cde5c607e404e68d2d5b8b` é `docs: add initial Scientific Kernel Gen 1 audit baseline`, cujo pai é o commit-base `880d567f42542c2a8c4114aec013f751940126c3`.
- Portanto, o commit informado `642074c...` está na cadeia de commits observada entre o baseline e o commit-base `880d567...` (direção ancestral: `880d567` → `2f08acd` → `642074c`).

### Limitação de resolução

A ferramenta GitHub desta sessão não suportou uma consulta direta à ref `/branches/feat/gen1-scientific-kernel-baseline` nem ao endpoint REST de comparação. A revisão foi vinculada ao commit retornado pelo `getfile` quando a ref da branch foi usada; o resultado não deve ser interpretado como uma observação atômica de HEAD se a branch for atualizada depois da consulta. Para reproduzir a identificação do commit, abra um dos links de arquivo abaixo e confira o SHA no permalink.

### Arquivos examinados e blob SHAs

| Caminho | Blob SHA observado | Evidência por permalink ao commit auditado |
|---|---|---|
| `src/zyql_runtime.py` | `91ca07b0d757dc891cd5eea96a449d6662faa216` | [arquivo](https://github.com/SerenaSolutions/zephirum-lang/blob/642074c33de2f6a065a9a30098fcacc48d07c020/src/zyql_runtime.py) |
| `src/zyql_quantum_gate.py` | `5668204ca6bd7206b8ad9a0bf1b35e29aa246c7a` | [arquivo](https://github.com/SerenaSolutions/zephirum-lang/blob/642074c33de2f6a065a9a30098fcacc48d07c020/src/zyql_quantum_gate.py) |
| `src/zquantum.py` | `35e9287ce498ba2456ee4e050d7902176267ca76` | [arquivo](https://github.com/SerenaSolutions/zephirum-lang/blob/642074c33de2f6a065a9a30098fcacc48d07c020/src/zquantum.py) |
| `src/qroute/core.py` | `8ef6b7061b61f2dba53c214033ecef8e7aad804d` | [arquivo](https://github.com/SerenaSolutions/zephirum-lang/blob/642074c33de2f6a065a9a30098fcacc48d07c020/src/qroute/core.py) |
| `src/qroute/graph.py` | `6c49ad394d795ba6826f2c6bc60e67c995d63a98` | [arquivo](https://github.com/SerenaSolutions/zephirum-lang/blob/642074c33de2f6a065a9a30098fcacc48d07c020/src/qroute/graph.py) |
| `src/qroute/grover.py` | `122d544c2732e8bab9240c694c85e45d67d7784e` | [arquivo](https://github.com/SerenaSolutions/zephirum-lang/blob/642074c33de2f6a065a9a30098fcacc48d07c020/src/qroute/grover.py) |
| `src/qroute/hardware.py` | `48e72c7bb0c4141f677e5d6a799aeb603f072125` | [arquivo](https://github.com/SerenaSolutions/zephirum-lang/blob/642074c33de2f6a065a9a30098fcacc48d07c020/src/qroute/hardware.py) |
| `src/qroute/receipt.py` | `b75eceffa36eec297bd116414f483dd8f54759c5` | [arquivo](https://github.com/SerenaSolutions/zephirum-lang/blob/642074c33de2f6a065a9a30098fcacc48d07c020/src/qroute/receipt.py) |
| `src/zephirum/adapters/qiskit_backend.py` | `c9a65862ecbe68e68b8397185c9304c660e43a4b` | [arquivo](https://github.com/SerenaSolutions/zephirum-lang/blob/642074c33de2f6a065a9a30098fcacc48d07c020/src/zephirum/adapters/qiskit_backend.py) |
| `src/zephirum/adapters/qbraid_backend.py` | `ecdcaaebddd9c54fb0967c57d969b12c4402899f` | [arquivo](https://github.com/SerenaSolutions/zephirum-lang/blob/642074c33de2f6a065a9a30098fcacc48d07c020/src/zephirum/adapters/qbraid_backend.py) |
| `src/zephirum/adapters/cudaq_backend.py` | `2eb4a67352105fcc3889602c36f3cf72fe0f4683` | [arquivo](https://github.com/SerenaSolutions/zephirum-lang/blob/642074c33de2f6a065a9a30098fcacc48d07c020/src/zephirum/adapters/cudaq_backend.py) |
| `src/zqea_canon.py` | `75f1526cbaee1d03223670c165f563a88328a0c9` | [arquivo](https://github.com/SerenaSolutions/zephirum-lang/blob/642074c33de2f6a065a9a30098fcacc48d07c020/src/zqea_canon.py) |
| `src/zqea_sig.py` | `9c95ef756c86e12e113727ecef057aad39803e28` | [arquivo](https://github.com/SerenaSolutions/zephirum-lang/blob/642074c33de2f6a065a9a30098fcacc48d07c020/src/zqea_sig.py) |
| `zysdk/client.py` | `d3b4606d7d042d2b589f1dd67f2917f96a6c0c4f` | [arquivo](https://github.com/SerenaSolutions/zephirum-lang/blob/642074c33de2f6a065a9a30098fcacc48d07c020/zysdk/client.py) |
| `zyql_science/motor.py` | `06326d50834a3a7e21eae1a0195c29ba4df93fce` | [arquivo](https://github.com/SerenaSolutions/zephirum-lang/blob/642074c33de2f6a065a9a30098fcacc48d07c020/zyql_science/motor.py) |
| `src/zyql_ten/s06_compute_router.py` | `f24b004b94fde0d0adbe5cf27840a4570004a2c5` | [arquivo](https://github.com/SerenaSolutions/zephirum-lang/blob/642074c33de2f6a065a9a30098fcacc48d07c020/src/zyql_ten/s06_compute_router.py) |
| `src/zyql_ten/s08_scientific_verification.py` | `51968cb38fd425cc31f23b558e99ff9a1221b991` | [arquivo](https://github.com/SerenaSolutions/zephirum-lang/blob/642074c33de2f6a065a9a30098fcacc48d07c020/src/zyql_ten/s08_scientific_verification.py) |
| `cpp/zyql_verdict.cpp` | `8c9c915bd577206b7852da859a52312fc1fad31b` | [arquivo](https://github.com/SerenaSolutions/zephirum-lang/blob/642074c33de2f6a065a9a30098fcacc48d07c020/cpp/zyql_verdict.cpp) |
| `tests/test_runtime.py` | `d094116035bb3956557f9d25463134c1a9742ad0` | [arquivo](https://github.com/SerenaSolutions/zephirum-lang/blob/642074c33de2f6a065a9a30098fcacc48d07c020/tests/test_runtime.py) |
| `tests/test_zyql_ten.py` | `5d4743662d35282fa6d83a5ad9f7780d03e56603` | [arquivo](https://github.com/SerenaSolutions/zephirum-lang/blob/642074c33de2f6a065a9a30098fcacc48d07c020/tests/test_zyql_ten.py) |

A tabela não é um hash-manifesto do repositório inteiro; limita-se aos arquivos diretamente citados nesta auditoria.

## 1. Inventário complementar

### `src/qroute/`

**VERIFICADO:** `__init__.py`, `cli.py`, `core.py`, `graph.py`, `grover.py`, `hardware.py`, `receipt.py` e `maps/` existem na branch. `core.decide` usa avaliação clássica do grafo, calcula Grover e decide `1`/`0`/`REFUSED`; `core.executa` pode chamar `hardware.executa` ou `dry_run` e emite recibo se `seal_path` for fornecido. Fontes: [`core.py#L25-L58`](https://github.com/SerenaSolutions/zephirum-lang/blob/642074c33de2f6a065a9a30098fcacc48d07c020/src/qroute/core.py#L25-L58), [`core.py#L61-L106`](https://github.com/SerenaSolutions/zephirum-lang/blob/642074c33de2f6a065a9a30098fcacc48d07c020/src/qroute/core.py#L61-L106), [`graph.py#L22-L80`](https://github.com/SerenaSolutions/zephirum-lang/blob/642074c33de2f6a065a9a30098fcacc48d07c020/src/qroute/graph.py#L22-L80), [`grover.py#L13-L36`](https://github.com/SerenaSolutions/zephirum-lang/blob/642074c33de2f6a065a9a30098fcacc48d07c020/src/qroute/grover.py#L13-L36), [`hardware.py#L103-L147`](https://github.com/SerenaSolutions/zephirum-lang/blob/642074c33de2f6a065a9a30098fcacc48d07c020/src/qroute/hardware.py#L103-L147).

**VERIFICADO:** `hardware.executa` consulta IBM Runtime, escolhe backend físico operacional quando não é especificado, transpila/submete e retorna job ID e contagens; `dry_run` usa `FakeMarrakesh` + Aer e retorna `job_id=None`, rotulado como ensaio, não QPU. Isso prova que o caminho de código existe, não que foi executado nesta auditoria. O arquivo também imprime aviso com nome da variável de token e tipo de exceção; não foi observada impressão do valor do token nas linhas examinadas.

**VERIFICADO:** `receipt.sela` cria `prev_sha3`, `nonce`, sequência e data; seu verificador delega ao canonicalizador unificado. `verifica_encadeamento` verifica selo, nonce, sequência e elo anterior. Há teste de encadeamento/adulteração em `tests/test_receipt_hardening.py`.

**HIPÓTESE:** Q-ROUTE é um orquestrador por domínio (rotas), não um seletor geral de backend científico. `graph.avalia` enumera rotas e restrições antes de Grover; essa análise não é um certificado formal universal.

### `src/zephirum/adapters/`

**VERIFICADO:** contém `__init__.py`, `qiskit_backend.py`, `qbraid_backend.py` e `cudaq_backend.py`. `__init__.py` exporta apenas `qiskit_backend` na lista `__all__`; os outros módulos são importáveis por caminho, mas não são apresentados ali como adaptadores exportados. [`__init__.py#L9-L15`](https://github.com/SerenaSolutions/zephirum-lang/blob/642074c33de2f6a065a9a30098fcacc48d07c020/src/zephirum/adapters/__init__.py#L9-L15).

- Qiskit: contrato `qubits`/`gates`, validação, construção, `estado_exato`, Aer local com seed e verificação de hash. [`qiskit_backend.py#L64-L105`](https://github.com/SerenaSolutions/zephirum-lang/blob/642074c33de2f6a065a9a30098fcacc48d07c020/src/zephirum/adapters/qiskit_backend.py#L64-L105), [`#L140-L197`](https://github.com/SerenaSolutions/zephirum-lang/blob/642074c33de2f6a065a9a30098fcacc48d07c020/src/zephirum/adapters/qiskit_backend.py#L140-L197).
- qBraid: consulta dispositivos/metadata; submete circuito; retorna `job_id`, device, shots e counts; inclui conversão de portas para conjunto declarado. [`qbraid_backend.py#L22-L101`](https://github.com/SerenaSolutions/zephirum-lang/blob/642074c33de2f6a065a9a30098fcacc48d07c020/src/zephirum/adapters/qbraid_backend.py#L22-L101), [`#L104-L188`](https://github.com/SerenaSolutions/zephirum-lang/blob/642074c33de2f6a065a9a30098fcacc48d07c020/src/zephirum/adapters/qbraid_backend.py#L104-L188).
- CUDA-Q: consulta targets declarados e recusa SDK/target ausente; compõe kernel a partir de subconjunto de operações. [`cudaq_backend.py#L25-L37`](https://github.com/SerenaSolutions/zephirum-lang/blob/642074c33de2f6a065a9a30098fcacc48d07c020/src/zephirum/adapters/cudaq_backend.py#L25-L37), [`#L54-L92`](https://github.com/SerenaSolutions/zephirum-lang/blob/642074c33de2f6a065a9a30098fcacc48d07c020/src/zephirum/adapters/cudaq_backend.py#L54-L92).

**RISCO VERIFICADO:** as interfaces diferem; por exemplo, CUDA-Q `_run_kernel` lê `gate`/`qubit` enquanto validação compartilhada Qiskit espera `op`/`qubits`. A validação pode aceitar um programa cujo campo de execução é ignorado/interpretado como default pelo kernel CUDA-Q. Requer teste de conformidade específico; não foi executado.

### `zysdk/`

**VERIFICADO:** `client.py`, `test_zysdk.py`, `RECEIPT_ZYSDK.json`. Cliente tem `Provedor`, `ProvedorREST`, `ProvedorLocal`, `Contagem`, `ErroDeProvedor`. REST requer HTTPS no construtor e define contrato `/jobs`/`/jobs/{id}`; provedor local aceita callback de simulação. [`client.py#L24-L51`](https://github.com/SerenaSolutions/zephirum-lang/blob/642074c33de2f6a065a9a30098fcacc48d07c020/zysdk/client.py#L24-L51), [`#L54-L133`](https://github.com/SerenaSolutions/zephirum-lang/blob/642074c33de2f6a065a9a30098fcacc48d07c020/zysdk/client.py#L54-L133).

**VERIFICADO:** `test_zysdk.py` inicia servidor HTTP local, subclassa `ProvedorREST` para usar esse servidor, valida fluxo e redaction, e testa simulador callback. O teste não constitui evidência de integração com provedor real nem hardware; “servidor falso: imita contrato, não fornecedor” está explícito no comentário do teste (`#L11-L12`). O teste escreve `RECEIPT_ZYSDK.json` no diretório ao executar (`#L75-L79`), de modo que deve ser executado em workspace limpo/controlado.

### `zyql_science/`

**VERIFICADO:** `__init__.py`, `motor.py`, `areas.py`, `bateria.py`, `APLICACOES.md`, `RECEIPT_SCIENCE.json`, `public_key.txt`. O motor aplica regras de proporção/comparação/energia; representa cinco strings de estado (`1`, `0`, `REFUSED`, `INCONCLUSIVE`, `ERROR`), gera hash SHA3 para `Decisao` e usa epsilon de Hoeffding. [`motor.py#L9-L45`](https://github.com/SerenaSolutions/zephirum-lang/blob/642074c33de2f6a065a9a30098fcacc48d07c020/zyql_science/motor.py#L9-L45), [`#L48-L101`](https://github.com/SerenaSolutions/zephirum-lang/blob/642074c33de2f6a065a9a30098fcacc48d07c020/zyql_science/motor.py#L48-L101).

**VERIFICADO:** `areas.py` encaminha casos de domínio para essas regras, e `bateria.py` cria/valida recibos via um pacote sibling `proofs_m1_s2_c3/authenticity/signed_receipt`; esse mecanismo Ed25519 é distinto de `src/zqea_sig.py` ML-DSA. A bateria cria chaves em execução e usa registro estático `RECEIPT_SCIENCE.json` como artefato versionado.

**RISCO:** o recibo estático declara `signature: null` em `authenticity`, contém um `_signature.value` Ed25519 e campos de tempo fixos; `RECEIPT_HASH` é SHA-256 truncado de parte do objeto (exclui `recibos`). Não presumir que o artefato representa execução reproduzida no commit auditado sem rodar e comparar o gerador/verificador. `bateria.py` usa valores numéricos embutidos nos próprios casos: isso é fixture/demonstração de regra, não evidência de dados experimentais externos.

### `cpp/`

**VERIFICADO:** `Makefile`, `zyql_verdict.cpp`, `zyql_verdict.hpp`. API C exporta `zyql_rota` e `zyql_veredito`. `zyql_rota` retorna 1 clássico, 0 recusado/negado conforme condições e 2 para estado final; header chama códigos “1 clássico, 2 quântico, 0 recusado” para rota e “1 autoriza, 0 nega, 2 recusa” para veredito. [`hpp#L8-L13`](https://github.com/SerenaSolutions/zephirum-lang/blob/642074c33de2f6a065a9a30098fcacc48d07c020/cpp/zyql_verdict.hpp#L8-L13), [`cpp#L8-L22`](https://github.com/SerenaSolutions/zephirum-lang/blob/642074c33de2f6a065a9a30098fcacc48d07c020/cpp/zyql_verdict.cpp#L8-L22).

**RISCO:** `zyql_veredito` não valida NaN/infinito explicitamente; comparações com NaN caem no `return 2` (recusa) por fluxo, mas isso não substitui contrato finito. Para `epsilon` NaN, ambos `epsilon < 0` e `epsilon >= .5` são falsos; então valores p0 poderão determinar 1/0. Teste adversarial necessário. Não foram executados compilador nem testes C++ nesta auditoria.

### `api/`

**VERIFICADO:** `chat.py` expõe função serverless Vercel, chama Responses API da OpenAI, lê `OPENAI_API_KEY` e `OPENAI_MODEL`, valida origem/tamanho/mensagens, limita chamadas por inst��ncia e só registra ferramentas ZYQL allow-listed. [`chat.py#L23-L43`](https://github.com/SerenaSolutions/zephirum-lang/blob/642074c33de2f6a065a9a30098fcacc48d07c020/api/chat.py#L23-L43), [`#L93-L107`](https://github.com/SerenaSolutions/zephirum-lang/blob/642074c33de2f6a065a9a30098fcacc48d07c020/api/chat.py#L93-L107), [`#L130-L208`](https://github.com/SerenaSolutions/zephirum-lang/blob/642074c33de2f6a065a9a30098fcacc48d07c020/api/chat.py#L130-L208).

**VERIFICADO:** `zyql_chat.py` valida allowlist, tipos/limites e força `hardware=False`, `sign=False`; não há execução arbitrária de código na ferramenta. [`zyql_chat.py#L69-L113`](https://github.com/SerenaSolutions/zephirum-lang/blob/642074c33de2f6a065a9a30098fcacc48d07c020/api/zyql_chat.py#L69-L113).

**RISCO:** limitador `_rate` é memória local do processo/serverless; comentário marca como best-effort. Não é rate limiter global. O endpoint depende da origem e proxy de deploy; controles adicionais de provedor devem ser considerados.

### `src/zyql_ten/`

**VERIFICADO:** dez módulos nomeados S01–S10, `native.py`, `qiskit_bridge.py`, `receipt.py`, `versions.py`, `__init__.py`, `__main__.py`. `s06_compute_router.run` escolhe CLASSICO/QUANTICO/REFUSED com base em solução clássica, flag estrutural, profundidade transpilation e orçamento; o módulo calcula custo Qiskit antes de devolver a rota. Não é um certificado matemático genérico. [`s06_compute_router.py#L7-L32`](https://github.com/SerenaSolutions/zephirum-lang/blob/642074c33de2f6a065a9a30098fcacc48d07c020/src/zyql_ten/s06_compute_router.py#L7-L32).

**VERIFICADO:** `s08_scientific_verification.run` compara probabilidades de circuitos `Statevector` com runtime `decide()`, repetindo chamadas para reprodutibilidade; classifica “evidencia” 1/0/REFUSED. Esse caminho usa comparação de duas implementações/cálculo, não um certificado independente que, antes de executar, prove que execução é dispensável. [`s08_scientific_verification.py#L11-L42`](https://github.com/SerenaSolutions/zephirum-lang/blob/642074c33de2f6a065a9a30098fcacc48d07c020/src/zyql_ten/s08_scientific_verification.py#L11-L42).

**VERIFICADO:** `tests/test_zyql_ten.py` cobre rotas, statevector/callable cross-check e C++ condicional; função do teste usa `skip` se biblioteca nativa não estiver compilada. Existência do teste não prova que ele passou nesta auditoria.

## 2. Auditoria Proof → Decision → Compute

### VERIFICADO

- `zyql_runtime.decide`: `_validate` precede gates; gates opcionais GHZ/memória são cálculos/simulações locais no fluxo importado; então cria gate, amostra circuito e toma decisão. Linhas 76–160 de `src/zyql_runtime.py`. A saída é uma decisão baseada em interferência/estimativa e condições declaradas, não em certificado formal geral verificado antes da execução.
- `qroute.core.decide`: primeiro enumera caminhos clássicos e avalia custo/risco/evidência declarada (`graph.avalia`), depois calcula probabilidade teórica de amplificação (`grover.amplitude_calls`), e então retorna veredito. `core.executa` só submete hardware se `hardware=True` explícito; se `dry=True`, usa simulador fake claramente rotulado. Isso é um pipeline com análise/roteamento antes de execução física opcional, mas não demonstra prova formal geral.
- `zyql_ten.s08_scientific_verification`: usa `Statevector` para baseline e chama `decide()` para comparação, com repetição. O código representa comparação entre métodos, não prova independente que antecede a computação que valida.
- `zyql_science.motor`: valida domínio básico/contagens, calcula epsilon e classifica dados; não implementa verificação de certificado matemático externo.
- `zqea_sig.verificar` verifica assinatura em bytes canonizados e `verificar_ancora` verifica cadeia/âncora. Isso verifica autenticidade/integridade sob a chave declarada, não prova o teorema ou resultado científico contido no recibo.

### Conclusão auditável

**VERIFICADO:** não encontrei, nos caminhos acima, Proof Engine geral que valide certificado aplicável antes de selecionar/executar o cálculo. Há validação prévia de entrada, checks de contrato/capacidade e referências clássicas/numéricas. Não devemos chamar essas atividades indistintamente de prova formal.

**HIPÓTESE:** a expressão “Proof → Compute” deve ser implementada inicialmente como políticas específicas por operação: um certificado verificável pode eliminar ou autorizar uma computação determinada; a ausência de certificado pode seguir para modo experimental se expressamente permitido, mantendo estado epistêmico separado.

**PROPOSTA:** RFC define `ProofEvidence` como evidência opcional/proveniente de verificador identificado e vincula exatamente operação, entradas e hipótese; sem resultado de prova, o executor não presume falsidade nem sucesso, e política escolhe `REFUSED` ou execução experimental autorizada.

## 3. Semântica adversarial dos estados

### Fatos de código

`Verdict` herda de `Enum`, não `IntEnum`; valores são `1`, `0`, `
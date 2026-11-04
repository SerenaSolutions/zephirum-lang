# ZYQL Conformance Spec — v1.1.0

Contrato normativo do núcleo de decisão trivalente ZYQL. Uma implementação é
**conformante** quando reproduz os vereditos e as recusas abaixo, e produz
recibos que passam na verificação de selo da casa.

A v1.1.0 corrige a v1.0.0 em dois pontos: a regra de decisão passou a descrever
o código como ele é (§3), e o canon do selo passou a ser único, com o formato
legado declarado (§5).

## 1. Vocabulário normativo

1. **veredito**: um de `1`, `0`, `REFUSED`. Não existe quarto valor.
2. **recusa (REFUSED)**: resultado de primeira classe, sempre acompanhado de `refusal_reason`.
3. **banda** (`margin`): limite de ruído amostral aceito, derivado de `epsilon` e `shots`.
4. **p0**: fração de leituras com o registrador de entrada todo zerado.
5. **recibo**: registro selado de uma decisão, com entradas, medida, banda e veredito.

## 2. Derivação da banda (obrigatória)

Para `epsilon` declarado em `(0, 0.5)` e `shots` inteiro positivo:

```
banda(eps, shots) = sqrt( ln(2/eps) / (2*shots) )
```

Família de `k` vereditos conjuntos (Bonferroni, erro de família ≤ eps):

```
banda_familia(eps, shots, k) = 2*banda(eps, shots) - banda(eps/k, shots)
```

Se `banda_familia <= 0`, a decisão é `REFUSED` com `refusal_reason = FAMILY_EXCEEDS_SHOTS`.
A implementação **não pode** aumentar `shots` para escapar da recusa.

Valores de referência: `banda(0.05, 256) = 0.0848813447`,
`banda(0.01, 1024) = 0.0508632385`.

## 3. Regra de decisão (obrigatória, conforme o código)

A decisão é tomada em duas etapas, e a primeira etapa que casa decide.

1. `p0 >= 1 - banda` → **branco de interferência**. O veredito clássico é `1` se
   `f(0) == 1`, senão `0`. O valor **não** vem do limiar: vem da leitura clássica
   de `f(0)`, que consome uma chamada de oráculo adicional. `mode` é
   `DECIDED_BY_INTERFERENCE`.
2. `p0 <= banda` → `REFUSED`, `refusal_reason = BALANCED_ORACLE`. Aqui a fase não
   colapsa o registrador de entrada, que é a assinatura do oráculo balanceado.
   Este ramo **não** produz veredito `0`.
3. Caso contrário (`banda < p0 < 1 - banda`) → `REFUSED`,
   `refusal_reason = INSIDE_NOISE_BAND`, `mode = INSUFFICIENT_CONFIDENCE`.

Consequência que a v1.0.0 declarava errado e aqui fica corrigida: veredito `0`
só existe pelo ramo 1, com `f(0) == 0`. Nunca por `p0` pequeno.

Comparações são inclusivas nas duas fronteiras (`>=` e `<=`), e as fronteiras
exatas são casos de teste obrigatórios.

## 4. Taxonomia de recusa (fechada)

`BALANCED_ORACLE`, `INSIDE_NOISE_BAND`, `FAMILY_EXCEEDS_SHOTS`,
`DEVICE_DECOHERED`, `EXTRAPOLATION_ILL_CONDITIONED`.

Motivo fora dessa lista é não conformidade. Cobertura da suíte:

1. `BALANCED_ORACLE`: caso dourado no simulador e regra em `p0` sintético na fronteira.
2. `INSIDE_NOISE_BAND`: `p0` sintético (o simulador ideal nunca cai na zona cinzenta).
3. `FAMILY_EXCEEDS_SHOTS`: caso dourado.
4. `DEVICE_DECOHERED`: porta do runtime com dispositivo declarado inconfiável,
   exigindo `REFUSED` e **zero** chamadas de oráculo.
5. `EXTRAPOLATION_ILL_CONDITIONED`: pertence ao estimador ZNE, fora do núcleo de
   decisão; coberto pela bateria do laboratório, não por esta suíte.

## 5. Selo do recibo (obrigatório, canon único)

Há **uma** canonicalização no repositório, a da casa, definida em
`src/battery_ci.py`:

```python
json.dumps(payload, sort_keys=True, ensure_ascii=True, default=str)
```

Quem precisar selar importa essa função. Duas canonicalizações vivas foi o
defeito da v1.0.0: o mesmo conteúdo selado por uma regra não conferia pela
outra, e o incidente derrubou o self-test uma vez.

Formatos de recibo aceitos, cada um com sua regra de payload:

1. **Casa** (`selo_sha3_256`): o selo cobre `rec["payload"]` quando existe,
   senão o recibo sem a própria chave.
2. **Q-route legado** (`sha3_256`): o selo cobre o recibo sem a própria chave.
   Os recibos de `examples/recibos/` foram reselados sob o canon único, com o
   conteúdo intacto.

Regras de auditoria:

1. Recibo **sem** selo é não conformidade. Não existe skip silencioso.
2. Selo que não bate é não conformidade.
3. A varredura cobre `experiments/**/*_receipt.json`, `examples/recibos/*.json`
   e `*_receipt.json` na raiz. Metadados de job e contagens não são recibos e
   ficam fora da varredura.

## 6. Porta de integridade do dispositivo

Antes de usar oráculo, a implementação **pode** medir fidelidade GHZ. Se a
fidelidade ficar abaixo do limiar declarado (padrão 0.80), o veredito é
`REFUSED` com `DEVICE_DECOHERED` e nenhum oráculo é consumido. O limiar usado
deve estar registrado no recibo.

## 7. Produto quântico

Todo produto quântico da casa emite **OpenQASM 3** no recibo ou no artefato de
execução, além do identificador do job quando roda em hardware real.

## 8. Como rodar a suíte

```
python conformance/run_conformance.py          # tabela legível, exit 0 ou 1
python conformance/run_conformance.py --json   # saída para agente externo
```

Códigos de saída: `0` conformante, `1` não conformante, `2` erro de execução.

Uma implementação de terceiro é testada do mesmo jeito: basta expor a decisão
como JSON no formato do `conformance/cases.json`.

## 9. Versão

`1.1.0`. Mudança de regra exige versão maior e registro no CHANGELOG.

# ZYQL Conformance Spec — v1.0.0

Contrato normativo do núcleo de decisão trivalente ZYQL. Uma implementação é
**conformante** quando reproduz os vereditos e as recusas abaixo, e produz
recibos que passam na verificação de selo da casa.

## 1. Vocabulário normativo

1. **veredito**: um de `1`, `0`, `REFUSED`. Não existe quarto valor.
2. **recusa (REFUSED)**: resultado de primeira classe, sempre acompanhado de `refusal_reason`.
3. **banda**: limite de ruído amostral aceito, derivado de `epsilon` e `shots`.
4. **recibo**: registro selado de uma decisão, com entradas, medida, banda e veredito.

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

## 3. Regra de decisão (obrigatória)

Seja `p0` a fração de leituras com o registrador de entrada todo zerado.

1. `p0 >= 1 - banda` → veredito `1`
2. `p0 <= banda` → veredito `0`
3. caso contrário → `REFUSED` com `refusal_reason = INSIDE_NOISE_BAND`

Para oráculo balanceado, a fase não colapsa o registrador de entrada:

4. entrada não zerada de forma dominante no oráculo balanceado → `REFUSED` com
   `refusal_reason = BALANCED_ORACLE`

## 4. Taxonomia de recusa (fechada)

`BALANCED_ORACLE`, `INSIDE_NOISE_BAND`, `FAMILY_EXCEEDS_SHOTS`,
`DEVICE_DECOHERED`, `EXTRAPOLATION_ILL_CONDITIONED`.

Motivo fora dessa lista é não conformidade.

## 5. Selo do recibo (obrigatório)

O recibo é JSON. O selo `selo_sha3_256` é o SHA3-256 hexadecimal de:

```python
json.dumps(payload, sort_keys=True, ensure_ascii=True, default=str)
```

onde `payload` é o recibo sem a própria chave `selo_sha3_256`; se o recibo tiver
um objeto `payload` aninhado, o selo cobre `rec["payload"]`.

Alterar qualquer byte do conteúdo invalida o selo.

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

`1.0.0`. Mudança de regra exige versão maior e registro no CHANGELOG.

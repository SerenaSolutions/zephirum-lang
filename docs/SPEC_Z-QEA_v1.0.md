# Especificação Z-QEA v1.0 — Recibos Verificáveis para Decisão Quântica

**Status:** rascunho normativo para revisão externa · **Data:** 08/11/2026
**Referência de implementação:** `src/zqea_sig.py` (ZEPHIRUM 2.5.7)
**Autoria:** Serena Quantum Solutions · **Licença deste documento:** Apache-2.0

Esta especificação descreve o que já existe no código. Onde a implementação e o
texto divergirem, a implementação está errada e deve ser corrigida — não o texto.
Os vetores de teste da seção 9 são gerados pela implementação e verificados por
`tools/conformance_zqea.py` no CI.

---

## 1. Escopo

Z-QEA define como um resultado de execução quântica vira um registro que terceiros
podem verificar offline, sem confiar em quem o emitiu. Ela cobre quatro coisas e
nada além delas:

1. **Selo de conteúdo** (`selo_sha3_256`): integridade do recibo.
2. **Assinatura pós-quântica** (`assinatura`, `chave_id`, `algoritmo`): autoria.
3. **Cadeia** (`prev_sha3`): ordem e continuidade de uma sequência de recibos.
4. **Âncora** (`Z-QEA-ANCORA`): compromisso sobre o tamanho e o topo da cadeia.

**Fora de escopo:** correção do algoritmo quântico, fidelidade do hardware,
veracidade das medições, identidade civil do assinante e certificação FIPS/CAVP.
Um recibo verificado prova que aquele conteúdo foi assinado por quem detém a
chave. Não prova que a experiência foi bem feita.

---

## 2. Terminologia normativa

MUST, MUST NOT, SHOULD e MAY seguem o uso de RFC 2119.

| Termo | Definição |
|---|---|
| Corpo | O recibo sem os campos `assinatura`, `chave_id` e `algoritmo`. |
| Selo | `SHA3-256` sobre a forma canônica do corpo (seção 4). |
| Cabeça | O selo do último elo de uma cadeia. |
| Elo | Um recibo dentro de uma cadeia. |
| Âncora | Registro assinado com `tipo`, `n_elos` e `head_sha3`. |

---

## 2-A. Semântica dos três resultados (normativa)

A proposição decidida é **P = "existe decisão uniforme para toda entrada"**.

| Resultado | Significado | Quando |
|---|---|---|
| `1` | P verdadeira com `f(x)=1` uniforme | evidência acima da banda superior |
| `0` | P verdadeira com `f(x)=0` uniforme | evidência abaixo da banda inferior |
| `REFUSED` com `BALANCED_ORACLE` | P falsa: a resposta **depende da entrada** | medição na região balanceada |
| `REFUSED` com `NOISE_BAND` | evidência insuficiente | `m < p0 < 1-m` |
| `REFUSED` com `SELFCHECK_LOW` | execução não atingiu o limiar de retorno | auto-verificação falhou |
| `REFUSED` com `FAMILY_EXCEEDS_SHOTS` | tiros insuficientes para a família | `m_max <= 0` |

Regra obrigatória: **nenhuma implementação pode converter `BALANCED_ORACLE` em `0`.**
`0` significa "proibido para toda entrada", que é diferente de "depende da entrada".
Confundir os dois autoriza decisões uniformes onde não existe uniformidade — o erro
mais perigoso que esta especificação existe para impedir.

Todo `REFUSED` MUST carregar `refusal_reason` da tabela acima. Recusa sem motivo é
não conforme.

## 3. Campos de um recibo

| Campo | Tipo | Obrigatório | Significado |
|---|---|---|---|
| `veredito` | inteiro ou string | sim | `1`, `0` ou `"REFUSED"` |
| `p0` | número finito | conforme | Probabilidade observada da hipótese nula |
| `selo_sha3_256` | hex de 64 caracteres minúsculos | sim | Selo do corpo |
| `prev_sha3` | hex de 64 ou `null` | em cadeia | Selo do elo anterior |
| `assinatura` | base64 | quando assinado | Assinatura ML-DSA-44 do corpo |
| `chave_id` | hex de 16 caracteres | quando assinado | Identificador da chave |
| `algoritmo` | string | quando assinado | `"ML-DSA-44 (FIPS 204, Dilithium)"` |

Implementações MUST ignorar campos desconhecidos ao verificar, mas SHOULD
preservá-los, porque eles entram no corpo assinado.

---

## 4. Canonicalização (normativa)

A forma canônica de um objeto JSON é o resultado de:

1. Ordenar as chaves lexicograficamente por ponto de código Unicode.
2. Não emitir espaços entre tokens (`separators=(",", ":")`).
3. Codificar como UTF-8 sem escapar caracteres não-ASCII (`ensure_ascii=False`).
4. **Recusar** `NaN`, `Infinity` e `-Infinity` (`allow_nan=False`).

Motivo da regra 4: esses valores não existem em JSON e tornariam a serialização
não determinística entre linguagens. Uma implementação que os aceite MUST ser
considerada não conforme.

**Limitação declarada:** números em ponto flutuante seguem a formatação da
linguagem de origem. Para valores que precisam ser idênticos entre implementações,
use inteiros ou strings decimais, nunca `float`. Esta especificação não define
formato binário de ponto flutuante.

---

## 5. Selo

```
selo = hex_minúsculo( SHA3-256( canonical(corpo) ) )
```

`corpo` exclui `assinatura`, `chave_id` e `algoritmo`, e inclui `selo_sha3_256`
apenas na forma vazia — ou seja, o campo do selo MUST ser removido antes de
calcular o selo.

Verificação: recalcular e comparar em tempo constante quando a comparação for
sensível a tempo; divergência produz `SEAL_MISMATCH`.

---

## 6. Assinatura

- Algoritmo: **ML-DSA-44** (FIPS 204). O campo `algoritmo` MUST ser exatamente a
  string da seção 3.
- A assinatura cobre `canonical(corpo)`, com `chave_publica` já presente no corpo
  quando existir.
- Assinaturas ML-DSA são **randomizadas**: dois recibos com o mesmo corpo têm
  assinaturas diferentes e ambos MUST verificar. Vetores de teste não podem fixar
  bytes de assinatura.
- `chave_id` MUST ser `hex(SHA3-256(chave_publica))[0:16]`.

**Verificação (normativa, nesta ordem):**

1. `algoritmo`, se presente, MUST ser igual ao esperado; senão recusar.
2. `chave_id`, se presente, MUST ser igual a `key_id(chave_publica)`; senão recusar.
3. Verificar a assinatura sobre o corpo.
4. Em modo estrito, `algoritmo` e `chave_id` MUST estar presentes.

Os passos 1 e 2 existem porque esses campos ficam fora do corpo assinado. Sem
eles, trocar o rótulo do algoritmo ou o identificador da chave não invalidaria a
assinatura. Esta regra foi adicionada em 08/11/2026 após auditoria independente.

**Não alegado:** certificação FIPS 140, CAVP ou CMVP. A implementação usa
`pqcrypto` e não foi submetida a laboratório de certificação.

---

## 7. Cadeia

Um elo MUST ter `prev_sha3` igual ao selo do elo imediatamente anterior, ou
`null` no primeiro elo. O elo MUST estar assinado.

Verificação de cadeia: cada elo assinado corretamente, cada `prev_sha3` coerente,
e o selo recalculado encadeando na ordem recebida. Falha produz
`assinatura invalida` ou `encadeamento quebrado` com a posição do elo.

**Limite conhecido:** a cadeia detecta adulteração, reordenação e remoção de elos
intermediários. Ela **não** detecta a remoção do último elo, porque nada dentro da
cadeia afirma quantos elos deveriam existir. Para isso existe a âncora.

---

## 8. Âncora externa

```
ancora = assinar({ "tipo": "Z-QEA-ANCORA",
                   "n_elos": N,
                   "head_sha3": cabeca })
```

Verificação da âncora contra uma cadeia:

1. A âncora MUST verificar sua assinatura.
2. Se `len(cadeia) < n_elos`: recusar com `truncamento`. Truncamento é o ataque que
   a âncora existe para pegar.
3. Se `len(cadeia) > n_elos`: aceitar com aviso de que existem elos posteriores à
   âncora, não cobertos por ela.
4. O selo do elo de índice `n_elos - 1` MUST ser igual a `head_sha3`.

**Regra de utilidade:** uma âncora guardada no mesmo diretório do histórico não
prova nada, porque quem apaga o último elo apaga a âncora também. A âncora só tem
valor quando o hash é publicado em local que o operador não controla: tag assinada,
release, DOI, e-mail selado ou registro público. Sem publicação externa, o nível de
conformidade máximo é L3.

---

## 9. Vetores de teste (gerados pela implementação)

Todos verificados por `tools/conformance_zqea.py`.

**T1 — canonicalização**
```
entrada : {"b":"ç","a":1}
bytes   : {"a":1,"b":"ç"}  (UTF-8, sem espaços)
sha3    : 54cd981318d240636aba047fd3ac8d0e6629f8ac8df137a001033370bd8e7220
```

**T2 — selo de corpo**
```
entrada : {"veredito":1,"p0":0.5,"n":3}
canônico: {"n":3,"p0":0.5,"veredito":1}
selo    : 96debfc868acae29079b4d26d2eb3cbd2bd3f1fe5c4ede2d3e54f4c1376a3a68
```

**T3 — identificador de chave**
```
chave_publica (bytes): 00 01 02 ... 1f
chave_id            : 050a48733bd5c275
```

**T4 — cabeça de elo**
```
entrada : {"veredito":1,"prev_sha3":null}
canônico: {"prev_sha3":null,"veredito":1}
cabeça  : 7000e88884f6d532a3b21224581253b0745438341e2b03b18865a6780ecc6ec8
```

**T5 — recusa de não-finito:** `_canon({"x": NaN})` MUST levantar erro.

---

## 10. Níveis de conformidade

| Nível | Requisitos | O que prova |
|---|---|---|
| L1 | Selo correto | Conteúdo íntegro desde o selo |
| L2 | L1 + assinatura verificada e metadados conferidos | Autoria por quem detém a chave |
| L3 | L2 + cadeia coerente | Ordem e continuidade, sem remoção intermediária |
| L4 | L3 + âncora publicada fora do repositório | Ausência de truncamento do topo |

Um sistema que se declara L4 MUST publicar a âncora de forma verificável. Declarar
L4 sem publicação externa é alegação falsa.

---

## 11. Códigos de recusa

`SEAL_MISMATCH` · `assinatura invalida` · `encadeamento quebrado` ·
`truncamento: ancora cobre N elos, recebidos M` · `cadeia vazia nao pode ser ancorada`

Implementações MUST usar o estado de recusa da linguagem quando a evidência for
insuficiente, em vez de emitir 0 ou 1. Recusar é um resultado válido, não uma
falha do sistema.

---

## 12. Versionamento

Mudança compatível (campo novo opcional, código de erro novo) incrementa a versão
menor. Mudança incompatível (canonicalização, algoritmo, regra de cadeia) incrementa
a maior e exige novo identificador de especificação. Este documento é v1.0.

---

## 13. Pendências para revisão externa

1. Definir formato numérico interoperável para `p0` (hoje, `float` da linguagem).
2. Avaliar assinatura sobre o conteúdo bruto original, além do canônico.
3. Publicar âncora em registro externo e documentar o procedimento operacional.
4. Submeter a um laboratório independente: revisão criptográfica e teste de
   conformidade por terceiro.

# Auditoria do repositorio inteiro (Nemotron-3 Ultra-550B, 30/10/2026)

Auditoria adversarial sobre manifesto completo do repositorio, antes do preprint.
Abaixo, cada achado **verificado contra o codigo-fonte**. Auditor tambem erra, e
o registro mostra o que ficou de pe e o que caiu.

## Achados REFUTADOS (o auditor leu o resumo, nao o codigo)

| Achado | Verificacao | Situacao |
|---|---|---|
| "Em hardware o TVD nao e calculado; a prova so vale no simulador" | `zyql_witness.witness()` calcula `ideal = _ideal_probs(...)` e `tvd_hat = _tvd(ideal, counts, n)` **depois** de qualquer rota (`_run_local` ou `_run_ibm`). Mesmo codigo, mesmos numeros. | **REFUTADO** |
| "`adaptive_margin` usa constante magica `gate_penalty=0.001`" | `grep -rn gate_penalty src/` nao retorna nada. `adaptive_margin` e derivada de Hoeffding: `sqrt(ln(2/eps)/(2*shots))`. | **REFUTADO** |
| "`zyql_witness` decide por heuristica em hardware" | O veredito em `witness()` usa `delta = sqrt(K*ln(2/alpha)/(2N))` e compara `[lower, upper]` com `epsilon`. Limite declarado no recibo. | **REFUTADO** |

## Achados CONFIRMADOS e tratados

| Achado | Tratamento | Evidencia |
|---|---|---|
| Modulos sem nenhuma assercao (`oq3`, `zkernel`, `zquantum`, `zyql_rag_layer`) | `tests/test_modulos_orfaos.py` com **16 assercoes**: serializacao QASM3 e round-trip, kernel/backends/processos, QCircuit (norma e superposicao), BM25 e parser de regra | CI verde |
| Recibo do WORLD-3 guarda metricas, **nao contagens brutas** — distribuicao do Grover nao auditavel | Contagens **recuperadas dos jobs ja pagos** (sem novo QPU): `w3_contagens_recuperadas.json` | 3/3 reps |
| `bm25_rank` estourava `TypeError` opaco com corpus de strings | `_texto()` aceita `str` ou `{'text': ...}` e levanta `ValueError` explicito | teste |
| Escopo inflado (`zquantum`, `zkernel`, `zyql_rag_layer`, `zyql_llm_compress`) | Decisao de escopo: preprint cobre nucleo e protocolos; resto vai para *Supplementary Software* | este documento |

## Achados CONFIRMADOS e ainda abertos

| Achado | Por que continua aberto |
|---|---|
| Transpilador sem `seed_transpiler` nem dump do pass manager | exige novo job com protocolo declarado |
| Sem power analysis da regra de agregacao 3/3 | analise estatistica propria a escrever |
| SPAM sem matriz por qubit | exige calibracao por qubit no dispositivo |
| `zqea_sig` fora do fluxo principal de recibos | WORLD-3 assina via `tools/signar_recibos.py`; integrar ao runtime e decisao pendente |
| Data Availability Statement com DOI imutavel | depende de deposito no Zenodo |

## Grover com distribuicao completa (o achado que virou dado novo)

| Rep | p(marcado) | ideal | TVD vs ideal | entropia | estados |
|---|---|---|---|---|---|
| 1 | 0.7816 | 0.9453 | 0.1637 | 1.350 bits | 8/8 |
| 2 | 0.7762 | 0.9453 | 0.1691 | 1.385 bits | 8/8 |
| 3 | 0.7600 | 0.9453 | 0.1853 | 1.454 bits | 8/8 |

Leitura: o Grover nao "falhou limpo" — os 8 estados aparecem, a entropia fica em
~45% do maximo (1,35-1,45 de 3 bits) e o TVD ao ideal e 0,16-0,19. A amplificacao
existe, mas o dispositivo espalha populacao pelos estados nao marcados. Isso era
invisivel quando so `p(marcado)` era reportado.

## Regra unificada de abstencao

`witness_from_counts(ideal, counts, epsilon, alpha)` aplica o **mesmo limite de
Hoeffding** da testemunha DJ a qualquer distribuicao. Antes, HOM e Grover decidiam
por bandas ad hoc; agora a linguagem tem uma unica regra auditavel de veredito.

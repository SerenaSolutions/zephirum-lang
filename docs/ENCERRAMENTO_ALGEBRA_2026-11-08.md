# Encerramento do ciclo — álgebra de decisões trivalentes

**Data:** 08/11/2026 · **Fechado por:** Superagent (Antigravity impedido por cota, HTTP 429 até ~14/11)
**Revisão externa do Antigravity:** pendente, não bloqueia o estado declarado abaixo.

## O que existe agora

`src/zyql_algebra.py`: composição de decisões trivalentes (E, OU, NÃO, sequência) em que
`k` é **contado** da expressão, o erro familiar é propagado por composição, e o poder
estatístico é verificado antes de qualquer aprovação. Recibo com selo SHA3-256
determinístico sobre forma canônica que inclui o operador.

## Duas rodadas de auditoria, três defeitos reais

| # | Defeito | Gravidade | Estado |
|---|---|---|---|
| A1 | `A E B` e `A OU B` com mesmo veredito geravam **o mesmo selo** | crítico | corrigido + teste |
| S2 | nó composto declarava o epsilon de **uma folha**, não o erro do conjunto | alto | corrigido + teste |
| S3 | duas recusas compostas descartavam o segundo motivo | médio | corrigido + teste |

Achado A4 (dependência): `SamplerV2` depreciado no runtime 0.50+. Migrado para o import
de topo `Sampler` e faixa fixada em `qiskit-ibm-runtime>=0.50,<0.53`. Reexecutado em
hardware para provar que a migração funciona.

## Evidência de hardware — duas execuções independentes

| Job | Backend | p0 (2000 shots) | Decisão única | Programa de 7 |
|---|---|---|---|---|
| `dboh76oqtr0c738crlng` | ibm_marrakesh | 0,9720 | veredito 1 | REFUSED por `FAMILY_EXCEEDS_SHOTS` |
| `dbohdelt7fqc7387s2n0` | ibm_marrakesh | 0,9870 | veredito 1 | REFUSED por `FAMILY_EXCEEDS_SHOTS` |

Replicação independente, mesmo resultado. Pré-registro selado antes das duas execuções
(`docs/PRE_REGISTRO_ALGEBRA_QPU.json`, selo `34e6fcd020b3aa02`, ML-DSA-44 verificável com
`PRE_REGISTRO_ALGEBRA_QPU.chave.json`).

## O que isso prova, e o que não prova

Prova: a aritmética do orçamento de erro é coerente com estatística de hardware, e a
recusa por poder insuficiente dispara onde a conta manda, sem caminho de aprovação.

Não prova: vantagem física sobre outros frameworks; correção de erro; utilidade prática
em carga de trabalho real. A fronteira `shots <= 14` para `eps=0,01` e `k=7` é aritmética,
não descoberta de física.

## Dívida declarada

1. Revisão do Antigravity sobre este código, quando a cota voltar (~14/11).
2. Validação externa por terceiro: ninguém fora do projeto executou os recibos ainda.
3. `sequencia` é associativa à esquerda e o selo é sensível à ordem quando as folhas
   diferem. Logicamente equivalente, estruturalmente distinto: está correto para recibo,
   mas precisa estar escrito na especificação.

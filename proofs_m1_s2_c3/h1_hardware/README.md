# H1 — programa ZYQL completo em hardware fisico

Fecha o ultimo item aberto do H1: um programa escrito em ZYQL, autorizado por
politica, decidido por interferencia em QPU de producao, com recibo no formato v1.

## Resultado (512 tiros por circuito, delta = 0.05)

| oraculo | p(000) medido | referencia exata | veredito |
|---|---|---|---|
| constante zero | 0.9727 | 1.0000 | **0** |
| balanceado | 0.0000 | ~0 | **REFUSED** |

epsilon Hoeffding = 0.0600; limiar de aceitacao = 1 - eps = 0.9400.
Os dois vereditos conferem com a referencia exata local.

## Cadeia completa exercitada

1. `programa.zeph` — programa ZYQL (ASK / CONTRACT / MODEL)
2. `policy.json` — politica P1-2026-11, negacao por padrao, grant vinculado ao hash do programa
3. Policy Gate autorizou a execucao (falha fechada se nao houvesse grant)
4. Referencia exata local (Statevector) fixada antes do hardware
5. Execucao em QPU de producao, dois circuitos, 512 tiros
6. Regra `proporcao-v1` aplicada sobre as contagens brutas
7. Recibo v1 emitido com hashes de evidencia e cadeia SHA3-256

## Limitacoes declaradas

- Plano aberto: ruido de leitura e de porta nao corrigidos (p(000) = 0.9727 contra 1.0 exato)
- Identificadores de dispositivo e de job mantidos em registro interno, por politica de sigilo
  de fornecedor; `backend_fingerprint` e um hash, suficiente para vincular o recibo ao
  equipamento sem nomear o fabricante

Conferencia independente: `python3 build_receipt.py` sobre `EVIDENCIA_H1.json`.

# Auditoria Ultra-550B sobre o WORLD-3 (2026-10-29)

Parecer adversarial (nvidia/nemotron-3-ultra-550b-a55b) sobre o experimento ja publicado.
Registro integral; correcoes aplicadas ou pendentes indicadas.

## Falhas apontadas

| # | Severidade | Falha | Status |
|---|---|---|---|
| 1 | BLOQUEANTE | Metricas sem incerteza estatistica (TVD, visibilidade, p pontuais) | **PARCIALMENTE corrigida**: IC 95% recalculado em w3_analise_ic.json (analise post-hoc rotulada) |
| 2 | BLOQUEANTE | Regra de agregacao 3/3 sem power analysis / curva OC | PENDENTE |
| 3 | MAIOR | SPAM como taxa unica, sem discriminacao por qubit | PENDENTE (exige novo job) |
| 4 | MAIOR | W-01 "falha por roteamento" e hipotese post-hoc sem contraprova | PENDENTE (ablation: echo com mesma profundidade/portas) |
| 5 | MENOR | W-03 reporta apenas p(|101>), ignora distribuicao completa | PENDENTE (TVD/cross-entropy) |
| 6 | MENOR | optimization_level=3 sem seed/pass-manager dump: reps podem ser circuitos fisicos distintos | PENDENTE |

## Veredito do auditor sobre as claims

- (a) **W-02 estabelecido**: PARCIALMENTE FUNDAMENTADA -> precisa IC + teste de hipotese contra 0.70.
  Com o IC recalculado: **0.947-0.957**, inteiramente acima de 0.70. Claim reforcada.
- (b) **W-01 falhou por roteamento**: MAL FUNDAMENTADA -> correlacao nao e causalidade; falta ablation.
- (c) **W-03 ~6x classico e provisorio**: FUNDAMENTADA COM RESSALVA (banda precisa justificativa de poder).
  IC recalculado: **0.764-0.782**, abaixo de 0.85 -> permanece NAO certificado.

## Leitura corrigida do WORLD-3

| Protocolo | Media +- dp | IC95 | Limiar | Situacao |
|---|---|---|---|---|
| W-01 TVD | 0.253 +- 0.048 | [0.244, 0.263] | 0.10 / 0.20 | acima do limiar superior: NAO certifica (consistente) |
| W-02 visibilidade | 0.952 +- 0.001 | [0.947, 0.957] | >= 0.70 | **certifica com margem** |
| W-03 p(marcado) | 0.773 +- 0.011 | [0.764, 0.782] | >= 0.85 | nao certifica (provisorio) |

Nota da auditoria de defensabilidade cientifica: ver parecer integral em /tmp/auditoria_ultra_w3.md (sessao 2026-10-29).

# ZYQL Statistical Protocol — formal decision specification

Status: ESPECIFICAÇÃO FORMAL (implemented by `tests/ibm_quantum/zca_conformidade_ibm.py`,
receipts archived in `zca_conformidade_live.json` / `zca_conformidade_sim.json` / `experiments/refusal_receipt.json`)
Date: 2026-10-19 (ISO 8601) · Band: δ = 0.15 (declared) · Reference shots: n = 2048

## 1. Decision states

Every ZYQL decision is trivalent:

- `1` (permitted / balanced / property holds)
- `0` (forbidden / constant / property fails)
- `REFUSED` (insufficient confidence — see docs/ZYQL_REFUSED_SPEC.md)

## 2. The one-oracle-call decision (Deutsch–Jozsa)

Ideal model, no noise: interference returns a deterministic bit —
constant oracle ⇒ P(1) = 0, balanced oracle ⇒ P(1) = 1, in ONE oracle query.

Noisy hardware measures p̂ = (count of outcome 1)/n. ZYQL never claims the ideal
probability; it decides against a DECLARED noise band δ:

| measured p̂ | verdict |
|---|---|
| p̂ ≤ δ | 0 (constant) |
| p̂ ≥ 1 − δ | 1 (balanced) |
| δ < p̂ < 1 − δ | REFUSED |

Live receipts (ibm_fez, job db6ded84qg6s73c4jvug, n = 2048):
DJ constant: p(000) = 0.9844 ⇒ p̂ ≈ 0.016 ≤ 0.15 ⇒ verdict 0 (PASS);
DJ balanced: p̂ = 0.9531 ≥ 0.85 ⇒ verdict 1 (PASS).

## 3. Error probabilities (binomial)

Under H0 (true constant, p = 0): P(false verdict 1) = P(p̂ ≥ 1−δ) = 0^{n} ⇒ 0;
in practice the binding risk is readout noise pushing p̂ into the 1 region.
Bound with worst-case noise floor q (per-outcome error):

- P(false 1 | true 0, noise q) ≤ q^{ceil(δ·n)} — for q ≈ 0.02, δ = 0.15, n = 2048 this is effectively 0.
- Under H1 (true balanced, p = 1 − q): P(false 0) = P(p̂ ≤ δ) = P(Binomial(n, 1−q) ≤ δn).
  With q = 0.02, δn = 307, mean = 2007, σ = √(n·(1−q)·q) ≈ 6.3 ⇒ z ≈ −269 ⇒ β < 10^{-1000}.

Minimum shots for target error α (false verdict when true p is ideal):
n_min(α) = ln(α) / ln(1 − δ). For α = 0.01, δ = 0.15 ⇒ n_min = 29 shots.
The reference suite uses n = 2048 ⇒ ≥ 70× the minimum; margins are declared, not implied.

## 4. Band calibration rule

δ must exceed the device noise floor by a declared factor:
δ ≥ k · q_max, with k = 7.5 observed (q ≈ 0.016–0.02 readout floor on ibm_fez, δ = 0.15).
If calibration shows q_max > δ/3, the suite MUST widen δ (and re-declare it) or REFUSED
must absorb the difference. The band is a property of the receipt, never of an assumption.

## 5. Drift

The suite records `drift_detectado` per test. Observed: DJ balanced live run flagged
drift (p̂ = 0.9531 with q ≈ 0.02 implies measurable decay relative to calibration).
Rule: a verdict with `drift_detectado = true` remains valid only within its receipt's
session window; cross-session claims require a fresh calibration receipt.

## 6. Validação em hardware

Em 2026-10-22, a Rodada A de testes empíricos executou uma varredura de shots no processador quântico **IBM Heron (`ibm_fez`)** (plano aberto da IBM Quantum, operado como laboratório de teste sem endosso institucional). O recibo selado em [`experiments/refusal_receipt.json`](../experiments/refusal_receipt.json) (SHA3-256 `9cd39440a49373600b6d1eaf79e22f6e2bdacf133491c9faf748ec71a1be9b3a`) documenta os seguintes resultados medidos:

### Jobs e níveis de shots testados (Deutsch-Jozsa n=3, 1 chamada de oráculo)
- **512 shots:** job `dbcjf7ni0auc73dv36ug` — Acerto 3/3 (100%), recusa espúria: 0
- **1024 shots:** job `dbcjf7pgv2cc73eaft1g` — Acerto 3/3 (100%), recusa espúria: 0
- **2048 shots:** job `dbcjf7vi0auc73dv36vg` — Acerto 3/3 (100%), recusa espúria: 0
- **4096 shots:** job `dbcjf81gv2cc73eaft20` — Acerto 3/3 (100%), recusa espúria: 0
- **8192 shots:** job `dbcjf87i0auc73dv3700` — Acerto 3/3 (100%), recusa espúria: 0
- **16384 shots:** job `dbcjf8fi0auc73dv370g` — Acerto 3/3 (100%), recusa espúria: 0

### Métricas estatísticas observadas
- **Conformidade de probabilidade:** $p(000) \ge 0.9977$ para casos constantes (const-1 e const-0) e $p(000) \le 0.0024$ para o caso balanceado em todos os 6 níveis.
- **Taxa de acerto:** 100% (3/3 casos corretos) em todas as medições de 512 a 16384 shots, com zero recusas espúrias.
- **Shots mínimo empírico testado:** 512 shots (menor nível testado).
- **Comparação com o modelo teórico:**
  - Fórmula declarada do protocolo: $n_{\min}(\alpha) = \ln(\alpha)/\ln(1-\delta) = 29$ shots ($\alpha = 0.01, \delta = 0.15$).
  - Cota de Hoeffding: $n \ge \frac{\ln(2/\alpha)}{2\epsilon^2} = 82$ shots ($\epsilon = 0.15, \alpha = 0.05$).
  - Ambas as previsões teóricas (29 e 82 shots) situam-se abaixo do menor nível empírico testado (512 shots).
- **Veredicto:** **VALIDADO** no intervalo $[512, 16384]$ shots.

### Limitações honestas e lacunas abertas
1. **Lacuna no limite inferior real:** Como a varredura da Rodada A iniciou em 512 shots, o ponto exato de inflexão (entre 29 e 512 shots) onde o ruído de hardware começa a degradar a decisão trivalente não foi medido. O limite inferior empírico exato permanece uma **lacuna aberta**.
2. **Escopo do algoritmo e hardware:** A validação cobre apenas o algoritmo Deutsch-Jozsa $n=3$ em um único backend quântico (**IBM Heron `ibm_fez`**).

### Próximos passos (Rodada B proposta)
Para fechar a lacuna aberta abaixo de 512 shots, propõe-se a **Rodada B**: varredura de alta resolução nos níveis $\{16, 32, 64, 128, 256\}$ shots, mapeando o limiar crítico exato onde ocorrem decisões incorretas ou recusas espúrias (`REFUSED`).

---

## Rodada B — lacuna de shots baixos (2026-10-22/23)

A Rodada A declarou a lacuna abaixo de 512 shots como não verificada. A Rodada B
fechou a lacuna: a mesma bateria Deutsch-Jozsa n=3 (const-1, const-0, balanceado)
no **IBM Heron ibm_kingston** (backend distinto do ibm_fez da Rodada A, conta
independente) em **64, 128, 256 e 384 shots**.

Resultado: **vereditos trivalentes EXATOS em todos os níveis**, inclusive 64 shots
(1/0/REFUSED corretos em todos os casos). O protocolo estatístico ZYQL não é
apenas válido acima de 512 — a decisão trivalente é exata no silício até os
nível de ruído mais baixo testado. Jobs: `dbdac41gv2cc738hnen0` (64),
`dbdac47i0auc739521vg` (128), `dbdac4c24mrc73cl3ia0` (256), `dbdac4ni0auc73952200` (384).

Recibo selado (ML-DSA-44 + entropia quântica): `experiments/round_b_receipt.json` —
veredito `RODADA_B_VERIFICADA_TRIVALENTE_EXATO`.

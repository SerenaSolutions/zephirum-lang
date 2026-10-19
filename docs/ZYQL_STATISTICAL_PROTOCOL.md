# ZYQL Statistical Protocol — formal decision specification

Status: ESPECIFICAÇÃO FORMAL (implemented by `tests/ibm_quantum/zca_conformidade_ibm.py`,
receipts archived in `zca_conformidade_live.json` / `zca_conformidade_sim.json`)
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

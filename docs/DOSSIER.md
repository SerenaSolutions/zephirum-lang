# ZEPHIRUM / ZYQL — Technical Dossier

**Trivalent quantum decision language with sealed, tamper-evident receipts.**
Version v2.1.0 · MIT license · Zenodo concept DOI 10.5281/zenodo.23632019

This dossier consolidates what the project is, what has been *measured on
real quantum hardware*, what it means for industry, and where its honest
limits are. Every technical claim below points to a sealed receipt in the
Z-QEA chain (20 receipts, all verifiable in-repo by `python -m battery_ci`).

---

## 1. What the language is

ZYQL is a quantum decision language where the answer is not binary. Every
computational claim resolves to one of:

- **1** — decided YES, within a declared statistical band
- **0** — decided NO, within a declared statistical band
- **REFUSED** — no honest decision is possible, *with a machine-readable reason*

REFUSED is not an error. It is a first-class answer with a traceable
taxonomy: noise above band, ambiguous evidence, missing signal, tampered
protocol, early stopping. Each decision can be sealed into a **Z-QEA
receipt**: SHA3-256 content hash, ML-DSA-44 post-quantum signature
(self-consistency, not authorship), and chaining to the previous receipt —
an auditable, tamper-evident ledger of what the machine actually decided.

## 2. What has been measured on real hardware

All results below ran on superconducting QPUs under sealed protocols
(protocol hashed SHA3-256 *before* submission; stopping rules verified at
runtime). No mitigation is folded into raw metrics.

| Result | Outcome | Receipt |
|---|---|---|
| GHZ-16 fidelity curve (n=12→16) | 0.7595 → 0.6118, below 0.80 trust gate → honest **REFUSED DEVICE_DECOHERED** | `c8182223` |
| ZNE folding (γ=1/3/5) with anti-extrapolation guard | MITIGATED 0.9292 → 0.958, guard margin 0.0442 | `c8182223` |
| Parameter-shift gradient decay on hardware | TRAINABLE across the full grid | `c8182223` |
| Sealed Deutsch–Jozsa, n=4, 2048 shots | p0 = 0.8999 < band 0.97 → **REFUSED** rather than false success | `ea1cc335` |
| Shot-stream independence, 2048 per-shot bits, 8 temporal batches, lag family K=5 (Bonferroni) | INDEPENDENCE PLAUSIBLE (lag-1 = -0.0104); stopping rule honored at runtime | `ea1cc335` |
| Dynamical decoupling XY4 on GHZ-16 | F_raw 0.4878 vs F_DD 0.3223 — **claim refuted and published as a result** | `40193cb0` |
| Trivalent QPE, eigenstate vs phase-mixture | Two refusals with **two different reasons** (noise vs ambiguity) in one algorithm — refusal taxonomy at algorithm level | `2759b0e0` |

The last two rows matter most: the language *refuses when refusing is the
truth*, and it *publishes refutations of its own team's ideas* with sealed
receipts. Nothing above exceeds its evidence.

## 3. Public commitment: m50

The dominant failure mode of the hardware cycle is correlated
decoherence: GHZ-16 infidelity (m = 1 − F_GHZ(16)) has a sealed baseline of
**0.3882** (receipt `c8182223`). Public commitment: **m ≤ 0.194 by
2027-04-25**, measured under sealed protocol, raw hardware, each
measurement a chained receipt. If the chain does not show it by then, the
commitment has *publicly failed* — falsifiable by design.
See `experiments/m50_spec.md`. First attack (in-circuit XY4 decoupling)
was already executed and **refuted** (receipt `40193cb0`).

## 4. Industry 5.0 applications (decision layer, not hype)

The honest value proposition is **auditable decision-making for industrial
automation** — not quantum replacing PLCs or classical optimizers.

1. **Safety interlocks (ESD) for oil platforms and substations** — trip /
   restrain / **REFUSED with reason** on fused sensor streams; the refusal
   taxonomy tells the safety engineer *what is wrong with the data*
   (noise, ambiguity, missing signal). Core primitive measured on
   hardware: receipt `2759b0e0`.
2. **Certified predictive maintenance** — maintenance orders sealed with
   declared statistical bands and post-quantum receipts (relevant for
   20+ year industrial assets). Evidence: receipt `ea1cc335` + intact
   20-receipt chain.
3. **Machining quality gates** — approve / reject / **refuse the
   borderline part** with declared margin instead of a blind threshold.
   Evidence: sealed DJ refusal, receipt `ea1cc335`.

Full document: `docs/INDUSTRY_5_0_SOLUTIONS.md`.

**Where classical wins (declared openly):** combinatorial scheduling at
today's scales, defect prediction with large tabular datasets, general
optimization. We do not sell those as quantum wins; our differentiator is
the sealed decision trail.

## 5. Ecosystem status

- 73/73 tests green; adversarial battery included (multi-lag independence
  guard, stopping-rule runtime verifier, seal-tamper detection)
- 20-receipt Z-QEA chain, integrity-verified in CI
- Automatic release archiving to Zenodo (concept DOI 10.5281/zenodo.23632019)
- Qiskit Ecosystem submission: PR #1433, automated validation passed,
  awaiting human review
- Reproduce everything: `pip install -e . && pytest` — receipts verified
  by the public CI on every push

## 6. Verification

Any third party can verify every claim in this dossier:

1. Clone the repository; run `python -m battery_ci` — all receipt seals
   recompute and verify, including the chain.
2. Each receipt names its hardware job IDs; re-run any experiment under
   the sealed protocol spec found inside the receipt itself.
3. The m50 commitment is checkable from the receipt chain alone.

*If a claim is not in a receipt, it is not in this dossier.*

# Internal Development Delegation — ZEPHIRUM/ZYQL Algorithm
2026-11-26 · derived from ZSKC v1.0 · owner of this plan: house AI operations layer

Rule: no work package is "done" without a reproducible test and its evidence state.
States: IMPLEMENTADO · TESTADO · REPRODUZIDO_INDEPENDENTEMENTE · FORMALMENTE_VERIFICADO ·
EXPERIMENTAL · ESPECIFICAÇÃO · NÃO_VERIFICADO · BLOQUEADO.

| WP | Scope | ZSKC clause | Owner front | State today | Acceptance test |
|---|---|---|---|---|---|
| WP1 | Adapter contracts for the Hybrid Execution Layer (CPU/GPU/QPU/sim): each adapter declares measured-vs-simulated, versions, determinism class | Art. 2, 3.4, 6 | runtime/integrations | ESPECIFICAÇÃO | contract test fails when an adapter lacks a declaration |
| WP2 | Conformance expansion: edge cases beyond 2^53, rounding at boundary, partial means, explicit refusal paths | Art. 3.1, 3.6 | language core | IMPLEMENTADO (partial) | every new case ships a failing-first test; corpus count published |
| WP3 | VERITAS verifier: one command checks receipt chain + CLAIMS.md ↔ artifact mapping; CI fails if a claim lacks evidence | Art. 2, 4 | receipts/evidence | ESPECIFICAÇÃO | CI red when a claim row has no artifact link |
| WP4 | Evidence index auto-generation: receipts/ + job ids → docs/EVIDENCIAS_QPU.md (backend, shots, job_id, verdict) | Art. 3.5 | receipts/evidence | ESPECIFICAÇÃO | generated file matches published numbers; drift fails CI |
| WP5 | Numerical precision contract: statevector [re,im] float64, rounding policy, declared tolerances per operation | Art. 3.1 | scientific kernel | NÃO_VERIFICADO (undocumented) | precision doc + test that pins tolerances |
| WP6 | Reproducibility container: pinned versions, published digest, parity test vs documented versions | Art. 3.2 | CI/infra | IMPLEMENTADO (container exists) | parity report published per release |
| WP7 | Independent tester onboarding: CALL_FOR_TESTERS → runnable checklist + report issue template | Art. 3.6 | governance/docs | ESPECIFICAÇÃO | one external tester completes the checklist end-to-end |

## Sequencing (the algorithm first)
1. WP2 (falsifiability corpus) — protects everything else.
2. WP5 (precision contract) — the kernel cannot refuse correctly without declared tolerances.
3. WP1 (adapter contracts) — hybrid layer honesty.
4. WP3 + WP4 (VERITAS + evidence index) — the audit trail becomes mechanical.
5. WP6 + WP7 — reproducibility and adversarial testers.

## Non-negotiables for every front
- No claim above EVIDENCIA in any channel (CLAIMS.md discipline).
- QPU runs: hashed pre-registration, declared shot budget, maturity label.
- Hardware cited as test laboratory only. Vendor neutrality in every public piece.
- Commits signed: Co-authored-by: SerenaSolutions <gronovatech@gmail.com>.

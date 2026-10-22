# ZEPHIRUM — External Peer Review Request

Auditoria externa aceita; esta página é a via pública de revisão por pares
(item 9 de `docs/AUDIT_RESPONSE_2026-10-19.md`). Regra da casa: nenhuma
alegação acima do que a evidência sustenta; a revisão independente é bem-vinda
e será registrada em `docs/AUDIT.md`, verbatim.

## What to review (claims, exactly as declared)

1. **Trivalent decisions on real hardware.** ZQ-GATE battery (verdicts `1` /
   `0` / `REFUSED`) and sealed Z-QEA receipts, reproducible in CI — the
   receipts carry their own rule (`selo_regra`).
2. **26-circuit sweep, IBM Heron `ibm_fez`** (job `dbbuh17i0auc73dtpaeg`):
   dominant channel 10/10, braid-word period 6/6, chi-square at 4096 shots
   detecting sub-1% readout bias, TV distance ≤ 4.5%.
3. **Gottesman–Knill as a classical certificate.** The labeling discipline
   `DECLARED_CLASSICAL × PROVEN_QUANTUM` — any circuit simulable in
   polynomial time classically must be declared as such, never sold as
   quantum advantage.
4. **DJ statistical protocol** (`docs/ZYQL_STATISTICAL_PROTOCOL.md`): noise
   band δ=0.15, binomial error bounds, minimum shots n_min = ln(α)/ln(1−δ),
   calibration against the observed noise floor (q≈0.016 on `ibm_fez`).
5. **Chemistry battery vs PySCF FCI** (`experiments/chemistry/`): H2, H2O,
   LiH, NH3 with declared error figures.

## How to review

```bash
git clone https://github.com/SerenaSolutions/zephirum-lang
cd zephirum-lang
pip install -e .                # audit finding #1 fix, deterministic imports
python tests/test_canonical.py  # canonical battery (CI runs the same)
```

Verify any receipt with the Marketplace Action or standalone:

```bash
python .github/actions/zqea-verify/zqea_verify.py <receipt.json> --strict-pq
```

Public benchmark reproduction: `experiments/benchmark_public/` (RUNBOOK.md,
RESULTS.md, verify.py).

## ZERONE (private)

Multi-round QEC claims live in the private `zerone-quantum-os`. Reviewers
may request a sealed tarball (Z-QEA receipt: integrity seal + ML-DSA-44
self-consistency) via a GitHub issue on this repository — same path offered
to the external auditor (audit item 8).

## Reviewer ground rules

- Attack the evidence, not the roadmap. Roadmap items are declared, not
  claimed.
- Negative results are welcome; they will be recorded verbatim in
  `docs/AUDIT.md`.
- REFUSED is a first-class answer: a reviewer failing to reproduce should
  file the exact receipt, job id and environment — no silent verdicts in
  either direction.

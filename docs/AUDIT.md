# External Audit Record — Z-QEA governance

This page records external audits of the repository, the house validation of
each finding, and remediation status. Audits are treated as evidence: recorded
verbatim in summary, never paraphrased into marketing.

## Audit #1 — GitHub Copilot code review (2026-10-21)

**Scope:** full repository, main branch.
**Verdict (verbatim summary):** *"coherent, well-named, well-documented, good
architecture for a research/prototype base... experimental/prototype project
with explicit scope and maturity limits."*

### Findings and house response

| # | Finding (Copilot) | House validation | Remediation | Status |
|---|-------------------|-------------------|-------------|--------|
| 1 | `sys.path` dynamic manipulation in modules | CONFIRMED — and worse than audited: the documented README quickstart (`from src.zyql_quantum_gate import ...`) was broken; path insertion pointed at repo root, not `src/` | `pyproject.toml` (`pip install -e .`), deterministic in-tree fallback, quickstart fixed and verified | **Fixed in v1.6.0** |
| 2 | Type layer works but is rigid, PoC-specific | CONFIRMED — `quantum_types.py` enforces no-cloning for the current circuit model only | Public roadmap item: generalized type layer | Roadmap R2 |
| 3 | Parser closer to a pre-parser than a full compiler | CONFIRMED — `.zph` handling is minimal by design ("language heart only") | Public roadmap item: AST + compile path | Roadmap R3 |
| 4 | Trivalent layer "needs care in production/benchmark" | PARTIALLY OBSOLETE — the audit did not account for `docs/ZYQL_STATISTICAL_PROTOCOL.md` (noise band, binomial bounds, minimum shots) and `docs/ZYQL_REFUSED_SPEC.md` (triggers R1-R6), which formalize exactly this | Protocol docs referenced from README; benchmark care listed on roadmap | Roadmap R4 |
| 5 | Repo is "prototype, not final product" | CONFIRMED — and declared by design (README: "Honest scope") | No action; this is the house honesty rule | Permanent |

### Findings the audit did not connect

- The evidence artifacts it saw ("job IDs, logs") are **real-hardware
  verification on IBM Heron (ibm_fez)**, merged to main in `experiments/`:
  jobs `dbbueufi0auc73dtp7og`, `dbbugbk24mrc73cif420`, Z-QEA receipts sealed.
- Statistical maturity exists ahead of the audit's reading: chemistry battery
  reproduces PySCF FCI with error 0; DJ protocol bounds (Hoeffding) declared.

**House conclusion:** audit accepted; strongest technical finding (#1) fixed in
v1.6.0; structural findings (#2, #3) accepted as declared roadmap, not defects.

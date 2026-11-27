# GEN1_IMPLEMENTATION_PLAN — smallest verifiable increment first

Order is mandatory. No phase starts before its predecessor's exit criterion is met.

## Phase 0 — Baseline and reference freeze (DONE, this commit)
Deliverables: `GEN1_BASELINE.md`, `GEN1_ARCHITECTURE.md`, `GEN1_RISK_REGISTER.md`, this plan.
Exit criterion met: every component claims a state backed by file/test evidence; discrepancies between `MATURITY.md`, `receipts.md` and `README.md` are registered.

## Phase 1 — Contracts and semantics (next, no code changes to runtime)
1. `ScientificProblem` contract: `problem_id`, `contract_version`, `domain`, `input`, `assumptions`, `constraints`, `tolerances`, `verification_requirements`, `evidence_requirements`.
2. `BackendCapability` contract: id, type (analytical/cpu/gpu/simulator/hardware), supported ops, limits, precision, deps, versions, failure modes.
3. `ScientificVerdict`: decision dimension (`1/0/REFUSED`) kept intact; epistemic dimension added separately (`PROVED/SUPPORTED/UNKNOWN`).
4. Fallback policy: explicit, recorded in the receipt, never silent.
Exit criterion: contracts tested against the existing API without changing legacy behaviour; a conformance corpus runs green.

## Phase 2 — Classical reference path
Wire one contract -> validation -> verdict -> CPU execution -> receipt -> verify path.
Exit criterion: same input reproduces the same receipt digest; failures produce explicit refusals.

## Phase 3 — Quantum simulation path
Same contract through the simulator adapter, labelled SIMULATION in the receipt.
Exit criterion: reproducible counts; divergence from the classical reference detected, not hidden.

## Phase 4 — Hardware path
Only through the documented adapter; explicit opt-in (already enforced in `backends/ibm.py`, `ZEPHIRUM_ALLOW_QPU_SUBMIT`); job id recorded only when the provider returns it.
Exit criterion: pre-declared protocol, verifiable receipt, limitations published, including negative results.

## Phase 5 — Evidence consolidation
One verifier across `qroute`, `zyql_ten` and `docker` receipt producers; tamper tests; provenance chain.
Exit criterion: a modified receipt is detected and the verifier explains the refusal.

## Phase 6 — Publication
External review, maturity reconciliation, release notes listing limitations.

## What is explicitly NOT in Gen 1
Own OS/bootloader, own compiler/simulator, universal QPU support, error correction, quantum-advantage claims, automatic theorem proving.

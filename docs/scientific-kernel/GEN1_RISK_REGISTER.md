# GEN1_RISK_REGISTER — ZEPHIRUM Scientific Kernel

| # | Risk | Severity | Evidence | Mitigation | Owner |
|---|---|---|---|---|---|
| R1 | Maturity claim divergence (`MATURITY.md` = PRODUÇÃO vs `README.md` = work in progress) | HIGH | both files in repo | founder decision; one document must win before any release | Founder |
| R2 | ML-DSA-44 status contradictory (BETA vs DECLARED ROADMAP) | HIGH | `docs/MATURITY.md`, `docs/receipts.md` | single source of truth; no external claim of post-quantum authorship until reconciled | Evidence |
| R3 | Hash presented as proof of truth/authorship | HIGH | risk of public misuse of `selo_sha3_256` | receipts state integrity-only; authorship is a separate layer | Evidence |
| R4 | No independent reproduction | HIGH | `CALL_FOR_TESTERS.md`, Discussion #141, 0 external reports | keep the call open; ship container + checklist | Red Team |
| R5 | Receipt shape differs across producers (`qroute`, `zyql_ten`, `docker`) | MEDIUM | three receipt modules exist | Phase 5 single verifier; no new format | Evidence |
| R6 | Optional adapter deps break collection (4 errors on `main`) | MEDIUM | baseline run | mark optional deps, skip cleanly, document install matrix | Security |
| R7 | Branch protection bypassed by admin pushes | MEDIUM | push receipt Nov 26 ("Bypassed rule violations") | all work via PR; founder merges | Chief Architect |
| R8 | Silent fallback hardware -> simulation | HIGH | new orchestrator risk | fallback explicit and recorded; refusal stays refusal | Hybrid |
| R9 | QPU submission without opt-in | HIGH | mitigated in PR #153 (`ZEPHIRUM_ALLOW_QPU_SUBMIT`) | keep default-off; test asserts no submission | Quantum |
| R10 | Credentials leaking into receipts/logs | HIGH | pasted directive contained token detections | redaction test; secrets never in receipts | Security |
| R11 | Gen 1 scope creep into OS/compiler | MEDIUM | directive explicitly forbids | scope list in plan; reject out-of-scope PRs | Chief Architect |
| R12 | Quantum-advantage claim without benchmark | HIGH | standing house rule | no claim without baseline + method | Veritas |

## Decision

**READY_FOR_CONTRACTS** — the audit is complete, every claim is traceable, and the blocking items (R1, R2) are founder decisions that do not prevent Phase 1 (contracts) from starting. No code was changed in this phase.

# TEAM_ALIGNMENT — single source of truth (2026-11-27)

Founder directive: expose every open point, align the team, remove conflicts.
Each row has a decision, an owner role and a standardized state.
States: IMPLEMENTADO / TESTADO / ESPECIFICACAO / EXPERIMENTAL / BLOQUEADO / NAO_VERIFICADO.

## 1. Open points and resolution

| # | Point | Conflict found | Decision | Owner role | State |
|---|---|---|---|---|---|
| 1 | Maturity of the trivalent gate | MATURITY.md says PRODUCAO, README says work in progress | MATURITY.md is authoritative at component level; README stays product level; reconciliation note in both | scientific-documentation | IMPLEMENTADO |
| 2 | ML-DSA-44 status | MATURITY.md says BETA, receipts.md says "declared roadmap" | BETA: implemented and verified locally, no external validation; receipts.md corrected | evidence-engineer | IMPLEMENTADO |
| 3 | License | House instruction BSL 1.1 + MIT vs repo LICENSE Apache-2.0 | Repo reality is Apache-2.0; no silent change, founder decision tracked in #156 | chief-architect | RESOLVIDO — Apache-2.0 prevalece (DOI 10.5281/zenodo.24250453, PyPI 2.5.9, LICENSE, pyproject); MIT é o depósito histórico v1.1.0; núcleo BSL vive fora deste repo. Ver docs/LICENSE_MAP.md |
| 4 | Hash algorithm | Receipts docs say SHA3-256, docker cert.py default is SHA-256 | SHA3-256 is canonical for receipts; SHA-256 only for legacy; migration in RFC-001 #154 | evidence-engineer | ESPECIFICACAO |
| 5 | Merge queue | 23 open PRs, several stacked | Fixed order 132, 131, 130, 120, 119, then Dependabot batch; never parallel | chief-architect | BLOQUEADO (checks) |
| 6 | Agent team | 9 profiles exist, Copilot agents are paid | Profiles stay ESPECIFICACAO; operation via AGENT_PROMPTS.md in plain Copilot Chat | chief-architect | ESPECIFICACAO |
| 7 | Internal algorithm WPs | Issues #146-#151 open without owner | Owners assigned in section 3 | chief-architect | ESPECIFICACAO |
| 8 | IBM job db85b0gr1c5c738lostg | Token expired, new secret not in sandbox | Stays BLOQUEADO; no result reported until the credential authenticates | quantum-engineer | BLOQUEADO |
| 9 | Isthmus submission | Parser required lowercase `- [x]` | RESOLVED: #1479 closed, bot opened PR #1480 | evidence-engineer | IMPLEMENTADO |
| 10 | CLA Assistant | Not installed; proposal pending | Skipped under the free-plan Copilot decision; revisit only if a contributor needs it | security-engineer | ESPECIFICACAO |
| 11 | Core Hardening 1.1 | Six fronts implemented, contract changes pending | PR #153 awaits independent review; contract changes in RFC-001 #154 | security-engineer | TESTADO (51 passed) |
| 12 | Gen 1 baseline | Audit done, docs published | PR #155 awaits review; decision READY_FOR_CONTRACTS | veritas-mathematical-auditor | IMPLEMENTADO |

## 2. Rules the whole team follows

1. No claim without a receipt, a job_id or a test that reproduces it.
2. No simulated result presented as hardware.
3. No fabricated benchmark, job id or success rate.
4. Hash proves integrity only, never truth, authorship or mathematical proof.
5. REFUSED is first-class, never coerced to 0 or 1.
6. No silent fallback between backends; every routing decision is recorded.
7. No merge to main without independent review and founder approval.

## 3. Work package ownership

| Issue | Work package | Owner role |
|---|---|---|
| #146 | WP2 conformance and falsifiability corpus | red-team + language-runtime-engineer |
| #147 | WP5 numerical precision contract | veritas-mathematical-auditor + hybrid-computing-architect |
| #148 | WP1 adapter contracts | quantum-engineer + hybrid-computing-architect |
| #149 | WP3 VERITAS verifier | evidence-engineer + veritas-mathematical-auditor |
| #150 | WP4 evidence index | evidence-engineer |
| #151 | WP7 tester onboarding | scientific-documentation |

## 4. What is NOT claimed

No quantum advantage. No universal OpenQASM 3 conformance. No independent reproduction yet. No production readiness of the hybrid kernel.

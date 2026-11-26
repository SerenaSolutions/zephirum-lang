# ZEPHIRUM SCIENTIFIC KERNEL CONSTITUTION (ZSKC)

**Version 1.0 · 2026-11-26 · Status: ESPECIFICAÇÃO (binding on all developers, researchers and AI agents of this repository)**

> **Golden rule.** The kernel does not exist to prove that ZEPHIRUM is right.
> It exists to prevent ZEPHIRUM from claiming to be right when it cannot demonstrate it.

## Preamble

This constitution defines the scientific identity of the ZEPHIRUM infrastructure before any
feature is added. It is a contract, not a manifesto. Every clause maps to an artifact that can
be inspected, executed or falsified in this repository.

## Article 1 — The three founding choices

1. **Mission: hybrid.** ZEPHIRUM is an infrastructure for classical-quantum hybrid computation:
   it decides what can be demonstrated classically, what requires quantum execution, and what
   must be refused.
2. **Governing principle: Proof → Compute.** Nothing executes without formal conditions of
   validity. The verdict (`1` / `0` / `REFUSED`) is produced offline; hardware is only a witness.
3. **Ambition: universal.** The infrastructure must serve different sciences, not one domain.
   Universality is earned by formal contracts (adapters, receipts, conformance), never by
   marketing breadth.

## Article 2 — The five layers and the integrity hierarchy

| Layer | Responsibility | Cannot claim |
|---|---|---|
| **ZEPHIRUM VERITAS** | integrity and certification of the whole stack | anything the lower layers cannot sustain mathematically |
| **Z# — Decision Core** | formal trivalent semantics: TRUE / FALSE / UNKNOWN(REFUSED) | a verdict without an interval that clears the declared band |
| **Scientific Kernel** | algebra, quantum state, operators, numeric precision | numerical precision it does not declare |
| **Hybrid Execution Layer** | CPU / GPU / QPU / simulators / backends | measurement where it only simulated |
| **Z-QEA — Evidence & Receipts** | provenance, integrity, reproducibility | a receipt for a run that did not happen |

**Article 2.1** — No layer may declare something the layer below cannot sustain mathematically.

## Article 3 — The six scientific commitments

1. **Mathematical integrity.** Every fundamental operation has a formal definition: domain,
   codomain, hypotheses and validity conditions. *Enforced by:* conformance corpus (`conformance/`),
   boundary tests (2^53 edge, rounding, partial means).
2. **Computational integrity.** No execution outside established conditions. Determinism where
   possible; physical randomness explicitly characterized. *Enforced by:* seeded reproducibility
   tests, `docker/` container parity.
3. **Epistemic integrity.** Absence of evidence is never converted into certainty. Unknown stays
   unknown; the boundary refuses instead of guessing. *Enforced by:* interval-clearance verdict
   logic; REFUSED as a first-class value.
4. **Physical integrity.** Simulation is never confused with measurement. *Enforced by:*
   SIMULATION MODE labels; backend + shots + job_id required in every published number.
5. **Evidence integrity.** Every verifiable claim carries evidence: receipt (SHA3-256 canonical
   seal, optional ML-DSA-44 signature) and, for hardware, the job id. *Enforced by:* `CLAIMS.md`
   classification (EVIDENCIA / PARCIAL / ROADMAP / NAO SUSTENTADO).
6. **Scientific falsifiability.** Any researcher must be able to try to prove the kernel wrong.
   Refutations are accepted into the CHANGELOG even when the maintainers disagree.
   *Enforced by:* `CALL_FOR_TESTERS.md`, Discussion #141 (adversarial verification, not endorsement).

## Article 4 — Claim discipline

1. Every public sentence about the project must appear in `CLAIMS.md`, classified.
2. Nothing above **EVIDENCIA** may be stated as fact in any public channel.
3. What is not claimed is stated explicitly (no quantum advantage; no integration-tested
   third-party adapters; no results beyond published receipts).
4. A claim that loses its evidence loses its status in the same commit that removes the evidence.

## Article 5 — Evidence states (house standard)

IMPLEMENTADO · TESTADO · REPRODUZIDO_INDEPENDENTEMENTE · FORMALMENTE_VERIFICADO ·
EXPERIMENTAL · ESPECIFICAÇÃO · NÃO_VERIFICADO · BLOQUEADO.
No artifact is described without one of these states.

## Article 6 — Infrastructure independence

The core must not depend exclusively on any vendor (hardware, cloud or model provider).
Adapters respect verifiable contracts; hardware is cited as a test laboratory only, never as
endorser or sponsor.

## Article 7 — Amendment

This constitution changes only by pull request that states (a) the clause, (b) the evidence
that motivates the change, (c) the falsification test that would justify reverting it.
Merging requires maintainer review; the change is recorded in the CHANGELOG.

## Signature

Issued under the authority of the founder, Reginaldo Pinezi Uhlmann (ORCID 0009-0005-3212-5179),
Serena Quantum Solutions. Executed by the house AI operations layer.
Co-authored-by: SerenaSolutions <gronovatech@gmail.com>

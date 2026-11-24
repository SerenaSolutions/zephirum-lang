# Call for independent testers — ZYQL / Z#

We are opening the exact-decision core (Z#) and the ZYQL runtime to independent testers.
The goal is adversarial verification, not endorsement.

## What you can test today
1. **Exact verdict before hardware.** Run the reference decision and compare it with your own computation. The verdict is produced offline; hardware is only a witness.
2. **Sealed receipts.** Every run emits a receipt with the verdict hash and, when hardware is used, the backend and job id. Try to forge one and tell us how.
3. **Conformance corpus.** Boundary cases: 2^53 arithmetic edge, cent rounding, range sums, partial means, and explicit refusal.
4. **Container reproducibility.** `docker run --rm ghcr.io/serenasolutions/zephirum-lang/infra test` and report any divergence from the documented versions.

## What we do NOT claim
1. We do not claim quantum advantage.
2. We do not claim hardware-verified results beyond the job ids published in `docs/EVIDENCIAS_QPU.md`.
3. We do not claim third-party adapters are integration-tested end to end.

## How to report
Open an issue with the template below. Reproducible failures get a public response and a receipt.

```
Environment: (OS, Python, image tag)
Case: (what you ran)
Expected:
Observed:
Receipt / job id:
Severity: (blocks correctness / cosmetic)
```

## Rules
1. No destructive testing against shared infrastructure.
2. Hardware runs respect the free-plan budget: 15 s per batch, 60 s per month for this repository.
3. Findings are published with credit unless you ask otherwise.

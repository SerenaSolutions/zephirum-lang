# Trivalent vs Boolean decision semantics

Boolean decision systems force a choice: 1 or 0, yes or no. The trivalent ZYQL core adds REFUSED,
and the difference is not cosmetic.

1. **Truth vs permission.** Booleans answer "is X true?". ZYQL answers "is X *decidable* right now,
   with the evidence at hand?" When the answer is no, you get REFUSED.
2. **Quantum grounding.** The core reads statistical dominance from a measured distribution
   (p0 of the interference pattern). Constant oracles produce dominance -> 1 or 0. Balanced oracles
   do not -> REFUSED. The verdict semantics map to physics, not to sentiment.
3. **Auditability.** Each verdict is sealed in a receipt (SHA3-256 + ML-DSA-44). An auditor sees not
   just the decision but the dominance data that produced it, and can verify the seal offline.

The cost: callers must handle three cases. The benefit: your failure mode becomes explicit data.

# Post-quantum receipts: SHA3 + ML-DSA-44 in practice

Every ZEPHIRUM experiment round ships a receipt designed to survive quantum computers.

Layer 1 (classical integrity): a SHA3-256 seal over the canonical JSON of the receipt payload.
Layer 2 (post-quantum authenticity): an ML-DSA-44 signature (FIPS 204, the NIST lattice signature
standard) over the same payload, with the *public key embedded in the receipt itself* — verification
needs no server, no account, no internet trust anchor.

The signature entropy is itself quantum: a measurement pool taken on IBM hardware
(`ibm_marrakesh`, sealed with its job id inside the receipt).

Practical notes we learned sealing real hardware rounds:

- Keep the canonicalization fixed (sorted keys, ensure_ascii, default=str) — a seal is only as
  stable as its serialization.
- Two layers, two failure modes: tampering breaks SHA3 instantly; a forged receipt fails ML-DSA
  verification even if the seal is recomputed consistently.
- Strict mode (`zqea-verify --strict-pq`) rejects receipts without the PQ layer. Legacy v1
  receipts remain valid but flagged.

See [Z-QEA Receipt Sealer / Verifier](https://github.com/SerenaSolutions/zqea-seal) for the
GitHub Actions that do this in CI.

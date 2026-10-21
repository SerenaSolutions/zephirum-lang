# GitHub Marketplace — Z-QEA Receipt Verifier

## Listing plan

- **Name:** Z-QEA Receipt Verifier
- **One-liner:** Verify the SHA3-256 seal of a Z-QEA receipt JSON — INTEGRAL
  passes the job, a broken seal fails it. *Nothing executes silently.*
- **Category:** Utilities → Security (CI/CD compliance checkpoint)
- **Action path (in-repo, legacy):**
  `uses: SerenaSolutions/zephirum-lang/.github/actions/zqea-verify@main`
- **Standalone marketplace repo (live):** https://github.com/SerenaSolutions/zqea-verify
  — use `uses: SerenaSolutions/zqea-verify@v1`. Release v1.0.0 published with
  self-test CI (sealed receipt passes, tampered receipt fails). Remaining step:
  owner's one-click publish in the Marketplace tab of the release page.

## Usage

```yaml
- name: Verify Z-QEA receipt
  uses: SerenaSolutions/zephirum-lang/.github/actions/zqea-verify@main
  with:
    receipt-file: experiments/s3_qutrit_final_receipt.json
```

Outputs: `status` (INTEGRAL/BROKEN), `seal` (recomputed SHA3-256).

## Pricing model (declared, honest)

- **Free forever:** this verifier — open source, MIT, no paywall. Its job is
  to make sealed receipts a public good.
- **Future hosted tier (declared roadmap):** signed receipts (ML-DSA-44 /
  FIPS 204, HSM-held keys), receipt registry and compliance reports —
  enterprise feature, priced separately. Nothing sold that does not exist.

## Compliance angle

Z-QEA receipts align with audit-trail expectations of governance standards
(e.g., ISO/IEC 42001 AI management, in-house editorial standard) — the Action
turns any CI pipeline into a checkpoint with tamper-evident evidence.

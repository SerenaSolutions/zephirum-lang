# GitHub Marketplace — Z-QEA Receipt Verifier

## Listing plan

- **Name:** Z-QEA Receipt Verifier
- **One-liner:** Verify the SHA3-256 seal of a Z-QEA receipt JSON — INTEGRAL
  passes the job, a broken seal fails it. *Nothing executes silently.*
- **Category:** Utilities → Security (CI/CD compliance checkpoint)
- **Action path (usable now, in-repo):**
  `uses: SerenaSolutions/zephirum-lang/.github/actions/zqea-verify@main`
- **Marketplace publishing:** move the action to its own public repo
  (`SerenaSolutions/zqea-verify`) and publish from there — requires the owner's
  click in the Marketplace tab. Draft ready.

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

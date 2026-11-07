# Zyclotron

Zyclotron is the experimental derivative-app synthesis layer for ZYQL. It does
not replace the ZYQL decision core. It compiles a validated blueprint into a
deterministic manifest that preserves evidence, constraints, rejected
alternatives, fail-closed runtime semantics, and SHA3-256 provenance hashes.

The compiler returns the same manifest and receipt for the same blueprint. It
returns `REFUSED` when evidence or constraints are missing, or when a blueprint
contains duplicate capabilities. A generated app remains a ZYQL derivative:
its runtime verdicts are `1`, `0`, and `REFUSED`.

```python
from zyclotron import compile_derivative_app

result = compile_derivative_app({
    "name": "audit_app",
    "purpose": "audit a decision pipeline",
    "evidence": ["receipt-001"],
    "constraints": ["fail closed"],
    "alternatives": ["unverified route"],
    "capabilities": ["inspect", "verify"],
})
assert result.decision == "1"
```

## Validation round

`experiments/zyclotron_round.py` runs 5,000 local state-vector trials: 1,000
trials at each level of 1,000, 2,000, 3,000, 4,000, and 5,000 shots. The first
round produced 100% classification accuracy for the tested constant and
balanced Deutsch-Jozsa cases. This is a simulator result, not a hardware-QPU
claim.

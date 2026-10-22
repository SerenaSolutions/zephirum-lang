# MIGRATION — bringing Zephirum into existing projects

## M1 — Into a Python project

```bash
pip install -e /path/to/zephirum-lang   # or add as a git dependency
```

- Kernel + gate + types: **pure Python stdlib, zero dependencies** — safe to
  embed anywhere.
- Photonic lab only: `numpy`, `scipy`.
- No install? `PYTHONPATH=src` works (the deterministic in-tree fallback).

```python
from zyql_quantum_gate import ZYQLQuantumGate
r = ZYQLQuantumGate(3, my_oracle).run_quantum()
if r["decision"] == "REFUSED":
    escalate_to_human(r)   # never retry silently — house rule
```

## M2 — The decision→receipt→verify pattern

1. Decide (Python, `.zph`, or C API) — a Z-QEA receipt is emitted.
2. Store the receipt with your artifact (it is plain JSON).
3. Verify at the gate: CI job, audit, or downstream consumer runs
   `zqea-verify`. A broken or missing seal fails the step.

Tamper-evidence for anything that must arrive exactly as sealed:
benchmark results, model cards, audit records.

## M3 — From Qiskit / OpenQASM 3 projects

- Out: `oq3.to_openqasm3(circuit.gates_applied, n)` — feed the output to
  Qiskit Runtime / any OpenQASM 3 consumer.
- In: `oq3.from_openqasm3(src)` — ingest existing OpenQASM 3.
- Round-trip is verified. Honest note: IBM ingests the compiled output;
  it does not run Zephyron natively.

## M4 — Into C projects

`src/zephirum.h` is the contract: one oracle call per decision, declared
noise band, canonical rational receipt (num/den — no 17-digit decimal
"truth"), SHA3-256 seal. ML-DSA-44 signatures on receipts are a declared
roadmap item (accredited CMVP module, HSM/KMS keys — never hand-rolled).

## M5 — Governance alignment

Receipts align with the audit-trail expectations of AI governance
standards (e.g. ISO/IEC 42001, in-house editorial standard): purpose,
rule class, decision, interference probability, oracle calls, noise
band, provenance, citations, timestamp, seal. The vendor of the QPU is
cited as test laboratory, never as endorser.

## M6 — Handling REFUSED (the part that changes your code)

In a binary codebase an ambiguous result is usually retried or guessed.
Here `REFUSED` is a first-class verdict: escalate, log the receipt,
degrade gracefully — do **not** loop the oracle until it answers 1 or 0.
The six refusal triggers are specified in `docs/ZYQL_REFUSED_SPEC.md`;
REFUSED never consumes QPU.

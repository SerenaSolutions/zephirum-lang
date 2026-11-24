# Validation path (staged)

The point of this document is that a stranger can check ZEPHIRUM without
trusting us first. Each stage is mechanical, fails loudly, and states what it
does **not** prove.

Run it:

```bash
pip install -e ".[pq]"      # optional extras used by the battery
python tools/validate_zephirum.py --battery --json validation_report.json
```

Exit `0` = every stage passed. Exit `1` = something failed. Exit `2` = the
harness itself could not run (never a pass).

## Stages

| Stage | What it checks | What it does **not** prove |
|---|---|---|
| E0 prerequisites | required core modules present; lists optional extras that are missing | that the extras are correctly installed |
| E1 version consistency | `VERSION` == `pyproject.toml` == `src/__init__.py` | that the release published matches this tree |
| E2 receipt seals | every receipt with a seal recomputes under the house canon (`selo_sha3_256` over `payload`; legacy `sha3_256` over the body) | authorship — a seal proves integrity, not who wrote it |
| E3 conformance | `conformance/run_conformance.py` returns CONFORMANTE | that the specification is the right one; only that the code matches the published spec |
| E4 test battery | `pytest tests` exits 0 | coverage; a passing battery is not a proof of correctness |
| E5 report seal | SHA3-256 over the canonical JSON of the whole report | that the environment is trustworthy |

The sealed report is the artifact to compare: same `report_sha3_256` on two
machines means the same verdict on the same tree.

## Runtime notes (measured, 2026-11-14)

Clean environment, Python 3.11.16: `E1`–`E3` pass; `E4` needs `qiskit-aer`
and `pqcrypto`. Without them the battery reports missing modules, not code
defects. With both installed: **119 passed, 4 skipped, 0 failed**.

Known wart, reported rather than patched here: `tests/test_kem.py` raises
`SystemExit(0)` at import time when `pqcrypto` is absent, which aborts the
whole pytest collection (`INTERNALERROR`) instead of skipping one file. The
honest fix is `pytest.importorskip("pqcrypto")`; it is left as a proposal
because it changes code owned by another front.

## Stage 2 (not implemented here)

Independent reproduction: a third party runs the command above and publishes
the `report_sha3_256` they obtained. Until that exists, everything in this
repository is self-verified. Self-verification is the weakest evidence level we
accept, and it is labelled as such.

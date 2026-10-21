# ZEPHIRUM — Public Roadmap

Declared in public, in the house honesty style: dates are intentions, scopes
are honest, nothing here is a promise of performance.

## Done

- **R1 — Packaging (v1.6.0):** `pip install -e .`, deterministic imports,
  broken quickstart fixed. *Status: shipped.*

## In progress

- **R0 — Scientific sweep harvest (v1.6.0):** 26-circuit sweep (braid angle,
  braid word, Pauli error map, chi-square per point) HARVESTED from IBM Heron
  `ibm_fez`, job `dbbuh17i0auc73dtpaeg`. Dominant channel 10/10, braid-word
  period 6/6, non-Abelian window measured at theta/pi in [0.3, 0.7].
  chi-square at 4096 shots detects sub-1% uncalibrated readout bias in all
  points — declared honestly; TV distance <= 4.5%. *Status: DONE.*

## Next

- **R2 — Generalized type layer:** extend `quantum_types.py` beyond the current
  circuit model (qutrit/qudit types already exercised in experiments; promote
  to first-class language types). *Depends on R3.*
- **R3 — Real compiler for `.zph`:** AST-based front end, type check, and
  OpenQASM 3 emission (today: transpiler + pre-parser). Semantic errors must
  stay explicit — nothing executes silently.
- **R4 — Benchmark protocol:** formal benchmark suite vs classical baselines
  under `docs/ZYQL_STATISTICAL_PROTOCOL.md`, including hardware calibration
  runs and drift validity windows.
- **R5 — ML-DSA-44 / FIPS 204 receipts:** migrate the SHA3-256 integrity seal
  to signed receipts via an accredited CMVP module with HSM/KMS-held keys.
  Never hand-rolled. *Declared since v1.5.0; unchanged.*

## Out of scope (permanent, by design)

- Zephirum OS distribution, bootloader, installer, activation keys.
- Claims of quantum advantage; useful executions without error correction are
  bounded well under 20 qubits (declared).

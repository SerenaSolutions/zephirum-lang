# Changelog

All notable changes to the ZEPHIRUM language are documented here.

## [1.4.3] - 2026-10-12
### Added
- `qif` quantum conditional (controlled-X decomposition, no collapse) - verified: Bell 1/2+1/2.
- First-class quantum types (`qbit`/`zyqbit`) with static no-cloning rejection.
- Native neural statement `zyql_rag`: docs -> BM25 -> translator -> interference gate -> receipt.
- Hardware confrontation vs textbook Qiskit (job db6dklcvf2bc73d122t0, ibm_fez): depth 2 / 0 two-qubit gates vs depth 10 / 3 CZ, both decide correctly.

## [1.0.0] - 2026-10-11
### Added
- Trivalent Deutsch-Jozsa decision gate with declared noise band (+-0.15).
- Z-QEA certificates with canonical rational arithmetic.
- ML-DSA-44 (FIPS 204) receipt sealing.
- IBM Quantum lab bridge (verified ingestion: job db4oqmcvf2bc73cutcgg).

## [0.3.0] - 2026-10-10
### Added
- Hybrid Stack (5 layers), RX/RY/RZ/SWAP/Toffoli, Pauli Monte Carlo noise.
- OpenQASM 3 round-trip import/export verified against the reference parser.

## [0.2.0] - 2026-10-09
### Added
- Zephyron -> OpenQASM 3 transpiler; state-vector kernel [re,im] float64.

## [0.1.0] "Ausra Bridge" - 2026-10-07
### Added
- State-vector kernel, parser (12 gates), Bell/GHZ/Grover/QFT verified.

# Changelog

All notable changes to the ZEPHIRUM language are documented here.

## [1.6.0] - 2026-10-21
### Added
- S3 qutrit miniature (experiments/): braiding non-commutativity and 3-channel
  fusion space (qutrit-in-qubits), noiseless with exact-zero deviation vs theory
  (canonical rational arithmetic) and verified on real hardware: IBM Heron
  ibm_fez, jobs dbbueufi0auc73dtp7og and dbbugbk24mrc73cif420; full ZYQL
  trivalent battery 3/3 PASS on hardware (receipt sealed in
  experiments/s3_qutrit_full_receipt.json). Scientific sweep of 26 circuits
  (job dbbuh17i0auc73dtpaeg) submitted; harvest pending.
- Packaging: pyproject.toml — `pip install -e .` exposes zkernel, zquantum,
  zyql_quantum_gate, quantum_types, zyql_rag_layer, oq3 as installable modules.
- docs/AUDIT.md: external audit record (GitHub Copilot audit, 2026-10-21) with
  our validation, findings and remediation status.
- docs/ROADMAP.md: public roadmap (compiler, type layer, benchmarks, FIPS 204).
- docs/PARTNERSHIP.md: GitHub partnership dossier.
- GitHub Pages deployment via GitHub Actions (site/).

- PennyLane cross-check (experiments/chemistry/pennylane_crosscheck.py):
  H2 VQE reproduces the battery FCI reference -1.13730604 Ha with error
  4.2e-09 (convention documented: PennyLane default unit is bohr; battery
  geometry is angstrom). Receipt sealed.
- New .zph examples: s3_qutrit.zph (fusion-space miniature), chemistry_h2.zph.
- .gitattributes: honest Linguist stats (receipts generated, assets vendored).
- docs/PROOFS.md: public index of proofs of concept (S3 non-Abelian
  miniature front and center) + proofs section on the Pages site.
- Scientific sweep harvested (job dbbuh17i0auc73dtpaeg, 26 circuits): braid
  angle sweep 10/10 dominant channels correct, non-Abelian window measured at
  theta/pi in [0.3,0.7]; braid-word period 6/6; Pauli error map exact.
  chi-square (4096 shots) fails in all points due to sub-1% uncalibrated
  readout bias — declared honestly; TV <= 4.5%. Master receipt re-sealed
  (C7). Data figure updated with all 10 measured points.
### Fixed
- Broken README quickstart: `from src.zyql_quantum_gate import ...` failed
  (sys.path.insert pointed at repo root, not src/). Modules now use a
  deterministic in-tree fallback and work installed or from source.
- Topics: removed typo tag `betta`.

## [1.5.0] - 2026-10-20
### Added
- Chemistry battery (experiments/chemistry): H2, LiH, H2O, NH3 — Jordan-Wigner
  mapping reproduces PySCF FCI exactly in all four molecules (error 0 / < 1e-10),
  battery receipt 85c20bc9. Nature-derived molecules through the full pipeline.
- Formal statistical protocol (docs/ZYQL_STATISTICAL_PROTOCOL.md): noise band
  d=0.15, binomial error bounds, minimum-shots formula, drift validity window.
- REFUSED formal spec (docs/ZYQL_REFUSED_SPEC.md): six triggers (R1-R6),
  bounded cost model (never consumes QPU), anti-DoS analysis, own receipt type.
- External audit response (docs/AUDIT_RESPONSE_2026-10-19.md): secrets scan
  clean over full history, dependencies locked (requirements-lock.txt).
### Changed
- Receipts documentation: SHA3-256 integrity seal is the implemented label;
  ML-DSA-44 (FIPS 204) signatures are a declared roadmap item (honest labeling).

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

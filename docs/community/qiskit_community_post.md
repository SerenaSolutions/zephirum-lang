# Trivalent quantum decisions with citable receipts: a Deutsch-Jozsa core validated across three Heron QPUs

**Post prepared for the Qiskit community (qiskit.slack.com) — scientific announcement, no marketing.**

---

## Summary

We report the validation of **ZYQL**, a trivalent exact-decision core built on
Deutsch-Jozsa interference, across **three IBM Quantum Heron processors**
(ibm_fez, ibm_kingston, ibm_marrakesh). Every run produces a sealed receipt
(SHA3-256 + ML-DSA-44, FIPS 204) binding the verdict to its job ID, backend,
calibration snapshot and shot count. The core decides `1 / 0 / REFUSED` and
never guesses silently: statistical margins are declared per verdict.

## Background

The Deutsch-Jozsa protocol [Deutsch & Jozsa, 1992] decides whether a boolean
oracle is constant or balanced with **one** oracle query, versus
`2^(n-1)+1` queries in the deterministic classical worst case. We extend this
to a three-valued decision semantics:

- constant-1 oracle → verdict **1**
- constant-0 oracle → verdict **0**
- balanced oracle → verdict **REFUSED** (no answer claimed; the circuit
  proves the answer space is split)

Margins use an adaptive Hoeffding bound (error epsilon, confidence delta
declared per decision), and a GHZ-state "device-trust gate" interrogates the
processor's coherence before any verdict is accepted.

## Experimental setup

- **Backends:** IBM Heron (127/156 qubit class): ibm_fez, ibm_kingston,
  ibm_marrakesh (IBM Quantum Open Plan)
- **Calibration at run time (ibm_kingston, 2026-10-24 20:25 UTC):**
  T1 = 242.8 us (mean), T2 = 184.0 us (mean), readout error = 2.02% (mean,
  best qubit 0.269%)
- **Shots:** 512-1024 per circuit; exact trivalent readout already achieved
  at 64 shots (Round B)
- **Verification:** results cross-checked in six quantum SDKs (Qiskit,
  OpenQASM 3, Cirq, PennyLane, Braket, Q#) with exact agreement
- **Receipts:** each run sealed with SHA3-256 integrity + ML-DSA-44
  authenticity; provenance chains link rounds

## Results (job IDs citable in the IBM Quantum platform)

1. **GHZ device-trust gate:** state fidelity **0.977** on ibm_kingston
   (job `dbdlb7424mrc739iievg`)
2. **Exact trivalent battery:** **9/9 exact** Deutsch-Jozsa decisions at
   n = 4, 5, 6 qubits (Round E), adaptive band +-0.042
3. **Bernstein-Vazirani [1997]:** secret recovered with p = 0.91
4. **Grover search [1996]:** n = 3 dominant p = 0.77; n = 4 target 1101
   found at p = 0.54 vs runner-up 0.06
5. **CHSH nonlocality [Clauser-Horne-Shimony-Holt, 1969]:** S = 2.71
   (theoretical 2.83) — clear violation of the classical bound S <= 2
6. **Repetition-code QEC:** single deterministic bit-flip injected (measured
   physical error 99.3%); majority vote leaves 1.5% logical error

## Discussion and limitations

We claim no error-corrected universal computation. Useful executions without
error correction remain limited (n <= 8 simulated; hardware runs reported
honestly with job IDs). The margins are statistical and declared; REFUSED is a
first-class outcome, not a failure. Hardware noise (readout ~2%) explains the
CHSH deficit (2.71 vs 2.83) within tolerance.

## Artifacts

- Code (MIT): https://github.com/SerenaSolutions/zephirum-lang
- Proof index with all job IDs: docs/PROOFS.md
- Hardware telemetry for the round above: experiments/round_f_hw_telemetry.json
- DOI: 10.5281/zenodo.23302046

## References

1. D. Deutsch, R. Jozsa. Rapid solutions of problems by quantum
   computation. Proc. R. Soc. Lond. A 439, 553 (1992).
2. E. Bernstein, U. Vazirani. Quantum complexity theory. SIAM J. Comput.
   26(5), 1411 (1997).
3. L. K. Grover. A fast quantum mechanical algorithm for database search.
   STOC '96, 212 (1996).
4. J. F. Clauser, M. A. Horne, A. Shimony, R. A. Holt. Proposed experiment
   to test local hidden-variable theories. Phys. Rev. Lett. 23, 880 (1969).
5. M. A. Nielsen, I. L. Chuang. Quantum Computation and Quantum Information.
   Cambridge Univ. Press (2000).

Questions and critique welcome — especially on the adaptive-margin design
and the repetition-code injection methodology.

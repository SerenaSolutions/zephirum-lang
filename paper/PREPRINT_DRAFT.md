# ZEPHIRUM: A Trivalent Decision Layer for Quantum Computing with Sealed Post-Quantum Receipts

**Maria Clara dos Anjos — SerenaSolutions, Campinas, Brazil. Draft v0.1 (target: quant-ph).**

## Abstract
Quantum software stacks force every outcome into a binary answer, laundering
statistical noise into false certainty. We present ZEPHIRUM, a trivalent
decision layer whose verdicts are 1 (affirmed), 0 (refuted) or REFUSED (the
declared margin does not resolve the claim). Margins are declared before data
(anti-peeking) via Hoeffding bounds with family-wise correction; every verdict
emits a sealed receipt (SHA3-256 canonical chain, ML-DSA-44 / FIPS 204
signatures) that is independently verifiable. On superconducting hardware the
layer confirmed a constant oracle within 256 shots (96.9% economy vs a fixed
8192-shot budget) and REFUSED gray-zone evidence with zero false confirmations
across 1,200 trials.

## 1. Introduction
The integrity gap in near-term quantum computing is not speed but honesty:
decisions are reported without declared margins, and noise becomes a green
checkmark. ZEPHIRUM positions decision — not execution — as the auditable unit.

## 2. The Trivalent Decision Core
Declared rule before data; one-sided Hoeffding band
b = sqrt(ln(1/alpha)/(2*shots)), alpha = epsilon/family (Bonferroni);
refusal taxonomy (INSIDE_NOISE_BAND, INSUFFICIENT_CONFIDENCE, CHAIN_BROKEN,
DEVICE_DECOHERED, GRADIENT_VANISHED) as first-class machine-readable outputs.

## 3. Sealed Receipt Chain (Z-QEA)
Canonical form (sorted keys, exact JSON), SHA3-256 seal over the receipt minus
the seal field, chained to the previous receipt; tampering with any historical
receipt breaks the chain on re-verification. Signatures per FIPS 204.

## 4. Efficiency Benchmarks (silicon leg, 156-qubit superconducting backend)
Kernel A (shots-to-verdict, early stop): verdict at 256 shots on hardware;
99.22% economy in noiseless simulation (64 vs 67 Hoeffding minimum vs 8192).
Kernel B (refusal fidelity): zero false confirmations in the gray zone
(p0 = 0.5625, 0.25) across 1,200 trials; REFUSED_BALANCED on balanced oracles.
Sealed receipts: 26-entry chain, verification battery ALL PASS.

## 5. Cross-SDK Parity
Identical trivalent verdicts (p0 = 1.0 / 0.0 exact) across four independent
paths (Qiskit, Cirq, PennyLane, OpenQASM 3 round-trip), sealed receipt efd0bb92.

## 6. Ecosystem Integration
Open source (MIT); bridges to seven quantum and classical stacks; CI decision
Action; Qiskit Ecosystem submission (PR #1433) under review at time of writing.

## 7. Reproducibility
All code, tests (81 permanent), receipts and benchmark protocols are public;
every number in this paper maps to a sealed receipt in the repository chain.

## References
Hoeffding (1963); NIST FIPS 204 (2024); project repository and receipt chain
(SerenaSolutions/zephirum-lang); book DOI 10.5281/zenodo.23676803.

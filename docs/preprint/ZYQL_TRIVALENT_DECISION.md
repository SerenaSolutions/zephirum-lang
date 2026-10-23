# ZYQL: A Trivalent Decision Core for Quantum Programs — draft v0.1

**Abstract.** Boolean decision systems silently coerce uncertainty into certainty. We present ZYQL,
a trivalent decision core (verdicts 1 / 0 / REFUSED) grounded in measured statistical dominance of
quantum interference, implemented as the ZEPHIRUM language and validated on IBM Heron superconducting
processors across 64-16384 shots with exact trivalent verdicts and zero spurious refusals. All
experimental rounds are sealed in two-layer receipts (SHA3-256 + ML-DSA-44, FIPS 204) whose public
keys are embedded, enabling offline third-party verification.

**1. Motivation.** Deutsch-Jozsa (DJ) gives a canonical witness for decision confidence: constant
oracles produce a dominant measurement (p0 -> 1); balanced oracles do not. We treat dominance as
the *decidability* criterion: absent dominance, the core returns REFUSED rather than an arbitrary
bit.

**2. Core.** The ZYQL gate runs DJ-style interference with one oracle call plus a classical probe,
producing verdicts: 1 (permitted, dominant-zero), 0 (forbidden, dominant-nonzero constant), REFUSED
(balanced / no dominance). The threshold theory for n=3 predicts exact verdicts above ~29-82 shots
(P=|a|^2 etc.); see docs/ZYQL_STATISTICAL_PROTOCOL.md.

**3. Hardware validation.** Round A (512-16384 shots, ibm_fez) and Round B (64-384 shots,
ibm_kingston; jobs dbdac41gv2cc738hnen0, dbdac47i0auc739521vg, dbdac4c24mrc73cl3ia0,
dbdac4ni0auc73952200): exact trivalent verdicts at every shot level, including 64 shots. Cross-language
agreement (Qiskit, OpenQASM 3, Cirq, PennyLane, Braket) is exact in simulation.

**4. Sealing.** Each round is sealed: SHA3-256 over canonical JSON + ML-DSA-44 signature; entropy
attestation from an IBM measurement pool (job dbcnmds24mrc73ck0p0g, ibm_marrakesh).

**5. Limitations.** Research prototype; classical-layer parser is minimalist; hardware claims are
reproducible with any IBM Quantum open-plan account (credentials cannot ship with artifacts by design).

**6. Availability.** https://github.com/SerenaSolutions/zephirum-lang (MIT). Future work: formal
semantics of REFUSED composition, continuous public benchmark (issue #28).

*Draft for arXiv (quant-ph / cs.PL) and Zenodo deposit. Data: experiments/ with sealed receipts.*

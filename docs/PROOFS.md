# Proofs of Concept — index

Every proof below is executable from this repository, carries a Z-QEA receipt
(SHA3-256 integrity seal), and cites laboratory job IDs where hardware was
used. IBM is cited as a test laboratory, never as an endorser.

## 1. Non-Abelian anyons — S3 qutrit miniature ⭐

**Claim proven (in miniature, scope declared):** the fusion space of a
non-Abelian anyon pair is 3-dimensional (a qutrit in 2 qubits) and **braiding
order is physically distinguishable** — the non-Abelian signature.

| Evidence | Mode | Result | Receipt |
|----------|------|--------|---------|
| Fusion channels (C1) | noiseless | exact 1/3+1/3+1/3, forbidden channel vetoed | `experiments/s3_qutrit_final_receipt.json` |
| Braiding non-commutativity (C2) | noiseless | commutator L1 norm = 6 (exact); B_R∘B_S → ch2, B_S∘B_R → ch1 | same |
| Noiseless round (C3) | noiseless | **total deviation vs theory = 0**, canonical rational arithmetic | same |
| ZYQL trivalent kernel (C4) | noiseless | 1 / 0 / REFUSED with 1 oracle call, 3/3 cases | same |
| Hardware miniature (C5) | **IBM Heron ibm_fez** | ch2 = 98.1% (job `dbbueufi0auc73dtp7og`) vs ch1 = 95.8% | same |
| ZYQL battery on hardware (C6) | **IBM Heron ibm_fez** | decisions 1, 0, REFUSED — 3/3 PASS (job `dbbugbk24mrc73cif420`) | `experiments/zyql_hardware_battery.json` |

- Script: `experiments/s3_qutrit_miniature.py` (noiseless, exact)
- Hardware submission: `experiments/submit_fez.py`, `experiments/zyql_hardware_battery.py`
- Master receipt seal: `a44192463ea669564a3da51728c8577e59e5684c67cf2d48f7a95442d548476a`
- In language: `examples/s3_qutrit.zph`
- News: QALQON — "the braid order is distinguishable on silicon"
  (https://serenasolutions.github.io/qalqon-quantum-ia/zephirum-v160.html)

**Expanded scientific sweep (26 circuits):** braid-angle sweep, braid-word
sweep and Pauli error map with chi-square per point — submitted to ibm_fez,
job `dbbuh17i0auc73dtpaeg`; harvest pending (roadmap R0). Scripts already in
repo: `experiments/scientific_sweep.py`, `experiments/analyze_sweep.py`.

## 2. Chemistry battery — exact classical validation

H2, LiH, H2O, NH3 via Jordan-Wigner: reproduces PySCF FCI exactly
(error 0 / < 1e-10). `experiments/chemistry/` — battery receipt `85c20bc9`.

## 3. PennyLane cross-check

H2 VQE (default.qubit) reproduces the battery FCI reference
-1.13730604 Ha with error 4.2e-09 — independent engine, same reference.
`experiments/chemistry/pennylane_crosscheck.py`
(receipt `4c6ef51c…`, convention documented: PennyLane default unit is bohr;
battery geometry is angstrom).

## 4. Deutsch-Jozsa trivalent gate on hardware

Constant purpose p(000) = 0.9844 (job `db6ded84qg6s73c4jvug`); same-task
confrontation vs textbook Qiskit (job `db6dklcvf2bc73d122t0`): depth 2 /
0 two-qubit gates vs depth 10 / 3 CZ. See README and `docs/`.

## 5. Minimum shots for reliable trivalent decision (Hardware Validation) ⭐

**Problem dossier:** [`docs/PROBLEM.md`](PROBLEM.md) — empirical reliability of ZYQL trivalent decision (1 / 0 / REFUSED) under hardware readout noise.

| Evidence | Mode | Result | Receipt |
|----------|------|--------|---------|
| Shot sweep (512 to 16384) | **IBM Heron ibm_fez** | 100% accuracy (3/3 cases across 6 shot levels), 0 spurious refusals | [`experiments/refusal_receipt.json`](../experiments/refusal_receipt.json) |
| Protocol verdict | Hardware validation | **VALIDADO** in interval [512, 16384] shots | same |
| Low-shot sweep (64 to 384) | **IBM Heron ibm_kingston** | 100% accuracy (3/3 cases across 4 shot levels), verdicts EXATO down to 64 shots — **sub-512 gap CLOSED** | [`experiments/round_b_receipt.json`](../experiments/round_b_receipt.json) |

- Hardware: IBM Heron `ibm_fez` (open plan, test laboratory)
- Jobs: `dbcjf7ni0auc73dv36ug` (512), `dbcjf7pgv2cc73eaft1g` (1024), `dbcjf7vi0auc73dv36vg` (2048), `dbcjf81gv2cc73eaft20` (4096), `dbcjf87i0auc73dv3700` (8192), `dbcjf8fi0auc73dv370g` (16384)
- Master receipt seal: `9cd39440a49373600b6d1eaf79e22f6e2bdacf133491c9faf748ec71a1be9b3a`
- Full details in [`docs/ZYQL_STATISTICAL_PROTOCOL.md`](ZYQL_STATISTICAL_PROTOCOL.md#6-validação-em-hardware).

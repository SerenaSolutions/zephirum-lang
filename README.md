<p align="center"><img src="assets/social-preview-1280x640.png" alt="ZYQL: Exact-decision language" width="640"></p>

# ZEPHIRUM

*The quantum programming language with receipts.*

![version](https://img.shields.io/badge/version-1.6.0-6e46b8)
![license](https://img.shields.io/badge/license-MIT-blue)
![kernel](https://img.shields.io/badge/kernel-statevector%20%5Bre%2Cim%5D%20float64-cyan)
![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.23302046-gold)

## Evidence — with the quantum figures

![S3 fusion channels measured on IBM Heron](assets/proofs/s3-fusion-hardware.png)

*Real-data figure: theoretical braid curves (gold: B_R∘B_S, violet: B_S∘B_R) and the
points measured on IBM Heron `ibm_fez` — 98.1% vs 95.8%. The braid order is
distinguishable on silicon. Full detail: [docs/PROOFS.md](docs/PROOFS.md).*

![Non-Abelian anyon braiding — AI art](assets/proofs/non-abelian-braids-art.png)

*Hero art (declared: AI-generated) — braided world-lines of non-Abelian anyons
converging into three fusion channels, the geometry the experiments probe.*

### Proofs of concept — non-Abelian anyons (S3 qutrit miniature)

| Claim | Mode | Result | Receipt |
|-------|------|--------|---------|
| Fusion space is 3-dimensional (qutrit in 2 qubits) | noiseless | exact 1/3+1/3+1/3, forbidden channel vetoed | [sealed receipt](experiments/s3_qutrit_final_receipt.json) |
| Braiding is non-Abelian (order matters) | noiseless | commutator L1 = 6 exact; B_R∘B_S → ch2, B_S∘B_R → ch1 | same |
| Noiseless round | noiseless | exact-zero deviation vs theory (canonical rationals) | same |
| ZYQL trivalent decisions 1 / 0 / REFUSED | **IBM Heron** | **3/3 PASS** (job `dbbugbk24mrc73cif420`) | [battery receipt](experiments/zyql_hardware_battery.json) |
| Braid order measured on real hardware | **IBM Heron** | **98.1% vs 95.8%** (job `dbbueufi0auc73dtp7og`) | [master receipt](experiments/s3_qutrit_final_receipt.json) |

Receipt seal (SHA3-256): `0277e09b78644a7193559b07f72590ec5705b11eeb7d4331a9e03962a4b30751`.
In language: [`examples/s3_qutrit.zph`](examples/s3_qutrit.zph).

ZEPHIRUM is a small quantum programming language. ZYQL is its decision algorithm:
every computational decision is trivalent - `1` (permitted), `0` (forbidden),
`REFUSED` (input-dependent or insufficient confidence) - and carries a sealed
receipt (SHA3-256 integrity seal, hash proves content integrity, not authorship).
ML-DSA-44 / FIPS 204 signatures are a DECLARED ROADMAP item — to be implemented
with an accredited module and HSM-held keys, never hand-rolled (see docs/receipts.md).

Decisions are produced by Deutsch-Jozsa interference, one oracle call, with a
declared noise band (+-0.15). Nothing executes silently: unknown syntax raises
an explicit error. Simulation mode is labeled as simulation.

Verified on real hardware (IBM Heron `ibm_fez`, cited as test laboratory with
verifiable job IDs; no endorsement claimed):
- Constant purpose: measured p(000)=0.9844 (job db6ded84qg6s73c4jvug)
- S3 qutrit miniature: fusion channels (qutrit-in-qubits) + braiding non-commutativity,
  noiseless with exact-zero deviation and on hardware: ch2=98.1% (RS) vs ch1=95.8% (SR),
  full ZYQL battery 3/3 PASS on `ibm_fez` (jobs `dbbueufi0auc73dtp7og`, `dbbugbk24mrc73cif420`;
  Z-QEA receipt sealed, see `experiments/`)
- Balanced purpose: p(000)=0.0000, orthogonal outcome 93.9%
- Same-task confrontation vs textbook Qiskit (job db6dklcvf2bc73d122t0):
  Zephyron transpiles to depth 2 / 0 two-qubit gates vs depth 10 / 3 CZ

The language:

```
circuit bell {
  qubit[2] q;
  H q[0];
  CNOT q[0] -> q[1];
}
```

## Quickstart

```bash
pip install -e .
python -c "from zyql_quantum_gate import ZYQLQuantumGate; \
g = ZYQLQuantumGate(3, lambda x: 1); print(g.run_quantum())"
```

(No install? `PYTHONPATH=src` works too. The old `from src.zyql_quantum_gate`
quickstart was broken — fixed in v1.6.0, see docs/AUDIT.md.)

## Layout

- `src/` - kernel (state-vector), OpenQASM 3 transpiler, trivalent gate,
  quantum types (no-cloning enforced), neural RAG layer
- `examples/` - `bell.zph`, `grover.zph`, `dj_constant.zph`
- `tests/` - canonical rational test battery
- `docs/` - language reference, receipt specification

## Honest scope

This repository contains the language heart only: kernel, types, gate, receipts.
It does not contain, and will never contain, the Zephirum OS distribution,
bootloader, installer, or activation keys. Simulations are labeled as
simulations; without error correction, useful executions are bounded well
under 20 qubits.

## Citation

See `CITATION.cff`. Software deposit: Zenodo concept DOI 10.5281/zenodo.23302046
(code MIT, companion thesis CC BY-NC-ND 4.0), (c) Serena Solutions.

## License

MIT - see [LICENSE](LICENSE).

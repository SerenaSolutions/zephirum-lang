# ZEPHIRUM — Learn Zephirum (progressive tutorial)

From first decision to sealed hardware receipts, one level at a time.
House rule: nothing below is aspirational — every command was executed and
its output recorded from this repository. When something is a roadmap item,
it says so.

## Level 0 — What you are actually learning

ZEPHIRUM's core is **not** a quantum circuit simulator. The core is the
**ZeptonQL trivalent decision**: every question returns exactly one of
`1`, `0` or `REFUSED` — and `REFUSED` is a first-class answer, never an
error (`docs/ZYQL_REFUSED_SPEC.md`). Quantum execution is an **optional
layer** on top. Every decision emits a **Z-QEA receipt** (SHA3-256 seal,
`docs/receipts.md`) so nothing executes silently.

## Level 1 — Install

```bash
git clone https://github.com/SerenaSolutions/zephirum-lang
cd zephirum-lang
pip install -e .          # deterministic imports (audit fix #1, v1.6.0)
```

No install? `PYTHONPATH=src` works too. The kernel is pure Python stdlib;
`numpy`/`scipy` are needed only by the photonic lab.

## Level 2 — Your first trivalent decision

```bash
python -c "from zyql_quantum_gate import ZYQLQuantumGate; \
import json; print(json.dumps(ZYQLQuantumGate(3, lambda x: 1).run_quantum(), indent=1))"
```

Recorded output:

```json
{
 "decision": 1,
 "mode": "DECIDED_BY_INTERFERENCE",
 "p0": 1.0,
 "rule": "band>=0.85",
 "error_bound": 1.8899509952982437e-40,
 "error_bound_type": "Hoeffding"
}
```

One oracle call decided it — Deutsch-Jozsa interference, not sampling.
`error_bound` is a declared statistical bound, not a promise.

## Level 3 — The three verdicts and the noise band

Change the oracle to an input-dependent (balanced) function:

```python
ZYQLQuantumGate(3, lambda x: x ^ 1).run_quantum()
```

Recorded output:

```json
{
 "decision": "REFUSED",
 "mode": "INSUFFICIENT_CONFIDENCE",
 "p0": 0.58251953125,
 "rule": "inside noise band (+-0.15), margin declared"
}
```

The interference pattern landed **inside the ±0.15 noise band** — the gate
refuses rather than guess. This is the design decision of the whole
language: `REFUSED` stands under noise. The band, its calibration and the
minimum-shots formula are formalized in
`docs/ZYQL_STATISTICAL_PROTOCOL.md`.

## Level 4 — The `.zph` surface

Owner decision (2026-10-21, `docs/ZYQL_LISP_SPEC.md`): the surface syntax
is **Lisp s-expressions**. Decisions and their audit trail share one
readable shape. Example — the classical trivalent core (`examples/decision_lisp.zph`):

```lisp
(decide (model governance) (purpose "Is use x permitted?")
  (rule (oracle all-ones)  -> 1)
  (rule (oracle all-zeros) -> 0)
  (rule (oracle balanced)  -> REFUSED))
```

Note: an earlier `circuit NAME { ... }` syntax (v1.4.3, `docs/language.md`)
still lives in `examples/bell.zph`, `grover.zph` and friends. Both surfaces
are documented; nothing was deleted silently.

## Level 5 — Quantum forms and the photonic lab

Quantum programs are explicit `(quantum ...)` forms. The photonic lab
(`examples/photon_battery.zph`) runs on an exact Fock simulator —
**no shots, no hardware, no shots faked**:

```bash
PYTHONPATH=src python src/zyql_lisp.py examples/photon_battery.zph
```

Recorded output:

```
ZYQL PHOTON LAB: round5-fotonica
  [hom-bunching] HOM_OK
  [mzi-interference] INTERFERENCIA_OK
  [trivalent:const-0] decisao=0
  [trivalent:const-1] decisao=1
  [trivalent:balanced] decisao=REFUSED
  [braid-order] ORDEM_IMPORTA
SELO: 0080b1e22b3bb9c34ffa3680bea4ff73c1536ef29d26c202477eb54ecc568fa6
recibo: experiments/round5_photonic_receipt.json
```

The receipt is emitted **by the language itself**.

## Level 6 — Types: no-cloning, enforced before execution

`quantum_types.py` makes the qbit a first-class type. Copying one is a
**type error**, raised at check time, before any execution:

```python
from quantum_types import QuantumLang, CompileError
L = QuantumLang(2)
q = L.qbit("q")
q.clone()   # CompileError: NO_CLONING: quantum value cannot be copied
```

## Level 7 — Receipts: verify, never trust

Every receipt carries `selo_sha3_256` — SHA3-256 over its canonical JSON.
Verify any receipt locally:

```bash
python .github/actions/zqea-verify/zqea_verify.py <receipt.json> --strict-pq
```

or in CI with the Marketplace Action (`SerenaSolutions/zqea-verify@v1`,
input `receipt-file`). Integrity is proven; authorship is not — the
security scope is declared in the Action's README.

## Level 8 — Real hardware: the honest bridge

IBM will never run Zephyron natively. `src/oq3.py` transpiles to
OpenQASM 3 (emit and ingest, round-trip verified) and Qiskit Runtime
ingests the compiled output. Hardware runs record the IBM job ID in the
receipt; the vendor is cited as test laboratory, never as endorser.
Provenance example: IBM Heron `ibm_fez`, sweep job `dbbuh17i0auc73dtpaeg`.

## Level 9 — CI battery

```bash
ZQG_MODE=battery python src/battery_ci.py            # trivalent battery
ZQG_MODE=verify-receipts python src/battery_ci.py     # re-seal every receipt
```

Exit 0 = all pass; any failure exits 1. Nothing passes silently — the CI
of this repository runs exactly this battery.

## Where to go next

- `docs/COOKBOOK.md` — copy-paste recipes
- `docs/MIGRATION.md` — bringing Zephirum into Python, C and CI
- `docs/REVIEW_REQUEST.md` — what independent reviewers are invited to attack
- `docs/ROADMAP.md` — what is declared, not claimed

# ZEPHIRUM Cookbook — recipes that actually ran

Every recipe below was executed against this repository; outputs shown are
recorded, not invented. Copy, paste, adjust the oracle.

## R1 — Trivalent decision from Python

```python
from zyql_quantum_gate import ZYQLQuantumGate
r = ZYQLQuantumGate(3, lambda x: 1).run_quantum()
# {'decision': 1, 'mode': 'DECIDED_BY_INTERFERENCE', 'p0': 1.0, ...}
```

One oracle call. For an input-dependent oracle the gate answers `REFUSED`
(inside the ±0.15 noise band) instead of guessing.

## R2 — Governance rule with REFUSED as policy

```lisp
;; examples/decision_lisp.zph
(decide (model governance) (purpose "Is use x permitted?")
  (rule (oracle all-ones)  -> 1)
  (rule (oracle all-zeros) -> 0)
  (rule (oracle balanced)  -> REFUSED))
```

Map `REFUSED` to "escalate to a human" in your application — the receipt
records why the gate refused.

## R3 — Verify a receipt locally (strict post-quantum layer)

```bash
git clone https://github.com/SerenaSolutions/zqea-verify
python zqea-verify/zqea_verify.py receipt.json --strict-pq
# Z-QEA: VERIFICADO — selo íntegro + ML-DSA-44 válido  (exit 0)
```

## R4 — Verify receipts in CI (Marketplace Action)

```yaml
- name: Verify Z-QEA receipt
  uses: SerenaSolutions/zqea-verify@v1
  with:
    receipt-file: experiments/s3_qutrit_final_receipt.json
```

A broken seal fails the job. Outputs: `status` (INTEGRAL/BROKEN), `seal`.

## R5 — Seal any JSON artifact in CI

```yaml
- uses: SerenaSolutions/zqea-seal@v2
  with:
    artifact: results/benchmark.json
```

The writing counterpart of the verifier: any artifact leaves CI sealed.

## R6 — Trivalent battery in any CI, offline

```bash
ZQG_MODE=battery python src/battery_ci.py
# constant-1 => 1, constant-0 => 0, balanced => REFUSED, 1 oracle call each
ZQG_MODE=verify-receipts python src/battery_ci.py   # re-seal every receipt in experiments/
```

No IBM account needed. Exit 1 on any failure. Or use the Action:
`uses: SerenaSolutions/zq-gate@v1`.

## R7 — First circuit: a Bell pair

```python
from zquantum import QCircuit
qc = QCircuit(2)
qc.h(0); qc.cnot(0, 1)
print(qc.measure_all(shots=1024))
```

## R8 — Deutsch-Jozsa with a trivalent verdict

```python
r = ZYQLQuantumGate(6, your_oracle).run_quantum()
# constant oracle -> 1 or 0; balanced -> REFUSED (never silently 1/0)
```

## R9 — Emit OpenQASM 3 for a real backend

```python
from zquantum import QCircuit
from oq3 import to_openqasm3
qc = QCircuit(2); qc.h(0); qc.cnot(0, 1)
print(to_openqasm3(qc.gates_applied, qc.n))
# OPENQASM 3.0; include "stdgates.inc"; ... — ingest with Qiskit Runtime
```

`oq3.from_openqasm3` goes the other way (round-trip verified). IBM runs
the compiled output, never Zephyron natively — declared, not hidden.

## R10 — Photonic lab on your machine

```bash
PYTHONPATH=src python src/zyql_lisp.py examples/photon_battery.zph
# 6 tests: HOM, MZI, trivalent 0/1/REFUSED, braid order — sealed receipt
```

Dual-rail photonic qubits on an exact Fock simulator. The receipt declares
`SIMULACAO FOTONICA LOCAL` — no shots faked.

## R11 — Chemistry battery (classical cross-check)

`experiments/chemistry/` — H2, H2O, LiH, NH3 vs PySCF FCI with declared
error figures (chem_H2 battery reproduces FCI with error 0). Run:

```bash
python experiments/chemistry/chemistry_battery.py
```

## R12 — C integration

`src/zephirum.h` declares the public C surface of the trivalent core:
one oracle call per decision, declared noise band, canonical rational
receipt (num/den), SHA3-256 seal. Bindings sit above this contract —
nothing decides above the core.

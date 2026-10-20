# Chemistry battery — nature-derived molecules

FCI reference (PySCF) x Jordan-Wigner mapping (Qiskit) x variational pipeline.
STO-3G basis. Simulation labeled DECLARED_CLASSICAL (statevector).

| Molecule | Qubits (JW) | FCI (Ha) | Mapped (Ha) | Mapping error |
|---|---|---|---|---|
| H2  | 4  | -1.137306 | -1.137306 | 0.0 |
| LiH | 12 | -7.882402 | -7.882402 | < 1e-10 |
| H2O | 14 | -75.012647 | -75.012647 | 0.0 |
| NH3 | 16 | -55.519086 | -55.519086 | 0.0 |

Run: `python3 chemistry_battery.py H2 LiH H2O NH3`
Battery receipt (SHA-256 over canonical results): 85c20bc9a0bd0c7e...
VQE limitation declared: shallow ansatz (depth 1, 120 sandbox iterations);
chemistry-grade ansaetze (UCCSD) and hardware execution are future work.

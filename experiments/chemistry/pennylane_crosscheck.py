# -*- coding: utf-8 -*-
"""PennyLane cross-check for the chemistry battery: H2 ground state.

House honesty: this is a SIMULATION (default.qubit, classical statevector).
Reference: PySCF FCI at the battery geometry (H2, 0.735 A, STO-3G,
-1.13730604 Ha — same reference as experiments/chemistry/chem_H2.json).
Conventions that matter (learned the honest way):
  - PennyLane molecular_hamiltonian default unit is BOHR; battery geometry
    is 0.735 ANGSTROM. unit="angstrom" is mandatory for apples-to-apples.
Receipt: Z-QEA, canonical rational error, SHA3-256 seal.

Dependency: pennylane>=0.41 + pyscf (not part of core language requirements).
"""
import json, time, hashlib
import pennylane as qml
from pennylane import numpy as np

REF_FCI_H2 = -1.13730604   # Ha, PySCF FCI, H2 0.735 A STO-3G (house battery)
GEOMETRY_ANGSTROM = 0.735  # matches experiments/chemistry/chem_H2.json

symbols = ["H", "H"]
coords = np.array([[0.0, 0.0, 0.0], [0.0, 0.0, GEOMETRY_ANGSTROM]])
H, n_wires = qml.qchem.molecular_hamiltonian(
    symbols, coords, method="pyscf", basis="sto-3g", unit="angstrom")

dev = qml.device("default.qubit", wires=n_wires)

@qml.qnode(dev)
def energy(theta):
    qml.PauliX(0)                                  # HF reference |1100>
    qml.PauliX(1)
    qml.DoubleExcitation(theta, wires=[0, 1, 2, 3])  # paired doubles ansatz
    return qml.expval(H)

e_hf = float(energy(0.0))
opt = qml.GradientDescentOptimizer(stepsize=0.4)
theta = np.array(0.0, requires_grad=True)
for _ in range(60):
    theta = opt.step(energy, theta)
E = float(energy(theta))
err = abs(E - REF_FCI_H2)

from fractions import Fraction
receipt = {
    "spec": "Z-QEA",
    "modulo": "experiments/chemistry/pennylane_crosscheck.py",
    "data": time.strftime("%Y-%m-%dT%H:%M:%S-03:00"),
    "modo": "SIMULACAO (pennylane default.qubit, VQE gradient descent, 60 iter)",
    "molecula": "H2 0.735 A STO-3G",
    "referencia": "PySCF FCI -1.13730604 Ha (bateria da casa, chem_H2.json)",
    "e_hf_hartree": round(e_hf, 8),
    "energia_vqe_ha": round(E, 8),
    "erro_vs_fci": round(err, 10),
    "erro_exato_frac": str(Fraction(err).limit_denominator(10**9)),
    "theta_final": round(float(theta), 8),
    "engine": "pennylane %s + pyscf" % qml.__version__,
    "declaracao": "cross-check independente da bateria quimica; convencao unit=angstrom obrigatoria",
}
canon = json.dumps(receipt, sort_keys=True, ensure_ascii=True)
receipt["selo_sha3_256"] = hashlib.sha3_256(canon.encode()).hexdigest()
json.dump(receipt, open("pennylane_crosscheck_receipt.json", "w"), indent=2)
print("E_HF =", round(e_hf, 8), "| E_VQE =", round(E, 8),
      "| erro vs FCI =", round(err, 10))
print("selo:", receipt["selo_sha3_256"][:32])

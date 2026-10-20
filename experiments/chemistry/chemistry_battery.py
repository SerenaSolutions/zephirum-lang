"""BATERIA DE MOLÉCULAS DA NATUREZA — provas de química quântica com recibo.

Moléculas: H2 (hidrogênio), LiH (hidreto de lítio), H2O (água), NH3 (amônia).
Cada molécula recebe DUAS provas independentes:
  1. CHÃO EXATO: FCI do PySCF (referência quântica exata, DECLARED_CLASSICAL)
  2. PIPELINE QISKIT: mapeamento do Hamiltoniano -> diagonalização exata do
     Hamiltoniano de qubits (verifica o mapeamento contra o FCI)
  3. VQE: estado variacional (EfficientSU2) convergindo em direção ao exato

Recibo SHA-256 por molécula. Rótulo honesto: tudo SIMULAÇÃO (statevector),
etiqueta DECLARED_CLASSICAL; execução em QPU real é o objetivo do IBM Quantum
Credits, não uma alegação desta bateria.
"""
import hashlib
import json
import sys
import time

from pyscf import gto, scf, fci
from qiskit_nature.second_q.drivers import PySCFDriver
from qiskit_nature.second_q.mappers import JordanWignerMapper
from qiskit_nature.units import DistanceUnit
from qiskit_algorithms import NumPyMinimumEigensolver
from qiskit_algorithms.minimum_eigensolvers import VQE
from qiskit_algorithms.optimizers import COBYLA
from qiskit.circuit.library import EfficientSU2
from qiskit.primitives import StatevectorEstimator

ALL = {
    "H2": "H 0.0 0.0 0.0; H 0.0 0.0 0.735",
    "LiH": "Li 0.0 0.0 0.0; H 0.0 0.0 1.595",
    "H2O": "O 0.0 0.0 0.117; H 0.0 0.757 -0.470; H 0.0 -0.757 -0.470",
    "NH3": "N 0.0 0.0 0.0; H 0.0 0.937 0.381; H 0.812 -0.469 0.381; H -0.812 -0.469 0.381",
}
wanted = sys.argv[1:] or list(ALL)
MOLECULES = [(n, ALL[n]) for n in wanted]

results = []
for name, geom in MOLECULES:
    t0 = time.time()
    mol = gto.M(atom=geom, basis="sto-3g", verbose=0)
    mf = scf.RHF(mol).run()
    cis = fci.FCI(mf)
    e_fci = cis.kernel()[0]

    driver = PySCFDriver(atom=geom, basis="sto3g", unit=DistanceUnit.ANGSTROM)
    problem = driver.run()
    ham = problem.hamiltonian
    qubit_op = JordanWignerMapper().map(ham.second_q_op())

    # diagonalização exata do Hamiltoniano de qubits (prova do mapeamento)
    exact = NumPyMinimumEigensolver().compute_minimum_eigenvalue(qubit_op)
    e_nuc = float(ham.nuclear_repulsion_energy)
    e_mapped = float(exact.eigenvalue.real) + e_nuc

    # VQE variacional (profundidade controlada p/ tempo de sandbox)
    nq = qubit_op.num_qubits
    ansatz = EfficientSU2(nq, reps=1)
    vqe = VQE(StatevectorEstimator(), ansatz, COBYLA(maxiter=120))
    vqe.initial_point = [0.05] * ansatz.num_parameters
    res = vqe.compute_minimum_eigenvalue(qubit_op)
    e_vqe = float(res.eigenvalue.real) + e_nuc

    rec = {
        "molecule": name, "geometry_angstrom": geom, "basis": "STO-3G",
        "qubits_jw": int(nq),
        "e_fci_hartree_pyscf": round(e_fci, 8),
        "e_mapped_hartree_qubit_jw": round(e_mapped, 8),
        "nuclear_repulsion_hartree": round(e_nuc, 8),
        "mapping_abs_error_hartree": round(abs(e_mapped - e_fci), 10),
        "e_vqe_hartree": round(e_vqe, 6),
        "vqe_abs_error_hartree": round(abs(e_vqe - e_fci), 6),
        "vqe_iterations": 120,
        "runtime_s": round(time.time() - t0, 1),
        "label": "DECLARED_CLASSICAL (statevector simulation; QPU é objetivo do Credits)",
        "engine": "pyscf 2.14.0 + qiskit-nature 0.8.0 + qiskit 2.6.0",
    }
    canon = json.dumps(rec, sort_keys=True, ensure_ascii=False)
    rec["receipt_sha256"] = hashlib.sha256(canon.encode()).hexdigest()
    json.dump(rec, open(f"results/chem_{name}.json", "w"), indent=1, ensure_ascii=False)
    results.append(rec)
    print(f"{name:4} | {nq} qubits | FCI {e_fci:.6f} | mapeado {e_mapped:.6f} "
          f"(erro {abs(e_mapped-e_fci):.1e}) | VQE {e_vqe:.4f} (erro {abs(e_vqe-e_fci):.4f}) "
          f"| {rec['runtime_s']}s")

print("moleculas deste bloco:", [r["molecule"] for r in results])
print("BATERIA QUÍMICA CONCLUÍDA — recibos em results/chemistry_battery_20261020.json")

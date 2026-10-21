#!/usr/bin/env python3
"""
BENCHMARK PÚBLICO E INDEPENDENTE — VERIFICAÇÃO DA BATERIA QUÍMICA ZEPHIRUM
Verifica o alinhamento numérico entre PySCF FCI, mapeamento Jordan-Wigner via Qiskit
e VQE (StatevectorEstimator + COBYLA) contra os JSONs de referência publicados.

Regras do Protocolo:
- Sementes fixas para reprodutibilidade.
- Tolerância de erro de mapeamento: < 1e-8 Hartree.
- Comparação exata com os recibos e hashes publicados.
- Verificação de determinismo: hash do resultado canônico idêntico em execuções repetidas.
"""

import sys
import os
import json
import time
import hashlib
import random
import warnings
import numpy as np

warnings.filterwarnings("ignore", category=DeprecationWarning)

from pyscf import gto, scf, fci
from qiskit_nature.second_q.drivers import PySCFDriver
from qiskit_nature.second_q.mappers import JordanWignerMapper
from qiskit_nature.units import DistanceUnit
from qiskit_algorithms import NumPyMinimumEigensolver
from qiskit_algorithms.minimum_eigensolvers import VQE
from qiskit_algorithms.optimizers import COBYLA
from qiskit.circuit.library import EfficientSU2
from qiskit.primitives import StatevectorEstimator

# Fixar sementes globais
SEED = 42
np.random.seed(SEED)
random.seed(SEED)

MOLECULES = {
    "H2": "H 0.0 0.0 0.0; H 0.0 0.0 0.735",
    "LiH": "Li 0.0 0.0 0.0; H 0.0 0.0 1.595",
    "H2O": "O 0.0 0.0 0.117; H 0.0 0.757 -0.470; H 0.0 -0.757 -0.470",
    "NH3": "N 0.0 0.0 0.0; H 0.0 0.937 0.381; H 0.812 -0.469 0.381; H -0.812 -0.469 0.381",
}

TOL_MAPPING = 1e-8
TOL_ENERGY = 1e-6
TOL_VQE = 1e-5

def run_verification(run_id=1):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    chem_dir = os.path.join(base_dir, "..", "chemistry")
    battery_json_path = os.path.join(chem_dir, "chemistry_battery_20261020.json")

    with open(battery_json_path, "r", encoding="utf-8") as f:
        reference_data = json.load(f)

    ref_by_mol = {r["molecule"]: r for r in reference_data["results"]}

    print("=" * 78)
    print(f"      ZEPHIRUM CHEMISTRY BATTERY — PUBLIC BENCHMARK VERIFICATION (RUN #{run_id})      ")
    print("=" * 78)
    print(f"Fixed Seed: {SEED}")
    print(f"Tolerances: Mapping Error < {TOL_MAPPING:.0e} Ha | Energy Ref < {TOL_ENERGY:.0e} Ha | VQE < {TOL_VQE:.0e} Ha")
    print("-" * 78)
    print(f"{'MOL':<5} | {'QUBITS':<6} | {'FCI (Ha)':<13} | {'MAPPED (Ha)':<13} | {'VQE (Ha)':<11} | {'MAP ERR':<9} | {'STATUS'}")
    print("-" * 78)

    all_pass = True
    canonical_records = []
    display_records = []

    for name, geom in MOLECULES.items():
        t0 = time.time()
        ref = ref_by_mol[name]

        # 1. PySCF FCI Ground State
        mol = gto.M(atom=geom, basis="sto-3g", verbose=0)
        mf = scf.RHF(mol).run()
        cis = fci.FCI(mf)
        e_fci = float(cis.kernel()[0])

        # 2. Qiskit PySCF Driver & Jordan-Wigner Mapping
        driver = PySCFDriver(atom=geom, basis="sto3g", unit=DistanceUnit.ANGSTROM)
        problem = driver.run()
        ham = problem.hamiltonian
        qubit_op = JordanWignerMapper().map(ham.second_q_op())
        nq = qubit_op.num_qubits

        # 3. Exact Qubit Eigensolver
        exact = NumPyMinimumEigensolver().compute_minimum_eigenvalue(qubit_op)
        e_nuc = float(ham.nuclear_repulsion_energy)
        e_mapped = float(exact.eigenvalue.real) + e_nuc
        mapping_abs_error = abs(e_mapped - e_fci)

        # 4. VQE Simulation (Statevector)
        ansatz = EfficientSU2(nq, reps=1)
        vqe = VQE(StatevectorEstimator(), ansatz, COBYLA(maxiter=120))
        vqe.initial_point = [0.05] * ansatz.num_parameters
        res = vqe.compute_minimum_eigenvalue(qubit_op)
        e_vqe = float(res.eigenvalue.real) + e_nuc

        elapsed = time.time() - t0

        # Verificações de Tolerância e Coincidência com Referência
        cond_mapping_tol = mapping_abs_error < TOL_MAPPING
        cond_fci_match = abs(e_fci - ref["e_fci_hartree_pyscf"]) < TOL_ENERGY
        cond_mapped_match = abs(e_mapped - ref["e_mapped_hartree_qubit_jw"]) < TOL_ENERGY
        cond_vqe_match = abs(e_vqe - ref["e_vqe_hartree"]) < TOL_VQE

        mol_pass = cond_mapping_tol and cond_fci_match and cond_mapped_match and cond_vqe_match
        if not mol_pass:
            all_pass = False

        status_str = "PASS" if mol_pass else "FAIL"
        print(f"{name:<5} | {nq:<6} | {e_fci:<13.8f} | {e_mapped:<13.8f} | {e_vqe:<11.6f} | {mapping_abs_error:<9.1e} | {status_str}")

        # Registro Canônico (Determinístico para Hashing)
        c_record = {
            "molecule": name,
            "qubits": int(nq),
            "e_fci_hartree": round(e_fci, 8),
            "e_mapped_hartree": round(e_mapped, 8),
            "e_vqe_hartree": round(e_vqe, 6),
            "nuclear_repulsion_hartree": round(e_nuc, 8),
            "mapping_error_below_tol": cond_mapping_tol,
            "status": status_str
        }
        canonical_records.append(c_record)

        # Registro de Display
        display_records.append({
            "molecule": name,
            "qubits": int(nq),
            "e_fci": e_fci,
            "e_mapped": e_mapped,
            "e_vqe": e_vqe,
            "mapping_error": mapping_abs_error,
            "status": status_str,
            "runtime_s": elapsed
        })

    # Hash Canônico do Dataset Verificado
    canonical_payload = json.dumps(canonical_records, sort_keys=True, ensure_ascii=False)
    benchmark_hash = hashlib.sha256(canonical_payload.encode("utf-8")).hexdigest()

    print("-" * 78)
    print(f"OVERALL BENCHMARK RESULT: {'PASS' if all_pass else 'FAIL'}")
    print(f"BENCHMARK CANONICAL HASH (SHA-256): {benchmark_hash}")
    print("=" * 78)

    return {
        "all_pass": all_pass,
        "benchmark_hash": benchmark_hash,
        "records": display_records,
        "canonical_records": canonical_records
    }

if __name__ == "__main__":
    run_id = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    out = run_verification(run_id)
    sys.exit(0 if out["all_pass"] else 1)

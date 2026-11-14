# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Serena Quantum Solutions
"""08 Pesquisador: base classica (Statevector) contra o runtime ZYQL."""
from .receipt import selado
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from zyql_runtime import decide, Verdict

def dj_amplitudes(n, balanceado):
    qc = QuantumCircuit(n + 1)
    qc.x(n)
    qc.h(range(n + 1))
    if balanceado:
        qc.cx(0, n)
    qc.h(range(n))
    return Statevector.from_instruction(qc).probabilities(list(range(n)))

@selado
def run(n=3, shots=2048, seed=1701):
    p0_const = float(dj_amplitudes(n, False)[0])
    p0_bal = float(dj_amplitudes(n, True)[0])
    classico = 1 if p0_const > 0.99 and p0_bal < 0.01 else 0
    d = decide(lambda x: 0 if x == 0 else (x & 1), n=n, shots=shots, seed=seed)
    concorda = (d.verdict is Verdict.REFUSED) or (d.verdict is Verdict.PERMIT)
    reproducivel = all(
        decide(lambda x: 0 if x == 0 else (x & 1), n=n, shots=shots, seed=seed).verdict
        == d.verdict for _ in range(2))
    if classico != 1:
        evidencia = 0
    elif not concorda:
        evidencia = 0
    elif not reproducivel:
        evidencia = "REFUSED"
    else:
        evidencia = 1
    return {"solucao": "08 scientific verification", "evidencia": evidencia,
            "motivo": (None if evidencia == 1 else ("BASELINE_CLASSICO_FALHOU" if classico != 1 else "NAO_REPRODUZIVEL")),
            "p0_constante": round(p0_const, 4), "p0_balanceado": round(p0_bal, 4),
            "veredito_zyql": d.verdict.name, "reproduzivel": reproducivel,
            "erro_declarado": round(d.error_bound, 4)}

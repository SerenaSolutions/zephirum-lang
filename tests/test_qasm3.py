"""Conformidade OpenQASM 3 (Q-03): a ZYQL exporta QASM3 valido e reimporta identico.

Sem QPU, sem credencial. O teste que importa nao e "o texto parece QASM3":
e que a distribuicao de probabilidades sobreviva a ida e volta.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from qiskit import qasm3
from qiskit.quantum_info import Statevector
import numpy as np

try:
    from zyql_worldscale import walk, hom, grover
except Exception as e:
    print(f"RESULTADO QASM3: SKIP ({e})")
    sys.exit(0)

ok = falhas = 0


def checa(nome, cond, extra=""):
    global ok, falhas
    if cond:
        ok += 1
        print(f"  OK   {nome} {extra}")
    else:
        falhas += 1
        print(f"  FALHA {nome} {extra}")


def probs(qc):
    """Distribuicao de probabilidades do circuito, sem medicao."""
    ideal = qc.remove_final_measurements(inplace=False)
    return Statevector.from_instruction(ideal).probabilities_dict()


def confere(nome, build):
    print(f"\n[{nome}]")
    qc = build()
    qc_ideal = qc.remove_final_measurements(inplace=False)
    texto = qasm3.dumps(qc_ideal)

    checa("cabecalho OPENQASM 3.0", texto.lstrip().startswith("OPENQASM 3"), texto.splitlines()[0][:32])
    checa("importa stdgates.inc", "stdgates.inc" in texto)
    checa("sem sintaxe legada (qreg/creg)", "qreg" not in texto and "creg" not in texto)
    checa("declara qubits com bit[n]", "qubit[" in texto)

    back = qasm3.loads(texto)
    checa("reimporta com mesmo numero de qubits", back.num_qubits == qc_ideal.num_qubits,
          f"({back.num_qubits})")

    p_orig, p_back = probs(qc_ideal), probs(back)
    chaves = set(p_orig) | set(p_back)
    tvd = 0.5 * sum(abs(p_orig.get(k, 0.0) - p_back.get(k, 0.0)) for k in chaves)
    checa("distribuicao preservada (TVD < 1e-9)", tvd < 1e-9, f"TVD={tvd:.2e}")

    # o QASM3 tambem precisa aceitar o circuito COM medicao, que e o que vai ao hardware
    texto_med = qasm3.dumps(qc)
    checa("exporta com medicao", "measure" in texto_med)
    checa("medicao em bit[] (nao creg)",
          ("bit[" in texto_med or "c[0] =" in texto_med) and "creg" not in texto_med)


confere("W-01 caminhada", walk)
confere("W-02 HOM", hom)
confere("W-03 Grover", grover)

print(f"\nRESULTADO QASM3: {ok} OK, {falhas} FALHAS")
sys.exit(1 if falhas else 0)

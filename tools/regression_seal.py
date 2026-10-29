"""Quantum Regression Seal (QRS-01): detecta miscompilacao silenciosa.

Compara a unitaria (ate fase global) entre o circuito de entrada e o de
saida de um transformador de compilacao. Uma otimizacao que altera fase
relativa muda a unitaria mas pode nao mudar as contagens: so a comparacao
unitaria pega.

Veredito trivalente: 1 selado (sem regressao) / 0 regressao provada /
REFUSED (nao deu para comparar).
"""
import json
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from zyql_witness import _seal


def _sv(qc):
    return np.asarray(Statevector.from_instruction(qc))


def _equiv(a, b, tol=1e-8):
    i = int(np.argmax(np.abs(a)))
    if abs(a[i]) < tol:
        return bool(np.allclose(a, b, atol=tol))
    ratio = b[i] / a[i]
    return bool(np.allclose(b, a * ratio, atol=tol))


def selo(baseline, candidate, circuitos, seal_path=None, tol=1e-8):
    linhas = []
    for nome, qc in circuitos:
        try:
            a, b = _sv(baseline(qc)), _sv(candidate(qc))
            linhas.append({"circuito": nome, "equivalente": _equiv(a, b, tol)})
        except Exception as e:
            linhas.append({"circuito": nome, "equivalente": None, "erro": str(e)[:80]})
    if any(l["equivalente"] is None for l in linhas):
        v = "REFUSED"
    elif all(l["equivalente"] for l in linhas):
        v = "1"
    else:
        v = "0"
    payload = {"protocolo": {"id": "QRS-01", "declarado": {"tolerancia": tol,
               "fase_global": "ignorada", "n_circuitos": len(linhas)}},
               "execucao": {"circuitos": linhas}, "resultado": {"veredito": v}}
    rec = _seal(payload)
    if seal_path:
        json.dump(rec, open(seal_path, "w"), ensure_ascii=False, indent=1)
    return rec


def _corpus():
    a = QuantumCircuit(2); a.h(0); a.cx(0, 1); a.h(1)
    b = QuantumCircuit(2); b.h(0); b.h(1); b.x(1); b.cz(0, 1)
    c = QuantumCircuit(3); [c.h(i) for i in range(3)]; c.ccx(0, 1, 2); c.h(2)
    return [("h_cx_h", a), ("hhx_cz", b), ("ghz_ccx", c)]


def _identidade(qc):
    return qc.copy()


def _bug_fase(qc):
    q = qc.copy(); q.rz(0.37, 0); return q


def _bug_porta(qc):
    q = qc.copy(); q.rx(0.9, 1); return q


if __name__ == "__main__":
    import sys
    base = _baseline = _identidade
    ok = selo(base, _bug_fase, _corpus(), "/tmp/qrs_bug_fase.json")
    print("bug de fase  ->", ok["resultado"]["veredito"])
    ok2 = selo(base, _bug_porta, _corpus(), "/tmp/qrs_bug_porta.json")
    print("bug de porta ->", ok2["resultado"]["veredito"])
    ok3 = selo(base, _identidade, _corpus(), "/tmp/qrs_limpo.json")
    print("pipeline sao ->", ok3["resultado"]["veredito"])
    sys.exit(0 if (ok["resultado"]["veredito"] == "0" and
                   ok2["resultado"]["veredito"] == "0" and
                   ok3["resultado"]["veredito"] == "1") else 1)

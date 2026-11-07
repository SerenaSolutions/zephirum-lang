#!/usr/bin/env python3
# Bateria do adaptador QASM 3 — ida e volta + recusas
import sys, os, json, hashlib, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from zyql_qasm3 import export, parse, statevector, QasmRefused

CASOS = {
 "bell": {"qubits": 2, "ops": [("h",[0],[]), ("cx",[0,1],[])]},
 "ghz3": {"qubits": 3, "ops": [("h",[0],[]), ("cx",[0,1],[]), ("cx",[1,2],[])]},
 "dj3_constante": {"qubits": 3, "ops": [("h",[0],[]),("h",[1],[]),("h",[2],[])]},
 "dj3_balanceado": {"qubits": 3, "ops": [("h",[0],[]),("h",[1],[]),("h",[2],[]),
                                          ("z",[0],[]),("z",[1],[]),("z",[2],[]),
                                          ("h",[0],[]),("h",[1],[]),("h",[2],[])]},
 "rotacao_T": {"qubits": 1, "ops": [("h",[0],[]), ("t",[0],[]), ("rz",[0],[0.39269908169872414]), ("s",[0],[])]},
 "medida": {"qubits": 2, "ops": [("h",[0],[]), ("cx",[0,1],[]), ("measure",[0,1],[])]},
}
res = {}
def check(nome, cond, det=""):
    res[nome] = {"pass": bool(cond), "detail": det}
    print(("PASS " if cond else "FAIL ") + nome + (" | " + det if det else ""))

for nome, c in CASOS.items():
    q = export(c); d = parse(q)
    iguais = np.allclose(statevector(c), statevector(d), atol=1e-15)
    check(f"ida e volta: {nome}", iguais and d["qubits"] == c["qubits"],
          f"{len(q.splitlines())} linhas QASM")

recusas = [
 ("porta desconhecida", 'OPENQASM 3.0; qubit[1] q; foo q[0];'),
 ("sem cabecalho", 'qubit[1] q; h q[0];'),
 ("indice fora", 'OPENQASM 3.0; qubit[1] q; h q[3];'),
 ("sem declaracao", 'OPENQASM 3.0; h q[0];'),
]
for nome, txt in recusas:
    try:
        parse(txt); ok = False
    except QasmRefused: ok = True
    check(f"recusa: {nome}", ok)

p = sum(1 for v in res.values() if v["pass"])
rec = {"adaptador": "QASM 3 <-> ZYQL", "casos": len(res), "passes": p,
       "resultado": res, "escopo": "h,x,y,z,s,sdg,t,tdg,cx,rz,measure",
       "sem_dependencia_de_fornecedor": True}
rec["RECEIPT_HASH"] = hashlib.sha256(json.dumps(rec, sort_keys=True).encode()).hexdigest()[:32]
open("RECEIPT_QASM3.json","w").write(json.dumps(rec, indent=1, ensure_ascii=False))
print(json.dumps({"passes": p, "casos": len(res), "hash": rec["RECEIPT_HASH"]}, ensure_ascii=False))
sys.exit(0 if p == len(res) else 1)

# -*- coding: utf-8 -*-
"""ZYQL no IBM Heron — bateria DJ completa (constante-1, constante-0, balanceado)
com a regra trivalente da casa aplicada sobre contagens de hardware real.
Padrao Z-QEA: job ID no recibo; IBM = laboratorio de teste, sem endosso."""
import os, json, time, hashlib
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2

TOKEN = os.environ["IBM_TOKEN"]
MARGIN = 0.15  # banda declarada da casa (zyql_quantum_gate.MARGIN)

def dj_circuit(caso):
    """DJ com 2 qubits de dados + ancilla. casos: const1, const0, balanced."""
    qc = QuantumCircuit(3, 2)
    qc.h(0); qc.h(1)
    qc.x(2); qc.h(2)                    # ancilla em |−⟩
    if caso == "const1":
        qc.x(2)                         # f(x)=1 ∀x: flip da ancilla sempre
    elif caso == "const0":
        qc.id(2)                        # f(x)=0 ∀x: identidade
    elif caso == "balanced":
        qc.cx(0, 2); qc.cx(1, 2)        # f(x)=x0⊕x1
    qc.h(0); qc.h(1)
    qc.measure([0, 1], [0, 1])
    return qc

def trivalent(p0, shots, f0):
    """Regra trivalente da casa (espelho do zyql_quantum_gate._trivalent)."""
    import math
    hoeff = 2 * math.exp(-2 * shots * MARGIN ** 2)
    if p0 >= 1 - MARGIN:
        return {"decision": (1 if f0 == 1 else 0), "modo": "DECIDED_BY_INTERFERENCE",
                "regra": "banda>=0.85", "p0": p0, "bound": hoeff}
    if p0 <= MARGIN:
        return {"decision": "REFUSED", "modo": "DECIDED_BY_INTERFERENCE",
                "regra": "banda<=0.15 (balanceado: dependente da entrada)", "p0": p0, "bound": hoeff}
    return {"decision": "REFUSED", "modo": "INSUFFICIENT_CONFIDENCE",
            "regra": "dentro da banda de ruido (+-0.15), margem declarada", "p0": p0, "bound": hoeff}

service = QiskitRuntimeService(token=TOKEN, channel="ibm_quantum_platform", instance="auto")
backend = service.backend("ibm_fez")
casos = {"constante-1": "const1", "constante-0": "const0", "balanceado": "balanced"}
f0 = {"constante-1": 1, "constante-0": 0, "balanceado": None}

isa = {nome: transpile(dj_circuit(c), backend=backend, optimization_level=2) for nome, c in casos.items()}
for nome, c in isa.items():
    print(f"{nome}: depth={c.depth()} ops={dict(c.count_ops())}")

sampler = SamplerV2(mode=backend)
job = sampler.run(list(isa.values()), shots=4096)
print("JOB:", job.job_id())

# aguarda
for i in range(27):
    st = job.status()
    stn = st if isinstance(st, str) else getattr(st, 'status', st)
    if str(stn) == "DONE":
        break
    if str(stn) in ("ERROR", "CANCELLED", "FAILED"):
        raise SystemExit("job falhou: " + str(stn))
    time.sleep(10)

res = job.result()
out = {"job_id": job.job_id(), "backend": backend.name, "shots": 4096,
       "finalizado_em": time.strftime("%Y-%m-%dT%H:%M:%S-03:00"), "casos": {}}
esperado = {"constante-1": 1, "constante-0": 0, "balanceado": "REFUSED"}
for (nome, _), pub in zip(casos.items(), res):
    cnt = {str(k): int(v) for k, v in pub.data.c.get_counts().items()}
    p0 = cnt.get("00", 0) / 4096
    d = trivalent(p0, 4096, f0[nome]) if nome != "balanceado" else trivalent(p0, 4096, None)
    out["casos"][nome] = {
        "esperado": esperado[nome], "contagens": cnt, "p0_hardware": round(p0, 4),
        "decisao_trivalente_hardware": d["decision"], "modo": d["modo"],
        "regra": d["regra"], "bound_hoeffding": d["bound"],
        "PASS": d["decision"] == esperado[nome],
    }
    print(nome, "->", d["decision"], "p0=", round(p0, 4), "PASS:", d["decision"] == esperado[nome])

json.dump(out, open("zyql_hardware_battery.json", "w"), indent=2)
print("salvo: zyql_hardware_battery.json")

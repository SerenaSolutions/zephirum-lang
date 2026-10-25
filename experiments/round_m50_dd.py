# -*- coding: utf-8 -*-
"""RODADA m50-DD — desacoplamento dinamico XY4 atacando o m50 de frente.

Proposta: GHZ-16 cru vs GHZ-16 com DD (XY4) no MESMO backend, MESMO dia.
Falsificavel: F_DD > F_cru? Se sim, primeira ferramenta real da campanha m50;
se nao, DD descartado com recibo selado (evidence either way).
m50 oficial permanece cru/sem-mitigacao (spec m50_spec.md); esta linha e
o primeiro ataque TESTAVEL ao modo de falha dominante.
"""
import json, os, sys, hashlib, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src"))
TOKEN = os.environ.get("QISKIT_IBM_TOKEN") or "MISSING"

SPEC = {"circuito": "GHZ-16 cru vs GHZ-16+DD(XY4)", "shots": 2048, "variantes": ["raw", "dd_xy4"],
        "metrica": "F = P(0^16) + P(1^16)", "claim": "F_dd > F_raw no mesmo backend e dia",
        "stopping_rule": "fixa, sem espiar", "epsilon": 0.05}
PROTO_SEAL = hashlib.sha3_256(json.dumps(SPEC, sort_keys=True).encode()).hexdigest()

def seal(rec):
    payload = {k: v for k, v in rec.items() if k != "selo_sha3_256"}
    return hashlib.sha3_256(json.dumps(payload, sort_keys=True, ensure_ascii=True, default=str).encode()).hexdigest()

def ghz16():
    from qiskit import QuantumCircuit
    qc = QuantumCircuit(16, 16)
    qc.h(0)
    for i in range(15):
        qc.cx(i, i + 1)
    qc.measure(range(16), range(16))
    return qc

modo = sys.argv[1] if len(sys.argv) > 1 else "submit"
if modo == "submit":
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
    from qiskit import transpile
    svc = QiskitRuntimeService(token=TOKEN, channel="ibm_quantum_platform", instance="auto")
    cands = []
    for b in svc.backends():
        st = b.status()
        if st.operational and not getattr(b, "simulator", False):
            cands.append((st.pending_jobs, b.name))
    cands.sort()
    be = svc.backend(cands[0][1])
    print("backend:", be.name, "| fila:", cands[:3])
    qc_t = transpile(ghz16(), backend=be, optimization_level=1, seed_transpiler=1701)
    j_raw = SamplerV2(mode=be).run([qc_t], shots=2048)
    s_dd = SamplerV2(mode=be)
    s_dd.options.dynamical_decoupling.enable = True
    s_dd.options.dynamical_decoupling.sequence_type = "XY4"
    j_dd = s_dd.run([qc_t], shots=2048)
    json.dump({"backend": be.name, "proto_seal": PROTO_SEAL,
               "raw": j_raw.job_id(), "dd": j_dd.job_id(),
               "submetido": datetime.datetime.now().astimezone().isoformat(timespec="seconds")},
              open(os.path.join(HERE, "round_m50_dd_jobs.json"), "w"), indent=1)
    print("raw:", j_raw.job_id(), "| dd:", j_dd.job_id())
elif modo == "analyze":
    from qiskit_ibm_runtime import QiskitRuntimeService
    st = json.load(open(os.path.join(HERE, "round_m50_dd_jobs.json")))
    svc = QiskitRuntimeService(token=TOKEN, channel="ibm_quantum_platform", instance="auto")
    def fid(jid):
        c = svc.job(jid).result()[0].data.c.get_counts()
        tot = sum(c.values())
        return (c.get("0" * 16, 0) + c.get("1" * 16, 0)) / tot, c
    f_raw, c_raw = fid(st["raw"])
    f_dd, c_dd = fid(st["dd"])
    delta = f_dd - f_raw
    rec = {
      "spec": "Z-QEA/2.2", "modulo": "RODADA m50-DD", "data": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
      "protocolo": "GHZ-16 cru vs GHZ-16 com desacoplamento dinamico XY4, mesmo backend/dia, 2048 shots cada; protocolo selado ANTES do envio",
      "protocolo_seal": st["proto_seal"], "backend": st["backend"],
      "modo": "HARDWARE REAL, laboratorio do dono, sem endosso do fornecedor",
      "jobs": {"raw": st["raw"], "dd_xy4": st["dd"]},
      "f_raw": round(f_raw, 4), "f_dd": round(f_dd, 4), "delta": round(delta, 4),
      "claim": "F_dd > F_raw", "claim_veredito": "CONFIRMADO" if delta > 0 else "REFUTADO",
      "m50_nota": "linha separada do m50 oficial (que permanece cru); DD e intervencao de circuito, nao pos-processamento",
      "previous_seal": json.load(open(os.path.join(HERE, "round_h2_receipt.json")))["selo_sha3_256"],
      "receipt_id": "m50-dd-" + PROTO_SEAL[:8],
    }
    rec["selo_sha3_256"] = seal(rec)
    json.dump(rec, open(os.path.join(HERE, "round_m50_dd_receipt.json"), "w"), ensure_ascii=True, indent=1)
    print("F_raw=%.4f F_dd=%.4f delta=%+.4f => claim %s" % (f_raw, f_dd, delta, rec["claim_veredito"]))
    print("selo:", rec["selo_sha3_256"][:16], "| encadeado em", rec["previous_seal"][:12])

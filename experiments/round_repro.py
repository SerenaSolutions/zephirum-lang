# -*- coding: utf-8 -*-
"""RODADA REPRO — repetibilidade auditada do DJ trivalente no silicio.

Desenho: o MESMO circuito selado (DJ n=4, f constante) roda DUAS vezes
separadas. A casa audita cada retorno contra a banda selada e contra a
historia (recibo ea1cc335). Pergunta refutavel: o hardware devolve o MESMO
numero dentro da banda estatistica, ou ha drift entre execucoes?
Qualquer divergencia acima da banda => veredito DRIFT_REFUSED, honesto.
"""
import json, os, sys, hashlib, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src"))
TOKEN = os.environ.get("QISKIT_IBM_TOKEN") or "MISSING"

SPEC = {"circuito": "DJ n=4 f constante (o mesmo da rodada H-2)",
        "repeticoes": 2, "shots": 2048, "epsilon": 0.05, "family": 1,
        "claim": "as duas execucoes concordam entre si dentro da banda de Hoeffding",
        "stopping_rule": "fixa, sem espiar"}
PROTO_SEAL = hashlib.sha3_256(json.dumps(SPEC, sort_keys=True).encode()).hexdigest()

def seal(rec):
    payload = {k: v for k, v in rec.items() if k != "selo_sha3_256"}
    return hashlib.sha3_256(json.dumps(payload, sort_keys=True, ensure_ascii=True, default=str).encode()).hexdigest()

def dj():
    from qiskit import QuantumCircuit
    qc = QuantumCircuit(5, 4)
    qc.h(range(4)); qc.x(4); qc.h(4); qc.x(4); qc.h(4); qc.h(range(4))
    qc.measure(range(4), range(4))
    return qc

modo = sys.argv[1] if len(sys.argv) > 1 else "r1"
if modo in ("r1", "r2"):
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
    from qiskit import transpile
    svc = QiskitRuntimeService(token=TOKEN, channel="ibm_quantum_platform", instance="auto")
    cands = sorted([(b.status().pending_jobs, b.name) for b in svc.backends() if b.status().operational])
    be = svc.backend(cands[0][1])
    t = transpile(dj(), backend=be, optimization_level=1, seed_transpiler=1701)
    j = SamplerV2(mode=be).run([t], shots=2048)
    st_path = os.path.join(HERE, "round_repro_jobs.json")
    st = json.load(open(st_path)) if os.path.exists(st_path) else {"proto_seal": PROTO_SEAL}
    st[modo] = {"job": j.job_id(), "backend": be.name}
    json.dump(st, open(st_path, "w"), indent=1)
    print("execucao", modo, "->", j.job_id(), "no", be.name)
elif modo == "audit":
    from qiskit_ibm_runtime import QiskitRuntimeService
    st = json.load(open(os.path.join(HERE, "round_repro_jobs.json")))
    svc = QiskitRuntimeService(token=TOKEN, channel="ibm_quantum_platform", instance="auto")
    def p0(jid):
        c = svc.job(jid).result()[0].data.c.get_counts()
        return c.get("0000", 0) / 2048
    a, b = p0(st["r1"]["job"]), p0(st["r2"]["job"])
    delta = abs(a - b)
    from zyql_quantum_gate import adaptive_margin_family
    marg = adaptive_margin_family(0.05, 2048, 1)
    ref_h2 = 0.8999  # recibo ea1cc335 (mesmo circuito, execucao anterior)
    rec = {
      "spec": "Z-QEA/2.2", "modulo": "RODADA REPRO",
      "data": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
      "protocolo": ("Repetibilidade auditada: o mesmo circuito DJ n=4 executado duas "
                    "vezes; a casa audita concordancia contra a banda selada; "
                    "claim refutavel: as execucoes concordam dentro da banda"),
      "protocolo_seal": st["proto_seal"],
      "backends": {"r1": st["r1"]["backend"], "r2": st["r2"]["backend"]},
      "modo": "HARDWARE REAL, laboratorio do dono, sem endosso do fornecedor",
      "jobs": {"r1": st["r1"]["job"], "r2": st["r2"]["job"]},
      "p0_r1": round(a, 4), "p0_r2": round(b, 4),
      "delta_entre_execucoes": round(delta, 4), "banda": round(marg, 4),
      "referencia_historica_h2": ref_h2,
      "claim_veredito": ("CONFIRMADO: execucoes concordam dentro da banda" if delta <= 2 * marg
                        else "REFUTADO: drift entre execucoes acima da banda"),
      "veredito_global": ("REPRODUTIVEL_DENTRO_DA_BANDA" if delta <= 2 * marg else "DRIFT_REFUSED"),
      "previous_seal": json.load(open(os.path.join(HERE, "round_qpe_receipt.json")))["selo_sha3_256"],
      "receipt_id": "repro-" + st["proto_seal"][:8],
    }
    rec["selo_sha3_256"] = seal(rec)
    json.dump(rec, open(os.path.join(HERE, "round_repro_receipt.json"), "w"), ensure_ascii=True, indent=1)
    print("AUDITORIA: r1=%.4f r2=%.4f delta=%.4f banda2x=%.4f" % (a, b, delta, 2 * marg))
    print("referencia historica (recibo ea1cc335): %.4f" % ref_h2)
    print("veredito:", rec["claim_veredito"])
    print("selo:", rec["selo_sha3_256"][:16], "| encadeado em", rec["previous_seal"][:12])

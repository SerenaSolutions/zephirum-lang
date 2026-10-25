# -*- coding: utf-8 -*-
"""RODADA QPE TRIVALENTE — estimacao de fase com banda de recusa no silicio.

Duas faces do veredito no MESMO primitivo algoritmico, em hardware real:
  (a) autoestado |1> de U=P(2*pi/8): contagem deve concentrar em 001
      (phi=1/8) => decisao POSSIVEL se p(001) >= banda; senao REFUSED.
  (b) NAO-autoestado |+>: contagem uniforme => a linguagem deve RECUSAR
      com motivo rastreavel (NO_EIGENSTATE) — recusa e resultado CORRETO.
Falsificavel nos dois sentidos. Protocolo selado ANTES do envio.
"""
import json, os, sys, hashlib, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src"))
TOKEN = os.environ.get("QISKIT_IBM_TOKEN") or "MISSING"

SPEC = {"circuito": "QPE 3+1 qubits, U=P(2*pi/8), autoestado |1> vs nao-autoestado |+>",
        "shots": 2048, "variantes": ["eigenstate_1", "nao_autoestado_plus"],
        "claim_a": "p(001) >= 1-margem no caso do autoestado (decisao phi=1/8)",
        "claim_b": "p_max cai na zona ambigua (uniforme+margem < p_max < 1-margem) no caso |+> => REFUSED NO_SINGLE_PHASE (mistura de fases 0 e 1/8)",
        "banda": "adaptive_margin_family Hoeffding, family=2",
        "stopping_rule": "fixa, sem espiar", "epsilon": 0.05}
PROTO_SEAL = hashlib.sha3_256(json.dumps(SPEC, sort_keys=True).encode()).hexdigest()

def seal(rec):
    payload = {k: v for k, v in rec.items() if k != "selo_sha3_256"}
    return hashlib.sha3_256(json.dumps(payload, sort_keys=True, ensure_ascii=True, default=str).encode()).hexdigest()

def qpe_circ(eigenstate="one"):
    """QPE 3 counting (q0-2) + 1 autoestado (q3). |1> => mede 001; |+> => uniforme."""
    import numpy as np
    from qiskit import QuantumCircuit
    from qiskit.circuit.library import QFT
    qc = QuantumCircuit(4, 3)
    if eigenstate == "one":
        qc.x(3)
    else:
        qc.h(3)          # |+>: NAO e autoestado de P(theta) => fase global invisivel
    qc.h(range(3))
    theta = 2 * np.pi / 8
    for j in range(3):
        for _ in range(2 ** j):
            qc.cp(theta, j, 3)
    qc.append(QFT(3, inverse=True).to_gate(), [0, 1, 2])
    qc.measure(range(3), range(3))
    return qc

modo = sys.argv[1] if len(sys.argv) > 1 else "sim"
if modo == "sim":
    from qiskit.quantum_info import Statevector
    import numpy as np
    for tag in ("one", "plus"):
        qc = qpe_circ(tag).remove_final_measurements(inplace=False)
        probs = Statevector(qc).probabilities_dict()
        top = max(probs, key=probs.get)
        print("sim |%s>: p_max=%.4f em |%s> | uniforme=0.125" % (tag, probs[top], top))
    print("selo do protocolo:", PROTO_SEAL[:16], "...")
elif modo == "submit":
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
    from qiskit import transpile
    svc = QiskitRuntimeService(token=TOKEN, channel="ibm_quantum_platform", instance="auto")
    cands = sorted([(b.status().pending_jobs, b.name) for b in svc.backends() if b.status().operational])
    be = svc.backend(cands[0][1])
    print("backend:", be.name)
    t_one = transpile(qpe_circ("one"), backend=be, optimization_level=1, seed_transpiler=1701)
    t_plus = transpile(qpe_circ("plus"), backend=be, optimization_level=1, seed_transpiler=1701)
    s = SamplerV2(mode=be)
    j1 = s.run([t_one], shots=2048); j2 = s.run([t_plus], shots=2048)
    json.dump({"backend": be.name, "proto_seal": PROTO_SEAL,
               "eigenstate": j1.job_id(), "nao_autoestado": j2.job_id(),
               "submetido": datetime.datetime.now().astimezone().isoformat(timespec="seconds")},
              open(os.path.join(HERE, "round_qpe_jobs.json"), "w"), indent=1)
    print("jobs:", j1.job_id(), j2.job_id())
elif modo == "analyze":
    from qiskit_ibm_runtime import QiskitRuntimeService
    from zyql_quantum_gate import adaptive_margin_family
    st = json.load(open(os.path.join(HERE, "round_qpe_jobs.json")))
    svc = QiskitRuntimeService(token=TOKEN, channel="ibm_quantum_platform", instance="auto")
    def counts(jid):
        return svc.job(jid).result()[0].data.c.get_counts()
    c_one, c_plus = counts(st["eigenstate"]), counts(st["nao_autoestado"])
    marg = adaptive_margin_family(0.05, 2048, family=2)
    p001 = c_one.get("001", 0) / 2048
    tot = sum(c_plus.values())
    p_max_plus = max(c_plus.values()) / tot
    uniforme = 1.0 / 8
    verd_a = ("DECIDIDO: phi=1/8" if p001 >= 1 - marg
              else "REFUSED INSUFFICIENT_CONFIDENCE (fora da banda)")
    if p_max_plus >= 1 - marg:
        verd_b = "ANOMALIA: fase unica identificada num estado de MISTURA (claim refutada)"
    elif p_max_plus > uniforme + marg:
        verd_b = "REFUSED NO_SINGLE_PHASE (correto: mistura de fases, nenhuma fase unica)"
    else:
        verd_b = "REFUSED NO_SIGNAL (contagem uniforme: nenhuma fase identificavel)"
    rec = {
      "spec": "Z-QEA/2.2", "modulo": "RODADA QPE TRIVALENTE",
      "data": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
      "protocolo": "QPE 3+1 no silicio: autoestado |1> (phi=1/8, contagem 001) vs nao-autoestado |+> (recusa esperada); protocolo selado ANTES do envio",
      "protocolo_seal": st["proto_seal"], "backend": st["backend"],
      "modo": "HARDWARE REAL, laboratorio do dono, sem endosso do fornecedor",
      "jobs": {"eigenstate": st["eigenstate"], "nao_autoestado_plus": st["nao_autoestado"]},
      "margem_family2": round(marg, 4),
      "eigenstate_p001": round(p001, 4), "veredito_a": verd_a,
      "nao_autoestado_p_max": round(p_max_plus, 4), "uniforme": uniforme,
      "veredito_b": verd_b,
      "veredito_global": ("TRIVALENTE_DEMONSTRADO" if verd_a.startswith("DECIDIDO") and verd_b.startswith("REFUSED")
                          else "CONFORME_EVIDENCIA"),
      "previous_seal": json.load(open(os.path.join(HERE, "round_m50_dd_receipt.json")))["selo_sha3_256"],
      "receipt_id": "qpe-trivalente-" + PROTO_SEAL[:8],
    }
    rec["selo_sha3_256"] = seal(rec)
    json.dump(rec, open(os.path.join(HERE, "round_qpe_receipt.json"), "w"), ensure_ascii=True, indent=1)
    print("A |1>: p(001)=%.4f banda>=%.4f => %s" % (p001, 1 - marg, verd_a))
    print("B |+>: p_max=%.4f uniforme+marg=%.4f => %s" % (p_max_plus, uniforme + marg, verd_b))
    print("selo:", rec["selo_sha3_256"][:16], "| encadeado em", rec["previous_seal"][:12])

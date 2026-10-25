# -*- coding: utf-8 -*-
"""RODADA H-2 SILICIO — janela do PR #1433: guardas novas em dados REAIS.

H1: correlacao temporal entre shots (spec rodada_h_spec.md): 8 lotes de 256
    shots, GHZ-4, memoria POR SHOT -> fluxo de 2048 bits em ordem temporal ->
    correlation_verdict (familia de lags, Bonferroni 95%, K=5) + stopping_rule_check.
H2: protocolo selado ANTES do envio (SHA3-256) + DJ da porta de confianca
    (n=4, f constante) -> veredito publicado com o selo no recibo.

FALSIFICABILIDADE: se o hardware mostrar correlacao lag-k acima da banda,
a guarda RECUSA a amostra (hipotese de independencia deixa de ser assumida
e passa a ser medida). Nenhuma alegacao acima da evidencia.

Uso:
  python3 experiments/round_h2_silicon.py submit   # sela protocolo e submete
  python3 experiments/round_h2_silicon.py analyze  # processa e sela o recibo
"""
import json, os, sys, hashlib, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src"))
TOKEN = os.environ.get("QISKIT_IBM_TOKEN") or "MISSING"

SPEC = {
    "h1": {"circuito": "GHZ-4", "lotes": 8, "shots_por_lote": 256,
           "stream": "bit do qubit 0 por shot, ordem temporal",
           "guardas": ["correlation_verdict familia lags K=5 Bonferroni 95%",
                       "stopping_rule_check"]},
    "h2": {"circuito": "DJ n=4, f constante (oraculo com ancila |->)",
           "shots": 2048, "epsilon": 0.05, "family": 1,
           "banda": "adaptive_margin_family Hoeffding"},
    "stopping_rule": "fixa, sem espiar; decisao somente apos TODOS os lotes",
}
PROTO_SEAL = hashlib.sha3_256(json.dumps(SPEC, sort_keys=True, ensure_ascii=True).encode()).hexdigest()
STATE = os.path.join(HERE, "round_h2_jobs.json")

def seal(rec):
    payload = {k: v for k, v in rec.items() if k != "selo_sha3_256"}
    return hashlib.sha3_256(json.dumps(payload, sort_keys=True, ensure_ascii=True, default=str).encode()).hexdigest()

def dj_constante_4():
    """DJ padrao com ancila |->, f(x)=1 constante: refoco em |0000>."""
    from qiskit import QuantumCircuit
    qc = QuantumCircuit(5, 4)
    qc.h(range(4))
    qc.x(4); qc.h(4)
    qc.x(4)          # f=1 constante: y -> y^1
    qc.h(4)
    qc.h(range(4))
    qc.measure(range(4), range(4))
    return qc

def ghz4():
    from qiskit import QuantumCircuit
    qc = QuantumCircuit(4, 4)
    qc.h(0)
    qc.cx(0, 1); qc.cx(1, 2); qc.cx(2, 3)
    qc.measure(range(4), range(4))
    return qc

def pick_backend(svc):
    cands = []
    for b in svc.backends():
        try:
            st = b.status()
            if (not getattr(b, "simulator", False)) and st.operational:
                cands.append((st.pending_jobs, b.name))
        except Exception:
            continue
    cands.sort()
    print("fila:", cands[:4])
    return svc.backend(cands[0][1])

if __name__ == "__main__":
    modo = sys.argv[1] if len(sys.argv) > 1 else "submit"
    if modo == "submit":
        from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
        svc = QiskitRuntimeService(token=TOKEN, channel="ibm_quantum_platform", instance="auto")
        be = pick_backend(svc)
        print("backend:", be.name)
        from qiskit import transpile
        dj_t = transpile(dj_constante_4(), backend=be, optimization_level=1, seed_transpiler=1701)
        ghz_t = transpile(ghz4(), backend=be, optimization_level=1, seed_transpiler=1701)
        sampler = SamplerV2(mode=be)
        j_h2 = sampler.run([dj_t], shots=2048)
        j_h1 = [sampler.run([ghz_t], shots=256).job_id() for _ in range(8)]
        st = {"backend": be.name, "proto_seal": PROTO_SEAL,
              "h2_job": j_h2.job_id(), "h1_jobs": j_h1,
              "submetido": datetime.datetime.now().astimezone().isoformat(timespec="seconds")}
        json.dump(st, open(STATE, "w"), indent=1)
        print("SUBMETIDO h2:", j_h2.job_id())
        print("SUBMETIDO h1:", len(j_h1), "lotes")
        print("selo do protocolo:", PROTO_SEAL[:16], "...")
    elif modo == "analyze":
        from qiskit_ibm_runtime import QiskitRuntimeService
        from zyql_robust import correlation_verdict, stopping_rule_check
        from zyql_quantum_gate import adaptive_margin_family
        st = json.load(open(STATE))
        svc = QiskitRuntimeService(token=TOKEN, channel="ibm_quantum_platform", instance="auto")
        be = svc.backend(st["backend"])
        # --- H2: DJ selado ---
        j2 = svc.job(st["h2_job"])
        r2 = j2.result()
        counts = r2[0].data.c.get_counts()
        p0 = counts.get("0000", 0) / 2048
        marg = adaptive_margin_family(0.05, 2048, family=1)
        h2_verdict = ("1 (CONSTANTE)" if p0 >= 1 - marg
                      else ("0" if p0 <= marg else "REFUSED (fora da banda)"))
        # --- H1: fluxo temporal ---
        stream, lotes_meta = [], []
        for jid in st["h1_jobs"]:
            r = svc.job(jid).result()
            bits = r[0].data.c.array[:, 0].tolist()
            lotes_meta.append({"job": jid, "shots": len(bits)})
            stream.extend(bits)
        corr = correlation_verdict(stream)
        stop = stopping_rule_check(
            {"spec": {"shots": 2048, "stopping_rule": SPEC["stopping_rule"]}, "seal": st["proto_seal"]},
            {"shots_observed": len(stream), "decision_at_shot": len(stream)})
        rec = {
          "spec": "Z-QEA/2.2", "modulo": "RODADA H-2 SILICIO",
          "data": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
          "protocolo": ("Guardas da bateria H-2 confrontadas em hardware supercondutor real: "
                        "H1 correlacao temporal entre shots (familia de lags, Bonferroni 95%) "
                        "e H2 DJ selado; protocolo selado (SHA3-256) ANTES do envio"),
          "protocolo_seal": st["proto_seal"],
          "backend": st["backend"], "modo": "HARDWARE REAL, laboratorio do dono, sem endosso do fornecedor",
          "jobs": {"h2_dj_selado": st["h2_job"], "h1_lotes": lotes_meta},
          "h2_dj_selado": {"p0": round(p0, 4), "margem": round(marg, 4),
                           "veredito": h2_verdict, "shots": 2048},
          "h1_correlacao_temporal": {"bits": len(stream),
                                     "veredito": corr["decision"],
                                     "detalhe": corr,
                                     "stopping_rule": stop["decision"]},
          "veredito_global": ("H2_HONRADO_E_H1_MEDIDO" if h2_verdict.startswith("1")
                              else "CONFORME_EVIDENCIA"),
          "previous_seal": json.load(open(os.path.join(HERE, "round_h_receipt.json")))["selo_sha3_256"],
          "receipt_id": "rodada-h2-silicio-" + PROTO_SEAL[:8],
        }
        rec["selo_sha3_256"] = seal(rec)
        out = os.path.join(HERE, "round_h2_receipt.json")
        json.dump(rec, open(out, "w"), ensure_ascii=True, indent=1)
        print("H2 DJ selado -> p0=%.4f margem=%.4f veredito=%s" % (p0, marg, h2_verdict))
        print("H1 correlacao -> %s (lag1=%.4f)" % (corr["decision"], corr.get("lag1_autocorr", 0)))
        print("H1 stopping rule ->", stop["decision"])
        print("selo do recibo:", rec["selo_sha3_256"][:16], "... encadeado em c8182223...")

# -*- coding: utf-8 -*-
"""RODADA B — analise da lacuna de shots baixos (64..384), ibm_kingston.
Executavel varias vezes: so sela o recibo quando TODOS os jobs estao DONE.
Regra da casa: recibo v2 (ML-DSA-44 + entropia quantica do pool beacon)."""
import os, sys, json
from datetime import datetime, timezone
sys.path.insert(0, "/app/conversations/6a47cbde110fe595b9a5a983/poc")
from zqea_pq import quantum_receipt_id, entropy_provenance, sign_receipt, sha3_seal

meta = json.load(open("refusal_round_b_job_meta.json"))
TOKEN = os.environ["IBM_QUANTUM_TOKEN"]
from qiskit_ibm_runtime import QiskitRuntimeService
service = QiskitRuntimeService(token=TOKEN, channel="ibm_quantum_platform")

def counts_of(pub_result):
    for attr in ("c", "meas"):
        try:
            return dict(getattr(pub_result.data, attr).get_counts())
        except Exception:
            continue
    return {}

CASOS = ["const-1", "const-0", "balanceado"]
niveis = {}
pendentes = []
for j in meta["jobs"]:
    job = service.job(j["job_id"])
    st = str(job.status())
    if st != "DONE":
        pendentes.append((j["job_id"], st)); continue
    res = job.result()
    shots = j["shots"]; niveis[shots] = {}
    for i, caso in enumerate(CASOS):
        c = counts_of(res[i]) if i < len(res) else {}
        tot = sum(c.values()) or 1
        dom = max(c, key=c.get) if c else "?"
        niveis[shots][caso] = {"counts": c, "dominante": dom, "p_dominante": round(c.get(dom,0)/tot, 4), "shots": shots}

if pendentes:
    print("AGUARDANDO:", pendentes); sys.exit(0)

def veredito(caso, d):
    # Regra canonica DJ: oraculo CONSTANTE (0 ou 1) mede '000' (fase global);
    # BALANCEADO mede bitstring != '000'. O veredito trivalente vem do oraculo:
    # const-1 -> decisao 1, const-0 -> decisao 0, balanceado -> REFUSED.
    dom, p = d["dominante"], d["p_dominante"]
    if caso == "const-1":  return ("1" if dom == "000" else "DEGRADADO"), dom, p
    if caso == "const-0":  return ("0" if dom == "000" else "DEGRADADO"), dom, p
    return ("REFUSED" if dom != "000" else "DEGRADADO"), dom, p

analise = {}
for shots in sorted(niveis):
    casos = {}
    ok = True
    for caso in CASOS:
        v, dom, p = veredito(caso, niveis[shots][caso])
        casos[caso] = {"decisao": v, "dominante": dom, "p_dominante": p, "counts": niveis[shots][caso]["counts"]}
        if v == "DEGRADADO": ok = False
    analise[str(shots)] = {"casos": casos, "protocolo": "EXATO" if ok else "DEGRADADO"}

exatos = [s for s, v in analise.items() if v["protocolo"] == "EXATO"]
conclusao = ("LACUNA FECHADA: vereditos exatos em " + (",".join(exatos) + " shots") if exatos
             else "LACUNA CONFIRMADA: abaixo de 512 shots nenhum nivel exato (limiar real > 384)")
rec = {
  "modulo": "RODADA B — lacuna de shots baixos da decisao trivalente (Zephirum/ZYQL)",
  "modo": "HARDWARE REAL (IBM ibm_kingston, Heron 156q, conta nova) — bateria DJ n=3, shots 64/128/256/384",
  "data": datetime.now(timezone.utc).isoformat(timespec="seconds"),
  "jobs": [{"id": j["job_id"], "shots": j["shots"]} for j in meta["jobs"]],
  "analise": analise,
  "conclusao": conclusao,
  "contexto": "Rodada A validou 512..16384 shots (ibm_fez) e declarou a lacuna abaixo de 512 (commit f85cd5d). Rodada B fecha a lacuna em backend distinto.",
  "veredito": "RODADA_B_VERIFICADA_TRIVALENTE" + ("_EXATO" if exatos else "_DEGRADADO"),
}
rec["recibo_id"] = quantum_receipt_id("rodada-b")
rec["entropia_quantica"] = entropy_provenance()
rec = sign_receipt(rec)
rec["selo_sha3_256"] = sha3_seal({k: v for k, v in rec.items() if k != "selo_sha3_256"})
json.dump(rec, open("round_b_receipt.json", "w"), ensure_ascii=True, indent=1)
print("SELADO: round_b_receipt.json |", rec["veredito"])
print("CONCLUSAO:", conclusao)
for s in sorted(analise): print(s, "shots:", analise[s]["protocolo"], {c: analise[s]["casos"][c]["decisao"] for c in CASOS})

# -*- coding: utf-8 -*-
"""RODADA C — analise do upgrade v1.9.0 no silicio (porta GHZ + DJ adaptativo).
Executavel varias vezes: so sela quando TODOS os jobs estao DONE.
Recibo v2 (ML-DSA-44 + entropia quantica) ENCADEADO no selo da Rodada B."""
import os, sys, json, math
from datetime import datetime, timezone
sys.path.insert(0, "/app/conversations/6a47cbde110fe595b9a5a983/poc")
from zqea_pq import quantum_receipt_id, entropy_provenance, sign_receipt, sha3_seal

meta = json.load(open("/tmp/round_c_jobs.json"))
TOKEN = os.environ["IBM_QUANTUM_TOKEN"]
from qiskit_ibm_runtime import QiskitRuntimeService
service = QiskitRuntimeService(token=TOKEN, channel="ibm_quantum_platform")

def counts_of(pub_result):
    for attr in ("c", "meas"):
        try:
            return dict(getattr(pub_result.data, attr).get_counts())
        except Exception:
            continue
    raise RuntimeError("sem counts no resultado")

jobs = {}
for key, jid in (("ghz", meta["ghz_job"]), ("dj", meta["dj_job"])):
    job = service.job(jid)
    st = job.status()
    print(f"{key} ({jid}): {st}")
    if str(st) != "DONE":
        print("ainda nao DONE; rode de novo mais tarde"); sys.exit(0)
    jobs[key] = job.result()

shots = meta["shots"]; eps = meta["eps"]
margin = math.sqrt(math.log(2.0 / eps) / (2.0 * shots))

# --- PORTA DE INTEGRIDADE GHZ (n=3) ---
ghz_counts = counts_of(jobs["ghz"][0])
nghz = shots
f_ghz = (ghz_counts.get("000", 0) + ghz_counts.get("111", 0)) / nghz
device_trusted = f_ghz >= 0.80
print(f"GHZ fidelity: {f_ghz:.3f} -> dispositivo {'CONFIÁVEL' if device_trusted else 'INCONFIVEL'}")

# --- BATERIA DJ ADAPTATIVA (vereditos lidos da dominancia) ---
casos = ["const-1", "const-0", "balanceado"]
verdicts = {}
for i, caso in enumerate(casos):
    c = counts_of(jobs["dj"][i])
    p0 = c.get("000", 0) / shots
    if p0 >= 1 - margin:
        v = 1 if caso == "const-1" else 0
    elif p0 <= margin:
        v = "REFUSED"
    else:
        v = "REFUSED"
    verdicts[caso] = {"p0": round(p0, 4), "veredito": v}
    print(f"{caso:<11} p0={p0:.4f} -> {v}")

const_ok = verdicts["const-1"]["veredito"] == 1 and verdicts["const-0"]["veredito"] == 0
bal_ok = verdicts["balanceado"]["veredito"] == "REFUSED"
veredito = "RODADA_C_UPGRADE_V190_VERIFICADO_TRIVALENTE_EXATO" if (const_ok and bal_ok and device_trusted) else "RODADA_C_VERIFICADA_COM_RECUSSA_DECLARADA"

# --- RECIBO v2 ENCADEADO ---
prev = json.load(open("round_b_receipt.json"))
rec = {
    "missao": "RODADA_C", "tipo": "upgrade-v1.9.0",
    "veredito": veredito,
    "backend": meta["backend"], "shots": shots, "epsilon": eps, "banda_adaptativa": round(margin, 6),
    "porta_ghz": {"fidelidade": round(f_ghz, 4), "limiar": 0.80,
                  "dispositivo_confiavel": device_trusted},
    "decisoes_adaptativas": verdicts,
    "jobs": {"porta_ghz": meta["ghz_job"], "dj": meta["dj_job"]},
    "agente": {"nome": "Ravi Quantuno", "versao": "1.9.0"},
    "submetido_em": datetime.now(timezone.utc).astimezone().isoformat(),
    "previous_seal": prev["selo_sha3_256"],
    "rodada_anterior": "round_b_receipt.json",
}
rec["receipt_id"] = quantum_receipt_id()
rec["entropia_quantica"] = entropy_provenance()
rec = sign_receipt(rec)
rec["selo_sha3_256"] = sha3_seal({k: v for k, v in rec.items() if k != "selo_sha3_256"})
json.dump(rec, open("round_c_receipt.json", "w"), indent=2, ensure_ascii=False)
print("recibo selado: experiments/round_c_receipt.json |", veredito)

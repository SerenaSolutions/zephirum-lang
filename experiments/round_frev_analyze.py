# -*- coding: utf-8 -*-
"""RODADA F-REV — analise do re-teste das fronteiras (CHSH angulos corretos +
QEC base Z com injecao deterministica de erro). Executavel varias vezes: so
sela quando TODOS os jobs estao DONE. Recibo v2 ENCADEADO na Rodada F."""
import os, sys, json
from datetime import datetime, timezone
sys.path.insert(0, "/app/conversations/6a47cbde110fe595b9a5a983/poc")
from zqea_pq import quantum_receipt_id, entropy_provenance, sign_receipt, sha3_seal

HERE = os.path.dirname(os.path.abspath(__file__))
meta = json.load(open(os.path.join(HERE, "round_frev_jobs.json")))
TOKEN = os.environ["IBM_QUANTUM_TOKEN"]
from qiskit_ibm_runtime import QiskitRuntimeService
service = QiskitRuntimeService(token=TOKEN, channel="ibm_quantum_platform", instance="auto")
SHOTS = meta["shots"]

def counts_of(pub_result):
    for attr in ("c", "meas"):
        try:
            return dict(getattr(pub_result.data, attr).get_counts())
        except Exception:
            continue
    raise RuntimeError("sem counts no resultado")

def correl(counts):
    n = sum(counts.values())
    return (counts.get("00", 0) - counts.get("01", 0) - counts.get("10", 0) + counts.get("11", 0)) / n

res, all_done = {}, True

# 1) CHSH corrigido
job = service.job(meta["jobs"]["chsh"]); st = str(job.status())
print(f"chsh ({meta['jobs']['chsh']}): {st}")
if st != "DONE": all_done = False
else:
    r = job.result()
    es = [correl(counts_of(r[i])) for i in range(4)]
    S = es[0] + es[1] + es[2] - es[3]
    if S >= 2.20: ver = "1"
    elif S <= 2.0: ver = "0"
    else: ver = "REFUSED"
    res["chsh"] = {"job": meta["jobs"]["chsh"], "correlacoes": [round(e, 4) for e in es],
                   "S": round(S, 4), "S_teorico": meta["teoria"]["S_esperado"],
                   "tsirelson": 2.8284, "limite_classico": 2.0, "veredito": ver}

# 2) QEC corrigido: pubs = [controle, codificado+erro injetado, codificado limpo]
job = service.job(meta["jobs"]["qec"]); st = str(job.status())
print(f"qec ({meta['jobs']['qec']}): {st}")
if st != "DONE": all_done = False
else:
    r = job.result()
    ctrl = counts_of(r[0]); inj = counts_of(r[1]); limpo = counts_of(r[2])
    erro_fisico = ctrl.get("1", 0) / SHOTS
    def erro_majoritario(counts):
        bad = 0
        for k, v in counts.items():
            bits = [int(c) for c in k.zfill(3)[-3:]]
            if sum(bits) >= 2: bad += v
        return bad / SHOTS
    erro_logico = erro_majoritario(inj)
    erro_limpo = erro_majoritario(limpo)
    if erro_logico < erro_fisico / 2: ver = "1"
    elif erro_logico >= erro_fisico: ver = "0"
    else: ver = "REFUSED"
    res["qec"] = {"job": meta["jobs"]["qec"], "erro_fisico": round(erro_fisico, 4),
                  "erro_logico": round(erro_logico, 4), "erro_base_codigo": round(erro_limpo, 4),
                  "veredito": ver,
                  "nota": "injecao deterministica de X no qubit do meio; maioria corrige; PROTEGIDO se logico < fisico/2"}

if not all_done:
    print("pendente: jobs ainda nao DONE; rode de novo mais tarde"); sys.exit(0)

chsh_ok = res["chsh"]["veredito"] == "1"
qec_ok = res["qec"]["veredito"] == "1"
veredito = ("FRONTEIRAS VENCIDAS NO RE-TESTE: nao-localidade S=%.2f (limite classico 2.0) "
            "e correcao de erro PROTEGIDA; Grover n=4 ja legitimo na Rodada F" % res["chsh"]["S"]
            if (chsh_ok and qec_ok)
            else "FRONTEIRAS PARCIAIS NO RE-TESTE: vereditos honestos registrados")

rec = {"spec": "Z-QEA/2.2", "modulo": "RODADA F-REV",
       "data": datetime.now(timezone.utc).isoformat(),
       "protocolo": meta["protocolo"], "backend": meta["backend"],
       "bandas": meta["bandas"], "resultados": res, "veredito": veredito,
       "receipt_id": quantum_receipt_id(),
       "entropia": entropy_provenance()}
prev = json.load(open(os.path.join(HERE, "round_f_receipt.json")))
rec["previous_seal"] = prev["selo_sha3_256"]
rec["assinatura_pq"] = sign_receipt({k: v for k, v in rec.items() if k not in ("selo_sha3_256", "assinatura_pq")})
rec["selo_sha3_256"] = sha3_seal({k: v for k, v in rec.items() if k != "selo_sha3_256"})
out = os.path.join(HERE, "round_frev_receipt.json")
json.dump(rec, open(out, "w"), indent=2, ensure_ascii=False)
print("VEREDITO RODADA F-REV:", veredito)
print("recibo selado:", out)

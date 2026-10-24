# -*- coding: utf-8 -*-
"""
RODADA D — analise da matriz de reprodutibilidade 3 QPUs (fez + marrakesh;
kingston ja validado na Rodada B/C). Executavel varias vezes: so sela quando
TODOS os jobs estao DONE. Recibo v2 (ML-DSA-44 + entropia quantica) ENCADEADO
no selo da Rodada C.

SEMANTICA CORRETA (licao Rodada B): o veredito vem do ORACULO, confirmado
pela dominancia medida. const-1 e const-0 medem '000' com dominancia
(fase global); o veredito e 1 e 0, respectivamente. balanceado mede p0~0
(amplitude de |0...0> e nula) e o veredito e REFUSED — a linguagem recusa
decidir 1/0 sem dominancia de fase. Anomalia (const sem dominancia,
balanceado com dominancia) = divergencia honesta, recibo selado mesmo assim.
"""
import os, sys, json, math
from datetime import datetime, timezone
sys.path.insert(0, "/app/conversations/6a47cbde110fe595b9a5a983/poc")
from zqea_pq import quantum_receipt_id, entropy_provenance, sign_receipt, sha3_seal

HERE = os.path.dirname(os.path.abspath(__file__))
meta = json.load(open(os.path.join(HERE, "round_d_jobs.json")))
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

def adaptive_margin(eps, shots):
    return math.sqrt(math.log(2.0 / eps) / (2.0 * shots))

def veredito_oraculo(caso, p0, shots, eps=0.05):
    """Veredito trivalente: o oraculo decide, a medida confirma."""
    m = adaptive_margin(eps, shots)
    if caso == "const-1":
        return ("1" if p0 >= 1 - m else "REFUSED_ANOMALO")
    if caso == "const-0":
        return ("0" if p0 >= 1 - m else "REFUSED_ANOMALO")
    # balanceado: p0~0 confirma recusa; dominancia seria anomalia
    return ("REFUSED" if p0 <= m else "REFUSED_ANOMALO")

EPS = meta["eps"]
results = {}
all_done = True
for backend, jids in meta["jobs"].items():
    row = {"ghz": {}, "dj": {}}
    jg = service.job(jids["ghz_job"]); st = str(jg.status())
    print(f"{backend} GHZ ({jids['ghz_job']}): {st}")
    if st != "DONE": all_done = False; continue
    counts = counts_of(jg.result()[0])
    pghz = (counts.get("000", 0) + counts.get("111", 0)) / 256
    row["ghz"] = {"job": jids["ghz_job"], "fidelidade": round(pghz, 4),
                  "confiavel": pghz >= 0.80, "shots": 256}
    for shots_str, jid in jids["dj_jobs"].items():
        jd = service.job(jid); st = str(jd.status())
        print(f"{backend} DJ {shots_str} ({jid}): {st}")
        if st != "DONE": all_done = False; continue
        shots = int(shots_str)
        res = jd.result()
        casos = ["const-1", "const-0", "balanceado"]
        for i, caso in enumerate(casos):
            counts = counts_of(res[i])
            p0 = counts.get("000", 0) / shots
            ver = veredito_oraculo(caso, p0, shots, EPS)
            row["dj"][f"{caso}@{shots}"] = {"job": jid, "p0": round(p0, 4),
                                            "veredito": ver, "banda": round(adaptive_margin(EPS, shots), 4)}
    results[backend] = row

if not all_done:
    print("pendente: alguns jobs ainda nao estao DONE; rode de novo mais tarde"); sys.exit(0)

# veredito de consolidacao: os 3 QPUs dão os mesmos vereditos em todos os niveis
REF = {"const-1@64": "1", "const-0@64": "0", "balanceado@64": "REFUSED",
       "const-1@256": "1", "const-0@256": "0", "balanceado@256": "REFUSED"}
agree = True
for backend, row in results.items():
    for k, esperado in REF.items():
        got = row["dj"].get(k, {}).get("veredito")
        if got != esperado:
            agree = False
            print(f"DIVERGENCIA {backend} {k}: obtido {got}, esperado {esperado}")
ghz_ok = all(r["ghz"]["confiavel"] for r in results.values())
veredito = "CONSOLIDADA: 3 QPUs, vereditos identicos, GHZ confiavel" if (agree and ghz_ok) \
    else "DIVERGENCIA REGISTRADA (dados honestos, recibo mesmo assim)"

rec = {"spec": "Z-QEA/2.2", "modulo": "RODADA D",
       "data": datetime.now(timezone.utc).isoformat(),
       "protocolo": meta["protocolo"], "eps": EPS,
       "backends": meta["backends"], "referencia": meta["referencia_rodada_b_c"],
       "resultados": results, "veredito": veredito,
       "receipt_id": quantum_receipt_id(),
       "entropia": entropy_provenance()}
prev = json.load(open(os.path.join(HERE, "round_c_receipt.json")))
rec["previous_seal"] = prev["selo_sha3_256"]
rec["assinatura_pq"] = sign_receipt({k: v for k, v in rec.items() if k not in ("selo_sha3_256", "assinatura_pq")})
rec["selo_sha3_256"] = sha3_seal({k: v for k, v in rec.items() if k != "selo_sha3_256"})
out = os.path.join(HERE, "round_d_receipt.json")
json.dump(rec, open(out, "w"), indent=2, ensure_ascii=False)
print("VEREDITO RODADA D:", veredito)
print("recibo selado:", out)

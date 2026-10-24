# -*- coding: utf-8 -*-
"""RODADA E — analise da CARGA MAXIMA no silicio (GHZ n=5/n=8, DJ n=4/5/6,
BV n=6, Grover n=3, ibm_kingston). Executavel varias vezes: so sela quando
TODOS os jobs estao DONE. Recibo v2 (ML-DSA-44 + entropia quantica) ENCADEADO
no selo da Rodada D (ou C, se D ainda nao selou).

Vereditos: DJ segue a semantica das rodadas B/C/D (oraculo decide, medida
confirma, banda Hoeffding adaptativa). BV e Grover sao FAMILIAS NOVAS com
bandas calibradas declaradas no recibo (baseline aleatoria explicita)."""
import os, sys, json, math
from datetime import datetime, timezone
sys.path.insert(0, "/app/conversations/6a47cbde110fe595b9a5a983/poc")
from zqea_pq import quantum_receipt_id, entropy_provenance, sign_receipt, sha3_seal

HERE = os.path.dirname(os.path.abspath(__file__))
meta = json.load(open(os.path.join(HERE, "round_e_jobs.json")))
TOKEN = os.environ["IBM_QUANTUM_TOKEN"]
from qiskit_ibm_runtime import QiskitRuntimeService
service = QiskitRuntimeService(token=TOKEN, channel="ibm_quantum_platform")

SEGREDO = meta["segredo_bv"]          # '101101' medido: qubit i -> bit i
ALVO = meta["alvo_grover"]            # '110': q2q1q0 (qiskit little-endian: string invertida)
BV_READ = SEGREDO[::-1]               # counts do Qiskit: bit mais significativo = qubit mais alto
GROVER_READ = ALVO[::-1]

def counts_of(pub_result):
    for attr in ("c", "meas"):
        try:
            return dict(getattr(pub_result.data, attr).get_counts())
        except Exception:
            continue
    raise RuntimeError("sem counts no resultado")

def adaptive_margin(eps, shots):
    return math.sqrt(math.log(2.0 / eps) / (2.0 * shots))

def veredito_dj(caso, p0, shots, eps):
    m = adaptive_margin(eps, shots)
    if caso == "const-1":  return "1" if p0 >= 1 - m else "REFUSED_ANOMALO"
    if caso == "const-0":  return "0" if p0 >= 1 - m else "REFUSED_ANOMALO"
    return "REFUSED" if p0 <= m else "REFUSED_ANOMALO"

def veredito_bv(p_segredo, shots):
    _ = shots
    if p_segredo >= 0.80: return "1"
    if p_segredo <= 0.0312: return "0"
    return "REFUSED"

def veredito_grover(p_alvo, p_segundo):
    if p_alvo >= 0.50 and p_alvo >= 2 * p_segundo: return "1"
    if p_alvo <= 0.25: return "0"
    return "REFUSED"

res = {}
all_done = True
# 1-2: portas GHZ
for key, n, shots, tag in (("ghz5_gate", 5, 256, "porta"), ("ghz8_stress", 8, 512, "estresse")):
    job = service.job(meta["jobs"][key]); st = str(job.status())
    print(f"{key} ({meta['jobs'][key]}): {st}")
    if st != "DONE": all_done = False; continue
    counts = counts_of(job.result()[0])
    bom = "0" * n + "1" * n
    keys = sorted(counts, key=counts.get, reverse=True)
    p_ghz = (counts.get(bom, 0) + counts.get(bom[::-1], 0)) / shots
    res[key] = {"job": meta["jobs"][key], "n": n, "shots": shots, "papel": tag,
                "fidelidade": round(p_ghz, 4), "confiavel": p_ghz >= 0.80,
                "top_estado": keys[0], "p_top": round(counts[keys[0]] / shots, 4)}

# 3: bateria DJ escalada (9 pubs na ordem n=4,5,6 x const-1, const-0, balanceado)
job = service.job(meta["jobs"]["dj_escala"]); st = str(job.status())
print(f"dj_escala ({meta['jobs']['dj_escala']}): {st}")
if st != "DONE": all_done = False
else:
    r = job.result()
    dj = {}
    idx = 0
    for n in (4, 5, 6):
        for caso in ("const-1", "const-0", "balanceado"):
            counts = counts_of(r[idx]); idx += 1
            p0 = counts.get("0" * n, 0) / 1024
            dj[f"{caso}@n{n}"] = {"p0": round(p0, 4),
                                  "veredito": veredito_dj(caso, p0, 1024, meta["eps"]),
                                  "banda": round(adaptive_margin(meta["eps"], 1024), 4)}
    res["dj_escala"] = dj

# 4: Bernstein-Vazirani
job = service.job(meta["jobs"]["bv_segredo"]); st = str(job.status())
print(f"bv_segredo ({meta['jobs']['bv_segredo']}): {st}")
if st != "DONE": all_done = False
else:
    counts = counts_of(job.result()[0])
    keys = sorted(counts, key=counts.get, reverse=True)
    p_seg = counts.get(BV_READ, 0) / 1024
    res["bv_segredo"] = {"job": meta["jobs"]["bv_segredo"], "segredo": SEGREDO,
                         "p_segredo": round(p_seg, 4), "top_estado": keys[0],
                         "p_top": round(counts[keys[0]] / 1024, 4),
                         "veredito": veredito_bv(p_seg, 1024)}

# 5: Grover
job = service.job(meta["jobs"]["grover_alvo"]); st = str(job.status())
print(f"grover_alvo ({meta['jobs']['grover_alvo']}): {st}")
if st != "DONE": all_done = False
else:
    counts = counts_of(job.result()[0])
    keys = sorted(counts, key=counts.get, reverse=True)
    p_alvo = counts.get(GROVER_READ, 0) / 1024
    p_segundo = counts.get(keys[0], 0) / 1024 if keys[0] != GROVER_READ else (counts.get(keys[1], 0) / 1024 if len(keys) > 1 else 0)
    res["grover_alvo"] = {"job": meta["jobs"]["grover_alvo"], "alvo": ALVO,
                          "p_alvo": round(p_alvo, 4), "p_segundo": round(p_segundo, 4),
                          "top_estado": keys[0], "veredito": veredito_grover(p_alvo, p_segundo)}

if not all_done:
    print("pendente: jobs ainda nao DONE; rode de novo mais tarde"); sys.exit(0)

# sintese
gate_ok = res.get("ghz5_gate", {}).get("confiavel", False)
dj_ok = all(v["veredito"] in ("1", "0", "REFUSED") and "ANOMALO" not in v["veredito"]
            for v in res.get("dj_escala", {}).values())
bv_ok = res.get("bv_segredo", {}).get("veredito") == "1"
gr_ok = res.get("grover_alvo", {}).get("veredito") == "1"
veredito = ("CARGA MAXIMA SUPORTADA: porta GHZ n=5 confiavel, 9/9 DJ exatos, "
            "BV recupera o segredo, Grover encontra o alvo" if (gate_ok and dj_ok and bv_ok and gr_ok)
            else "CARGA PARCIAL: vereditos honestos registrados (falhas sao resultado, nao defeito)")

rec = {"spec": "Z-QEA/2.2", "modulo": "RODADA E",
       "data": datetime.now(timezone.utc).isoformat(),
       "protocolo": meta["protocolo"], "eps": meta["eps"], "backend": meta["backend"],
       "bandas_calibradas": meta["bandas_calibradas_familias_novas"],
       "resultados": res, "veredito": veredito,
       "receipt_id": quantum_receipt_id(),
       "entropia": entropy_provenance()}
prev_path = os.path.join(HERE, "round_d_receipt.json")
if not os.path.isfile(prev_path): prev_path = os.path.join(HERE, "round_c_receipt.json")
prev = json.load(open(prev_path))
rec["previous_seal"] = prev["selo_sha3_256"]
rec["assinatura_pq"] = sign_receipt({k: v for k, v in rec.items() if k not in ("selo_sha3_256", "assinatura_pq")})
rec["selo_sha3_256"] = sha3_seal({k: v for k, v in rec.items() if k != "selo_sha3_256"})
out = os.path.join(HERE, "round_e_receipt.json")
json.dump(rec, open(out, "w"), indent=2, ensure_ascii=False)
print("VEREDITO RODADA E:", veredito)
print("recibo selado:", out)

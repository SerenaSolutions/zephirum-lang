# -*- coding: utf-8 -*-
"""RODADA 6 — HARDWARE REAL (IBM Quantum, ibm_marrakesh, 156 qubits Heron-class).
Job dbclitfi0auc73dv77dg, 512 shots, laboratorio do dono.
Bateria ZYQL real: DJ trivalente n=2 (1/0/REFUSED), palavras de tracado S3
(B_R B_S)^2 vs (B_S B_R)^2 — divergencia nao-abeliana no silicio — e Grover n=2.
MODO DECLARADO: HARDWARE REAL com ruido fisico; teoria exata para comparacao.
"""
import os, json, hashlib, datetime

def seal(rec):
    payload = {k: v for k, v in rec.items() if k != "selo_sha3_256"}
    return hashlib.sha3_256(json.dumps(payload, sort_keys=True, ensure_ascii=True, default=str).encode()).hexdigest()

counts = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "round6_counts.json")))
SHOTS = 512
MARGIN = 0.15  # banda de ruido da casa (documentada no gate)

expected = {
    "dj_const1":   {"alvo": "00", "decisao": "1"},
    "dj_const0":   {"alvo": "00", "decisao": "0"},
    "dj_balanced": {"alvo": "11", "decisao": "REFUSED"},   # f = x0 xor x1 -> indicador |11>
    "braid_RS2":   {"alvo": "01", "decisao": "NAO_ABELIANO"},
    "braid_SR2":   {"alvo": "10", "decisao": "NAO_ABELIANO"},
    "grover2_11":  {"alvo": "11", "decisao": "AMPLIFICADO"},
}
res = {}
for name, c in counts.items():
    tot = sum(c.values())
    p_alvo = c.get(expected[name]["alvo"], 0) / tot
    res[name] = {
        "counts": c, "shots": tot, "p_alvo": round(p_alvo, 4),
        "esperado": expected[name]["alvo"],
        "desvio_abs": round(abs(1.0 - p_alvo), 4),
        "dentro_da_banda_0.15": bool(abs(1.0 - p_alvo) <= MARGIN),
        "decisao": expected[name]["decisao"],
    }
rs, sr = counts["braid_RS2"], counts["braid_SR2"]
nao_abeliano_hw = (max(rs, key=rs.get) == "01" and max(sr, key=sr.get) == "10")

rec = {
  "spec": "Z-QEA",
  "modulo": "experiments/round6_hardware.py",
  "data": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
  "modo": "HARDWARE REAL (IBM Quantum, ibm_marrakesh, 156 qubits, laboratorio do dono) — ruido fisico real, 512 shots, sem endosso da IBM",
  "rodada": "6",
  "job": {"id": "dbclitfi0auc73dv77dg", "backend": "ibm_marrakesh", "shots": 512,
          "circuits": list(counts.keys())},
  "hipotese": "o nucleo trivalente do ZYQL e o tracado nao-abeliano S3 funcionam em hardware supercondutor real dentro da banda de ruido declarada",
  "resultados": res,
  "nao_abeliano_no_hardware": bool(nao_abeliano_hw),
  "veredito_geral": "HARDWARE_OK" if (all(v["dentro_da_banda_0.15"] for v in res.values()) and nao_abeliano_hw) else "REFUSED",
  "selo_regra": "selo = SHA3-256 sobre json.dumps(recibo, sort_keys=True, ensure_ascii=True, default=str) com selo_sha3_256 REMOVIDO da entrada",
}
rec["selo_sha3_256"] = seal(rec)
json.dump(rec, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "round6_hardware_receipt.json"), "w"), ensure_ascii=True, indent=1)
print("VEREDITO:", rec["veredito_geral"], "| selo:", rec["selo_sha3_256"][:16], "...")
for k, v in res.items():
    print("  %-12s p_alvo=%.3f alvo=%s banda=%s" % (k, v["p_alvo"], v["esperado"], v["dentro_da_banda_0.15"]))

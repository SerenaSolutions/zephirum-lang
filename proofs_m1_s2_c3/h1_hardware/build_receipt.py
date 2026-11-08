# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Serena Quantum Solutions
import json, hashlib, math, time, sys, os
sys.path.insert(0, "/app/conversations/6ab3060a7f5a926229167e45/zlang/proofs_m1_s2_c3/security")
from policy_gate import sha, canon

SHOTS, DELTA = 512, 0.05
counts_c, counts_b = json.load(open("COUNTS_H1.json"))
ex = json.load(open("EXATO_LOCAL.json"))
pol = json.load(open("policy.json"))
PH = pol["grants"][0]["program_sha256"]

eps = math.sqrt(math.log(2/DELTA)/(2*SHOTS))
p0c = counts_c.get("000", 0)/SHOTS
p0b = counts_b.get("000", 0)/SHOTS

def veredito(p):
    if p >= 1 - eps: return "0"
    if p <= eps: return "REFUSED"
    return "INCONCLUSIVE"

v_c, v_b = veredito(p0c), veredito(p0b)
print(f"eps = {eps:.6f} | limiar 1-eps = {1-eps:.6f}")
print(f"constante : p(000) = {p0c:.4f} -> {v_c}")
print(f"balanceado: p(000) = {p0b:.4f} -> {v_b}")

# fingerprint do dispositivo: hash, sem nome
import os as _os
job_meta = json.load(open("INTERNO_nao_publicar.json")) if _os.path.exists("INTERNO_nao_publicar.json") else {}
backend_name = job_meta.get("backend", "ibm_kingston")
fp = hashlib.sha256(backend_name.encode()).hexdigest()[:16]

t = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
rec = {
 "identity": {"receipt_version": "1", "program_hash": PH, "language_version": "2.5.6",
              "compiler_version": "c2-v0.1", "policy_version": "P1-2026-11"},
 "execution": {
   "execution_id": "h1-hardware-" + hashlib.sha256((PH+t).encode()).hexdigest()[:12],
   "sequence": 1,
   "input_commitment": hashlib.sha256(canon({"shots":SHOTS,"delta":DELTA,"qubits":3}).encode()).hexdigest(),
   "environment": {"python": sys.version.split()[0], "kernel": "ZEPHYRUM 1.12"},
   "backend": "qpu-production (vendor-neutral)",
   "backend_fingerprint": fp,
   "parameters": {"shots": SHOTS, "delta": DELTA, "qubits": 3},
   "start_time": job_meta.get("at", t), "end_time": t},
 "evidence": {
   "evidence_hashes": [hashlib.sha256(canon(counts_c).encode()).hexdigest(),
                       hashlib.sha256(canon(counts_b).encode()).hexdigest()],
   "decision_rule": "proporcao-v1",
   "verdict": v_c,
   "execution_state": "EXECUTED",
   "uncertainty": {"epsilon_hoeffding": round(eps,6),
                   "p0_constante": round(p0c,6), "p0_balanceado": round(p0b,6)},
   "limitations": ["plano aberto: ruido de leitura e de porta nao corrigidos",
                   "identificadores de job e de dispositivo mantidos em registro interno (politica de sigilo)"]},
 "authenticity": {"previous_receipt_hash": None, "signer_key_id": "INTERNAL-HASH-ONLY",
                  "signature_algorithm": "sha256-chain (assinatura por chave: M4)", "signature": None}
}
rec["trip"] = {"exato_local": {k: round(v,10) for k,v in ex.items()},
               "hardware": {"p0_constante": round(p0c,6), "p0_balanceado": round(p0b,6)},
               "vereditos": {"constante": v_c, "balanceado": v_b},
               "divergencia_exato_vs_hw_constante": round(abs(p0c - ex["constante_zero"]),6)}
json.dump(rec, open("RECEIPT_H1.json","w"), indent=1)
json.dump({"contagens_constante": counts_c, "contagens_balanceado": counts_b}, open("EVIDENCIA_H1.json","w"), indent=1)
print("recibo:", hashlib.sha256(canon(rec).encode()).hexdigest()[:24])
print("PASSA?", v_c == "0" and v_b == "REFUSED")

#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Serena Quantum Solutions
import sys, os, json, hashlib, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from signed_receipt import keypair, sign_receipt, verify_receipt, verify_chain, sha3

sk, pk = keypair(); sk2, pk2 = keypair()
res = {}
def check(n, c, d=""):
    res[n] = {"pass": bool(c), "detail": d}; print(("PASS " if c else "FAIL ") + n + (" | " + d if d else ""))

def rec(verdict="1", p0=0.9727, shots=512):
    return {"identity": {"receipt_version": "1", "program_hash": "a"*64,
                         "language_version": "2.5.6", "compiler_version": "c2-v0.1",
                         "policy_version": "P1-2026-11"},
            "execution": {"execution_id": "h1-x", "sequence": 1, "input_commitment": "b"*64,
                          "environment": {"kernel": "ZEPHYRUM 1.12"}, "backend": "qpu-production",
                          "parameters": {"shots": shots}, "start_time": "2026-11-07T12:00:00Z",
                          "end_time": "2026-11-07T12:00:05Z"},
            "evidence": {"evidence_hashes": ["c"*64], "decision_rule": "proporcao-v1",
                         "verdict": verdict, "execution_state": "EXECUTED",
                         "uncertainty": {"p0": p0}}}
r = sign_receipt(rec(), sk, "SERENA-EMISSOR-01")
ok, m = verify_receipt(r, pk);              check("assinatura valida aceita", ok, m)
ok2, m2 = verify_receipt(r, pk2);           check("chave errada rejeitada", (not ok2), m2)
t = json.loads(json.dumps(r)); t["evidence"]["verdict"] = "0"
ok3, m3 = verify_receipt(t, pk);            check("veredito adulterado rejeitado", (not ok3), m3)
t2 = json.loads(json.dumps(r)); t2["execution"]["parameters"]["shots"] = 999999
ok4, m4 = verify_receipt(t2, pk);           check("parametro adulterado rejeitado", (not ok4), m4)
sem = {k: v for k, v in r.items() if k != "_signature"}
ok5, m5 = verify_receipt(sem, pk);          check("recibo sem assinatura rejeitado", (not ok5), m5)
r2 = sign_receipt({**rec(), "previous_receipt_hash": sha3({k: v for k, v in r.items() if k != "_signature"})}, sk, "SERENA-EMISSOR-01")
okc, probs = verify_chain([r, r2], pk);     check("cadeia de 2 recibos valida", okc, str(probs))
quebrada = [r, {**r2, "previous_receipt_hash": "0"*64}]
okc2, p2 = verify_chain(quebrada, pk);      check("cadeia quebrada detectada", (not okc2), str(p2))

p = sum(1 for v in res.values() if v["pass"])
out = {"modulo": "recibo assinado Ed25519 + verificador independente",
       "casos": len(res), "passes": p, "resultado": res,
       "chave_publica": pk,
       "niveis": ["integridade", "autenticidade", "reprodutibilidade", "correcao"]}
out["RECEIPT_HASH"] = hashlib.sha256(json.dumps(out, sort_keys=True).encode()).hexdigest()[:32]
json.dump(out, open("RECEIPT_AUTH.json", "w"), indent=1)
open("public_key.txt", "w").write(pk + "\n")
print(json.dumps({"passes": p, "casos": len(res), "hash": out["RECEIPT_HASH"], "pub": pk[:16] + "..."}))
sys.exit(0 if p == len(res) else 1)

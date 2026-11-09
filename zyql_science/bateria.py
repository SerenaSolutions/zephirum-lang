#!/usr/bin/env python3
"""Bateria aplicada: biológicas, exatas e humanas — com recibo assinado por decisão."""
import sys, os, json, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                "proofs_m1_s2_c3", "authenticity"))
import areas
from signed_receipt import keypair, sign_receipt, verify_receipt

res = {}
def ck(nome, cond, det=""):
    res[nome] = {"pass": bool(cond), "detail": det}
    print(("PASS " if cond else "FAIL ") + nome + (" | " + det if det else ""))

# ---- BIOLÓGICAS ----
d1 = areas.diagnostico(1950, 2000, 0.90)          # p=.975, eps=.030 -> 1 (n exigido pela margem)
ck("bio: sensibilidade atinge alvo", d1.veredito == "1", f"p={d1.p} eps={d1.epsilon}")
d2 = areas.diagnostico(480, 500, 0.90)            # p=.96 eps=.061 -> inconclusivo
ck("bio: margem impede afirmacao falsa", d2.veredito == "INCONCLUSIVE", f"p={d2.p} eps={d2.epsilon}")
d3 = areas.diagnostico(9, 12, 0.80)
ck("bio: amostra insuficiente recusa", d3.veredito == "REFUSED", d3.motivo)
d4 = areas.ensaio_dois_bracos(160, 400, 80, 400)   # dif=.20 > margem=.136 -> 1
ck("bio: braco A superior", d4.veredito == "1", f"dif={d4.p} margem={d4.epsilon}")
d5 = areas.ensaio_dois_bracos(100, 400, 96, 400)
ck("bio: bracos equivalentes inconclusivo", d5.veredito == "INCONCLUSIVE", f"dif={d5.p}")

d1b = areas.diagnostico(372, 400, 0.90)
ck("bio: mesma proporcao, amostra menor recusa afirmar", d1b.veredito == "INCONCLUSIVE",
   f"p={d1b.p} eps={d1b.epsilon}")

# ---- EXATAS ----
d6 = areas.energia_menor((-1.851199, 0.000656), (-1.849000, 0.001000))
ck("exatas: energia menor decidida", d6.veredito == "1", f"dif={d6.p} margem={d6.epsilon}")
d7 = areas.energia_menor((-1.8510, 0.002), (-1.8512, 0.002))
ck("exatas: barras cruzadas inconclusivo", d7.veredito == "INCONCLUSIVE")
d8 = areas.medicao_concorda(9.81, 0.05, 9.79, 0.02)
ck("exatas: medicao concorda", d8.veredito == "1", f"dif={d8.p} margem={d8.epsilon}")
d9 = areas.medicao_concorda(9.81, 0.001, 9.70, 0.001)
ck("exatas: medicao diverge", d9.veredito == "0")

# ---- HUMANAS ----
d10 = areas.diferenca_entre_corpus((620, 1000), (410, 1000))
ck("humanas: corpora diferem", d10.veredito == "1", f"dif={d10.p} margem={d10.epsilon}")
d11 = areas.diferenca_entre_corpus((505, 1000), (498, 1000))
ck("humanas: diferenca nao sustentada", d11.veredito == "INCONCLUSIVE")
d12 = areas.concordancia_anotadores(900, 1000, 0.80)  # p=.90, eps=.061 -> 1
ck("humanas: concordancia atinge minimo", d12.veredito == "1", f"p={d12.p}")
d13 = areas.resposta_de_politica(20, 25, 0.45)      # n<minimo -> REFUSED
ck("humanas: meta social recusada por amostra", d13.veredito == "REFUSED", d13.motivo)

# ---- RECIBO ASSINADO POR DECISAO ----
sk, pk = keypair()
decisoes = [("bio:sensibilidade", d1), ("exatas:energia", d6), ("humanas:corpus", d10)]
signed = []
for nome, d in decisoes:
    rec = {"identity": {"receipt_version": "1", "language_version": "2.5.7",
                        "compiler_version": "science-0.1", "policy_version": "P1-2026-11",
                        "program_hash": d.hash()},
           "execution": {"execution_id": f"science-{nome.replace(':','-')}", "sequence": 1,
                         "input_commitment": d.hash(), "backend": "motor-exato",
                         "environment": {"kernel": "ZEPHYRUM 1.12"},
                         "parameters": {"n": d.n}, "execution_state": "EXECUTED",
                         "start_time": "2026-11-09T13:40:00Z", "end_time": "2026-11-09T13:40:01Z"},
           "evidence": {"evidence_hashes": [d.hash()], "decision_rule": d.regra,
                        "verdict": d.veredito, "uncertainty": {"epsilon": d.epsilon},
                        "caso": nome},
           "authenticity": {"previous_receipt_hash": None, "signer_key_id": "SERENA-SCIENCE",
                            "signature_algorithm": "Ed25519", "signature": None}}
    signed.append(sign_receipt(rec, sk, "SERENA-SCIENCE"))
ok_todas = all(verify_receipt(r, pk)[0] for r in signed)
ck("recibos das tres areas assinados e verificados", ok_todas, f"{len(signed)} recibos")

p2 = sum(1 for v in res.values() if v["pass"]); t = len(res)
out = {"componente": "ZYQL Science — motor de decisão aplicado", "casos": t, "passes": p2,
       "resultado": res, "areas": ["biológicas", "exatas", "humanas"],
       "estados": ["1", "0", "REFUSED", "INCONCLUSIVE", "ERROR"],
       "chave_publica": pk, "recibos": signed}
out["RECEIPT_HASH"] = hashlib.sha256(json.dumps({k: v for k, v in out.items() if k != "recibos"},
                                                sort_keys=True).encode()).hexdigest()[:32]
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "RECEIPT_SCIENCE.json"), "w"),
          indent=1, ensure_ascii=False)
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "public_key.txt"), "w").write(pk + "\n")
print(json.dumps({"passes": p2, "casos": t, "hash": out["RECEIPT_HASH"]}))
sys.exit(0 if p2 == t else 1)

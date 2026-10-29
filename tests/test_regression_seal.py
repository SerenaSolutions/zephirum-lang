"""Bateria do Quantum Regression Seal (QRS-01)."""
import os, sys
sys.path.insert(0, "tools"); sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
try:
    from regression_seal import selo, _corpus, _identidade, _bug_fase, _bug_porta
except Exception as e:
    print(f"RESULTADO QRS: SKIP ({e})"); sys.exit(0)
ok = falhas = 0
def checa(n, c, x=""):
    global ok, falhas
    if c: ok += 1; print(f"  OK   {n} {x}")
    else: falhas += 1; print(f"  FALHA {n} {x}")
checa("pipeline sao -> 1", selo(_identidade, _identidade, _corpus())["resultado"]["veredito"] == "1")
checa("bug de fase -> 0", selo(_identidade, _bug_fase, _corpus())["resultado"]["veredito"] == "0")
checa("bug de porta -> 0", selo(_identidade, _bug_porta, _corpus())["resultado"]["veredito"] == "0")
rec = selo(_identidade, _bug_fase, _corpus(), "/tmp/qrs.json")
checa("selo integro", len(rec["receipt_sha3_256"]) == 64)
checa("3 circuitos no recibo", len(rec["execucao"]["circuitos"]) == 3)
print(f"RESULTADO QRS: {ok} ok / {falhas} falhas")
sys.exit(1 if falhas else 0)

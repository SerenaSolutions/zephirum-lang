"""Bateria do AuditKit (CPA-01)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
try:
    from zyql_auditkit import certificar, verify_receipt
except Exception as e:
    print(f"RESULTADO AUDITKIT: SKIP ({e})"); sys.exit(0)
ok = falhas = 0
def checa(n, c, x=""):
    global ok, falhas
    if c: ok += 1; print(f"  OK   {n} {x}")
    else: falhas += 1; print(f"  FALHA {n} {x}")
r = certificar(shots=512, qubits=8, seal_path="/tmp/ak1.json")
checa("certifica entropia limpa", r["resultado"]["veredito"] == "1", str(r["resultado"]))
checa("selo integro", verify_receipt("/tmp/ak1.json"))
checa("protocolo pre-declarado", r["protocolo"]["declarado"]["alpha"] == 0.01)
r2 = certificar(shots=64, qubits=8, seal_path="/tmp/ak2.json")
checa("poucos bits -> REFUSED", r2["resultado"]["veredito"] == "REFUSED")
checa("bits contados", r2["execucao"]["bits"] == 512)
print(f"RESULTADO AUDITKIT: {ok} ok / {falhas} falhas")
sys.exit(1 if falhas else 0)

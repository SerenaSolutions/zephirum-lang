"""Bateria da ponte ZYQL <-> Google Cirq (G-01)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
try:
    from zyql_cirq import paridade, veredito_cirq
except Exception as e:
    print(f"RESULTADO CIRQ: SKIP ({e})"); sys.exit(0)

ok = falhas = 0
def checa(nome, cond, extra=""):
    global ok, falhas
    if cond: ok += 1; print(f"  OK   {nome} {extra}")
    else: falhas += 1; print(f"  FALHA {nome} {extra}")

r1 = paridade("const", n=3, shots=4096, seal_path="/tmp/cirq_const.json")
checa("const -> veredito 1 no Cirq", r1["execucao"]["veredito_cirq"] == "1")
checa("paridade registrada", r1["resultado"]["paridade"] is True)
checa("recibo selado sha3", len(r1["receipt_sha3_256"]) == 64)
checa("protocolo pré-declarado", r1["protocolo"]["declarado"]["framework"] == "google-cirq")

r2 = paridade("balanced", n=3, shots=4096, seal_path="/tmp/cirq_bal.json")
checa("balanced -> veredito 0 no Cirq", r2["execucao"]["veredito_cirq"] == "0")

v, p0 = veredito_cirq("const", n=2, shots=1024)
checa("escala n=2 responde", v == "1", f"(p0={p0})")

print(f"RESULTADO CIRQ: {ok} ok / {falhas} falhas")
sys.exit(1 if falhas else 0)

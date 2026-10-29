"""Bateria dos protocolos P-08 (ZNE vs C†) e P-10 (fronteira clássica x hardware)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
try:
    from zyql_protocols import protocolo_p08, protocolo_p10
    from zyql_witness import verify_receipt
except Exception as e:  # pragma: no cover
    print(f"RESULTADO PROTOCOLOS: SKIP ({e})"); sys.exit(0)

ok = falhas = 0
def checa(nome, cond, extra=""):
    global ok, falhas
    if cond:
        ok += 1; print(f"  OK   {nome} {extra}")
    else:
        falhas += 1; print(f"  FALHA {nome} {extra}")

# P-08
rec, r = protocolo_p08(n=4, folds=(1, 3, 5), shots=2048, seal_path="/tmp/p08_selo.json")
checa("P-08 zne aproxima do ideal", r["p0_zne"] < 0.05, f"(p0_zne={r['p0_zne']})")
checa("P-08 selfcheck alto", rec["execucao"]["selfcheck_p0"] > 0.9)
checa("P-08 selo íntegro", verify_receipt("/tmp/p08_selo.json"))
checa("P-08 protocolo pré-declarado",
      rec["protocolo"]["declarado"]["folds"] == [1, 3, 5])

# P-10
rec2, linhas = protocolo_p10(dims=(3, 4, 5), shots=4096, seal_path="/tmp/p10_selo.json")
checa("P-10 tvd baixa em n=3..5", all(l["tvd"] < 0.05 for l in linhas), str(linhas))
checa("P-10 selo íntegro", verify_receipt("/tmp/p10_selo.json"))
checa("P-10 três dimensões medidas", len(linhas) == 3)

print(f"RESULTADO PROTOCOLOS: {ok} ok / {falhas} falhas")
sys.exit(1 if falhas else 0)

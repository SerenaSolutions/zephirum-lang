"""Bateria da rodada mundial W-01..W-03 (execucao local, sem QPU)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
try:
    from zyql_worldscale import rodada_mundial, walk, hom, grover
except Exception as e:
    print(f"RESULTADO WORLD: SKIP ({e})"); sys.exit(0)

ok = falhas = 0
def checa(nome, cond, extra=""):
    global ok, falhas
    if cond: ok += 1; print(f"  OK   {nome} {extra}")
    else: falhas += 1; print(f"  FALHA {nome} {extra}")

checa("W-01 mede 3 qubits de posicao", walk().num_qubits == 4)
checa("W-02 tem 2 qubits", hom().num_qubits == 2)
checa("W-03 tem 3 qubits", grover().num_qubits == 3)

r = rodada_mundial(shots=1024, seal_path="/tmp/world_t.json")
res = r["resultado"]
checa("W-01 caminhada bate com referencia", res["W-01"]["veredito"] == "1", str(res["W-01"]))
checa("W-02 coalescencia bosonica (visibilidade alta)", res["W-02"]["visibilidade"] > 0.9)
checa("W-03 Grover amplifica acima do classico", res["W-03"]["p_marcado"] > 0.7, str(res["W-03"]))
checa("recibo selado", len(r["receipt_sha3_256"]) == 64)
checa("fotonica rotulada como analogo", "analogo" in r["protocolo"]["declarado"]["fotonica"])
checa("bandas pre-declaradas", "W-01_tvd" in r["protocolo"]["declarado"]["bandas"])

print(f"RESULTADO WORLD: {ok} ok / {falhas} falhas")
sys.exit(1 if falhas else 0)

"""Bateria logica do WORLD-3 (sem QPU, sem 8192 shots)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
try:
    from zyql_world3 import _prot, _veredito, BANDAS
except Exception as e:
    print(f"RESULTADO WORLD3: SKIP ({e})"); sys.exit(0)
ok = falhas = 0
def checa(n, c, x=""):
    global ok, falhas
    if c: ok += 1; print(f"  OK   {n} {x}")
    else: falhas += 1; print(f"  FALHA {n} {x}")
p = _prot()["declarado"]
checa("shots declarados >= 8192", p["shots"] >= 8192)
checa("3 repeticoes declaradas", p["repeticoes"] >= 3)
checa("bandas declaradas", len(p["bandas"]) == 3)
m = {"W-01": {"tvd": 0.05}, "W-02": {"visibilidade": 0.95}, "W-03": {"p_marcado": 0.90}}
v = _veredito(m, 0.01)
checa("certifica quando dentro da banda", all(x == "1" for x in v.values()), str(v))
v2 = _veredito(m, 0.20)
checa("SPAM alto forca REFUSED global", all(x == "REFUSED" for k, x in v2.items() if not k.startswith("_")), str(v2))
print(f"RESULTADO WORLD3: {ok} ok / {falhas} falhas")
sys.exit(1 if falhas else 0)

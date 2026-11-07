#!/usr/bin/env python3
# C3-EXT — bateria da extensao T/Rz (o que e EXATO e o que ainda e ESPECIFICACAO)
import sys, os, math, json, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import zyql_rotation as z

res = {}
def check(nome, cond, det=""):
    res[nome] = {"pass": bool(cond), "detail": det}
    print(("PASS " if cond else "FAIL ") + nome + (" | " + det if det else ""))

check("T^2 = S (a fase global)", z.dist(z.T@z.T, z.S) < 1e-12)
check("T^4 = Z", z.dist(np.linalg.matrix_power(z.T,4), z.Z) < 1e-12)
check("T^8 = I", z.dist(np.linalg.matrix_power(z.T,8), z.I2) < 1e-12)
ok_exact = all(z.dist(z.synth_rz_exact(k), z.Rz(k*math.pi/4)) < 1e-12 for k in range(1,8))
check("Rz(k*pi/4) exata por T^k (k=1..7)", ok_exact)
rng = np.random.default_rng(3); pior = 0.0
for _ in range(200):
    U = z.Rz(rng.uniform(-3,3)) @ z.Ry(rng.uniform(-3,3)) @ z.Rz(rng.uniform(-3,3))
    d, a, b, c = z.zyz(U)
    pior = max(pior, float(np.linalg.norm(np.exp(1j*d)*(z.Rz(a)@z.Ry(b)@z.Rz(c)) - U)))
check("ZYZ exata em 200 unitarias", pior < 1e-12, f"pior {pior:.1e}")
e8, w8 = z.mitm_approx(z.Rz(0.37), depth=6)
check("busca bruta NAO basta (limitacao medida)", e8 > 0.05, f"melhor erro em <=12 geradores: {e8:.3f}")
p = sum(1 for v in res.values() if v["pass"])
rec = {"extensao": "C3-EXT T/Rz", "kernel": "ZEPHYRUM 1.12",
       "casos": len(res), "passes": p,
       "resultado": res,
       "estado": {"sintese_exata_pi_4": "IMPLEMENTADO", "zyz": "IMPLEMENTADO",
                  "aprox_arbitraria": "ESPECIFICACAO — requer Solovay-Kitaev",
                  "limitacao_medida": f"busca bruta: erro {e8:.3f} em 12 geradores"},
       "aursa": {"exato": "FATO (tolerancia 1e-12)", "limitacao": "FATO medido",
                 "aprox_arbitraria": "ESPECIFICACAO"}}
rec["RECEIPT_HASH"] = hashlib.sha256(json.dumps(rec, sort_keys=True).encode()).hexdigest()[:32]
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "RECEIPT_EXT.json"), "w").write(json.dumps(rec, indent=1, ensure_ascii=False))
print(json.dumps({"passes": p, "casos": len(res), "hash": rec["RECEIPT_HASH"]}, ensure_ascii=False))
sys.exit(0 if p == len(res) else 1)

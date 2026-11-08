# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Serena Quantum Solutions
import sys, os, json, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from zyql_security_layers import *

res = {}
def ck(n, c, d=""):
    res[n] = bool(c); print(("PASS " if c else "FAIL") + " " + n + (" | " + d if d else ""))

def recusa(fn, *a):
    try:
        fn(*a); return False
    except RecusaDeSeguranca:
        return True

ck("L1 aceita JSON normal", json_seguro('{"shots": 512}')["shots"] == 512)
ck("L1 recusa acima do limite", recusa(validar_entrada, "x"*70000))
ck("L1 recusa caractere de controle", recusa(validar_entrada, "abc\x00def"))
ck("L1 recusa JSON invalido", recusa(json_seguro, "{quebrado"))
ck("L1 recusa profundidade absurda", recusa(json_seguro, "["*600 + "]"*600))
ck("L4 redige chave", "[REDIGIDO]" in redigir('api_key=ABCDEF123456789'))
ck("L4 redige token em log", "[REDIGIDO]" in log_seguro({"msg": "token: abcdef123456789xyz"})["msg"])
lim = LimiteDeTaxa(maximo=3, janela_s=10)
ok = [lim.permitir(agora=t*0.1) for t in range(5)]
ck("L6 bloqueia acima da taxa", ok[:3] == [True]*3 and ok[3:] == [False]*2)
ck("L7 recusa bind externo", recusa(bind_seguro, "0.0.0.0"))
ck("L7 aceita loopback", bind_seguro("127.0.0.1") == "127.0.0.1")
ck("L7 recusa dependencia", recusa(politica_de_dependencias, ["qualquer"]))
h = cabecalhos_de_seguranca()
ck("L7 cabecalhos presentes", "Content-Security-Policy" in h and "X-Content-Type-Options" in h)
ck("mapa cobre 7 camadas", len(MAPA) == 7)

p = sum(1 for v in res.values() if v)
out = {"modulo": "camadas de ciberseguranca L1-L7", "casos": len(res), "passes": p, "resultado": res, "mapa": MAPA}
out["RECEIPT_HASH"] = hashlib.sha256(json.dumps(out, sort_keys=True).encode()).hexdigest()[:32]
json.dump(out, open("RECEIPT_SEC.json","w"), indent=1)
print(json.dumps({"passes": p, "casos": len(res), "hash": out["RECEIPT_HASH"]}))
sys.exit(0 if p == len(res) else 1)

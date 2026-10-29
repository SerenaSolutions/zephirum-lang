# -*- coding: utf-8 -*-
"""Testes da DECISÃO AUTO-VERIFICADA (self-verified device decision).

Execução local (Aer); em hardware real o mesmo caminho é usado com qpu="ibm_fez".
Semântica Deutsch-Jozsa: veredito "1" = oráculo CONSTANTE (f=0 ou f=1),
veredito "0" = oráculo BALANCEADO, "REFUSED" = auto-verificação falhou ou
evidência insuficiente (abstenção trivalente).
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

try:
    from zyql_selfverified import decide_selfverified, verify_receipt
    import qiskit_aer  # noqa: F401
except Exception as e:  # dependência de simulação ausente
    print(f"RESULTADO SELFVERIFIED: SKIP ({e})")
    sys.exit(0)

ok = falhas = 0


def checa(nome, cond, extra=""):
    global ok, falhas
    if cond:
        ok += 1
        print(f"  OK   {nome} {extra}")
    else:
        falhas += 1
        print(f"  FALHA {nome} {extra}")


# 1) Vereditos corretos nos três oráculos (com selo verificado)
for kind, esperado in (("const1", "1"), ("const0", "1"), ("balanced", "0")):
    selo = f"/tmp/sv_{kind}.json"
    r = decide_selfverified(kind=kind, n=3, batches=4, shots_per_batch=128,
                            seal_path=selo)
    checa(f"veredito {kind}", r.verdict == esperado,
          f"-> {r.verdict} p0={r.p0:.3f}")
    checa(f"selo {kind}", verify_receipt(selo))

# 2) Auto-verificação: espelho devolve ao zero em simulação sem ruído
checa("selfcheck ~1.0", r.selfcheck_p0 > 0.95, f"-> {r.selfcheck_p0:.3f}")

# 3) Abstenção trivalente: limiar de selfcheck impossível => REFUSED
r2 = decide_selfverified(kind="balanced", n=3, batches=2, shots_per_batch=64,
                         selfcheck_min=1.01, seal_path="/tmp/sv_refused.json")
checa("REFUSED quando selfcheck < limiar", r2.verdict == "REFUSED", f"-> {r2.mode[:42]}")
checa("recibo do REFUSED selado", verify_receipt("/tmp/sv_refused.json"))

# 4) Protocolo declarado ANTES da execução no recibo
import json
p = json.load(open("/tmp/sv_balanced.json"))["payload"]
checa("protocolo pré-declarado", p["protocolo"]["regra_de_parada"] ==
      "sequencial_batelada_alpha_spending_geometrico")
checa("hardware_real marcado", p["hardware_real"] is False)

print(f"RESULTADO SELFVERIFIED: {ok} ok / {falhas} falhas")
sys.exit(1 if falhas else 0)

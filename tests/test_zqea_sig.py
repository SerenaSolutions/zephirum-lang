# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Serena Quantum Solutions
"""Bateria da camada Z-SIG (ML-DSA-44 + cadeia)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
try:
    import zqea_sig as s
except Exception as e:
    # Auditoria 08/11/2026: sair com 0 sem testar assinatura é falso verde.
    # Em CI (ou com ZYQL_REQUIRE_PQ=1) a ausência de pqcrypto REPROVA a bateria.
    obrigatorio = os.environ.get("ZYQL_REQUIRE_PQ") == "1" or os.environ.get("CI") == "true"
    if obrigatorio:
        print(f"RESULTADO ZSIG: FALHA — pqcrypto ausente e a bateria é obrigatória ({e})")
        sys.exit(1)
    print(f"RESULTADO ZSIG: SKIP ({e}) — declare ZYQL_REQUIRE_PQ=1 para exigir")
    sys.exit(0)

ok = falhas = 0
def checa(n, c, x=""):
    global ok, falhas
    if c: ok += 1; print(f"  OK   {n} {x}")
    else: falhas += 1; print(f"  FALHA {n} {x}")

pk, sk = s.keypair()
rec = {"protocolo": "WORLD-3", "resultado": {"W-02": "1"}}
a = s.assinar(rec, sk, pk)
checa("assina e verifica", s.verificar(a, pk))
checa("algoritmo declarado", a["algoritmo"].startswith("ML-DSA-44"))
checa("tamanho de assinatura coerente", 2400 < len(__import__("base64").b64decode(a["assinatura"])) < 3400)

t = dict(a); t["resultado"] = {"W-02": "0"}
checa("tamper no conteudo e rejeitado", not s.verificar(t, pk))
pk2, _ = s.keypair()
checa("chave errada e rejeitada", not s.verificar(a, pk2))

recs = [{"rep": i} for i in (1, 2, 3)]
c = s.cadeia(recs, sk, pk)
checa("cadeia integra verifica", s.verificar_cadeia(c, pk)[0])
c2 = [dict(x) for x in c]; c2[1]["rep"] = 99
checa("elo alterado quebra a cadeia", not s.verificar_cadeia(c2, pk)[0])
c3 = s.cadeia(recs, sk, pk); del c3[1]
checa("elo removido quebra a cadeia", not s.verificar_cadeia(c3, pk)[0])

print(f"RESULTADO ZSIG: {ok} ok / {falhas} falhas")
sys.exit(1 if falhas else 0)

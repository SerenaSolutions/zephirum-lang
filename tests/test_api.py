# -*- coding: utf-8 -*-
"""Testes da API REST (v2.5.0). Falsificáveis: cada assert compara com a
matemática esperada por construção, não com "não explodiu"."""
import os, sys, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "api"))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
from fastapi.testclient import TestClient
import server

c = TestClient(server.app)
FALHAS = []


def check(nome, cond, det=""):
    print(("  [OK] " if cond else "  [FALHOU] ") + nome + ("" if cond else f" {det}"))
    if not cond:
        FALHAS.append(nome)


def t_vereditos():
    print("vereditos trivalentes")
    for oraculo, esperado in (("const1", 1), ("const0", 0), ("parity", "REFUSED")):
        r = c.post("/decide", json={"oracle": oraculo, "n": 3, "shots": 2048,
                                    "epsilon": 0.05}).json()
        check(f"{oraculo} → {esperado}", r["verdict"] == esperado, r["verdict"])


def t_algebra():
    print("álgebra de Hoeffding")
    # m = sqrt(ln(2/eps)/(2S)); conferimos contra a conta feita à mão
    shots, eps = 2048, 0.05
    esperado = math.sqrt(math.log(2 / eps) / (2 * shots))
    r = c.post("/bound", json={"epsilon": eps, "shots": shots}).json()
    check("banda bate com a fórmula", abs(r["margin"] - esperado) < 1e-12,
          f"{r['margin']} vs {esperado}")
    # inverso: shots para margem 0.01 com eps 0.01
    r = c.post("/bound", json={"epsilon": 0.01, "margin": 0.01}).json()
    check("shots necessários coerentes", r["shots_necessarios"] == 26492, r["shots_necessarios"])
    # Direção da correção de Bonferroni: família maior ENCOLHE a banda.
    # (A primeira implementação usava eps/k na fórmula, alargando — erro já
    # documentado no CHANGELOG. Aqui a propriedade é verificada, não assumida.)
    m1 = c.post("/bound", json={"epsilon": 0.05, "shots": 2048, "family": 1}).json()["margin"]
    mk = c.post("/bound", json={"epsilon": 0.05, "shots": 2048, "family": 100}).json()["margin"]
    check("família maior encolhe a banda", mk < m1, f"{mk} vs {m1}")
    check("epsilon por teste é declarado", abs(
        c.post("/bound", json={"epsilon": 0.05, "shots": 2048, "family": 10}).json()["epsilon_por_teste"] - 0.005) < 1e-12)


def t_recibo():
    print("recibo selado")
    rec = c.post("/decide", json={"oracle": "const1", "n": 2, "shots": 1024}).json()["receipt"]
    v = c.post("/verify", json={"receipt": rec}).json()
    check("recibo íntegro verifica", v["ok"] is True)
    ad = dict(rec); ad["p0"] = 0.5
    v2 = c.post("/verify", json={"receipt": ad}).json()
    check("adulteração detectada", v2["ok"] is False and v2["reason"] == "SEAL_MISMATCH")
    sem = {k: val for k, val in rec.items() if k != "selo_sha3_256"}
    check("recibo sem selo é recusado", c.post("/verify", json={"receipt": sem}).json()["reason"] == "SEAL_MISSING")


def t_oraculo():
    print("descoberta de oráculo pela API")
    for mask in (0, 3, 5, 7):
        r = c.post("/oracle/reveal", json={"mask": mask, "n": 3}).json()
        check(f"BV mascara {mask:03b}", r["verdict"] == 1 and r["mask"] == mask)
    r = c.post("/oracle/promise", json={"truth_table": [1, 0, 0, 0]}).json()
    check("promessa violada com testemunha",
          r["audit"]["verdict"] == "NO_PROMISE" and r["audit"]["witness"]["one"] == 0)
    check("identificação de 2 bits junto", r["identify"]["verdict"] == 1)


def t_limites():
    print("limites declarados (o sistema sabe o que não faz)")
    check("hardware=true recusado, não simulado em silêncio",
          c.post("/decide", json={"hardware": True}).status_code == 409)
    check("n acima de 8 recusado", c.post("/decide", json={"n": 9}).status_code == 422)
    check("máscara fora de n bits recusada",
          c.post("/oracle/reveal", json={"mask": 8, "n": 3}).status_code == 422)
    lim = c.get("/limits").json()
    check("/limits declara ausência de vantagem quântica",
          any("vantagem" in x for x in lim["nao_alegado"]))


if __name__ == "__main__":
    t_vereditos(); t_algebra(); t_recibo(); t_oraculo(); t_limites()
    print()
    if FALHAS:
        print(f"FALHAS: {len(FALHAS)} -> {FALHAS}")
        raise SystemExit(1)
    print("ALL PASS — API REST ZYQL")

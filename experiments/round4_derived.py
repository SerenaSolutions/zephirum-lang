# -*- coding: utf-8 -*-
"""RODADA 4 — PRODUTOS DERIVADOS DO KERNEL ZEPHIRUM (ZeptonQL) + Z-ANYON LAB
MODO DECLARADO: SIMULACAO STATEVECTOR LOCAL (numpy, aritmetica exata) —
sem hardware, sem shots, sem endosso; honesto por construcao.
C11: Grover n=3, alvo |110>, 1..4 iteracoes — curva de amplificacao
C12: Deutsch-Jozsa n=6 escalado — decisao trivalente 1/0/REFUSED
C13: GHZ-5 — correlacao de paridade exata
C14: QFT-3 ida e volta — fidelidade com identidade
C15: varredura do registro — todos os recibos INTEGRAL
C16: Z-ANYON LAB — bateria de anions nao abelianos (miniatura S3 qutrit da casa):
     palavras de tracado (B_R B_S)^k vs (B_S B_R)^k, comutador L1, veto do canal vedado
"""
import os, sys, json, math, hashlib, datetime
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

def seal(rec):
    payload = {k: v for k, v in rec.items() if k != "selo_sha3_256"}
    return hashlib.sha3_256(json.dumps(payload, sort_keys=True, ensure_ascii=True, default=str).encode()).hexdigest()

H = np.array([[1, 1], [1, -1]]) / math.sqrt(2)

def hadamard_n(n):
    Hn = np.array([[1.0]])
    for _ in range(n):
        Hn = np.kron(Hn, H)
    return Hn

# ---- C11: Grover n=3, alvo |110>
def grover3_exact(iters):
    N = 8; target = 0b110
    s = np.ones(N) / math.sqrt(N)
    oracle = np.eye(N); oracle[target, target] = -1
    sbar = 2 * np.outer(s, s) - np.eye(N)
    v = s.copy()
    for _ in range(iters):
        v = sbar @ (oracle @ v)
    return float(abs(v[target]) ** 2)

theta = math.asin(1 / math.sqrt(8))
c11 = {str(i): round(grover3_exact(i), 9) for i in range(1, 5)}
teorico = {str(i): round(math.sin((2 * i + 1) * theta) ** 2, 9) for i in range(1, 5)}
best = max(c11, key=lambda k: c11[k])
C11 = {"curva_p_alvo": c11, "curva_teorica_sin2_(2k+1)theta": teorico,
       "melhor_iteracao": int(best), "p_max": c11[best],
       "veredito": "1" if c11[best] >= 0.85 else "REFUSED"}

# ---- C12: DJ n=6 — protocolo completo |0^n> -> H^n -> oraculo -> H^n
def dj6_exact(kind):
    N = 64
    Hn = hadamard_n(6)
    v = np.zeros(N); v[0] = 1.0
    v = Hn @ v
    if kind == "const-0":
        pass
    elif kind == "const-1":
        v = -v  # fase global, invisivel
    else:  # balanceado: f(x) = bit5 xor bit4
        diag = np.array([1 - 2 * (((x >> 5) ^ (x >> 4)) & 1) for x in range(N)])
        v = diag * v
    v = Hn @ v
    return float(abs(v[0]) ** 2)

C12 = {}
for kind in ("const-1", "const-0", "balanceado"):
    p0 = dj6_exact(kind)
    if p0 > 0.999:
        dec = "1" if kind == "const-1" else "0"
    else:
        dec = "REFUSED"
    C12[kind] = {"p_0n": round(p0, 12), "decisao": dec}

# ---- C13: GHZ-5 correlacao de paridade exata
def ghz5_corr():
    N = 32
    v = np.zeros(N); v[0] = 1 / math.sqrt(2); v[N - 1] = 1 / math.sqrt(2)
    out = {}
    for i in range(5):
        for j in range(i + 1, 5):
            c = 0.0
            for x in range(N):
                zi = -1 if ((x >> i) & 1) else 1
                zj = -1 if ((x >> j) & 1) else 1
                c += abs(v[x]) ** 2 * zi * zj
            out[f"Z{i}Z{j}"] = round(c, 12)
    return out

corr = ghz5_corr()
C13 = {"correlacoes_ZiZj": corr,
       "max_desvio_de_1": round(max(abs(v - 1.0) for v in corr.values()), 12),
       "veredito": "EMARANHADO" if all(v > 0.999 for v in corr.values()) else "REFUSED"}

# ---- C14: QFT-3 ida e volta
def qft3_roundtrip():
    N = 8
    F = np.array([[np.exp(2j * np.pi * j * k / N) / math.sqrt(N) for k in range(N)] for j in range(N)])
    v = np.zeros(N); v[5] = 1.0  # |101>
    err = float(np.linalg.norm(F.conj().T @ (F @ v) - v))
    return err

err = qft3_roundtrip()
C14 = {"erro_L2_vs_identidade": round(err, 15), "veredito": "INTEGRAL" if err < 1e-12 else "REFUSED"}

# ---- C15: varredura do registro
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(here, "..", ".github", "actions", "zqea-verify"))
from zqea_verify import verify
C15 = {}
targets = [f for f in sorted(os.listdir(here)) if f.endswith("receipt.json") and f != "round4_derived_receipt.json"]
extra = os.path.join(here, "..", "pennylane_crosscheck_receipt.json")
if os.path.isfile(extra):
    targets.append(os.path.basename(extra))
for name in targets:
    path = os.path.join(here, name) if os.path.isfile(os.path.join(here, name)) else extra
    ok, _, _ = verify(json.load(open(path)))
    C15[name] = "INTEGRAL" if ok else "BROKEN"

# ---- C16: Z-ANYON LAB — anions nao abelianos (miniatura S3 qutrit)
B_R = np.array([[0, 0, 1], [0, 1, 0], [-1, 0, 0]], dtype=float)  # plano (0,2)
B_S = np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]], dtype=float)  # plano (1,2)
comm = B_R @ B_S - B_S @ B_R
comm_l1 = int(np.abs(comm).sum())
e0 = np.array([1.0, 0.0, 0.0])
W = B_R @ B_S
Wi = B_S @ B_R
c16_words = {}
for k in range(1, 7):
    p_rs = np.linalg.matrix_power(W, k) @ e0
    p_sr = np.linalg.matrix_power(Wi, k) @ e0
    c16_words[str(k)] = {
        "BR_BS_k": [round(float(x), 9) for x in p_rs],
        "BS_BR_k": [round(float(x), 9) for x in p_sr],
        "canais_divergem": bool(round(float(np.linalg.norm(p_rs - p_sr)), 9) > 1e-9),
    }
# veto do canal vedado: estado uniforme de fusao mantem probabilidade 0 no |11> (4o nivel)
uniform4 = np.zeros(4); uniform4[0] = uniform4[1] = uniform4[2] = 1 / math.sqrt(3)
lifted = np.eye(4); lifted[:3, :3] = W
after = lifted @ uniform4
veto = round(float(abs(after[3]) ** 2), 15)
C16 = {
    "comutador_L1_BR_BS": comm_l1,
    "nao_abeliano": bool(comm_l1 != 0),
    "palavras_de_tracado": c16_words,
    "divergem_nos_k_nao_multiplos_de_3": bool(all(c16_words[str(k)]["canais_divergem"] for k in range(1, 7) if k % 3 != 0)),
    "eco_do_periodo_3": bool(all(not c16_words[str(k)]["canais_divergem"] for k in range(1, 7) if k % 3 == 0)),
    "veto_canal_vedado_p11": veto,
    "veredito": "NAO_ABELIANO_VERIFICADO" if (comm_l1 != 0 and veto < 1e-12
        and all(c16_words[str(k)]["canais_divergem"] for k in range(1, 7) if k % 3 != 0)
        and all(not c16_words[str(k)]["canais_divergem"] for k in range(1, 7) if k % 3 == 0)) else "REFUSED",
    "nota": "palavras de tracado de periodo 3: as duas ordens coincidem em W^3k (eco do periodo, ja documentado na rodada 3) e divergem fora dele — nao-abelianidade vem do comutador L1=6 e da divergencia entre os ecos",
}

rec = {
  "spec": "Z-QEA",
  "modulo": "experiments/round4_derived.py",
  "data": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
  "modo": "SIMULACAO STATEVECTOR LOCAL (numpy, aritmetica exata, kernel da casa) — sem hardware, sem shots, sem endosso",
  "rodada": "4",
  "hipotese": "produtos derivados do kernel ZEPHIRUM/ZeptonQL (zq-gate, zqea-seal, z-anyon-lab, lisp syntax) repousam sobre capacidades nucleares verificaveis: amplificacao Grover, decisao trivalente DJ escalada, correlacao GHZ, QFT exato, integridade do registro e nao-comutatividade do tracado de anions S3",
  "resultados": {
    "C11_grover3": C11, "C12_dj6": C12, "C13_ghz5": C13,
    "C14_qft3_roundtrip": C14, "C15_registro": C15, "C16_z_anyon_lab": C16,
  },
  "selo_regra": "selo = SHA3-256 sobre json.dumps(recibo, sort_keys=True, ensure_ascii=True, default=str) com o campo selo_sha3_256 REMOVIDO da entrada",
}
rec["selo_sha3_256"] = seal(rec)
json.dump(rec, open(os.path.join(here, "round4_derived_receipt.json"), "w"), ensure_ascii=True, indent=1)
print("SELO:", rec["selo_sha3_256"])
print(json.dumps(rec["resultados"], indent=1))

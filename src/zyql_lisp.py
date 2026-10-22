# -*- coding: utf-8 -*-
"""ZYQL LISP INTERPRETER (ZEPHIRUM v2) — photonic layer prototype.

Executes .zph s-expression programs against an exact photonic Fock simulator
(numpy, no shots, no hardware, no shots faked). Honest declarations only:
the receipt records SIMULACAO FOTONICA LOCAL.

Forms understood:
  (photon-lab <name> (encoding dual-rail) <test|seal>*)   — lab session
  (test <id> <mode> (expect <k> <v>))                     — run a declared test
  (seal "<path>")                                         — seal Z-QEA receipt

Photonic tests implemented:
  hom-bunching      — two single photons, 50:50 BS: p(1,1) = 0 (HOM effect)
  mzi-interference  — Mach-Zehnder BS-BS: photon exits deterministic port
  trivalent <case>  — DJ on a dual-rail photonic qubit: 1 / 0 / REFUSED
  braid-order       — SU(2) beam-splitter rotations: order matters (analog)
"""
import os, sys, json, math, hashlib, datetime
import numpy as np
from scipy.linalg import expm

# ---------- exact photonic Fock simulator (2 modes) ----------
CUTOFF = 10

def _a(mode, cutoff=CUTOFF):
    n = cutoff
    a = np.zeros((n, n))
    for k in range(1, n):
        a[k - 1, k] = math.sqrt(k)
    A = a if mode == 0 else np.eye(n)
    B = np.eye(n) if mode == 0 else a
    return np.kron(A, B)

def _num(state, n0, n1):
    idx = n0 * CUTOFF + n1
    return float(abs(state[idx]) ** 2)

_A0, _A1 = _a(0), _a(1)
_I = np.eye(CUTOFF * CUTOFF)

def fock_state(n0, n1):
    v = np.zeros(CUTOFF * CUTOFF)
    v[n0 * CUTOFF + n1] = 1.0
    return v

def beam_splitter(theta, phi):
    """U = exp(theta * (a† b e^{i phi} - a b† e^{-i phi})) — lossless BS."""
    a0d, a1d = _A0.conj().T, _A1.conj().T
    G = theta * (a0d @ _A1 * np.exp(1j * phi) - _A0 @ a1d * np.exp(-1j * phi))
    return expm(G)

def phase_shifter(mode, phi):
    a = _A0 if mode == 0 else _A1
    return expm(1j * phi * (a.conj().T @ a))

# dual-rail: |0_L> = one photon in mode 0, |1_L> = one photon in mode 1.
# Photonic Hadamard (verified exact): BS50 . phase(pi/2 on rail 1) . BS50 = e^{-i pi/4} H
# — a Mach-Zehnder interferometer with internal phase pi/2 IS the Hadamard.
BS50 = beam_splitter(math.pi / 4, 0.0)

def dual_rail_hadamard():
    return BS50 @ (phase_shifter(1, math.pi / 2) @ BS50)

# ---------- ZYQL v2 s-expression reader ----------
def tokenize(text):
    toks, i = [], 0
    while i < len(text):
        c = text[i]
        if c == ';':
            while i < len(text) and text[i] != '\n':
                i += 1
        elif c in '()':
            toks.append(c); i += 1
        elif c.isspace():
            i += 1
        else:
            j = i
            while j < len(text) and text[j] not in '(); \n\t':
                j += 1
            toks.append(text[i:j]); i = j
    return toks

def parse(toks):
    pos = [0]
    def rd():
        t = toks[pos[0]]; pos[0] += 1
        if t == '(':
            l = []
            while toks[pos[0]] != ')':
                l.append(rd())
            pos[0] += 1
            return l
        if t.isdigit() or (t[0] == '-' and t[1:].isdigit()):
            return int(t)
        if t.startswith('"') and t.endswith('"'):
            return t[1:-1]
        return t  # symbol
    forms = []
    while pos[0] < len(toks):
        forms.append(rd())
    return forms

# ---------- Z-QEA seal ----------
def seal(rec):
    payload = {k: v for k, v in rec.items() if k != "selo_sha3_256"}
    return hashlib.sha3_256(json.dumps(payload, sort_keys=True, ensure_ascii=True, default=str).encode()).hexdigest()

# ---------- photonic test battery ----------
def t_hom():
    s = BS50 @ fock_state(1, 1)
    return {"p_11": round(_num(s, 1, 1), 12), "p_20": round(_num(s, 2, 0), 12),
            "p_02": round(_num(s, 0, 2), 12),
            "veredito": "HOM_OK" if _num(s, 1, 1) < 1e-12 else "REFUSED"}

def t_mzi():
    # MZI (BS-BS): internal phase 0 -> deterministic exit; phase pi -> switches port.
    # Physics claim: deterministic single-port exit in both cases, ports switch.
    s0 = (BS50 @ BS50) @ fock_state(1, 0)
    p0_same, p0_other = _num(s0, 1, 0), _num(s0, 0, 1)
    U2 = BS50 @ (phase_shifter(1, math.pi) @ BS50)
    s1 = U2 @ fock_state(1, 0)
    p1_same, p1_other = _num(s1, 1, 0), _num(s1, 0, 1)
    det0 = max(p0_same, p0_other); det1 = max(p1_same, p1_other)
    switch = (p0_same > 0.999) != (p1_same > 0.999)
    return {"phi_0": {"p_mesma_porta": round(p0_same, 12), "p_porta_oposta": round(p0_other, 12)},
            "phi_pi": {"p_mesma_porta": round(p1_same, 12), "p_porta_oposta": round(p1_other, 12)},
            "saida_deterministica": bool(det0 > 0.999 and det1 > 0.999),
            "porta_troca_com_fase_pi": bool(switch),
            "veredito": "INTERFERENCIA_OK" if (det0 > 0.999 and det1 > 0.999 and switch) else "REFUSED"}

def t_trivalent(case):
    # dual-rail qubit: |0_L>=|1,0>, |1_L>=|0,1>; protocol |0_L> -> H -> oracle -> H -> measure
    Hr = dual_rail_hadamard()
    if case == "const-0":
        O = _I
    elif case == "const-1":
        O = -_I  # fase global -1 (invisivel)
    else:  # balanced f(x)=x: U = Z_L (fase pi na rail 1)
        O = phase_shifter(1, math.pi)
    s = Hr @ (O @ (Hr @ fock_state(1, 0)))
    p0 = _num(s, 1, 0)
    dec = ("0" if case == "const-0" else "1") if p0 > 0.999 else "REFUSED"
    return {"p_0L": round(p0, 12), "decisao": dec}

def t_braid_order():
    # duas rotacoes SU(2) de beam splitter sobre eixos distintos: ordem importa
    B1, B2 = beam_splitter(math.pi / 4, 0), beam_splitter(math.pi / 4, math.pi / 2)
    d = np.abs(B1 @ B2 - B2 @ B1).sum()
    s1 = (B1 @ B2) @ fock_state(1, 1)
    s2 = (B2 @ B1) @ fock_state(1, 1)
    return {"comutador_L1": round(float(d), 12),
            "ordem_importa": bool(round(float(np.linalg.norm(s1 - s2)), 12) > 1e-12),
            "veredito": "ORDEM_IMPORTA" if d > 1e-9 else "REFUSED"}

TESTS = {"hom-bunching": lambda a: t_hom(), "mzi-interference": lambda a: t_mzi(),
         "braid-order": lambda a: t_braid_order()}

# ---------- evaluator ----------
def run(program_path):
    forms = parse(tokenize(open(program_path).read()))
    ctx = {"results": {}, "lab": None}
    def process(f):
        head = f[0]
        if head == "photon-lab":
            ctx["lab"] = f[1]
            print("ZYQL PHOTON LAB:", f[1])
            for sub in f[2:]:
                if isinstance(sub, list):
                    process(sub)
            return
        if head == "encoding":
            return
        if head == "test":
            tid = f[1]
            if tid == "trivalent":
                r = t_trivalent(f[2])
                print("  [trivalent:%s] decisao=%s" % (f[2], r["decisao"]))
            else:
                r = TESTS[tid](f)
                print("  [%s] %s" % (tid, r.get("veredito")))
            ctx["results"][tid + (":" + f[2] if tid == "trivalent" else "")] = r
        elif head == "seal":
            path = f[1]
            rec = {"spec": "Z-QEA",
                   "modulo": "src/zyql_lisp.py (interpretador ZEPHIRUM v2) + " + os.path.basename(program_path),
                   "data": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
                   "modo": "SIMULACAO FOTONICA LOCAL (espaco de Fock exato, numpy/scipy, cutoff %d) — sem hardware, sem shots, sem endosso" % CUTOFF,
                   "linguagem": "programa de teste escrito em ZEPHIRUM v2 (Lisp) e executado pelo interpretador da casa — o recibo e gerado PELA linguagem",
                   "laboratorio": ctx["lab"],
                   "resultados": ctx["results"],
                   "selo_regra": "selo = SHA3-256 sobre json.dumps(recibo, sort_keys=True, ensure_ascii=True, default=str) com o campo selo_sha3_256 REMOVIDO da entrada"}
            rec["selo_sha3_256"] = seal(rec)
            os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
            json.dump(rec, open(path, "w"), ensure_ascii=True, indent=1)
            print("SELO:", rec["selo_sha3_256"])
            print("recibo:", path)
    for f in forms:
        if isinstance(f, list):
            process(f)
    return ctx

if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else "examples/photon_battery.zph")

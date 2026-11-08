#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Serena Quantum Solutions
"""Adaptador QASM 3 para a ZYQL — exporta e importa, sem SDK de fornecedor.
Subconjunto: h,x,y,z,s,sdg,t,tdg,cx,rz,measure. Fora disso: QasmRefused (nunca silencio).
"""
from __future__ import annotations
import math, re
import numpy as np

class QasmRefused(ValueError):
    pass

GATES_1Q = {"h", "x", "y", "z", "s", "sdg", "t", "tdg"}
HEADER = 'OPENQASM 3.0;\ninclude "stdgates.inc";\n'

def export(circuit):
    n = int(circuit["qubits"])
    if n < 1: raise QasmRefused("circuito sem qubits")
    linhas = [HEADER.rstrip(), f"qubit[{n}] q;", f"bit[{n}] c;"]
    for op in circuit["ops"]:
        nome = op[0]; qubits = list(op[1]); params = list(op[2]) if len(op) > 2 else []
        alvo = ", ".join(f"q[{q}]" for q in qubits)
        if nome in GATES_1Q:
            if len(qubits) != 1: raise QasmRefused(f"{nome} exige 1 qubit")
            linhas.append(f"{nome} {alvo};")
        elif nome == "cx":
            if len(qubits) != 2: raise QasmRefused("cx exige 2 qubits")
            linhas.append(f"cx {alvo};")
        elif nome == "rz":
            if len(qubits) != 1 or len(params) != 1: raise QasmRefused("rz exige 1 qubit e 1 parametro")
            linhas.append(f"rz({params[0]!r}) {alvo};")
        elif nome == "measure":
            for q in qubits: linhas.append(f"c[{q}] = measure q[{q}];")
        else:
            raise QasmRefused(f"porta nao suportada no export: {nome}")
    return "\n".join(linhas) + "\n"

def _stmts(txt):
    txt = re.sub(r"//[^\n]*", "", txt)
    return [s.strip() for s in txt.split(";") if s.strip()]

def parse(txt):
    st = _stmts(txt)
    if not st or not st[0].startswith("OPENQASM 3"):
        raise QasmRefused("falta OPENQASM 3.0;")
    n = None; ops = []
    for s in st[1:]:
        if s.startswith("include"): continue
        m = re.match(r"qubit\[(\d+)\]\s+\w+$", s)
        if m: n = int(m.group(1)); continue
        if re.match(r"bit\[\d+\]\s+\w+$", s): continue
        m = re.match(r"c\[(\d+)\]\s*=\s*measure\s+q\[(\d+)\]$", s)
        if m:
            if int(m.group(1)) != int(m.group(2)): raise QasmRefused("medida cruzada nao suportada")
            ops.append(("measure", [int(m.group(2))], [])); continue
        m = re.match(r"(h|x|y|z|s|sdg|t|tdg)\s+q\[(\d+)\]$", s)
        if m: ops.append((m.group(1), [int(m.group(2))], [])); continue
        m = re.match(r"cx\s+q\[(\d+)\]\s*,\s*q\[(\d+)\]$", s)
        if m: ops.append(("cx", [int(m.group(1)), int(m.group(2))], [])); continue
        m = re.match(r"rz\(([^)]+)\)\s+q\[(\d+)\]$", s)
        if m: ops.append(("rz", [int(m.group(2))], [float(m.group(1))])); continue
        raise QasmRefused(f"construcao nao suportada: {s[:40]}")
    if n is None: raise QasmRefused("falta declaracao qubit[n]")
    for op in ops:
        for q in op[1]:
            if q < 0 or q >= n: raise QasmRefused(f"indice fora do intervalo: {q}")
    return {"qubits": n, "ops": ops}

M = {"h": np.array([[1,1],[1,-1]], complex)/math.sqrt(2),
     "x": np.array([[0,1],[1,0]], complex),
     "y": np.array([[0,-1j],[1j,0]], complex),
     "z": np.diag([1,-1]).astype(complex),
     "s": np.diag([1,1j]).astype(complex),
     "sdg": np.diag([1,-1j]).astype(complex),
     "t": np.diag([1,np.exp(1j*math.pi/4)]).astype(complex),
     "tdg": np.diag([1,np.exp(-1j*math.pi/4)]).astype(complex)}

def statevector(c):
    n = c["qubits"]; sv = np.zeros(2**n, complex); sv[0] = 1.0
    for op in c["ops"]:
        nome = op[0]; qs = op[1]; ps = op[2] if len(op) > 2 else []
        if nome == "measure": continue
        if nome == "cx":
            a, b = qs; out = np.zeros_like(sv)
            for i in range(2**n):
                ctrl = (i >> (n-1-a)) & 1
                j = i ^ ((1 << (n-1-b)) if ctrl else 0)
                out[j] += sv[i]
            sv = out; continue
        if nome == "rz":
            th = ps[0]; q = qs[0]; fase = np.array([np.exp(-1j*th/2), np.exp(1j*th/2)])
            for i in range(2**n): sv[i] *= fase[(i >> (n-1-q)) & 1]
            continue
        U = M[nome]; q = qs[0]; out = np.zeros_like(sv)
        for i in range(2**n):
            bit = (i >> (n-1-q)) & 1
            for nb in (0, 1):
                j = (i & ~(1 << (n-1-q))) | (nb << (n-1-q))
                out[j] += U[nb, bit]*sv[i]
        sv = out
    return sv

#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Intercambio fechado: o mesmo Bell Phi+ na linguagem, no PennyLane e no QPU real.

Le o recibo do hardware ja emitido (origem qpu), executa o mesmo programa em
PennyLane local com o mesmo numero de tiros e compara a paridade. O recibo final
declara os dois lados e o desvio, sem esconder o erro do hardware.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pennylane as qml

AQUI = Path(__file__).resolve().parent
RECIBO_QPU = AQUI / "recibo_qpu_16pilares.json"
SAIDA = AQUI / "recibo_interop_pennylane.json"
SHOTS = 4096


def sha3(v) -> str:
    return hashlib.sha3_256(json.dumps(v, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def paridade(counts: dict) -> float:
    total = sum(counts.values())
    par = sum(v for k, v in counts.items() if k.count("1") % 2 == 0)
    return par / total


def rodar_pennylane(shots: int) -> dict:
    """Mesmo programa: H em q0, CNOT(q0,q1), medicao total."""
    dev = qml.device("default.qubit", wires=2, seed=20261114)

    @qml.set_shots(shots)
    @qml.qnode(dev)
    def circuito():
        qml.Hadamard(wires=0)
        qml.CNOT(wires=[0, 1])
        return qml.counts()

    counts = circuito()
    return {k.replace(" ", ""): int(v) for k, v in counts.items()}


def main() -> int:
    if not RECIBO_QPU.exists():
        print("sem recibo de QPU para comparar; rode experiments/qpu_16pilares.py primeiro")
        return 2
    qpu = json.loads(RECIBO_QPU.read_text())
    if qpu.get("origem") != "qpu":
        print("o recibo existente nao e de hardware:", qpu.get("origem"))
        return 2

    counts_pl = rodar_pennylane(SHOTS)
    p_qpu = paridade(qpu["counts"])
    p_pl = paridade(counts_pl)
    desvio = abs(p_qpu - p_pl)
    margem = float(np.sqrt(np.log(2 / 0.05) / (2 * SHOTS))) * np.sqrt(2)

    recibo = {
        "programa": "Bell Phi+ (H q0, CX q0-q1, medicao total)",
        "shots": SHOTS,
        "pontas": {
            "qpu": {"backend": qpu["backend"], "counts": qpu["counts"], "paridade": round(p_qpu, 6),
                    "recibo_hash": qpu["recibo_hash"][:16]},
            "pennylane": {"device": "default.qubit", "counts": counts_pl, "paridade": round(p_pl, 6),
                          "versao": qml.__version__},
        },
        "desvio_paridade": round(desvio, 6),
        "margem_combinada": round(float(margem), 6),
        "dentro_da_margem": bool(desvio <= margem),
        "leitura": ("hardware e simulador concordam dentro da margem estatistica"
                    if desvio <= margem else
                    "desvio maior que a margem: ha erro de hardware a caracterizar"),
    }
    recibo["recibo_hash"] = sha3(recibo)
    SAIDA.write_text(json.dumps(recibo, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f'qpu={p_qpu:.4f} pennylane={p_pl:.4f} desvio={desvio:.4f} margem={margem:.4f} '
          f'concorda={recibo["dentro_da_margem"]}')
    print("recibo:", recibo["recibo_hash"][:16])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

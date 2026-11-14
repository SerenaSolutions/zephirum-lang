#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""ZYQL + Qiskit: da pergunta ao recibo, num comando.

O que este script demonstra, sem retórica:
  1. um circuito é construído e transpilado pelo Qiskit;
  2. é executado e devolve contagens;
  3. as contagens viram pergunta para a camada de decisão ZYQL;
  4. o veredito sai com incerteza declarada e recibo selado por SHA3-256.

A pergunta aqui é honesta e pequena: o estado GHZ preparado tem fidelidade acima
de 0,80? Roda duas vezes: no simulador ideal e num modelo de ruído declarado. No
ideal a resposta é trivial (tudo cai em 000 ou 111) e isso não prova nada. O que
importa é o segundo caso: com ruído, a fração cai e a camada de decisão tem de
escolher entre dizer 0 e dizer que os tiros não bastaram.

Três cenários declarados antes de rodar: ideal (controle positivo), ruído de 2% em
cada CX, e controle negativo com o terceiro entrelaçamento removido de propósito.
Se a camada disser 1 no controle negativo, ela está quebrada.

Nenhuma alegação de vantagem quântica. Simulador, um seed, um circuito.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import pathlib
import sys
import tempfile

RAIZ = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from qiskit import QuantumCircuit, transpile          # noqa: E402
from qiskit_aer import AerSimulator                   # noqa: E402
from qiskit_aer.noise import NoiseModel, depolarizing_error  # noqa: E402

import zyclotron_service                              # noqa: E402

SHOTS = 2048
SEED = 1701
LIMIAR = 0.80
DELTA = 0.05


def canon(v) -> str:
    return json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def camada_de_decisao():
    """Carrega o app emitido: a decisão medida é a que vai ao usuário."""
    bp = {"name": "auditor-trivalente", "purpose": "decidir com recibo",
          "evidence": ["contagens"], "constraints": ["local"], "capabilities": ["decidir"]}
    codigo, res = zyclotron_service.emit_service(bp)
    assert res.decision == "1"
    destino = pathlib.Path(tempfile.mkdtemp()) / "app_emitido.py"
    destino.write_text(codigo, encoding="utf-8")
    spec = importlib.util.spec_from_file_location("app_emitido", destino)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def executar(cenario: str):
    """Devolve (circuito transpilado, backend, contagens) para um cenário."""
    qc = QuantumCircuit(3, 3)
    qc.h(0); qc.cx(0, 1)
    if cenario != "negativo":
        qc.cx(1, 2)  # no controle negativo o terceiro entrelaçamento falta de proposito
    qc.measure([0, 1, 2], [0, 1, 2])

    if cenario == "ideal" or cenario == "negativo":
        backend = AerSimulator()
    else:
        # ruído declarado: 2% de despolarização em cada porta de 2 qubits
        modelo = NoiseModel()
        modelo.add_all_qubit_quantum_error(depolarizing_error(0.02, 2), ["cx"])
        backend = AerSimulator(noise_model=modelo)

    tqc = transpile(qc, backend=backend, seed_transpiler=SEED)
    resultado = backend.run(tqc, shots=SHOTS, seed_simulator=SEED).result()
    return tqc, backend, resultado.get_counts()


def main() -> int:
    mod = camada_de_decisao()
    linhas, recibos = [], []
    for rotulo, cenario in (("ideal", "ideal"), ("ruido 2%", "ruido"), ("controle -", "negativo")):
        tqc, backend, counts = executar(cenario)
        validos = counts.get("000", 0) + counts.get("111", 0)
        payload = {"counts": {"ghz": validos}, "shots": SHOTS, "delta": DELTA,
                   "threshold": LIMIAR, "key": "ghz"}
        decisao, veredito = mod.decidir(payload)
        recibo = {
            "circuito": "ghz-3 (sem o 3o entrelacamento no controle negativo)",
            "cenario": rotulo, "backend": backend.name,
            "shots": SHOTS, "seed": SEED, "qubits": tqc.num_qubits,
            "profundidade_transpilada": tqc.depth(),
            "contagens": dict(sorted(counts.items())),
            "fracao_ghz": round(validos / SHOTS, 6),
            "pergunta": f"fracao_ghz > {LIMIAR}?",
            "veredito": veredito, "epsilon": decisao.get("epsilon"),
            "recibo_decisao": decisao.get("receipt_hash"),
            "regra": "proporcao-v1 (Hoeffding)",
        }
        recibo["receipt_hash"] = hashlib.sha3_256(canon(recibo).encode()).hexdigest()
        recibos.append(recibo)
        linhas.append((rotulo, recibo["profundidade_transpilada"], recibo["fracao_ghz"],
                       veredito, recibo["epsilon"], recibo["receipt_hash"]))

    print(f"{'cenário':11s} {'prof':>5s} {'fração GHZ':>11s} {'veredito':>9s} {'ε':>8s}  recibo SHA3-256")
    for c, prof, frac, v, eps, h in linhas:
        print(f"{c:11s} {prof:5d} {frac:11.4f} {v:>9s} {eps:8.5f}  {h[:24]}…")
    print()
    saida = {"receipts": recibos}
    (RAIZ / "demo/ultima_execucao.json").write_text(
        json.dumps(saida, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(saida, indent=2, ensure_ascii=False, sort_keys=True))
    return 0


def _antigo_main() -> int:  # noqa: D401 - mantido apenas como referencia historica
    qc = QuantumCircuit(3, 3)
    qc.h(0); qc.cx(0, 1); qc.cx(1, 2)
    qc.measure([0, 1, 2], [0, 1, 2])
    backend = AerSimulator()
    tqc = transpile(qc, backend=backend, seed_transpiler=SEED)
    resultado = backend.run(tqc, shots=SHOTS, seed_simulator=SEED).result()
    counts = resultado.get_counts()

    # 3. a pergunta para a linguagem: quantos tiros caíram nos estados válidos do GHZ
    validos = counts.get("000", 0) + counts.get("111", 0)
    payload = {"counts": {"ghz": validos}, "shots": SHOTS, "delta": DELTA,
               "threshold": LIMIAR, "key": "ghz"}
    decisao, veredito = camada_de_decisao().decidir(payload)

    # 4. recibo: o que rodou, com que parâmetros, e o que foi decidido
    recibo = {
        "circuito": "ghz-3", "backend": backend.name, "shots": SHOTS,
        "seed_transpilador": SEED, "seed_simulador": SEED,
        "qubits": tqc.num_qubits, "profundidade_transpilada": tqc.depth(),
        "contagens": dict(sorted(counts.items())),
        "fracao_ghz": round(validos / SHOTS, 6),
        "pergunta": f"fracao_ghz > {LIMIAR}?",
        "veredito": veredito, "epsilon": decisao.get("epsilon"),
        "recibo_decisao": decisao.get("receipt_hash"),
        "regra": "proporcao-v1 (Hoeffding)",
    }
    recibo["receipt_hash"] = hashlib.sha3_256(canon(recibo).encode()).hexdigest()

    print(f"circuito      : {recibo['circuito']} | {recibo['qubits']} qubits | profundidade {recibo['profundidade_transpilada']}")
    print(f"execução      : {recibo['backend']} | {SHOTS} tiros | seed {SEED}")
    print(f"contagens     : {recibo['contagens']}")
    print(f"fração GHZ    : {validos}/{SHOTS} = {recibo['fracao_ghz']}")
    print(f"pergunta      : {recibo['pergunta']}")
    print(f"veredito      : {veredito} (ε = {recibo['epsilon']})")
    print(f"recibo SHA3   : {recibo['receipt_hash']}")
    print()
    print(json.dumps(recibo, indent=2, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

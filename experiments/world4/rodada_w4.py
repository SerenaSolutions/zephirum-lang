# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Serena Quantum Solutions
"""WORLD-4: proximo estagio da rodada mundial.

Declarado ANTES da execucao (selo SHA3 do protocolo gravado antes de qualquer submissao):
  - W-03a: Grover |101> k=2, transpilacao optimization_level=1 (controle, igual ao WORLD-3)
  - W-03b: mesmo circuito, escolha do melhor transpile por (portas 2q, profundidade) entre seeds
  - SPAM por qubit: idle + X em cada qubit (4 circuitos), erro de leitura por qubit
  - 3 repeticoes independentes, 8192 shots, um job por repeticao
Bandas: W-03 p >= 0.85 certifica, < 0.70 rejeita, entre isso REFUSED.
        TVD <= 0.15 certifica, > 0.30 rejeita.
        SPAM: todas as taxas <= 0.05 certifica, qualquer > 0.10 rejeita.
"""
import hashlib, json, os, sys, time
from pathlib import Path

AQUI = Path(__file__).parent
sys.path.insert(0, str(AQUI.parent.parent / "src"))

from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister, transpile
from qiskit_aer import AerSimulator
from zyql_worldscale import grover, _ideal, _tvd
from qroute import hardware as hw

PROTO = {
    "id": "WORLD-4", "data": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "reps": 3, "shots": 8192,
    "circuitos": ["W-03a_level1", "W-03b_otimizado", "SPAM_idle", "SPAM_x0", "SPAM_x1", "SPAM_x2"],
    "bandas": {"W-03_p": [0.85, 0.70], "W-03_tvd": [0.15, 0.30], "SPAM": [0.05, 0.10]},
    "agregacao": "1 se as 3 reps certificam; 0 se todas reprovam; senao REFUSED",
    "analise_de_poder": {"banda": 0.85, "n": 8192, "erro_tipo_I_em_0.845": 0.0012,
                          "ponto_cego": "entre 0.83 e 0.85 o poder e ~0: dispositivo quase bom nunca certifica"},
    "nao_cobre": "ablacao de W-01 e SPAM resolvido por qubit-pais; ficam para WORLD-5",
}
sha_proto = hashlib.sha3_256(json.dumps(PROTO, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
PROTO["sha3_protocolo"] = sha_proto
(AQUI / "protocolo_w4.json").write_text(json.dumps(PROTO, indent=1, ensure_ascii=False))
print("protocolo selado ANTES da execucao:", sha_proto[:32])


def circuitos_spam():
    c = {}
    idle = QuantumCircuit(QuantumRegister(3, "q"), ClassicalRegister(3, "c"))
    idle.measure([0, 1, 2], [0, 1, 2])
    c["SPAM_idle"] = idle
    for q in range(3):
        qc = QuantumCircuit(QuantumRegister(3, "q"), ClassicalRegister(3, "c"))
        qc.x(q); qc.measure([0, 1, 2], [0, 1, 2])
        c[f"SPAM_x{q}"] = qc
    return c


def melhor_transpile(qc, backend, seeds=(0, 1, 2, 3, 4, 5)):
    melhor, metr = None, None
    for s in seeds:
        t = transpile(qc, backend=backend, optimization_level=3, seed_transpiler=s)
        m = (sum(1 for i in t.data if len(i.qubits) == 2), t.depth())
        if metr is None or m < metr:
            melhor, metr = t, m
    return melhor, metr


def main():
    tok, nome_tok = hw._token()
    if not tok:
        print("sem chave IBM valida"); return
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
    svc = QiskitRuntimeService(channel="ibm_quantum_platform", token=tok)
    b = svc.least_busy(operational=True, simulator=False)
    print(f"backend: {b.name} | chave: {nome_tok}")

    base = grover("101", iters=2)
    spams = circuitos_spam()
    t1 = transpile(base, backend=b, optimization_level=1, seed_transpiler=7)
    t3, metr3 = melhor_transpile(base, backend=b)
    print(f"W-03 level1: {sum(1 for i in t1.data if len(i.qubits)==2)} portas 2q, prof {t1.depth()}")
    print(f"W-03 otimiz.: {metr3[0]} portas 2q, prof {metr3[1]}")

    ideal = _ideal(base, shots=20000)
    reps, jobs = [], []
    for rep in range(1, PROTO["reps"] + 1):
        lote = {"W-03a_level1": t1, "W-03b_otimizado": t3}
        lote.update({k: transpile(v, backend=b, optimization_level=1) for k, v in spams.items()})
        nome_ordem = list(lote)
        job = Sampler(mode=b).run([lote[k] for k in nome_ordem], shots=PROTO["shots"])
        res = job.result()
        cts = {k: res[i].data.c.get_counts() for i, k in enumerate(nome_ordem)}
        n = sum(cts["W-03a_level1"].values())
        p1 = cts["W-03a_level1"].get("101", 0) / n
        p3 = cts["W-03b_otimizado"].get("101", 0) / sum(cts["W-03b_otimizado"].values())
        tvd = _tvd(ideal, cts["W-03b_otimizado"], 3)
        spam = {}
        idle = cts["SPAM_idle"]; ni = sum(idle.values())
        for q in range(3):
            e0 = sum(v for k, v in idle.items() if k.replace(" ", "")[2 - q] == "1") / ni
            cx = cts[f"SPAM_x{q}"]; nx = sum(cx.values())
            e1 = sum(v for k, v in cx.items() if k.replace(" ", "")[2 - q] == "0") / nx
            spam[f"q{q}"] = round((e0 + e1) / 2, 4)
        reps.append({"rep": rep, "job_id": job.job_id(),
                     "p_level1": round(p1, 4), "p_otimizado": round(p3, 4),
                     "tvd": round(tvd, 4), "spam_por_qubit": spam,
                     "distribuicao": {k: round(v / sum(cts['W-03b_otimizado'].values()), 4)
                                      for k, v in sorted(cts["W-03b_otimizado"].items())}})
        jobs.append(job.job_id())
        print(f"rep{rep} job={job.job_id()} p_l1={p1:.4f} p_opt={p3:.4f} tvd={tvd:.4f} spam={spam}")

    def ver(p, banda):
        return "1" if p >= banda[0] else ("0" if p < banda[1] else "REFUSED")
    vs_opt = [ver(r["p_otimizado"], PROTO["bandas"]["W-03_p"]) for r in reps]
    vs_l1 = [ver(r["p_level1"], PROTO["bandas"]["W-03_p"]) for r in reps]
    vs_tvd = [ver(max(r["tvd"], 0) * -1 + 1, (1 - PROTO["bandas"]["W-03_tvd"][1], 1 - PROTO["bandas"]["W-03_tvd"][0])) for r in reps]
    vs_tvd = ["1" if r["tvd"] <= 0.15 else ("0" if r["tvd"] > 0.30 else "REFUSED") for r in reps]
    spam_max = max(max(r["spam_por_qubit"].values()) for r in reps)
    vs_spam = "1" if spam_max <= 0.05 else ("0" if spam_max > 0.10 else "REFUSED")

    def agrega(v):
        return "1" if all(x == "1" for x in v) else ("0" if all(x == "0" for x in v) else "REFUSED")

    final = {"protocolo": PROTO, "execucao": {"dispositivo": b.name, "chave": nome_tok,
             "depth_level1": t1.depth(), "depth_otimizado": metr3[1],
             "portas2q_level1": sum(1 for i in t1.data if len(i.qubits) == 2),
             "portas2q_otimizado": metr3[0], "reps": reps, "jobs": jobs},
             "vereditos": {"W-03_otimizado": agrega(vs_opt), "W-03_level1": agrega(vs_l1),
                           "W-03_tvd": agrega(vs_tvd), "SPAM": vs_spam},
             "p_medio_otimizado": round(sum(r["p_otimizado"] for r in reps) / len(reps), 4),
             "p_medio_level1": round(sum(r["p_level1"] for r in reps) / len(reps), 4),
             "ideal": round(1 - 2 * 0 + sum(v for k, v in ideal.items() if k == "101"), 4)}
    final["sha3_resultado"] = hashlib.sha3_256(
        json.dumps(final, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    (AQUI / "w4_final.json").write_text(json.dumps(final, indent=1, ensure_ascii=False))
    print("\nVEREDITOS:", final["vereditos"])
    print("p medio: otimizado", final["p_medio_otimizado"], "| level1", final["p_medio_level1"],
          "| ideal", final["ideal"])
    print("selo do resultado:", final["sha3_resultado"][:32])


if __name__ == "__main__":
    main()

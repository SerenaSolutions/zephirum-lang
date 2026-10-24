# -*- coding: utf-8 -*-
"""
RODADA F — AS FRONTEIRAS (o teste dificil que faltava, ordem do dono)
Tres certificados que nenhum prototipo de brinquedo passa:
  (1) CHSH / desigualdade de BELL (2048 shots): o dispositivo prova
      NAO-LOCALIDADE (S > 2). Porta mais profunda que GHZ: nao basta ser
      coerente, tem que violar o limite classico. S >= 2.20 -> 1;
      2.0 < S < 2.20 -> REFUSED; S <= 2.0 -> 0 (dispositivo classico).
  (2) QEC — CODIGO DE REPETICAO bit-flip (2048 shots): 1 qubit logico em
      3 fisicos + 2 de sindrome, decodificacao por maioria. VEREDITO:
      erro logico < erro fisico -> PROTEGIDO (1); senao REFUSED. Ataca a
      limitacao declarada no MATURITY.md ("sem correcao de erro").
  (3) GROVER n=4 (2048 shots): 16 estados, 3 iteracoes, alvo 1101 —
      o dobro da escala da Rodada E. p >= 0.50 e >= 2x segundo -> 1;
      p <= 0.20 -> 0; senao REFUSED.
Backend: ibm_kingston. 3 jobs, 10.752 shots totais. CARGA PESADA.
"""
import os, json
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2

BACKEND = "ibm_kingston"
SHOTS = 2048
ALVO_GROVER = "1101"   # q3q2q1q0; counts do Qiskit: inverter

def chsh_circuit(a, b):
    qc = QuantumCircuit(2, 2)
    qc.h(0); qc.cx(0, 1)
    qc.ry(2 * a, 0); qc.ry(2 * b, 1)
    qc.measure([0, 1], [0, 1])
    return qc

def qec_encoded():
    # |+> codificado em 3 qubits (repeticao), sindrome extraida, decode X
    qc = QuantumCircuit(5, 5)
    qc.h(0)                      # estado |+>
    qc.cx(0, 1); qc.cx(0, 2)     # encode: |+++>
    qc.cx(0, 3); qc.cx(1, 3)     # s0 = q0 XOR q1
    qc.cx(1, 4); qc.cx(2, 4)     # s1 = q1 XOR q2
    qc.h(0); qc.h(1); qc.h(2)    # base X para leitura logica
    qc.measure([0, 1, 2, 3, 4], [0, 1, 2, 3, 4])
    return qc

def qec_control():
    # baseline fisico: |+> SEM codigo, mesma leitura
    qc = QuantumCircuit(5, 5)
    qc.h(0)
    qc.h(0)  # h de novo = leitura em X de |+> (esperado '1')
    qc.measure([0], [0])
    return qc

def grover4():
    import math
    qc = QuantumCircuit(4, 4)
    qc.h(range(4))
    zeros = [i for i in range(4) if ALVO_GROVER[i] == "0"]
    for _ in range(3):
        # oraculo de fase no alvo
        for i in zeros: qc.x(i)
        qc.h(3); qc.mcx([0, 1, 2], 3); qc.h(3)
        for i in zeros: qc.x(i)
        # difusor
        qc.h(range(4)); qc.x(range(4))
        qc.h(3); qc.mcx([0, 1, 2], 3); qc.h(3)
        qc.x(range(4)); qc.h(range(4))
    qc.measure(range(4), range(4))
    return qc

def main():
    token = os.environ["IBM_QUANTUM_TOKEN"]
    service = QiskitRuntimeService(token=token, channel="ibm_quantum_platform", instance="auto")
    backend = service.backend(BACKEND)
    sampler = SamplerV2(mode=backend)
    jobs = {}
    import math
    circs = [transpile(chsh_circuit(a, b), backend=backend, optimization_level=2)
             for a, b in ((0, math.pi/4), (0, 3*math.pi/4),
                          (math.pi/2, math.pi/4), (math.pi/2, 3*math.pi/4))]
    j = sampler.run(circs, shots=SHOTS)
    jobs["chsh"] = j.job_id(); print("CHSH (4 circuitos):", j.job_id())

    circs = [transpile(qec_control(), backend=backend, optimization_level=2),
             transpile(qec_encoded(), backend=backend, optimization_level=2)]
    j = sampler.run(circs, shots=SHOTS)
    jobs["qec"] = j.job_id(); print("QEC repeticao (controle+codificado):", j.job_id())

    j = sampler.run([transpile(grover4(), backend=backend, optimization_level=2)], shots=SHOTS)
    jobs["grover4"] = j.job_id(); print("Grover n=4 alvo 1101:", j.job_id())

    out = {"rodada": "F", "protocolo": "fronteiras: CHSH nao-localidade + QEC repeticao + Grover n=4",
           "backend": BACKEND, "shots": SHOTS, "alvo_grover": ALVO_GROVER,
           "bandas": {"chsh": "S>=2.20 -> 1; 2.0<S<2.20 -> REFUSED; S<=2.0 -> 0",
                      "qec": "erro_logico < erro_fisico -> 1 (PROTEGIDO); senao REFUSED",
                      "grover": "p>=0.50 e >=2x segundo -> 1; p<=0.20 -> 0; senao REFUSED"},
           "jobs": jobs}
    with open("/tmp/round_f_jobs.json", "w") as f:
        json.dump(out, f, indent=1)
    print("jobs submetidos. Analise com experiments/round_f_analyze.py quando DONE.")

if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""
RODADA F-REV — re-teste das duas fronteiras invalidadas por bug de design
na Rodada F. Licoes aplicadas: (1) VERIFICAR A TEORIA COM STATEVECTOR ANTES
DE SUBMETER (o bug da Rodada F era ry(2a) dobrando o angulo — E teorico=0);
(2) codigo de repeticao tem que codificar na MESMA base do estado.

(1) CHSH corrigido: rotacoes ry(theta) DIRETAS nos ajustes
    (0, pi/4), (0, -pi/4), (pi/2, pi/4), (pi/2, -pi/4);
    S = E1 + E2 + E3 - E4; teoria S = 2*sqrt(2) = 2.828 (Tsirelson).
    Bandas: S>=2.20 -> 1; 2.0<S<2.20 -> REFUSED; S<=2.0 -> 0.
(2) QEC corrigido: |0> codificado em |000> (CX na base Z), INJECAO
    DETERMINISTICA de X no qubit do meio, decodificacao por maioria.
    Controles: (a) |0> + mesmo X sem codigo -> erro fisico ~100%;
    (b) |000> codificado sem injecao -> ruido de base do codigo.
    Veredito: erro_logico(injetado) << erro_fisico -> 1 (PROTEGIDO).

Backend: ibm_kingston. 2048 shots por pub.
"""
import os, json, math
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Statevector, SparsePauliOp
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2

BACKEND = "ibm_kingston"
SHOTS = 2048
AJUSTES = [(0.0, math.pi/4), (0.0, -math.pi/4), (math.pi/2, math.pi/4), (math.pi/2, -math.pi/4)]

def chsh_circuit(ta, tb):
    qc = QuantumCircuit(2, 2)
    qc.h(0); qc.cx(0, 1)
    qc.ry(ta, 0); qc.ry(tb, 1)
    qc.measure([0, 1], [0, 1])
    return qc

def qec_encoded(injeta_erro):
    qc = QuantumCircuit(3, 3)
    qc.cx(0, 1); qc.cx(0, 2)      # |0> -> |000>
    if injeta_erro: qc.x(1)        # erro bit-flip deterministico no meio
    qc.measure(range(3), range(3))
    return qc

def qec_control():                  # |0> + mesmo X, SEM codigo
    qc = QuantumCircuit(1, 1)
    qc.x(0)
    qc.measure(0, 0)
    return qc

def teoria_chsh():
    """Auditoria pre-submissao: E teorico de cada ajuste e S esperado."""
    es = []
    for ta, tb in AJUSTES:
        qc = chsh_circuit(ta, tb); qc.remove_final_measurements(inplace=True)
        e = Statevector(qc).expectation_value(SparsePauliOp("ZZ")).real
        es.append(e)
    S = es[0] + es[1] + es[2] - es[3]
    return es, S

def main():
    es, S = teoria_chsh()
    print("TEORIA CHSH:", [f"{e:+.4f}" for e in es], "S =", round(S, 4))
    assert S > 2.7, "TEORIA INVALIDA — NAO SUBMETER (licao da Rodada F)"
    teo_qec = Statevector.from_label("0").expectation_value(SparsePauliOp("Z")).real
    print("TEORIA QEC: |0> codificado, maioria corrige X no meio; controle mede |1> (erro fisico ~1)")

    token = os.environ["IBM_QUANTUM_TOKEN"]
    service = QiskitRuntimeService(token=token, channel="ibm_quantum_platform", instance="auto")
    backend = service.backend(BACKEND)
    sampler = SamplerV2(mode=backend)
    jobs = {}

    circs = [transpile(chsh_circuit(ta, tb), backend=backend, optimization_level=2) for ta, tb in AJUSTES]
    j = sampler.run(circs, shots=SHOTS)
    jobs["chsh"] = j.job_id(); print("CHSH corrigido (4 circuitos):", j.job_id())

    circs = [transpile(qec_control(), backend=backend, optimization_level=2),
             transpile(qec_encoded(injeta_erro=True), backend=backend, optimization_level=2),
             transpile(qec_encoded(injeta_erro=False), backend=backend, optimization_level=2)]
    j = sampler.run(circs, shots=SHOTS)
    jobs["qec"] = j.job_id(); print("QEC corrigido (controle + injetado + limpo):", j.job_id())

    out = {"rodada": "F-rev", "protocolo": "re-teste das fronteiras invalidadas: CHSH angulos corretos + QEC base Z com injecao de erro",
           "backend": BACKEND, "shots": SHOTS, "ajustes_chsh": AJUSTES,
           "teoria": {"E": [round(e, 4) for e in es], "S_esperado": round(S, 4)},
           "bandas": {"chsh": "S>=2.20 -> 1; 2.0<S<2.20 -> REFUSED; S<=2.0 -> 0",
                      "qec": "erro_logico(injetado) < erro_fisico/2 -> 1 (PROTEGIDO); erro_logico>=erro_fisico -> 0; senao REFUSED"},
           "jobs": jobs}
    with open("/tmp/round_frev_jobs.json", "w") as f:
        json.dump(out, f, indent=1)
    print("jobs submetidos.")

if __name__ == "__main__":
    main()

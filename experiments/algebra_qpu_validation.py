# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Serena Quantum Solutions
"""Validacao em QPU do orcamento de erro familiar da algebra trivalente.

Hipotese (pre-registrada em docs/PRE_REGISTRO_ALGEBRA_QPU.json):
  A algebra RECUSA por poder insuficiente exatamente quando a margem rigorosa
  fica <= 0, e essa fronteira e aritmetica, nao empirica.
  Para eps=0.01 e k=7: recusa se e so se shots <= 14.
  Para eps=0.05 e k=1: nunca recusa com shots >= 15.

Na QPU medimos decisoes reais e verificamos que:
  (a) a decisao unica com shots=2000 nao e recusada por poder;
  (b) a mesma decisao avaliada como programa de 7 testes com eps=0.01 e
      shots=10 e RECUSADA com FAMILY_EXCEEDS_SHOTS, sem aprovar.
"""
import json, os, sys

from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, Sampler

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from zyql_algebra import Decisao, n_testes, recibo_da_expressao, sequencia, RECUSA
from zyql_quantum_gate import adaptive_margin_family

EPS, S_ALTA, S_BAIXA = 0.05, 2000, 10


def veredito_de_p0(p0, shots, eps=EPS):
    """Decisao 'estado preparado e |0>' com banda derivada, sem otimismo."""
    m = adaptive_margin_family(eps, shots, family=1, modo="rigorous")
    if p0 - 0.5 > m:
        return Decisao(1, eps, shots)
    if 0.5 - p0 > m:
        return Decisao(0, eps, shots)
    return Decisao(RECUSA, eps, shots, refusal_reason="P0_DENTRO_DA_BANDA")


def main():
    servico = QiskitRuntimeService(channel="ibm_quantum_platform",
                                   token=os.environ["IBM_QUANTUM_TOKEN_3"])
    backend = servico.least_busy(operational=True, simulator=False)
    qc = QuantumCircuit(1, 1)
    qc.measure(0, 0)
    tc = transpile(qc, backend, optimization_level=1)
    job = Sampler(mode=backend).run([tc], shots=S_ALTA)
    print("JOB_ID=%s BACKEND=%s" % (job.job_id(), backend.name))
    res = job.result()[0].data.c.get_counts()
    total = sum(res.values())
    p0 = res.get("0", 0) / total
    print("p0=%.4f (%d shots)" % (p0, total))

    d1 = veredito_de_p0(p0, total)
    print("decisao unica: veredito=%r k=%d recusa=%r" % (d1.veredito, n_testes(d1), d1.refusal_reason))

    programa = sequencia(*[Decisao(d1.veredito, 0.01, S_BAIXA) if d1.veredito != RECUSA
                           else Decisao(RECUSA, 0.01, S_BAIXA, refusal_reason=d1.refusal_reason)
                           for _ in range(7)])
    r = recibo_da_expressao(programa)
    print("programa de 7: n_testes=%d veredito=%r motivo=%r" % (r["n_testes"], r["veredito"], r["refusal_reason"]))

    saida = {"job_id": job.job_id(), "backend": backend.name, "p0": round(p0, 6),
             "shots": total, "decisao_unica": r["forma"], "veredito_unico": d1.veredito,
             "programa_7": {"n_testes": r["n_testes"], "veredito": r["veredito"],
                            "refusal_reason": r["refusal_reason"],
                            "selo_sha3_256": r["selo_sha3_256"]}}
    json.dump(saida, open("experiments/algebra_qpu_result.json", "w"), indent=1)
    print("RECIBO_PRONTO")


if __name__ == "__main__":
    main()

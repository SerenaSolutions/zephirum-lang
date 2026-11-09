# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Serena Quantum Solutions
"""06 Arquiteto: roteador de execucao classico, ML ou quantico (Qiskit)."""
from qiskit import QuantumCircuit, transpile

def custo_quantico(n_qubits, profundidade_relativa=3):
    """Proxy de custo: profundidade transpilada da rotina de estimativa."""
    qc = QuantumCircuit(n_qubits)
    qc.h(range(n_qubits))
    for _ in range(profundidade_relativa):
        for q in range(n_qubits - 1):
            qc.cx(q, q + 1)
        qc.h(range(n_qubits))
    return transpile(qc, basis_gates=["u", "cx"], optimization_level=1).depth()

def run(n_qubits, tem_solucao_classica, problema_estrutural, orcamento=40):
    custo_q = custo_quantico(n_qubits) if 1 <= n_qubits <= 20 else None
    if tem_solucao_classica:
        rota, motivo = "CLASSICO", "SOLUCAO_CLASSICA_CONHECIDA"
    elif not problema_estrutural:
        rota, motivo = "CLASSICO", "ESTRUTURA_NAO_EXPLORAVEL"
    elif custo_q is None:
        rota, motivo = "REFUSED", "TAMANHO_FORA_DE_AVALIACAO"
    elif custo_q > orcamento:
        rota, motivo = "REFUSED", "ORCAMENTO_DE_PROFUNDIDADE"
    else:
        rota, motivo = "QUANTICO", None
    return {"solucao": "06 compute router", "rota": rota, "motivo": motivo,
            "custo_quantico": custo_q, "qubits": n_qubits,
            "orcamento": orcamento}

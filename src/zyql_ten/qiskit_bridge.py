# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Serena Quantum Solutions
"""Ponte entre a camada ZYQL e as chamadas nativas do Qiskit.

Mesma funcao em duas representacoes: callable puro para o nucleo ZYQL e
circuito nativo para execucao e transpilacao. O cruzamento entre as duas e
verificado em cross_check, para que divergencia apareca como falha de teste.
"""
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Statevector


def dj_function(n, tipo="constante", valor=0):
    """Funcao f(x) -> {0,1} na forma que o runtime ZYQL consome."""
    if tipo == "constante":
        return lambda x: valor & 1
    if tipo == "balanceado":
        return lambda x: bin(x).count("1") & 1
    raise ValueError(f"tipo desconhecido: {tipo}")


def dj_circuit(n, tipo="constante", valor=0):
    """Circuito Deutsch-Jozsa nativo do Qiskit (n qubits de dados + 1 ancilla)."""
    qc = QuantumCircuit(n + 1, name=f"dj_{tipo}")
    qc.x(n)
    for i in range(n + 1):
        qc.h(i)
    if tipo == "balanceado":
        for i in range(n):
            qc.cx(i, n)
    elif tipo == "constante":
        if valor & 1:
            qc.x(n)
    else:
        raise ValueError(f"tipo desconhecido: {tipo}")
    for i in range(n):
        qc.h(i)
    return qc


def p0_from_circuit(n, tipo="constante", valor=0):
    """Probabilidade de |0...0> nos qubits de dados, via Statevector do Qiskit."""
    qc = dj_circuit(n, tipo, valor)
    return float(Statevector.from_instruction(qc).probabilities(list(range(n)))[0])


def transpiled_cost(qc, budget=40):
    """As tres metricas de sistema: qubits programaveis, profundidade e throughput.

    O throughput aqui e local (circuitos por segundo do transpilador). Em QPU o
    campo passa a declarar a medicao do backend, nunca um valor estimado.
    """
    import time
    t0 = time.perf_counter()
    t = transpile(qc, basis_gates=["u", "cx"], optimization_level=1)
    dt = max(time.perf_counter() - t0, 1e-9)
    depth = t.depth()
    return {"qubits": qc.num_qubits, "profundidade": depth,
            "throughput_circuitos_s": round(1 / dt, 1),
            "throughput_origem": "transpilador_local",
            "orcamento": budget, "cabe": depth <= budget}


def cross_check(n, tipo="constante", valor=0):
    """Confere se callable e circuito concordam sobre a constancia da funcao."""
    f = dj_function(n, tipo, valor)
    valores = {f(x) for x in range(1 << n)}
    por_callable = "constante" if len(valores) == 1 else "balanceado"
    p0 = p0_from_circuit(n, tipo, valor)
    por_circuito = "constante" if p0 > 0.5 else "balanceado"
    return {"callable": por_callable, "circuito": por_circuito, "p0": p0,
            "concordam": por_callable == por_circuito}

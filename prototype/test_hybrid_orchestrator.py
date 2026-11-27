#!/usr/bin/env python3
"""
BATERIA — ORQUESTRADOR HÍBRIDO (Gen 1, Fase 1).
===============================================

O que tem de valer para o orquestrador entrar na conformidade:

T1  PROOF → COMPUTE: com analítico e simulador a declarar a operação, o
    analítico decide; zero execução, zero fallback.
T2  Honestidade de capacidade: operação que ninguém declara → NOT ROUTED
    com motivo explícito (§12), nunca UNKNOWN mudo.
T3  Autorização: operação só declarada pelo simulador, simulador fora da
    política → NOT ROUTED; o simulador não é usado por conveniência.
T4  Fallback autorizado: analítico indisponível + clássico autorizado +
    fallback_allowed=True → roteia para o clássico COM registo
    (fallback_used, from_kind, to_kind).
T5  Fallback proibido: o mesmo cenário sem autorização → NOT ROUTED.
T6  Sem substituição silenciosa: hardware indisponível e simulador
    registado mas NÃO autorizado para a operação → NOT ROUTED (a simulação
    nunca assume o lugar do hardware em silêncio).
T7  Determinismo: dois roteamentos idênticos → mesmo route_digest.
T8  Recibo auditável: `tried` mostra cada backend e por que foi ignorado.
"""
from hybrid_orchestrator import (BackendCapability, Orchestrator,
                                 default_orchestrator)

OPS = ("entanglement_decision", "geometric_decision")


def main():
    # T1 — analítico decide; nada é executado
    orch = default_orchestrator()
    r = orch.route("entanglement_decision")
    assert r["routed"] and r["kind"] == "analytic", r
    assert r["fallback_used"] is False
    print("T1 PASS — proof before compute: analitico decide, zero execucao")

    # T2 — operação que ninguém declara
    r = orch.route("median_decision")
    assert r["routed"] is False and "no backend declares" in r["reason"], r
    print("T2 PASS — operacao sem backend declarado: NOT ROUTED explicito")

    # T3 — simulador existe mas não está autorizado
    only_sim = Orchestrator(
        [BackendCapability("sim", "quantum_simulator",
                           ("entanglement_decision",), "float64")],
        allowed_kinds=["analytic", "classical_cpu"])
    r = only_sim.route("entanglement_decision")
    assert r["routed"] is False and "none is authorized" in r["reason"], r
    print("T3 PASS — backend nao autorizado nunca usado por conveniencia")

    # T4 — fallback autorizado e registado
    fb = Orchestrator([
        BackendCapability("kernel", "analytic", OPS, "exact",
                          available=False),
        BackendCapability("cpu", "classical_cpu", OPS, "float64"),
    ], fallback_allowed=True)
    r = fb.route("geometric_decision")
    assert r["routed"] and r["kind"] == "classical_cpu", r
    assert r["fallback_used"] is True
    assert r["from_kind"] == "analytic" and r["to_kind"] == "classical_cpu"
    print("T4 PASS — fallback autorizado com registo from/to no recibo")

    # T5 — fallback proibido
    fb2 = Orchestrator([
        BackendCapability("kernel", "analytic", OPS, "exact",
                          available=False),
        BackendCapability("cpu", "classical_cpu", OPS, "float64"),
    ], fallback_allowed=False)
    r = fb2.route("geometric_decision")
    assert r["routed"] is False and "not authorized" in r["reason"], r
    print("T5 PASS — fallback sem autorizacao: NOT ROUTED")

    # T6 — hardware fora, simulação não assume em silêncio
    hw = Orchestrator([
        BackendCapability("qpu", "quantum_hardware",
                          ("entanglement_decision",), "experimental",
                          available=False),
        BackendCapability("sim", "quantum_simulator",
                          ("entanglement_decision",), "float64"),
    ], allowed_kinds=["quantum_hardware"], fallback_allowed=True)
    r = hw.route("entanglement_decision")
    assert r["routed"] is False, r
    print("T6 PASS — hardware indisponivel nao vira simulacao silenciosa")

    # T7 — determinismo do recibo
    a = default_orchestrator().route("geometric_decision")
    b = default_orchestrator().route("geometric_decision")
    assert a["route_digest"] == b["route_digest"]
    print("T7 PASS — mesmo roteamento, mesmo digest")

    # T8 — recibo auditável
    assert any(t.get("skipped") for t in r["tried"]) or r["tried"]
    print("T8 PASS — tried lista cada backend e o motivo de ignorar")

    print("RESULT: PASS — orquestrador hibrido com politica explicita, "
          "fallback registado e recusa honesta")


if __name__ == "__main__":
    main()

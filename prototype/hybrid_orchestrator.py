#!/usr/bin/env python3
"""
ORQUESTRADOR HÍBRIDO — ZEPHIRUM Scientific Kernel Gen 1, Fase 1.
================================================================

A peça que faltava entre o núcleo de decisão e os backends: escolher ONDE
uma operação é executada, com política explícita e recibo verificável.

Regras (todas testadas em test_hybrid_orchestrator.py):

1. PROOF → COMPUTE: o backend analítico tem prioridade absoluta. Se uma
   família pode ser decidida por forma fechada, nenhum backend de execução
   é considerado.
2. HONESTIDADE DE CAPACIDADE: um backend só recebe operações que DECLARA.
   Declarar "aceito a representação" não é declarar suporte.
3. FALLBACK EXPLÍCITO: trocar de estratégia só com fallback_allowed=True,
   e a troca fica registada no recibo (from/to/fallback_used).
4. SEM SUBSTITUIÇÃO SILENCIOSA: hardware indisponível nunca vira simulação
   (nem o contrário). Backend não autorizado nunca é usado por conveniência.
5. RECUSA EXPLÍCITA (§12): sem backend adequado, o resultado é NOT ROUTED
   com o motivo — nunca um UNKNOWN mudo.

O recibo de roteamento é determinístico: mesma entrada, mesmo digest.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from decision_kernel import digest

# prioridade: prova antes de executar; analítico > clássico > simulador > hardware
KIND_PRIORITY = ("analytic", "classical_cpu", "quantum_simulator",
                 "quantum_hardware")


class BackendCapability:
    """Contrato de capacidade: um backend declara o que REALMENTE faz."""

    def __init__(self, name, kind, operations, precision, version="",
                 limits=None, available=True):
        if kind not in KIND_PRIORITY:
            raise ValueError("unknown backend kind: %r" % kind)
        if not isinstance(available, bool):
            raise ValueError(
                "available must be a bool, not %r (no truthiness)"
                % (available,))
        self.name = name
        self.kind = kind
        self.operations = frozenset(operations)
        self.precision = precision          # "exact" | "float64" | ...
        self.version = version
        self.limits = dict(limits or {})
        self.available = available

    def supports(self, operation):
        return operation in self.operations

    def as_dict(self):
        return {"name": self.name, "kind": self.kind,
                "operations": sorted(self.operations),
                "precision": self.precision, "version": self.version,
                "limits": self.limits, "available": self.available}


class Orchestrator:
    """Seleção de backend com política declarada e recibo auditável."""

    def __init__(self, backends, allowed_kinds=None, fallback_allowed=False):
        self.backends = list(backends)
        if allowed_kinds is None:
            self.allowed_kinds = KIND_PRIORITY
        else:
            self.allowed_kinds = tuple(allowed_kinds)
            if not self.allowed_kinds:
                raise ValueError(
                    "empty policy authorizes nothing: fail-closed (par.12)")
        for k in self.allowed_kinds:
            if k not in KIND_PRIORITY:
                raise ValueError("unknown kind in policy: %r" % k)
        if not isinstance(fallback_allowed, bool):
            raise ValueError(
                "fallback_allowed must be a bool, not %r (no truthiness)"
                % (fallback_allowed,))
        self.fallback_allowed = fallback_allowed

    def _ordered(self, operation):
        """Backends que declaram a operação, por prioridade de kind."""
        return sorted((b for b in self.backends if b.supports(operation)),
                      key=lambda b: KIND_PRIORITY.index(b.kind))

    def route(self, operation):
        """Devolve o recibo de roteamento (dict) — nunca executa nada."""
        candidates = self._ordered(operation)
        tried = []
        receipt = {"operation": operation, "routed": False, "backend": None,
                   "kind": None, "reason": "", "fallback_used": False,
                   "from_kind": None, "to_kind": None, "tried": tried}

        if not candidates:
            receipt["reason"] = (
                "NOT ROUTED (par.12): no backend declares operation %r — "
                "declaring a representation is not declaring support"
                % operation)
            return self._seal(receipt)

        authorized = []
        for b in candidates:
            if b.kind not in self.allowed_kinds:
                tried.append({"backend": b.name, "kind": b.kind,
                              "skipped": "kind not authorized by policy"})
                continue
            if not b.available:
                tried.append({"backend": b.name, "kind": b.kind,
                              "skipped": "declared unavailable"})
                continue
            authorized.append(b)
            tried.append({"backend": b.name, "kind": b.kind,
                          "selected": False})

        if not authorized:
            receipt["reason"] = (
                "NOT ROUTED (par.12): operation %r has declared backends but "
                "none is authorized and available under the current policy — "
                "no silent substitution" % operation)
            return self._seal(receipt)

        chosen = authorized[0]
        # fallback = o backend de maior prioridade autorizado NÃO é o primeiro
        # candidato declarado (ex.: analítico indisponível, clássico assumiu)
        first_declared = candidates[0]
        fallback_used = (first_declared.kind != chosen.kind)
        # REGRA 4 (Red Team 2026-11-27): simulação NUNCA substitui hardware
        # em silêncio — nem o contrário. Se hardware declara a operação,
        # rotear para simulador é substituição e exige fallback autorizado.
        hw_declared = [b for b in candidates if b.kind == "quantum_hardware"]
        if chosen.kind == "quantum_simulator" and hw_declared:
            fallback_used = True
            first_declared = hw_declared[0]
        if fallback_used and not self.fallback_allowed:
            receipt["reason"] = (
                "NOT ROUTED (par.12): preferred backend %r (%s) is not "
                "available and fallback to %r (%s) is not authorized"
                % (first_declared.name, first_declared.kind, chosen.name,
                   chosen.kind))
            return self._seal(receipt)

        for t in tried:
            if t["backend"] == chosen.name:
                t["selected"] = True
        receipt.update({
            "routed": True,
            "backend": chosen.name,
            "kind": chosen.kind,
            "precision": chosen.precision,
            "fallback_used": fallback_used,
            "from_kind": first_declared.kind if fallback_used else None,
            "to_kind": chosen.kind if fallback_used else None,
            "reason": ("decided by %s backend (%s precision) — proof before "
                       "compute" % (chosen.kind, chosen.precision)),
        })
        return self._seal(receipt)

    @staticmethod
    def _seal(receipt):
        receipt["route_digest"] = digest(receipt)
        return receipt


def default_orchestrator(analytic=True, cpu=True, simulator=True,
                         hardware=None, fallback_allowed=False):
    """Orquestrador padrão do Gen 1: analítico + CPU + simulador."""
    ops = ("entanglement_decision", "threshold_sum_decision",
           "geometric_decision", "mean_decision", "determinant_decision")
    backends = []
    if analytic:
        backends.append(BackendCapability(
            "zephirum-kernel", "analytic", ops, "exact", version="0.3"))
    if cpu:
        backends.append(BackendCapability(
            "cpu-reference", "classical_cpu", ops, "float64",
            version="python3"))
    if simulator:
        backends.append(BackendCapability(
            "qsim-simulator", "quantum_simulator",
            ("entanglement_decision",), "float64", version="statevector-2q"))
    if hardware:
        backends.append(BackendCapability(
            "qpu-adapter", "quantum_hardware", ("entanglement_decision",),
            "experimental", version="unconfigured", available=False))
    allowed = ["analytic", "classical_cpu", "quantum_simulator"]
    if hardware:
        allowed.append("quantum_hardware")
    return Orchestrator(backends, allowed_kinds=allowed,
                        fallback_allowed=fallback_allowed)


if __name__ == "__main__":
    orch = default_orchestrator()
    for op in ("entanglement_decision", "median_decision"):
        r = orch.route(op)
        print(op, "->", r["kind"] if r["routed"] else "NOT ROUTED")
        print("   ", r["reason"])

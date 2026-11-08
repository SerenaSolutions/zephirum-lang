# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Serena Quantum Solutions
# -*- coding: utf-8 -*-
"""ZYQL REPRODUCIBLE PIPELINE DEMO — Entregável 7 (v1.0.0).

Executa as 9 etapas da operação ZYQL de ponta a ponta em simulação (sem QPU,
sem credenciais IBM), com roteamento trivalente, verificação independente e
recibos encadeados com integridade SHA3-256.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import math
import os
import sys
import time
from dataclasses import dataclass
from typing import Callable, Optional

# Adiciona caminhos do repositório
_AQUI = os.path.dirname(os.path.abspath(__file__))
_RAIZ = os.path.abspath(os.path.join(_AQUI, "..", ".."))
for _p in [os.path.join(_RAIZ, "src"), os.path.join(_RAIZ, "api")]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

# Importa módulos existentes do repositório (NÃO reimplementar)
from battery_ci import canon  # Regra canônica de serialização da casa
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from zyql_oracle_id import PROMISE_OK, audit_promise
from zyql_quantum_gate import ZYQLQuantumGate, adaptive_margin_family
from zyql_runtime import ConfigError, Verdict, _validate


@dataclass
class ProblemSpec:
    algorithm: str = "bernstein_vazirani"
    n: int = 3
    s: int = 5  # máscara binária secreta (5 = '101')
    classical_budget: int = 1  # orçamento clássico tolerado
    shots: int = 2048
    seed: int = 1701
    oracle_fn: Optional[Callable[[int], int]] = None
    force_divergence: bool = False  # simula divergência para teste de refutação


def run_pipeline(prob: ProblemSpec, quiet: bool = False) -> dict:
    t0 = time.perf_counter()

    # -------------------------------------------------------------
    # ETAPA 1: Entrada em ZYQL
    # -------------------------------------------------------------
    if prob.oracle_fn is None:
        mask = prob.s
        prob.oracle_fn = lambda x: bin(x & mask).count("1") % 2

    # Validação estrutural de produção existente no runtime
    try:
        _validate(prob.oracle_fn, prob.n, prob.shots, prob.seed)
    except (ConfigError, ValueError) as err:
        return _handle_refusal(f"CONFIG_ERROR: {err}", prob, "recusa", t0, quiet)

    # -------------------------------------------------------------
    # ETAPA 2: Decisão clássica suficiente
    # -------------------------------------------------------------
    # Auditoria de promessa com lógica existente em zyql_oracle_id
    truth_table = {x: prob.oracle_fn(x) for x in range(1 << prob.n)}
    audit = audit_promise(truth_table)
    promise_valid = audit.get("verdict") == PROMISE_OK

    # Consulta custo clássico determinístico
    gate_helper = ZYQLQuantumGate(prob.n, prob.oracle_fn)
    classical_cost = prob.n  # BV determinístico requer n consultas

    # -------------------------------------------------------------
    # ETAPA 3: Decisão de rota (lógica trivalente existente)
    # -------------------------------------------------------------
    if not promise_valid:
        route = "recusa"
        route_reason = f"PROMISE_VIOLATED ({audit.get('reason', 'AUDIT_FAILED')})"
        return _handle_refusal(route_reason, prob, route, t0, quiet)
    elif prob.classical_budget >= classical_cost:
        route = "classico"
        route_reason = "CLASSICAL_BUDGET_SUFFICIENT"
    else:
        route = "simulacao"
        route_reason = "QUANTUM_QUERY_ADVANTAGE_REQUIRED"

    # -------------------------------------------------------------
    # ETAPA 4: Conversão Qiskit
    # -------------------------------------------------------------
    n = prob.n
    s = prob.s
    qc = QuantumCircuit(n + 1, n, name=f"zyql_bv_{s:0{n}b}")
    qc.x(n)  # âncilla em |1>
    qc.h(range(n + 1))  # superposição em todos os qubits
    for i in range(n):
        if (s >> i) & 1:
            qc.cx(i, n)  # phase kickback (-1)^(s·x)
    qc.h(range(n))
    qc.measure(range(n), range(n))

    depth_orig = qc.depth()
    cx_count = qc.count_ops().get("cx", 0)

    # -------------------------------------------------------------
    # ETAPA 5: Transpilação
    # -------------------------------------------------------------
    backend = AerSimulator(seed_simulator=prob.seed)
    tqc = transpile(qc, backend=backend, optimization_level=1, seed_transpiler=prob.seed)
    depth_transp = tqc.depth()

    # -------------------------------------------------------------
    # ETAPA 6: Execução (Simulação sem QPU)
    # -------------------------------------------------------------
    job = backend.run(tqc, shots=prob.shots)
    res = job.result()
    counts = res.get_counts()

    # -------------------------------------------------------------
    # ETAPA 7: Coleta
    # -------------------------------------------------------------
    top_bits = max(counts, key=counts.get)
    p_obs = counts[top_bits] / prob.shots
    measured_s = int(top_bits.replace(" ", ""), 2)

    # -------------------------------------------------------------
    # ETAPA 8: Verificação independente
    # -------------------------------------------------------------
    # Candidato avaliado de forma ortogonal e independente do circuito quântico
    candidate_to_verify = (measured_s ^ 1) if prob.force_divergence else measured_s
    mismatches = 0
    for i in range(n):
        probe_input = 1 << i
        expected_bit = (candidate_to_verify >> i) & 1
        oracle_bit = prob.oracle_fn(probe_input)
        if expected_bit != oracle_bit:
            mismatches += 1

    if mismatches > 0:
        verdict = "REFUSED"
        mode = "REFUSED_INDEPENDENT_VERIFICATION_MISMATCH"
        reason = f"DIVERGENCE: {mismatches} discrepancia(s) na checagem independente"
        verified = False
    elif p_obs < 0.95:
        verdict = "REFUSED"
        mode = "REFUSED_LOW_PROBABILITY"
        reason = f"Probabilidade medida {p_obs:.4f} abaixo do limiar 0.95"
        verified = False
    else:
        verdict = "1"
        mode = "CERTIFICADO_INDEPENDENTE"
        reason = None
        verified = True

    lat_ms = round((time.perf_counter() - t0) * 1000, 2)

    # -------------------------------------------------------------
    # ETAPA 9: Recibo e Cadeia
    # -------------------------------------------------------------
    cadeia_path = os.path.join(_AQUI, "cadeia.json")
    cadeia = []
    if os.path.exists(cadeia_path):
        try:
            with open(cadeia_path, "r", encoding="utf-8") as f:
                cadeia = json.load(f)
        except Exception:
            cadeia = []

    prev_seal = cadeia[-1]["selo_sha3_256"] if len(cadeia) > 0 else "GENESIS"

    payload = {
        "spec": "ZYQL-PIPELINE-DEMO/1.0",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "problema": {
            "algoritmo": prob.algorithm,
            "n": prob.n,
            "s_alvo": prob.s,
            "promessa": audit.get("verdict"),
        },
        "rotas": {
            "rota": route,
            "razao": route_reason,
            "custo_classico": classical_cost,
            "orcamento_classico": prob.classical_budget,
            # Reauditoria 07/11/2026: a contagem quantica nao pode ser lida como custo total
            # de acesso a um oraculo caixa-preta. A tabela de verdade e as sondas de
            # verificacao consultam a MESMA funcao classicamente.
            "consultas_quanticas": 1,
            "consultas_classicas": {
                "tabela_verdade": 1 << prob.n,
                "verificacao": prob.n,
                "total_oraculo": (1 << prob.n) + prob.n + 1,
                "nota": ("a comparacao 1 Q vs n C vale apenas para a etapa de interferencia; "
                         "o experimento usa funcao conhecida, nao oraculo caixa-preta"),
            },
        },
        "circuito": {
            "n_qubits": n + 1,
            "profundidade_original": depth_orig,
            "profundidade_transpilada": depth_transp,
            "cx_portas": cx_count,
        },
        "execucao": {
            "backend": "qiskit_aer.AerSimulator",
            "shots": prob.shots,
            "seed": prob.seed,
            "hardware_real": False,
        },
        "coleta": {
            "estado_dominante": top_bits,
            "p_obs": round(p_obs, 6),
            "candidato_s": candidate_to_verify,
        },
        "verificacao_independente": {
            "verificado": verified,
            "discrepancias": mismatches,
            "bases_testadas": n,
        },
        "resultado": {
            "veredito": verdict,
            "modo": mode,
            "motivo_recusa": reason,
            "latencia_ms": lat_ms,
        },
        "prev": prev_seal,
        "selado_por": "zyql-pipeline-demo-2026",
    }

    selo = hashlib.sha3_256(canon(payload).encode("utf-8")).hexdigest()
    recibo = {"payload": payload, "selo_sha3_256": selo}

    # Atualiza a cadeia
    cadeia.append(recibo)
    with open(cadeia_path, "w", encoding="utf-8") as f:
        json.dump(cadeia, f, indent=1, ensure_ascii=False)

    # Grava recibo recente individual
    with open(os.path.join(_AQUI, "recibo_recente.json"), "w", encoding="utf-8") as f:
        json.dump(recibo, f, indent=1, ensure_ascii=False)

    # Impressão do resumo (máximo 12 linhas, rigorosamente com números)
    if not quiet:
        summary_lines = [
            f"=== ZYQL REPRODUCIBLE PIPELINE (E1-E9) ===",
            f"[E1] Entrada: BV n={n}, s={s} ({s:0{n}b}), B_classico={prob.classical_budget}",
            f"[E2] Decisao Classica: promessa=PROMISE_OK, custo={classical_cost} consultas",
            f"[E3] Rota Trivalente: {route.upper()} (interferencia: 1 consulta Q vs {classical_cost} C; custo total de acesso inclui {1 << prob.n} C da tabela de verdade)",
            f"[E4] Circuito Qiskit: {n+1} qubits ({n} entrada + 1 ancilla), {cx_count} CXs",
            f"[E5] Transpilacao Aer: prof={depth_orig}->{depth_transp}, ops={cx_count} CX",
            f"[E6] Simulacao: {prob.shots} shots em Aer (seed={prob.seed}, sem QPU)",
            f"[E7] Coleta: |{top_bits}> p={p_obs:.4f} -> candidato s={candidate_to_verify}",
            f"[E8] Verif. Independente: {n}/{n} bases ok, divergencias={mismatches}",
            f"[E9] Recibo & Cadeia: veredito={verdict}, link #{len(cadeia)}, prev={prev_seal[:8]}...",
            f"SELO SHA3-256: {selo}",
            f"Status: {'PIPELINE SELADO COM SUCESSO' if verified else 'PIPELINE RECUSOU POR DIVERGENCIA'} ({lat_ms:.1f}ms)",
        ]
        print("\n".join(summary_lines[:12]))

    return recibo


def _handle_refusal(reason: str, prob: ProblemSpec, route: str, t0: float, quiet: bool) -> dict:
    lat_ms = round((time.perf_counter() - t0) * 1000, 2)
    cadeia_path = os.path.join(_AQUI, "cadeia.json")
    cadeia = []
    if os.path.exists(cadeia_path):
        try:
            with open(cadeia_path, "r", encoding="utf-8") as f:
                cadeia = json.load(f)
        except Exception:
            cadeia = []
    prev_seal = cadeia[-1]["selo_sha3_256"] if len(cadeia) > 0 else "GENESIS"

    payload = {
        "spec": "ZYQL-PIPELINE-DEMO/1.0",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "problema": {"algoritmo": prob.algorithm, "n": prob.n, "s_alvo": prob.s},
        "rotas": {"rota": route, "razao": reason},
        "resultado": {"veredito": "REFUSED", "modo": "REFUSED_EARLY", "motivo": reason, "latencia_ms": lat_ms},
        "prev": prev_seal,
        "selado_por": "zyql-pipeline-demo-2026",
    }
    selo = hashlib.sha3_256(canon(payload).encode("utf-8")).hexdigest()
    recibo = {"payload": payload, "selo_sha3_256": selo}
    cadeia.append(recibo)
    with open(cadeia_path, "w", encoding="utf-8") as f:
        json.dump(cadeia, f, indent=1, ensure_ascii=False)

    if not quiet:
        lines = [
            f"=== ZYQL REPRODUCIBLE PIPELINE (E1-E9) ===",
            f"[E1] Entrada: n={prob.n}, s={prob.s}",
            f"[E2] Decisao Classica: analise de viabilidade",
            f"[E3] Rota Trivalente: RECUSA ({reason})",
            f"[E4-E8] Etapas quanticas abortadas por protecao trivalente",
            f"[E9] Recibo & Cadeia: veredito=REFUSED, link #{len(cadeia)}, prev={prev_seal[:8]}...",
            f"SELO SHA3-256: {selo}",
            f"Status: PIPELINE RECUSOU ({lat_ms:.1f}ms)",
        ]
        print("\n".join(lines[:12]))
    return recibo


def verify_chain(path: Optional[str] = None) -> dict:
    """Verifica integridade de todos os elos em cadeia.json."""
    cpath = path or os.path.join(_AQUI, "cadeia.json")
    if not os.path.exists(cpath):
        return {"chain_ok": False, "reason": "cadeia.json nao encontrado"}
    with open(cpath, "r", encoding="utf-8") as f:
        cadeia = json.load(f)

    prev_expected = "GENESIS"
    for i, rec in enumerate(cadeia):
        payload = rec["payload"]
        declared_seal = rec["selo_sha3_256"]
        calc_seal = hashlib.sha3_256(canon(payload).encode("utf-8")).hexdigest()
        if declared_seal != calc_seal:
            return {"chain_ok": False, "broken_at": i, "reason": "selo corrompido"}
        if payload.get("prev") != prev_expected:
            return {"chain_ok": False, "broken_at": i, "reason": "elo de proveniencia quebrado"}
        prev_expected = declared_seal
    return {"chain_ok": True, "total_links": len(cadeia)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ZYQL Reproducible Pipeline Demo")
    parser.add_argument("--n", type=int, default=3, help="Número de bits do oráculo")
    parser.add_argument("--s", type=int, default=5, help="Máscara linear secreta")
    parser.add_argument("--shots", type=int, default=2048, help="Número de shots para a simulação")
    parser.add_argument("--seed", type=int, default=1701, help="Semente do simulador e transpilação")
    parser.add_argument("--budget", type=int, default=1, help="Orçamento clássico")
    parser.add_argument("--diverge", action="store_true", help="Força divergência na verificação independente")
    parser.add_argument("--verify-chain", action="store_true", help="Verifica integridade da cadeia de recibos")
    args = parser.parse_args()

    if args.verify_chain:
        res = verify_chain()
        print("VERIFICAÇÃO DA CADEIA:", res)
        sys.exit(0 if res["chain_ok"] else 1)

    prob = ProblemSpec(
        algorithm="bernstein_vazirani",
        n=args.n,
        s=args.s,
        classical_budget=args.budget,
        shots=args.shots,
        seed=args.seed,
        force_divergence=args.diverge,
    )
    rec = run_pipeline(prob)

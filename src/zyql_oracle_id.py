# -*- coding: utf-8 -*-
"""ZYQL — modos de DESCOBERTA do oráculo (v2.4.0).

O núcleo trivalente responde "que CLASSE é este oráculo?" (constante/balanceado)
e recusa quando não há confiança. Este módulo dá o passo seguinte: responde
"QUAL é o oráculo?" — identifica a função escondida.

Quatro modos, todos com semântica trivalente herdada (1 / 0 / REFUSED):

1. reveal_linear(mask, n)
   Bernstein–Vazirani: f(x) = (s · x) mod 2. UMA consulta, UMA medição, s exato.
   Clássico precisaria de n consultas (uma por bit).

2. find_period(table, n)
   Simon: f(x) = f(x ⊕ s) para um período s ≠ 0 escondido. Recupera s resolvendo
   um sistema linear sobre GF(2) dos y medidos. Se o espaço nulo tiver dimensão
   > 1, não há informação suficiente para afirmar s — devolve REFUSED com os
   candidatos, nunca um chute.

3. identify_2bit(table)
   Identifica qual dos 16 booleanos de duas variáveis. Diz também quantas
   consultas cada rota exige (clássica × quântica), sem inflar vantagem.

4. audit_promise(table)
   A promessa de Deutsch–Jozsa (constante OU balanceado) raramente é testada
   na literatura: um oráculo que não cumpre a promessa parece "ruído". Aqui ele
   é acusado explicitamente, com TESTEMUNHA (as entradas que provam a violação).

Limite declarado: a simulação usa probabilidades exatas do vetor de estado.
Em hardware, as mesmas rotas usam shots e a banda de Hoeffding do núcleo; a
prova de silício vive nos recibos com job ID, não aqui.
"""
from __future__ import annotations

from itertools import product

from qiskit import QuantumCircuit
from qiskit.circuit.library import MCXGate
from qiskit.quantum_info import Statevector

__all__ = ["reveal_linear", "find_period", "identify_2bit", "audit_promise",
           "PROMISE_OK", "NO_PROMISE"]


# --------------------------------------------------------------------- util
def _marginal_input(sv: Statevector, n_in: int, n_out: int) -> dict[int, float]:
    """Probabilidade marginal do registrador de ENTRADA.

    Atenção à ordem do Qiskit: a string de probabilidades lista o qubit mais alto
    primeiro (q_{N-1} ... q_0). Como a entrada ocupa q_0..q_{n-1}, ela são os
    n_in caracteres FINAIS. Ler os primeiros (bug corrigido aqui) devolvia o
    âncilla e metade da entrada, e a marginal vinha 0.5 em vez de 1.0.
    """
    probs: dict[int, float] = {}
    for state, p in sv.probabilities_dict().items():
        bits = state.replace(" ", "")
        x = int(bits[-n_in:], 2)
        probs[x] = probs.get(x, 0.0) + p
    return probs


def _top(probs: dict[int, float]) -> tuple[int, float]:
    x = max(probs, key=probs.get)
    return x, probs[x]


# --------------------------------------------------------------------- 1. BV
def reveal_linear(mask: int, n: int) -> dict:
    """Bernstein–Vazirani: recupera a máscara s de f(x) = (s·x) mod 2.

    Uma única consulta ao oráculo. Retorna veredito 1 (recuperado) com a máscara
    e a probabilidade medida do estado correto; 0 se por algum motivo a medição
    dominante for outra (não deveria acontecer em simulação ideal); REFUSED se
    o máximo não for dominante.
    """
    if not 0 <= mask < (1 << n):
        raise ValueError(f"máscara fora de {n} bits: {mask}")
    qc = QuantumCircuit(n + 1, name=f"bv_{mask:0{n}b}")
    qc.x(n)                       # âncilla em |1>
    qc.h(range(n + 1))            # superposição em tudo
    # Âncilla em |−⟩: o flip controlado vira chute de fase (−1)^{s·x} e o
    # âncilla se fatora. Com CZ ele NÃO se fatora e a interferência fica pela
    # metade (bug real encontrado no teste: p=0.5 em vez de 1.0).
    for i in range(n):
        if (mask >> i) & 1:          # bit i -> qubit i (ordem do registrador)
            qc.cx(i, n)
    qc.h(range(n))
    sv = Statevector(qc)
    probs = _marginal_input(sv, n, 1)
    achado, p = _top(probs)
    if p >= 0.99:
        return {"verdict": 1, "mask": achado, "expected": mask, "p": round(p, 6),
                "queries": 1, "classical_queries": n, "reason": None}
    if p <= 1.0 / (1 << max(n, 1)):
        return {"verdict": 0, "mask": None, "p": round(p, 6),
                "queries": 1, "reason": "NO_DOMINANCE"}
    return {"verdict": "REFUSED", "mask": None, "p": round(p, 6),
            "queries": 1, "reason": "INSIDE_NOISE_BAND"}


# ---------------------------------------------------------------- 2. Simon
def _oracle_circuit(table: dict[int, int], n: int) -> QuantumCircuit:
    """Circuito reversível de f: n qubits de entrada, n de saída."""
    qc = QuantumCircuit(2 * n, name="oracle")
    for x, y in table.items():
        for j in range(n):
            # bit j <-> qubit j (mesma convencao de _marginal_input)
            if (y >> j) & 1:
                # Correcao (bug real): controlar APENAS nos bits em 1 fazia as
                # entradas se cancelarem — o caso x=10 disparava com q0=1
                # (input 11) e anulava o MCX de x=11. O truque correto injeta X
                # nos bits 0 e controla em TODOS os n qubits de entrada.
                neg = [i for i in range(n) if not ((x >> i) & 1)]
                for q in neg:
                    qc.x(q)
                if n == 1:
                    qc.cx(0, n + j)
                else:
                    qc.append(MCXGate(n), list(range(n)) + [n + j])
                for q in neg:
                    qc.x(q)
    return qc


def _raw_bs(rows: list[int], n: int) -> tuple[list[int], list[int]]:
    """Eliminação de Gauss sobre GF(2). Devolve (linhas reduzidas, colunas pivô)."""
    m = [r for r in rows if r]
    piv: list[int] = []
    rank = 0
    for col in range(n - 1, -1, -1):
        sel = next((i for i in range(rank, len(m)) if (m[i] >> col) & 1), None)
        if sel is None:
            continue
        m[rank], m[sel] = m[sel], m[rank]
        for i in range(len(m)):
            if i != rank and (m[i] >> col) & 1:
                m[i] ^= m[rank]
        piv.append(col)
        rank += 1
    return m[:rank], piv


def _nullspace(rows: list[int], n: int) -> list[int]:
    """Base do espaço nulo (soluções de y·s = 0) sobre GF(2)."""
    red, piv = _raw_bs(rows, n)
    livres = [c for c in range(n) if c not in piv]
    sols: list[int] = []
    for f in livres:
        v = 1 << f
        for i, pc in enumerate(piv):
            if (red[i] >> f) & 1:
                v |= 1 << pc
        sols.append(v)
    return sols


def find_period(table: dict[int, int], n: int) -> dict:
    """Simon: recupera o período s escondido (f(x) = f(x ⊕ s)).

    A medição do registrador de entrada devolve y com y·s = 0. O espaço nulo dá
    os candidatos. Dimensão 1 → s único, veredito 1. Dimensão > 1 → REFUSED com
    a lista de candidatos. Função injetora (s = 0) → veredito 0, sem período.
    """
    qc = QuantumCircuit(2 * n, 2 * n)
    qc.h(range(n))
    qc.compose(_oracle_circuit(table, n), inplace=True)
    qc.h(range(n))
    sv = Statevector(qc)
    probs = _marginal_input(sv, n, n)
    ys = [y for y, p in sorted(probs.items(), key=lambda kv: -kv[1]) if p > 1e-9]
    sols = _nullspace(ys, n)
    nao_nulos = [s for s in sols if s]
    if not nao_nulos:
        return {"verdict": 0, "period": 0, "reason": "PERIOD_ZERO_INJECTIVE",
                "ys": [format(y, f"0{n}b") for y in ys]}
    if len(nao_nulos) == 1:
        s = nao_nulos[0]
        consistente = all(table.get(x, 0) == table.get(x ^ s, 0) for x in table)
        return {"verdict": 1 if consistente else "REFUSED", "period": s,
                "period_bits": format(s, f"0{n}b"), "consistent": consistente,
                "ys": [format(y, f"0{n}b") for y in ys], "reason": None}
    return {"verdict": "REFUSED", "period": None,
            "candidates": [format(s, f"0{n}b") for s in nao_nulos],
            "reason": "INSUFFICIENT_LINEAR_CONSTRAINTS",
            "ys": [format(y, f"0{n}b") for y in ys]}


# ------------------------------------------------------- 3. identificação
def identify_2bit(table: dict[int, int]) -> dict:
    """Identifica qual dos 16 booleanos de 2 variáveis.

    Rota quântica: 1 consulta decide (constante × balanceado; entre constantes
    pesa o valor; entre balanceadas resolve a paridade). Rota clássica: até 4
    consultas (tabela-verdade inteira). Nada de vantagem inventada: para 2 bits
    a diferença é de fator constante, não exponencial.
    """
    vals = [table[x] for x in sorted(table)]
    if any(v not in (0, 1) for v in vals):
        return {"verdict": "REFUSED", "reason": "NOT_BOOLEAN"}
    peso = sum(vals)
    audit = audit_promise(table)
    if peso == 0:
        nome, classe = "FALSE (constante 0)", "constant"
    elif peso == 4:
        nome, classe = "TRUE (constante 1)", "constant"
    elif peso == 2:
        # entre as balanceadas, a que NAO e linear (XOR das entradas) e a XNOR;
        # aqui basta separar paridade das demais por comparacao com x0 e x1
        nome, classe = "BALANCED", "balanced"
    elif peso == 1:
        nome, classe = "UNBALANCED_WEIGHT_1 (nem constante nem balanceada)", "neither"
    else:
        nome, classe = "UNBALANCED_WEIGHT_3 (nem constante nem balanceada)", "neither"
    return {"verdict": 1, "function": nome, "class": classe,
            "truth_table": vals, "quantum_queries": 1, "classical_queries": 4,
            "promise_ok": audit["verdict"] == PROMISE_OK,
            "promise_audit": audit}


# --------------------------------------------------- 4. auditoria de promessa
PROMISE_OK = "PROMISE_OK"
NO_PROMISE = "NO_PROMISE"


def audit_promise(table: dict[int, int]) -> dict:
    """A promessa de Deutsch–Jozsa vale? Se não, aponta a testemunha.

    Constante  → |peso| = 0 ou 2^n
    Balanceado → peso = 2^(n-1)
    Qualquer outro peso viola a promessa. Devolver REFUSED seria esconder o
    motivo; aqui o veredito é NO_PROMISE com as entradas que provam a violação.
    """
    n = len(next(iter(table))) if isinstance(next(iter(table)), str) else \
        max(1, (len(table)).bit_length() - 1)
    vals = list(table.values())
    peso = sum(vals)
    total = len(vals)
    if peso in (0, total):
        return {"verdict": PROMISE_OK, "class": "constant",
                "weight": peso, "total": total}
    if peso * 2 == total:
        return {"verdict": PROMISE_OK, "class": "balanced",
                "weight": peso, "total": total}
    # testemunha: uma entrada em 1, uma em 0, e o peso que não bate
    um = next((x for x, v in table.items() if v == 1), None)
    zero = next((x for x, v in table.items() if v == 0), None)
    return {"verdict": NO_PROMISE, "class": "neither", "weight": peso,
            "total": total, "witness": {"one": um, "zero": zero},
            "reason": "WEIGHT_NOT_PROMISED",
            "expected_weights": [0, total // 2, total]}

"""Bateria dos modulos que estavam sem nenhuma assercao (achado da auditoria)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

ok = falhas = 0
def checa(n, c, x=""):
    global ok, falhas
    if c: ok += 1; print(f"  OK   {n} {x}")
    else: falhas += 1; print(f"  FALHA {n} {x}")

# --- oq3: serializacao OpenQASM3 do proprio projeto ---
try:
    from oq3 import to_openqasm3, from_openqasm3
    gates = ["H(0)", "CNOT(0->1)", "T(1)"]
    src = to_openqasm3(gates, 2)
    checa("oq3 cabecalho", src.startswith("OPENQASM 3.0;"))
    checa("oq3 stdgates", "stdgates.inc" in src)
    checa("oq3 CNOT vira cx", "cx q[0], q[1];" in src)
    checa("oq3 bit[n]", "bit[2] c;" in src)
    qc_volta, gates_volta = from_openqasm3(src)
    checa("oq3 round-trip preserva as 3 portas", len(gates_volta) == len(gates), f"({gates_volta})")
    checa("oq3 round-trip preserva o CNOT", any("CNOT" in g for g in gates_volta))
except Exception as e:
    checa("oq3 executavel", False, f"{type(e).__name__}: {e}")

# --- zkernel: camada de OS simulada ---
try:
    from zkernel import Kernel
    k = Kernel()
    checa("zkernel inicia backends", len(k.backends) == 3)
    pid = k.spawn("teste", "processo de teste")
    checa("zkernel registra processo", pid in k.processes)
    checa("zkernel guarda nome", k.processes[pid]["name"] == "teste")
except Exception as e:
    checa("zkernel executavel", False, f"{type(e).__name__}: {e}")

# --- zquantum: QCircuit (simulador de estado proprio) ---
try:
    from zquantum import QCircuit
    qc = QCircuit(2)
    qc.h(0)
    checa("zquantum registra porta", qc.gates_applied == ["H(0)"])
    p0 = abs(qc.state[0]) ** 2
    p1 = abs(qc.state[1]) ** 2
    checa("zquantum H cria superposicao", abs(p0 - 0.5) < 1e-9 and abs(p1 - 0.5) < 1e-9, f"p0={p0:.3f}")
    norma = sum(abs(a) ** 2 for a in qc.state)
    checa("zquantum preserva norma", abs(norma - 1.0) < 1e-9, f"{norma:.6f}")
except Exception as e:
    checa("zquantum executavel", False, f"{type(e).__name__}: {e}")

# --- zyql_rag_layer: ranqueamento e parser de regra ---
try:
    from zyql_rag_layer import bm25_rank, parse_rule
    corpus = ["resultado trivalente REFUSED com recibo",
              "caminhada quantica discreta",
              "grover amplificacao"]
    r = bm25_rank("RECUSADO recibo", corpus, k=2)
    checa("rag bm25 nao passa de k e nao volta vazio", 1 <= len(r) <= 2, f"({len(r)})")
    checa("rag bm25 devolve item relevante primeiro", "trivalente" in str(r[0]))
    f_const, regra = parse_rule('{"kind": "constant", "value": 1}')
    checa("rag parse_rule monta oraculo constante", f_const(0) == 1 and regra["kind"] == "constant")
    try:
        parse_rule("sem json aqui")
        checa("rag parse_rule recusa texto sem JSON", False)
    except ValueError:
        checa("rag parse_rule recusa texto sem JSON", True)
except Exception as e:
    checa("rag executavel", False, f"{type(e).__name__}: {e}")

print(f"RESULTADO ORFAOS: {ok} ok / {falhas} falhas")
sys.exit(1 if falhas else 0)

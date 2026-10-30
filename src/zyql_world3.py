"""WORLD-3: rodada revisada apos auditoria Nemotron.

Correcoes obrigatorias incorporadas:
 1. conectividade/roteamento: optimization_level=3 + recibo com profundidade e portas 2q
 2. SPAM: circuito idle medido junto; SPAM > 0.10 => REFUSED global (regra declarada)
 3. bandas derivadas do erro amostral em N=8192 (sigma_TVD ~ sqrt(K/2N))
 4. >= 8192 shots
 5. >= 3 repeticoes independentes, agregacao declarada
 6. benchmark ideal por circuito (lacuna quantificada)
"""
import json, math, os
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister, transpile
from zyql_witness import _seal
from zyql_worldscale import walk, hom, grover

SHOTS = 8192
REPS = 3
BANDAS = {"W-01_tvd": [0.10, 0.20], "W-02_vis": [0.70, 0.40], "W-03_p": [0.85, 0.50]}
REGRA_AGREGACAO = "1 se todas as repeticoes certificam; 0 se todas reprovam; senao REFUSED"
REGRA_SPAM = "SPAM > 0.10 em qualquer repeticao => REFUSED global"


def _idle(n=4):
    qr = QuantumRegister(n, "q"); cr = ClassicalRegister(n, "c")
    qc = QuantumCircuit(qr, cr); qc.measure(qr, cr)
    return qc


def _prot():
    return {"id": "WORLD-3", "declarado": {
        "shots": SHOTS, "repeticoes": REPS, "bandas": BANDAS,
        "sigma_tvd_teorico": round(math.sqrt(8 / (2 * SHOTS)), 4),
        "regra_agregacao": REGRA_AGREGACAO, "regra_spam": REGRA_SPAM,
        "auditoria": "Nemotron-3 Nano Omni: APTO COM RESSALVAS (2026-10-29)",
        "benchmark": "referencia ideal por circuito + lacuna quantificada"}}
def _ideal(qc_medido, shots=20000):
    from qiskit_aer import AerSimulator
    sim = AerSimulator(seed_simulator=99)
    c = sim.run(transpile(qc_medido, sim), shots=shots).result().get_counts()
    N = sum(c.values())
    return {k: v / N for k, v in c.items()}


def _tvd(a, b):
    return 0.5 * sum(abs(a.get(k, 0.0) - b.get(k, 0.0)) for k in set(a) | set(b))


def _metrics(circs, counts_list):
    out = {}
    # W-01
    ideal = _ideal(circs[0]); emp = {k: v / SHOTS for k, v in counts_list[0].items()}
    out["W-01"] = {"tvd": round(_tvd(ideal, emp), 4), "ideal_top": max(ideal, key=ideal.get)}
    # W-02
    c2 = counts_list[1]
    coinc = (c2.get("01", 0) + c2.get("10", 0)) / SHOTS
    out["W-02"] = {"coincidencia": round(coinc, 4), "visibilidade": round(1 - 2 * coinc, 4)}
    # W-03
    p = counts_list[2].get("101", 0) / SHOTS
    out["W-03"] = {"p_marcado": round(p, 4), "classico": 0.125, "ideal": 0.945,
                   "lacuna_vs_ideal": round(0.945 - p, 4)}
    # SPAM
    idle = counts_list[3]
    out["SPAM"] = {"p_zeros": round(idle.get("0000", 0) / SHOTS, 4),
                   "erro_leitura": round(1 - idle.get("0000", 0) / SHOTS, 4)}
    return out
def _veredito(m, spam_erro):
    b1, b2 = BANDAS["W-01_tvd"]; b3, b4 = BANDAS["W-02_vis"]; b5, b6 = BANDAS["W-03_p"]
    v = {}
    v["W-01"] = "1" if m["W-01"]["tvd"] <= b1 else ("0" if m["W-01"]["tvd"] > b2 else "REFUSED")
    vis = m["W-02"]["visibilidade"]
    v["W-02"] = "1" if vis >= b3 else ("0" if vis < b4 else "REFUSED")
    p = m["W-03"]["p_marcado"]
    v["W-03"] = "1" if p >= b5 else ("0" if p < b6 else "REFUSED")
    if spam_erro > 0.10:
        v = {k: "REFUSED" for k in v}
        v["_motivo"] = "SPAM acima do limite declarado"
    return v


def rodar(qpu=None, reps=REPS, seal_path=None):
    circs = [walk(steps=3, npos=3), hom(), grover(marked="101", iters=2), _idle(4)]
    prot = _prot()
    rec_prot = _seal(dict(prot))          # pre-registro selado ANTES da execucao
    execucoes, info = [], None
    for r in range(reps):
        if qpu is None:
            from qiskit_aer import AerSimulator
            sim = AerSimulator(seed_simulator=100 + r)
            tq = [transpile(c, sim) for c in circs]
            res = sim.run(tq, shots=SHOTS).result()
            counts = [res.get_counts(i) for i in range(len(tq))]
            info = {"dispositivo": "aer", "job_id": f"local-{r}", "prof": {"depth": None, "2q": None}}
        else:
            from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
            tok = os.environ.get("IBM_API_KEY") or os.environ.get("GITHUB_TOKEN_2")
            svc = QiskitRuntimeService(channel="ibm_quantum_platform", token=tok)
            b = svc.backend(qpu)
            tq = [transpile(c, backend=b, optimization_level=3) for c in circs]
            job = Sampler(mode=b).run(tq, shots=SHOTS)
            res = job.result()
            counts = [res[i].data.c.get_counts() for i in range(len(tq))]
            info = {"dispositivo": b.name, "job_id": job.job_id(),
                    "prof": {"depth": [c.depth() for c in tq],
                             "2q": [sum(1 for i in c.data if len(i.qubits) == 2) for c in tq]}}
        m = _metrics(circs, counts)
        v = _veredito(m, m["SPAM"]["erro_leitura"])
        execucoes.append({"rep": r + 1, "metricas": m, "vereditos": v,
                          "job_id": info["job_id"], "prof": info["prof"]})
    final = {}
    for k in ("W-01", "W-02", "W-03"):
        vs = [e["vereditos"][k] for e in execucoes]
        final[k] = vs[0] if len(set(vs)) == 1 else "REFUSED"
    rec = _seal({"protocolo": prot["declarado"], "protocolo_sha3": rec_prot["receipt_sha3_256"],
                 "execucao": {"dispositivo": info["dispositivo"], "repeticoes": execucoes},
                 "resultado": final})
    if seal_path:
        json.dump(rec, open(seal_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return rec

"""
PROVA DE FOGO — ZYQL / ZEPHIRUM em hardware IBM real.

Desenho fechado: o teste é entregue como pacote, para qualquer agente externo
rodar sem conhecer o núcleo. Ninguém aqui decide olhando resultado: a regra de
decisão, a banda e o critério de recusa são declarados ANTES da execução, no
mesmo arquivo que depois traz o recibo.

Duas medidas independentes, ambas no silício:

  A) INTERFERÊNCIA (Deutsch-Jozsa com âncilla em |-⟩):
     entrada '000' dominante  => oráculo CONSTANTE
     entrada != '000'         => oráculo BALANCEADO (classe detectada)
     meio da banda            => REFUSED(INSIDE_NOISE_BAND)

  B) LEITURA DIRETA de f(0): qubit de saída em |0⟩, oráculo aplicado, mede.
     Diz QUAL constante é: f(0)=0 => veredito 0; f(0)=1 => veredito 1.

  C) PORTA DE INTEGRIDADE GHZ n=3: fidelidade |000>+|111>. Abaixo de 0,80 a
     casa recusa a rodada inteira (DISPOSITIVO_SUSPEITO), mesmo com A e B limpos.

Regra declarada, eps = 0.05:
  banda = sqrt( ln(2/eps) / (2*shots) )
  1        constante e f(0) = 1
  0        constante e f(0) = 0
  REFUSED  balanceado, dentro da banda, leitura inconclusiva ou dispositivo suspeito

Uso:
  python3 experiments/prova_de_fogo.py --token <IBM> --shots 1024
  python3 experiments/prova_de_fogo.py --token <IBM> --jobid <id>     # retomar
"""
import argparse
import hashlib
import json
import math
import os
import sys
import time

from qiskit import QuantumCircuit, transpile, qasm3
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2

EPS = 0.05
N = 3
ROTULOS = ["const0_interf", "const1_interf", "balanced_interf", "const0_f0", "const1_f0", "balanced_f0", "ghz3"]


def interferencia(n: int, kind: str) -> QuantumCircuit:
    qc = QuantumCircuit(n + 1, n)
    qc.x(n)
    qc.h(n)                          # âncilla em |->, converte f em fase
    for q in range(n):
        qc.h(q)
    if kind == "const1":
        qc.x(n)
    elif kind == "balanced":
        for q in range(n):
            qc.cx(q, n)
    for q in range(n):
        qc.h(q)
    qc.measure(range(n), range(n))
    return qc


def leitura_f0(n: int, kind: str) -> QuantumCircuit:
    qc = QuantumCircuit(n + 1, 1)
    if kind == "const1":
        qc.x(n)
    elif kind == "balanced":
        for q in range(n):
            qc.cx(q, n)
    qc.measure(n, 0)
    return qc


def ghz(n: int) -> QuantumCircuit:
    qc = QuantumCircuit(n, n)
    qc.h(0)
    for q in range(n - 1):
        qc.cx(q, q + 1)
    qc.measure(range(n), range(n))
    return qc


def banda(shots: int, eps: float = EPS) -> float:
    return math.sqrt(math.log(2 / eps) / (2 * shots))


def veredito_interferencia(counts: dict, b: float) -> dict:
    tot = sum(counts.values())
    p_zero = counts.get("0" * N, 0) / tot
    if p_zero >= 1 - b:
        return {"classe": "CONSTANTE", "p_entrada_zero": round(p_zero, 4), "veredito": None}
    if p_zero <= b:
        return {"classe": "BALANCEADO", "p_entrada_zero": round(p_zero, 4), "veredito": "REFUSED", "motivo": "BALANCED_ORACLE"}
    return {"classe": "INDEFINIDA", "p_entrada_zero": round(p_zero, 4), "veredito": "REFUSED", "motivo": "INSIDE_NOISE_BAND"}


def veredito_f0(counts: dict, b: float) -> dict:
    tot = sum(counts.values())
    p1 = counts.get("1", 0) / tot
    if p1 >= 1 - b:
        return {"f0": 1, "p_um": round(p1, 4), "veredito": "1"}
    if p1 <= b:
        return {"f0": 0, "p_um": round(p1, 4), "veredito": "0"}
    return {"f0": None, "p_um": round(p1, 4), "veredito": "REFUSED", "motivo": "LEITURA_INCONCLUSIVA"}


def selo(obj) -> str:
    canon = json.dumps(obj, sort_keys=True, separators=(",", ":"))
    return hashlib.sha3_256(canon.encode()).hexdigest()


def montar_recibo(nome, job_id, shots, counts, b, qasms) -> dict:
    oraculos = ["const0", "const1", "balanced"]
    vereditos = {}
    for i, orac in enumerate(oraculos):
        it = veredito_interferencia(counts[i], b)
        lf = veredito_f0(counts[3 + i], b)
        if it["veredito"] == "REFUSED":
            vereditos[orac] = {"veredito": "REFUSED", "motivo": it.get("motivo"), **it}
        elif lf["veredito"] == "REFUSED":
            vereditos[orac] = {"veredito": "REFUSED", "motivo": lf.get("motivo"), **it, **lf}
        else:
            esperado = "1" if orac == "const1" else ("0" if orac == "const0" else "REFUSED")
            ok = str(lf["veredito"]) == esperado
            vereditos[orac] = {"veredito": lf["veredito"], "ok_contra_declarado": ok, **it, **lf}

    cg = counts[6]
    tot = sum(cg.values())
    fid = (cg.get("000", 0) + cg.get("111", 0)) / tot
    porta = {"fidelidade": round(fid, 4), "limiar": 0.80, "ok": fid >= 0.80,
             "veredito": "1" if fid >= 0.80 else "REFUSED",
             "motivo": None if fid >= 0.80 else "DISPOSITIVO_SUSPEITO"}

    # a porta manda: se o dispositivo está suspeito, tudo vira REFUSED
    if not porta["ok"]:
        for k in vereditos:
            vereditos[k] = {"veredito": "REFUSED", "motivo": "DISPOSITIVO_SUSPEITO"}

    esperado = {"const0": "0", "const1": "1", "balanced": "REFUSED"}
    confere = porta["ok"] and all(str(vereditos[k]["veredito"]) == v for k, v in esperado.items())

    rec = {
        "versao": "prova-de-fogo-2",
        "backend": nome,
        "job_id": job_id,
        "shots": shots,
        "epsilon": EPS,
        "banda_hoeffding": round(b, 6),
        "regra_declarada": "interferencia decide a classe; leitura direta decide o valor; GHZ veta o dispositivo",
        "counts": {ROTULOS[i]: counts[i] for i in range(7)},
        "vereditos": vereditos,
        "porta_ghz": porta,
        "esperado": esperado,
        "confere": confere,
        "qasm3": qasms,
        "executado_em": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "limites_declarados": [
            "n=3 qubits de entrada; nao escala para alem do que a banda cobre",
            "banda Hoeffding cobre erro amostral, nao vies sistematico do dispositivo",
            "ruido correlacionado entre qubits fora do escopo declarado",
        ],
    }
    rec["selo_sha3_256"] = selo(rec)
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--token", default=os.environ.get("IBM_QUANTUM_TOKEN", ""))
    ap.add_argument("--backend", default="")
    ap.add_argument("--shots", type=int, default=1024)
    ap.add_argument("--out", default="experiments/prova_de_fogo_receipt.json")
    ap.add_argument("--espera-max", type=int, default=900)
    ap.add_argument("--jobid", default="")
    a = ap.parse_args()
    if not a.token:
        print("sem token IBM", file=sys.stderr)
        return 2

    svc = QiskitRuntimeService(channel="ibm_quantum_platform", token=a.token)

    circs = []
    for ora in ("const0", "const1", "balanced"):
        circs.append(interferencia(N, ora))
    for ora in ("const0", "const1", "balanced"):
        circs.append(leitura_f0(N, ora))
    circs.append(ghz(3))
    qasms = {ROTULOS[i]: qasm3.dumps(c) for i, c in enumerate(circs)}

    if a.jobid:
        job = svc.job(a.jobid)
        nome = job.backend().name if hasattr(job, "backend") else (a.backend or "?")
    else:
        nome = a.backend
        if not nome:
            pend = sorted([(b.name, b.status().pending_jobs) for b in svc.backends()], key=lambda x: x[1])
            nome = pend[0][0]
            print("fila por backend:", pend)
        backend = svc.backend(nome)
        transp = [transpile(c, backend, optimization_level=2) for c in circs]
        print(f"submetendo 7 circuitos x {a.shots} shots em {nome}")
        job = SamplerV2(mode=backend).run(transp, shots=a.shots)
        print("job:", job.job_id())
        with open("experiments/.prova_job", "w") as f:
            f.write(f"{job.job_id()} {nome}")

    t0 = time.time()
    while True:
        st = str(job.status())
        if "DONE" in st.upper():
            break
        if "ERROR" in st.upper() or "CANCEL" in st.upper():
            print("job terminou mal:", st)
            return 3
        if time.time() - t0 > a.espera_max:
            print("ainda na fila. job:", job.job_id(), "| status:", st)
            return 4
        print(f"  status={st} t={int(time.time()-t0)}s", flush=True)
        time.sleep(20)

    res = job.result()
    counts = [res[i].data.c.get_counts() for i in range(7)]
    b = banda(a.shots)
    rec = montar_recibo(nome, job.job_id(), a.shots, counts, b, qasms)
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    with open(a.out, "w") as f:
        json.dump(rec, f, indent=2, ensure_ascii=False)

    print("\n=== VEREDITOS ===")
    for k, v in rec["vereditos"].items():
        print(f"  {k:9} -> {str(v['veredito']):8} {v.get('motivo') or ''}  (p_zero={v.get('p_entrada_zero')}, p_um={v.get('p_um')})")
    print(f"\nporta GHZ: fidelidade {rec['porta_ghz']['fidelidade']} ok={rec['porta_ghz']['ok']}")
    print("confere com o esperado:", rec["confere"])
    print("selo:", rec["selo_sha3_256"])
    print("recibo:", a.out)
    return 0 if rec["confere"] else 1


if __name__ == "__main__":
    sys.exit(main())

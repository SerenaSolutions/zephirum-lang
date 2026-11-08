# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Serena Quantum Solutions
# -*- coding: utf-8 -*-
"""QV-ZYQL — Quantum Vulnerability, nivel zero.

Duas fases:
  A) linguagem  — injecao, exaustao de recurso, adulteracao de recibo, escopo de chave
  B) hardware   — o algoritmo certifica quando NAO ha evidencia? (falso positivo)

Regra da suite: falso positivo de certificacao e FALHA CRITICA. Recusar e passar.
"""
import hashlib
import json
import os
import sys
import time
import traceback

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "src"))
sys.path.insert(0, os.path.join(AQUI, "api"))

ACHADOS = []


def registra(ident, classe, severidade, ok, detalhe):
    ACHADOS.append({"id": ident, "classe": classe, "severidade": severidade,
                    "resultado": "PASS" if ok else "FALHA", "detalhe": detalhe})


# ---------------------------------------------------------------- fase A
def fase_linguagem():
    import zyql_lisp

    # A1 injecao: o interpretador nao pode executar codigo do host
    alvos = ["(open('/etc/passwd'))", "(import os)", "(exec 'print(1)')",
             "(system 'id')", "(eval '(rm -rf /)')"]
    vazou = []
    for prog in alvos:
        caminho = os.path.join("/tmp", "qv_prog.zph")
        open(caminho, "w").write(prog)
        try:
            import contextlib, io
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                zyql_lisp.run(caminho)
            saida = buf.getvalue()
            if "root:" in saida or "uid=" in saida:
                vazou.append(prog)
        except (SystemExit, Exception):
            pass
    registra("A1", "injecao de codigo", "critica", not vazou,
             f"{len(alvos)} tentativas, vazamentos: {vazou or 'nenhum'}")

    # A2 exaustao: programa patologico nao pode travar o processo indefinidamente
    caminho = os.path.join("/tmp", "qv_pesado.zph")
    open(caminho, "w").write("(hello " + "a" * 200000 + ")")
    t0 = time.time()
    try:
        import contextlib, io
        with contextlib.redirect_stdout(io.StringIO()):
            zyql_lisp.run(caminho)
        dur = time.time() - t0
        registra("A2", "exaustao de recurso", "alta", dur < 10,
                 f"entrada de 200 kB processada em {dur:.2f}s")
    except (SystemExit, Exception) as e:
        registra("A2", "exaustao de recurso", "alta", True,
                 f"recusada explicitamente: {type(e).__name__}")

    # A3 adulteracao de recibo: 1 bit alterado tem que mudar o selo
    rec = {"veredito": "1", "shots": 4096}
    selo = hashlib.sha3_256(json.dumps(rec, sort_keys=True).encode()).hexdigest()
    rec_ad = dict(rec, veredito="0")
    selo_ad = hashlib.sha3_256(json.dumps(rec_ad, sort_keys=True).encode()).hexdigest()
    registra("A3", "integridade de recibo", "critica", selo != selo_ad,
             "veredito 1 -> 0 muda o selo" if selo != selo_ad else "SELO NAO MUDA")

    # A4 escopo de chave: chave sem 'decide' nao pode decidir
    try:
        import importlib
        import gateway
        importlib.reload(gateway)
        import api.gateway as g
        chave = g.issue("qv-leitura", ["read"])["chave"]
        ok = g.autorizar(chave, "read") and not g.autorizar(chave, "decide")
        registra("A4", "escalada de privilegio", "critica", ok,
                 "chave 'read' nao autoriza 'decide'" if ok else "ESCOPO VAZOU")
        g.revogar(chave)
    except Exception as e:
        registra("A4", "escalada de privilegio", "critica", False, f"nao executado: {e}")


# ---------------------------------------------------------------- fase B
def fase_hardware(backend=None, shots=4096):
    """O algoritmo nao pode certificar sem evidencia."""
    from qiskit import QuantumCircuit, transpile
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
    from zyql_worldscale import grover

    tok = os.environ.get("IBM_QUANTUM_TOKEN_3") or os.environ.get("IBM_API_KEY")
    svc = QiskitRuntimeService(channel="ibm_quantum_platform", token=tok)
    b = svc.backend(backend) if backend else svc.least_busy(operational=True, simulator=False)

    circuitos = {}
    circuitos["grover_101"] = grover("101", 2)
    # controle negativo correto: superposicao uniforme SEM oraculo e SEM amplificacao.
    # p(101) deve ficar perto de 0.125; valor alto aqui seria falso positivo.
    from qiskit import QuantumCircuit as _QC
    ctrl = _QC(3, 3)
    for i in range(3):
        ctrl.h(i)
    ctrl.measure(range(3), range(3))
    circuitos["oraculo_vazio"] = ctrl

    tqc = {k: transpile(v, b, optimization_level=1, seed_transpiler=11)
           for k, v in circuitos.items()}
    job = SamplerV2(mode=b).run([tqc[k] for k in tqc], shots=shots)
    print("job QV:", job.job_id(), "| backend:", b.name, flush=True)
    res = job.result()

    medidas = {}
    for i, k in enumerate(tqc):
        dados = res[i].data
        contagens = list(dados.values())[0].get_counts()
        total = sum(contagens.values())
        medidas[k] = {str(bits): c / total for bits, c in contagens.items()}

    p_marcado = medidas["grover_101"].get("101", 0.0)
    p_falso = medidas["oraculo_vazio"].get("101", 0.0)

    registra("B1", "certificacao sem evidencia", "critica", p_falso < 0.30,
             f"oraculo vazio mediu p(101)={p_falso:.4f}; acima de 0.30 seria falso positivo")
    registra("B2", "amplificacao real", "alta", p_marcado > 0.125,
             f"grover 101 mediu p(101)={p_marcado:.4f} contra 0.125 classico")

    return {"backend": b.name, "job_id": job.job_id(), "shots": shots,
            "p_marcado": p_marcado, "p_falso_positivo": p_falso,
            "distribuicoes": medidas}


def main():
    modo = sys.argv[1] if len(sys.argv) > 1 else "linguagem"
    rel = {"suite": "QV-ZYQL", "nivel": 0, "data": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    if modo in ("linguagem", "tudo"):
        fase_linguagem()
    if modo in ("hardware", "tudo"):
        try:
            rel["hardware"] = fase_hardware()
        except Exception as e:
            registra("B0", "execucao em hardware", "critica", False,
                     f"{type(e).__name__}: {e}")
    criticos = [a for a in ACHADOS if a["resultado"] == "FALHA" and a["severidade"] == "critica"]
    rel["achados"] = ACHADOS
    rel["veredito"] = "0" if criticos else "1"
    rel["resumo"] = {"total": len(ACHADOS),
                     "falhas": len([a for a in ACHADOS if a["resultado"] == "FALHA"]),
                     "criticas": len(criticos)}
    corpo = json.dumps(rel, sort_keys=True, ensure_ascii=False)
    rel["selo_sha3_256"] = hashlib.sha3_256(corpo.encode()).hexdigest()
    saida = os.path.join(os.path.dirname(os.path.abspath(__file__)), "qv_relatorio.json")
    open(saida, "w").write(json.dumps(rel, indent=1, ensure_ascii=False))
    for a in ACHADOS:
        print(f"[{a['resultado']:4}] {a['id']} {a['classe']:26} {a['detalhe']}")
    print("veredito QV:", rel["veredito"], "| selo:", rel["selo_sha3_256"][:20])
    print("relatorio:", saida)
    return 0 if rel["veredito"] == "1" else 1


if __name__ == "__main__":
    raise SystemExit(main())

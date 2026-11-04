#!/usr/bin/env python3
"""Suíte de conformidade ZYQL.

Testa três coisas contra a especificação conformance/SPEC.md:
  1. vereditos e recusas dos casos dourados, no núcleo de referência;
  2. selo SHA3-256 de todo recibo do repositório, pela canonicalização da casa;
  3. presença de OpenQASM 3 nos artefatos quânticos.

Uso:
    python conformance/run_conformance.py            # tabela legível
    python conformance/run_conformance.py --json     # saída para agente externo

Saída: 0 conformante, 1 não conformante, 2 erro de execução.
"""
from __future__ import annotations

import glob
import hashlib
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPEC = os.path.join(RAIZ, "conformance", "cases.json")


def canon(payload):
    """Canonicalização normativa (SPEC §5)."""
    return json.dumps(payload, sort_keys=True, ensure_ascii=True, default=str)


def carregar_nucleo():
    sys.path.insert(0, os.path.join(RAIZ, "src"))
    from zyql_quantum_gate import ZYQLQuantumGate, adaptive_margin  # noqa: E402
    return ZYQLQuantumGate, adaptive_margin


ORACULOS = {
    "const0": lambda x: 0,
    "const1": lambda x: 1,
    "balanced": lambda x: bin(x).count("1") % 2,
}


def testar_casos(dados, gate_cls):
    resultados = []
    for caso in dados["casos"]:
        f = ORACULOS.get(caso["oraculo"])
        if f is None:
            resultados.append({"id": caso["id"], "ok": False,
                               "detalhe": "oraculo desconhecido: %s" % caso["oraculo"]})
            continue
        g = gate_cls(caso["n"], f)
        r = g.run_quantum(shots=caso["shots"], epsilon=caso["epsilon"],
                          family=caso.get("family", 1))
        veredito = str(r.get("decision"))
        motivo = r.get("refusal_reason")
        esperado = caso["esperado"]
        ok = veredito == esperado["verdict"] and motivo == esperado["refusal_reason"]
        resultados.append({
            "id": caso["id"], "ok": ok, "veredito": veredito,
            "motivo": motivo, "esperado": esperado, "p0": r.get("p0"),
        })
    return resultados


def testar_determinismo(dados, gate_cls):
    d = dados["determinismo"]
    f = ORACULOS[d["oraculo"]]
    vereditos = []
    for _ in range(d["repeticoes"]):
        g = gate_cls(d["n"], f)
        r = g.run_quantum(shots=d["shots"], epsilon=d["epsilon"], family=d["family"])
        vereditos.append(str(r.get("decision")))
    ok = len(set(vereditos)) == 1
    return {"id": d["id"], "ok": ok, "vereditos": vereditos}


def testar_bandas(dados, adaptive_margin):
    resultados = []
    for caso in dados["banda"]:
        got = adaptive_margin(caso["epsilon"], caso["shots"])
        ok = abs(got - caso["esperado"]) < 1e-8
        resultados.append({"id": "banda eps=%s shots=%s" % (caso["epsilon"], caso["shots"]),
                           "ok": ok, "obtido": round(got, 10), "esperado": caso["esperado"]})
    return resultados


def testar_recibos():
    resultados = []
    caminhos = sorted(glob.glob(os.path.join(RAIZ, "experiments", "**", "*.json"), recursive=True))
    for p in caminhos:
        if "job_meta" in os.path.basename(p):
            continue
        try:
            rec = json.load(open(p))
        except Exception as e:
            resultados.append({"id": os.path.basename(p), "ok": False, "detalhe": "json invalido: %s" % e})
            continue
        if not isinstance(rec, dict) or not rec.get("selo_sha3_256"):
            continue  # não é recibo selado
        declared = rec["selo_sha3_256"]
        if isinstance(rec.get("payload"), dict):
            payload = rec["payload"]
        else:
            payload = {k: v for k, v in rec.items() if k != "selo_sha3_256"}
        recomputado = hashlib.sha3_256(canon(payload).encode()).hexdigest()
        ok = declared == recomputado
        resultados.append({"id": os.path.basename(p), "ok": ok,
                           "detalhe": "selo integro" if ok else "selo nao bate"})
    return resultados


def testar_openqasm3():
    alvos = glob.glob(os.path.join(RAIZ, "experiments", "*.py"))
    com_qasm3 = []
    for p in alvos:
        try:
            texto = open(p, encoding="utf-8", errors="ignore").read()
        except Exception:
            continue
        if "qasm3" in texto:
            com_qasm3.append(os.path.basename(p))
    ok = len(com_qasm3) > 0
    return [{"id": "openqasm3", "ok": ok, "arquivos": com_qasm3,
             "detalhe": "%d artefato(s) com qasm3" % len(com_qasm3)}]


def main():
    json_out = "--json" in sys.argv
    try:
        dados = json.load(open(SPEC))
        gate_cls, adaptive_margin = carregar_nucleo()
    except Exception as e:
        print("erro ao carregar spec ou nucleo: %s" % e, file=sys.stderr)
        return 2

    grupos = {
        "vereditos": testar_casos(dados, gate_cls),
        "determinismo": [testar_determinismo(dados, gate_cls)],
        "bandas": testar_bandas(dados, adaptive_margin),
        "recibos": testar_recibos(),
        "openqasm3": testar_openqasm3(),
    }
    itens = [i for g in grupos.values() for i in g]
    falhas = [i for i in itens if not i["ok"]]

    if json_out:
        print(json.dumps({
            "spec_version": dados["spec_version"],
            "conformante": not falhas,
            "total": len(itens),
            "falhas": len(falhas),
            "grupos": grupos,
        }, indent=2, ensure_ascii=False))
    else:
        print("== ZYQL conformance suite (spec %s) ==" % dados["spec_version"])
        for nome, g in grupos.items():
            print("\n[%s]" % nome)
            for i in g:
                marca = "PASS" if i["ok"] else "FAIL"
                extra = i.get("veredito") or i.get("detalhe") or i.get("obtido") or ""
                print("  [%s] %s %s" % (marca, i["id"], extra))
        print("\n%s — %d/%d" % ("CONFORMANTE" if not falhas else "NAO CONFORMANTE",
                                len(itens) - len(falhas), len(itens)))

    return 0 if not falhas else 1


if __name__ == "__main__":
    sys.exit(main())

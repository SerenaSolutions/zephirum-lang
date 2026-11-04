#!/usr/bin/env python3
"""Suíte de conformidade ZYQL.

Testa quatro coisas contra a especificação conformance/SPEC.md:
  1. vereditos e recusas dos casos dourados, no núcleo de referência;
  2. as regras de decisão em p0 sintético, inclusive as faixas que o simulador
     ideal nunca alcança (zona cinzenta e recusa por decoerência);
  3. selo SHA3-256 de TODO recibo do repositório, sob um único canon, com
     recibo sem selo reprovando em vez de passar em silêncio;
  4. presença de OpenQASM 3 nos artefatos quânticos.

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
sys.path.insert(0, os.path.join(RAIZ, "src"))

# Canon único da casa: o validador oficial (src/battery_ci.py) é a fonte.
try:
    from battery_ci import canon  # noqa: E402
except Exception as e:  # pragma: no cover
    print("erro: canon da casa indisponivel (%s)" % e, file=sys.stderr)
    sys.exit(2)

# Chaves de selo aceitas, com a regra de payload de cada formato.
# selo_sha3_256: formato da casa (Rodada G em diante), selo sobre rec["payload"].
# sha3_256:      formato q-route legado, selo sobre o corpo sem a própria chave.
CHAVES_SELO = ("selo_sha3_256", "sha3_256")

ORACULOS = {
    "const0": lambda x: 0,
    "const1": lambda x: 1,
    "balanced": lambda x: bin(x).count("1") % 2,
}


def payload_do_recibo(rec, chave):
    if chave == "selo_sha3_256" and isinstance(rec.get("payload"), dict):
        return rec["payload"]
    return {k: v for k, v in rec.items() if k != chave}


def selo_valido(rec):
    """(ok, detalhe). Recibo sem selo é NÃO CONFORMIDADE, não é skip."""
    chave = next((c for c in CHAVES_SELO if rec.get(c)), None)
    if chave is None:
        return False, "recibo sem selo (%s ausente)" % " / ".join(CHAVES_SELO)
    payload = payload_do_recibo(rec, chave)
    recomputado = hashlib.sha3_256(canon(payload).encode()).hexdigest()
    if rec[chave] != recomputado:
        return False, "selo %s nao bate" % chave
    return True, "selo integro (%s)" % chave


def carregar_nucleo():
    from zyql_quantum_gate import ZYQLQuantumGate, adaptive_margin  # noqa: E402
    return ZYQLQuantumGate, adaptive_margin


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


def testar_regras(dados, gate_cls):
    """Regras de decisão em p0 sintético (SPEC §3).

    O simulador ideal só produz p0 = 0 ou 1, então a zona cinzenta e o limiar
    inferior nunca aparecem pelos casos dourados. Aqui a regra é exercitada
    direto na função de decisão do núcleo, sem inventar portão paralelo.
    """
    resultados = []
    for caso in dados.get("regras", []):
        f = ORACULOS[caso["oraculo"]]
        g = gate_cls(caso["n"], f)
        r = g._trivalent(caso["p0"], caso["shots"], margin=caso["banda"])
        veredito = str(r.get("decision"))
        motivo = r.get("refusal_reason")
        ok = veredito == caso["esperado"]["verdict"] and motivo == caso["esperado"]["refusal_reason"]
        resultados.append({"id": caso["id"], "ok": ok, "veredito": veredito,
                           "motivo": motivo, "p0": caso["p0"]})
    return resultados


def testar_porta_dispositivo():
    """A recusa por decoerência dispara e NÃO gasta oráculo (SPEC §6).

    O dublê substitui a medição GHZ por um dispositivo inconfiável declarado:
    o que se testa aqui é o caminho de recusa do runtime, não a física.
    """
    import zyql_runtime

    original = zyql_runtime.ghz_integrity
    resultados = []
    try:
        zyql_runtime.ghz_integrity = lambda **kw: {
            "fidelity_ghz": 0.4210, "threshold": 0.80,
            "device_trusted": False, "mode": "GHZ_INTEGRITY_GATE"}
        d = zyql_runtime.decide(ORACULOS["const1"], n=3, shots=256,
                                require_device_trust=True, device_shots=256)
        motivo = str(d.refusal_reason) if getattr(d, "refusal_reason", None) else str(d.mode)
        ok = d.verdict.name == "REFUSED" and "DECOHERED" in (motivo + str(d.mode)).upper() \
            and d.oracle_calls == 0
        resultados.append({"id": "porta-dispositivo: recusa sem oraculo", "ok": ok,
                           "detalhe": "%s, oraculo=%d" % (d.verdict.name, d.oracle_calls)})
    except Exception as e:
        resultados.append({"id": "porta-dispositivo", "ok": False, "detalhe": str(e)[:80]})
    finally:
        zyql_runtime.ghz_integrity = original
    return resultados


def testar_determinismo(dados, gate_cls):
    d = dados["determinismo"]
    f = ORACULOS[d["oraculo"]]
    vereditos = []
    for _ in range(d["repeticoes"]):
        g = gate_cls(d["n"], f)
        r = g.run_quantum(shots=d["shots"], epsilon=d["epsilon"], family=d["family"])
        vereditos.append(str(r.get("decision")))
    return {"id": d["id"], "ok": len(set(vereditos)) == 1, "vereditos": vereditos}


def testar_bandas(dados, adaptive_margin):
    resultados = []
    for caso in dados["banda"]:
        got = adaptive_margin(caso["epsilon"], caso["shots"])
        ok = abs(got - caso["esperado"]) < 1e-8
        resultados.append({"id": "banda eps=%s shots=%s" % (caso["epsilon"], caso["shots"]),
                           "ok": ok, "obtido": round(got, 10), "esperado": caso["esperado"]})
    return resultados


def recibos_do_repositorio():
    """Todo recibo do repositório, inclusive fora de experiments/."""
    padroes = [
        "experiments/**/*_receipt.json",
        "examples/recibos/*.json",
        "*_receipt.json",
    ]
    achados = []
    for padrao in padroes:
        achados.extend(glob.glob(os.path.join(RAIZ, padrao), recursive=True))
    return sorted(set(achados))


def testar_recibos():
    resultados = []
    for p in recibos_do_repositorio():
        nome = os.path.relpath(p, RAIZ)
        try:
            rec = json.load(open(p, encoding="utf-8"))
        except Exception as e:
            resultados.append({"id": nome, "ok": False, "detalhe": "json invalido: %s" % str(e)[:50]})
            continue
        if not isinstance(rec, dict):
            resultados.append({"id": nome, "ok": False, "detalhe": "recibo nao e objeto json"})
            continue
        ok, detalhe = selo_valido(rec)
        resultados.append({"id": nome, "ok": ok, "detalhe": detalhe})
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
    return [{"id": "openqasm3", "ok": bool(com_qasm3), "arquivos": com_qasm3,
             "detalhe": "%d artefato(s) com qasm3" % len(com_qasm3)}]


def main():
    json_out = "--json" in sys.argv
    try:
        dados = json.load(open(SPEC, encoding="utf-8"))
        gate_cls, adaptive_margin = carregar_nucleo()
    except Exception as e:
        print("erro ao carregar spec ou nucleo: %s" % e, file=sys.stderr)
        return 2

    grupos = {
        "vereditos": testar_casos(dados, gate_cls),
        "regras": testar_regras(dados, gate_cls),
        "porta_dispositivo": testar_porta_dispositivo(),
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
                motivo = " (%s)" % i["motivo"] if i.get("motivo") else ""
                print("  [%s] %s %s%s" % (marca, i["id"], extra, motivo))
        print("\n%s — %d/%d" % ("CONFORMANTE" if not falhas else "NAO CONFORMANTE",
                                len(itens) - len(falhas), len(itens)))

    return 0 if not falhas else 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Executa o protocolo selado de validação da semântica trivalente do ZYQL.

Ordem obrigatória: confere o selo do protocolo ANTES de executar qualquer caso.
Se o texto do protocolo mudou desde a selagem, aborta com código 2.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import pathlib
import platform
import sys
import tempfile

RAIZ = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

import zyclotron_service  # noqa: E402

PROTOCOLO = RAIZ / "validacao/PROTOCOLO.md"
SELO = RAIZ / "validacao/protocolo.sha3"
SAIDA = RAIZ / "validacao/resultado.json"

SHOTS = (64, 128, 512, 2048)
DELTAS = (0.01, 0.05, 0.2)
LIMIARES = tuple(round(0.1 * i, 2) for i in range(1, 10))

BP = {"name": "auditor-trivalente", "purpose": "decidir com recibo",
      "evidence": ["contagens"], "constraints": ["local"], "capabilities": ["decidir"]}


def canon(v) -> str:
    return json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def conferir_selo() -> str:
    atual = hashlib.sha3_256(PROTOCOLO.read_bytes()).hexdigest()
    esperado = SELO.read_text(encoding="utf-8").strip()
    if atual != esperado:
        print("PROTOCOLO ALTERADO APOS A SELAGEM", file=sys.stderr)
        print(f"  selado:  {esperado}\n  atual:   {atual}", file=sys.stderr)
        raise SystemExit(2)
    return atual


def carregar_app():
    """Emite o aplicativo e o importa. O objeto medido é o código emitido."""
    codigo, res = zyclotron_service.emit_service(BP)
    assert res.decision == "1", "blueprint reprovado"
    destino = pathlib.Path(tempfile.mkdtemp()) / "app_emitido.py"
    destino.write_text(codigo, encoding="utf-8")
    spec = importlib.util.spec_from_file_location("app_emitido", destino)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    selo = conferir_selo()
    mod = carregar_app()

    viol = {h: [] for h in ("H1", "H2", "H3", "H4", "H5", "H6", "H7")}
    vereditos = {"1": 0, "0": 0, "INCONCLUSIVE": 0, "REFUSED": 0}
    eps_vistos = []
    casos = 0
    hashes = []

    # --- H1 a H4: grade fatorial declarada no protocolo ---
    for shots in SHOTS:
        passo = max(1, shots // 32)
        for delta in DELTAS:
            for limiar in LIMIARES:
                for k in range(0, shots + 1, passo):
                    payload = {"counts": {"000": k}, "shots": shots,
                               "delta": delta, "threshold": limiar}
                    rec, v = mod.decidir(payload)
                    casos += 1
                    vereditos[v] = vereditos.get(v, 0) + 1
                    p = k / shots
                    eps = math.sqrt(math.log(2 / delta) / (2 * shots))
                    eps_vistos.append(eps)
                    hashes.append(rec["receipt_hash"])
                    if v == "1" and not (p - eps > limiar):
                        viol["H1"].append({"shots": shots, "delta": delta, "limiar": limiar, "k": k})
                    if v == "0" and not (p + eps < limiar):
                        viol["H2"].append({"shots": shots, "delta": delta, "limiar": limiar, "k": k})
                    if abs(p - limiar) > eps and v not in ("1", "0"):
                        viol["H3"].append({"shots": shots, "delta": delta, "limiar": limiar, "k": k, "v": v})
                    if v == "INCONCLUSIVE" and abs(p - limiar) > eps:
                        viol["H4"].append({"shots": shots, "delta": delta, "limiar": limiar, "k": k})

    # --- H5: contrato fechado ---
    contrato = [
        {"counts": {"000": 300}, "shots": 512, "delta": 0.05, "threshold": t}
        for t in (-1.0, 0.0, 1.0, 1.5, float("nan"), "abc", "")
    ] + [
        {"counts": {"000": 300}, "shots": 512, "delta": dx, "threshold": 0.5}
        for dx in (0.0, 1.0, -0.1, 2.0, "x", float("nan"))
    ] + [
        {"counts": {"000": 0}, "shots": s, "delta": 0.05, "threshold": 0.5}
        for s in (0, -5)
    ]
    for payload in contrato:
        rec, v = mod.decidir(payload)
        casos += 1
        if v != "REFUSED":
            viol["H5"].append({"payload": {k: str(x) for k, x in payload.items()}, "v": v,
                               "reason": rec.get("reason")})

    # --- H6: monotonicidade e escala de eps ---
    eps_por_shots = {s: math.sqrt(math.log(2 / 0.05) / (2 * s)) for s in SHOTS}
    ordem = [eps_por_shots[s] for s in SHOTS]
    if not all(ordem[i] > ordem[i + 1] for i in range(len(ordem) - 1)):
        viol["H6"].append({"motivo": "eps nao decresce com shots", "eps": eps_por_shots})
    for grande, pequeno, fator in ((512, 64, 8), (2048, 512, 4)):
        razao = eps_por_shots[pequeno] / eps_por_shots[grande]
        teorica = math.sqrt(fator)
        if abs(razao - teorica) > 0.01 * teorica:
            viol["H6"].append({"motivo": "escala nao e 1/sqrt(shots)",
                               "razao": razao, "teorica": teorica})

    # --- H7: determinismo e cobertura do limiar no recibo ---
    base = {"counts": {"000": 498}, "shots": 512, "delta": 0.05, "threshold": 0.5}
    primeiro = mod.decidir(base)[0]["receipt_hash"]
    for _ in range(49):
        if mod.decidir(dict(base))[0]["receipt_hash"] != primeiro:
            viol["H7"].append({"motivo": "mesmo payload gerou hash diferente"}); break
    h40 = mod.decidir(dict(base, threshold=0.4))[0]["receipt_hash"]
    if h40 == primeiro:
        viol["H7"].append({"motivo": "limiar nao entra no hash do recibo"})
    casos += 51

    resultado = {
        "protocolo_sha3_256": selo,
        "executado_em": __import__("datetime").datetime.now(
            __import__("datetime").timezone.utc).isoformat(timespec="seconds"),
        "ambiente": {"python": platform.python_version(), "plataforma": platform.system()},
        "objeto": "funcao decidir() do app emitido por zyclotron_service.emit_service",
        "regra": "proporcao-v1 (intervalo de Hoeffding)",
        "casos_executados": casos,
        "distribuicao_vereditos": vereditos,
        "eps_min": round(min(eps_vistos), 6),
        "eps_max": round(max(eps_vistos), 6),
        "hashes_distintos": len(set(hashes)),
        "hipoteses": {h: {"casos_verificados": casos if h != "H6" else len(SHOTS),
                          "violacoes": len(v), "exemplos": v[:5],
                          "status": "SUPORTADA" if not v else "REFUTADA"}
                      for h, v in viol.items()},
        "limitacoes": [
            "dominio finito e discreto: ausencia de contraexemplo nao e prova universal",
            "uma execucao por configuracao, sem estudo estatistico",
            "sem assinatura: o recibo prova integridade, nao autoria (marco 03)",
        ],
    }
    corpo = {k: v for k, v in resultado.items()}
    resultado["receipt_hash_agregado"] = hashlib.sha3_256(canon(corpo).encode()).hexdigest()
    SAIDA.write_text(json.dumps(resultado, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"protocolo selado conferido: {selo[:16]}…")
    print(f"casos: {casos} | vereditos: {vereditos}")
    print(f"eps: {resultado['eps_min']} a {resultado['eps_max']} | hashes distintos: {resultado['hashes_distintos']}")
    for h, d in resultado["hipoteses"].items():
        print(f"  {h}: {d['status']:10s} violacoes={d['violacoes']}")
    print(f"recibo agregado: {resultado['receipt_hash_agregado']}")
    refutadas = [h for h, d in resultado["hipoteses"].items() if d["status"] == "REFUTADA"]
    return 1 if refutadas else 0


if __name__ == "__main__":
    raise SystemExit(main())

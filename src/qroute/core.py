"""Pipeline Q-ROUTE: avaliacao classica -> busca de Grover -> veredito trivalente -> recibo.

Semantica do veredito (a mesma do nucleo ZYQL, aplicada a rotas):
  1        rota aprovada: existe rota viavel E a evidencia dos trechos esta completa
  0        rejeitado: nenhuma rota viavel, e todas as exclusoes se apoiam em dado medido
  REFUSED  evidencia insuficiente: ha rota candidata sem evidencia que poderia mudar a decisao
"""
import os

from . import graph, grover, receipt

LIMIAR_GROVER = 0.5
NOTA_COMPARACAO = ("comparacao algoritmica de chamadas ao oraculo; nao e ganho de tempo "
                   "medido, nao ha execucao em hardware nesta rodada")


def _incertas(rotas, budget):
    """Rotas que poderiam ser aprovadas se o trecho sem evidencia fosse medido."""
    return [r for r in rotas
            if r["evidencia_ausente"] and not r["bloqueada"] and r["custo"] <= budget and not r["valida"]]


def decide(mapa, budget, risk_max, iteracoes=None):
    rotas = graph.avalia(mapa, budget, risk_max)
    viaveis = [r for r in rotas if r["valida"]]
    melhor = graph.melhor(rotas)
    g = grover.amplitude_calls(len(rotas), [r["id"] for r in viaveis], iteracoes)
    incertas = _incertas(rotas, budget)
    incertas_relevantes = [r for r in incertas if melhor is None or r["custo"] < melhor["custo"]]

    if incertas_relevantes:
        veredito, razao = "REFUSED", "rota mais barata (%s, R$ %d) tem trecho sem evidencia" % (
            incertas_relevantes[0]["trecho"], incertas_relevantes[0]["custo"])
    elif viaveis and g["p_sucesso"] >= LIMIAR_GROVER:
        veredito = "1"
        razao = "melhor rota %s com evidencia completa; Grover amplificou as %d rotas viaveis" % (
            melhor["trecho"], g["M"])
    elif not viaveis and incertas:
        veredito, razao = "REFUSED", "nenhuma rota viavel e ha trecho sem evidencia"
    else:
        veredito, razao = "0", "nenhuma rota satisfaz as restricoes com dado medido"

    return {
        "mapa": mapa.get("nome", "?"),
        "origem": mapa["origem"], "destino": mapa["destino"],
        "restricoes": {"orcamento": budget, "risco_max": risk_max},
        "rotas_candidatas": len(rotas),
        "rotas": rotas,
        "viaveis": [r["id"] for r in viaveis],
        "melhor_rota": melhor,
        "grover": g,
        "incertas": [r["trecho"] for r in incertas],
        "veredito": veredito,
        "razao": razao,
        "nota_comparacao": NOTA_COMPARACAO,
    }


def executa(mapa_path, budget=None, risk_max=None, iteracoes=None, seal_path=None, silencioso=False,
            hardware=False, backend=None, dry=False, shots=1024):
    mapa = graph.load(mapa_path)
    rest = mapa.get("restricoes", {})
    budget = rest.get("orcamento", 120) if budget is None else budget
    risk_max = rest.get("risco_max", 0.35) if risk_max is None else risk_max
    r = decide(mapa, budget, risk_max, iteracoes)
    r["fonte_mapa"] = os.path.basename(mapa_path)
    if hardware or dry:
        from . import hardware as _hw
        g = r["grover"]
        marcados = [m for m in r["viaveis"]]
        res = (_hw.dry_run(g["n_qubits"], marcados, g["iteracoes"], shots) if dry
               else _hw.executa(g["n_qubits"], marcados, g["iteracoes"], shots, backend))
        r["hardware"] = res
        confirmado = res["ic95"][0] > 0.5
        r["confirmacao_hardware"] = "confirmado" if confirmado else "refutado"
        if not confirmado and r["veredito"] == "1":
            r["veredito"] = "REFUSED"
            r["razao"] = "hardware nao confirmou a amplificacao (IC95 inferior %.3f <= 0.5)" % res["ic95"][0]
        if not silencioso:
            print("hw      : %s | p_medido=%.4f IC95=[%.3f, %.3f] | shots=%d | profundidade=%d | job=%s" % (
                res["modo"], res["p_medido"], res["ic95"][0], res["ic95"][1], res["shots"],
                res["profundidade_transpilada"], res["job_id"]))
            print("veredito: %s (%s)" % (r["veredito"], r["razao"]))
    if not silencioso:
        g, m = r["grover"], r["melhor_rota"]
        print("Q-ROUTE | mapa: %s | candidatas: %d | qubits: %d" % (r["fonte_mapa"], r["rotas_candidatas"], g["n_qubits"]))
        print("classico: %d rotas enumeradas | melhor: %s | custo R$ %d | risco max %.2f" % (
            r["rotas_candidatas"], m["trecho"] if m else "—", m["custo"] if m else 0, m["risco"] if m else 0))
        print("grover  : N=%d | marcadas=%d | iteracoes=%d | p_sucesso=%.4f | oraculo: classico %d vs grover %d" % (
            g["N"], g["M"], g["iteracoes"], g["p_sucesso"], g["chamadas_classicas"], g["chamadas_grover"]))
        print("veredito: %s (%s)" % (r["veredito"], r["razao"]))
    if seal_path:
        anterior = receipt.le_anterior(seal_path)
        corpo = {"spec": "Q-ROUTE/v1", "modulo": "src/qroute (ZYQL 2.2.0)",
                 "modo": ("HARDWARE IBM QUANTUM" if hardware else
                          "ENSAIO EM BACKEND FALSO (nao e QPU)" if dry else
                          "SIMULACAO EXATA EM VETOR DE ESTADO — sem hardware, sem shots"),
                 "entrada": r, "nota": NOTA_COMPARACAO}
        rec = receipt.sela(corpo, seal_path, anterior)
        r["recibo"] = {"arquivo": seal_path, "sha3_256": rec["sha3_256"], "prev_sha3": anterior}
        if not silencioso:
            print("recibo  : %s selo=%s%s" % (seal_path, rec["sha3_256"][:32] + "…",
                                              " prev=" + anterior[:16] + "…" if anterior else " (primeiro)"))
    return r

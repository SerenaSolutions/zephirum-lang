"""Mapa de rotas: enumeracao de caminhos simples e avaliacao classica de restricoes.

Sem heuristica escondida: todas as rotas simples origem->destino sao enumeradas.
O classico e a referencia honesta contra a qual o quantico e comparado."""
import json


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _adj(mapa):
    adj = {}
    for e in mapa["arestas"]:
        adj.setdefault(e["de"], []).append(e)
    return adj


def candidatas(mapa):
    """Todas as rotas simples entre origem e destino (sem repetir no)."""
    adj, out = _adj(mapa), []

    def dfs(no, caminho, visitados):
        if no == mapa["destino"]:
            out.append(list(caminho))
            return
        for e in adj.get(no, []):
            if e["para"] in visitados:
                continue
            visitados.add(e["para"])
            caminho.append(e)
            dfs(e["para"], caminho, visitados)
            caminho.pop()
            visitados.discard(e["para"])

    dfs(mapa["origem"], [], {mapa["origem"]})
    return out


def resumo(rota):
    custo = sum(e["custo"] for e in rota)
    risco = max(e["risco"] for e in rota)
    evid = sorted({e.get("evidencia", "ausente") for e in rota})
    return {
        "trecho": "→".join([rota[0]["de"]] + [e["para"] for e in rota]),
        "custo": custo,
        "risco": round(risco, 4),
        "bloqueada": any(e.get("status") == "bloqueada" for e in rota),
        "evidencia": evid,
        "evidencia_ausente": "ausente" in evid,
    }


def avalia(mapa, budget, risk_max):
    """Aplica as restricoes declaradas e devolve todas as rotas com o motivo de cada exclusao."""
    rotas = []
    for i, r in enumerate(candidatas(mapa)):
        s = resumo(r)
        s["id"] = i
        motivos = []
        if s["bloqueada"]:
            motivos.append("trecho bloqueado")
        if s["risco"] > risk_max:
            motivos.append("risco %.2f > limite %.2f" % (s["risco"], risk_max))
        if s["custo"] > budget:
            motivos.append("custo %d > orcamento %d" % (s["custo"], budget))
        s["motivos"] = motivos
        s["valida"] = not motivos
        rotas.append(s)
    return rotas


def melhor(rotas):
    """Rota valida de menor custo; empate resolvido por menor risco."""
    v = [r for r in rotas if r["valida"]]
    return min(v, key=lambda r: (r["custo"], r["risco"])) if v else None

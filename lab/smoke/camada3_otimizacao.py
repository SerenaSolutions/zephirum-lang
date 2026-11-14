# SPDX-License-Identifier: Apache-2.0
"""Camada 3: orquestracao com estado, busca hibrida e cache."""
import json, sys

def main():
    from langgraph.graph import END, StateGraph
    from typing import TypedDict

    class Estado(TypedDict):
        pergunta: str
        veredito: int

    def decidir(e):
        return {"veredito": 1 if "recibo" in e["pergunta"] else 2}

    g = StateGraph(Estado)
    g.add_node("decidir", decidir)
    g.set_entry_point("decidir")
    g.add_edge("decidir", END)
    app = g.compile()
    r = app.invoke({"pergunta": "existe recibo?", "veredito": 0})

    cache = {}
    def com_cache(chave, fn):
        if chave not in cache:
            cache[chave] = fn(chave)
        return cache[chave]

    hibrida = {"lexical": 0.62, "denso": 0.71}
    final = 0.5 * hibrida["lexical"] + 0.5 * hibrida["denso"]
    print(json.dumps({"camada": 3, "ok": r["veredito"] == 1 and len(cache) <= 1,
                      "grafo": r, "hibrida": round(final, 3),
                      "cache_hits": com_cache("k", lambda k: 1) == com_cache("k", lambda k: 2)}))
    return 0

if __name__ == "__main__":
    sys.exit(main())

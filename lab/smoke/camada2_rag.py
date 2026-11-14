# SPDX-License-Identifier: Apache-2.0
"""Camada 2: chunking, embeddings, banco vetorial, saida estruturada."""
import json, sys

def chunkar(texto, n=120):
    return [texto[i:i+n] for i in range(0, len(texto), n)] or [""]

def main():
    from pydantic import BaseModel
    from rank_bm25 import BM25Okapi
    import chromadb

    class Achado(BaseModel):
        veredito: int
        motivo: str | None = None

    docs = chunkar("ZYQL decide antes de executar. Recibo prova. Portao recusa sem evidencia. " * 6)
    bm25 = BM25Okapi([d.lower().split() for d in docs])
    lexical = float(max(bm25.get_scores("recibo prova".lower().split())))

    cli = chromadb.Client()
    col = cli.get_or_create_collection("zyql_lab")
    col.add(ids=[f"d{i}" for i in range(len(docs))], documents=docs)
    denso = col.count()

    a = Achado(veredito=1, motivo=None)
    print(json.dumps({"camada": 2, "ok": denso == len(docs) and lexical > 0,
                      "chunks": len(docs), "lexical": round(lexical, 3),
                      "vetorial": denso, "estruturado": a.model_dump()}))
    return 0

if __name__ == "__main__":
    sys.exit(main())

"""Assina e encadeia os recibos do WORLD-3 com ML-DSA-44.

Demonstracao da camada Z-SIG. AVISO: a chave privada e efemera, gerada nesta
execucao e NAO e gravada. Em producao ela vive em HSM ou secret manager; aqui
interessa provar o mecanismo, nao a proveniencia historica.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
import zqea_sig as sig  # noqa: E402

BASE = pathlib.Path(__file__).resolve().parents[1] / "experiments" / "world_scale_20261029"


def main():
    recibos = [json.load(open(BASE / f"w3_rep{i}.json", encoding="utf-8")) for i in (1, 2, 3)]
    pk, sk = sig.keypair()
    encadeados = sig.cadeia(recibos, sk, pk)
    ok, motivo = sig.verificar_cadeia(encadeados, pk)

    saida = {
        "spec": sig.SPEC,
        "algoritmo": sig.ALG,
        "chave_publica_b64": __import__("base64").b64encode(pk).decode(),
        "chave_id": sig.key_id(pk),
        "aviso": "chave efemera de demonstracao; nao grava a chave privada",
        "verificacao": {"ok": ok, "motivo": motivo},
        "recibos": encadeados,
    }
    destino = BASE / "recibos_assinados.json"
    json.dump(saida, open(destino, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"cadeia de {len(encadeados)} recibos assinada | {sig.ALG}")
    print("chave_id:", saida["chave_id"], "| verificacao:", ok, "-", motivo)
    print("arquivo:", destino.relative_to(BASE.parents[1]))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

"""Sela em SHA3-256 o prompt e a resposta de uma inferencia local.

Grava recibo JSON com os hashes, o commit, o run e o custo (zero de API).
Nao assina: chave privada ML-DSA-44 nao vive em CI.
"""
import hashlib, json, os, sys


def sha3(path):
    h = hashlib.sha3_256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    prompt, resposta, saida = sys.argv[1], sys.argv[2], sys.argv[3]
    rec = {
        "tipo": "recibo-integridade-sha3",
        "modelo": os.environ.get("MODELO", "desconhecido"),
        "custo_api": "0 (inferencia local)",
        "sha3_256_prompt": sha3(prompt),
        "sha3_256_resposta": sha3(resposta),
        "commit": os.environ.get("GITHUB_SHA", ""),
        "run_id": os.environ.get("GITHUB_RUN_ID", ""),
        "assinatura": "ausente (ML-DSA-44 exige chave fora do CI)",
    }
    with open(saida, "w", encoding="utf-8") as f:
        json.dump(rec, f, indent=2, ensure_ascii=False)
    print(json.dumps(rec, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

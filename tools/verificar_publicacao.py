"""Verifica se o que publicamos e o que declaramos batem entre si.

Motivo: revisar de memoria ja gerou erro (comentario duplicado no PR,
numero de submissao tido como errado sem conferir, afirmacao de que o
e-mail nao chegou). Este script e a regra: numero so entra em relatorio
depois de conferido por chamada real.

Uso:  python tools/verificar_publicacao.py [--offline]
Saida: 0 se tudo confere, 1 se algo divergir.
"""
import json
import pathlib
import sys
import tomllib
import urllib.error
import urllib.request

RAIZ = pathlib.Path(__file__).resolve().parents[1]
OFFLINE = "--offline" in sys.argv

DOIS = "https://api.datacite.org/dois/10.5281/zenodo.23632019"
PYPI = "https://pypi.org/pypi/zephirum/json"


def get(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": "zephirum-verify/1"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read()


def main():
    falhas = []

    projeto = tomllib.load(open(RAIZ / "pyproject.toml", "rb"))["project"]
    versao_local = projeto["version"]
    print(f"versao no pyproject : {versao_local}")

    if OFFLINE:
        print("modo offline: pulando checagens de rede")
        return 0

    # 1. o pacote publicado tem a mesma versao do pyproject?
    try:
        _, corpo = get(PYPI)
        info = json.loads(corpo)["info"]
        if info["version"] != versao_local:
            falhas.append(f"PyPI em {info['version']} != pyproject {versao_local}")
        print(f"versao no PyPI      : {info['version']}")
    except Exception as e:
        falhas.append(f"PyPI inacessivel: {type(e).__name__}")

    # 2. o DOI citado e nosso? (titulo com ZEPHIRUM)
    try:
        _, corpo = get(DOIS)
        d = json.loads(corpo)["data"]["attributes"]
        titulo = (d.get("titles") or [{}])[0].get("title", "")
        if "ZEPHIRUM" not in titulo.upper():
            falhas.append(f"DOI nao aponta para ZEPHIRUM: {titulo[:60]}")
        print(f"DOI                 : {titulo[:60]}")
    except Exception as e:
        falhas.append(f"DOI inacessivel: {type(e).__name__}")

    # 3. numeros do WORLD-3 batem com os recibos selados?
    base = RAIZ / "experiments" / "world_scale_20261029"
    try:
        recs = [json.load(open(base / f"w3_rep{i}.json", encoding="utf-8")) for i in (1, 2, 3)]
        cert = json.load(open(base / "w3_analise_ic.json", encoding="utf-8"))
        v02 = [r["execucao"]["repeticoes"][0]["metricas"]["W-02"]["visibilidade"] for r in recs]
        media = round(sum(v02) / len(v02), 3)
        citado = cert["resultado"]["W-02"]["media"]
        if abs(media - citado) > 0.001:
            falhas.append(f"W-02 media nos recibos {media} != {citado} no documento de analise")
        print(f"W-02 visibilidade   : recibos {media} | analise {citado}")
    except Exception as e:
        falhas.append(f"recibos do WORLD-3 ilegiveis: {type(e).__name__}")

    # 4. links citados em site e docs respondem?
    for url in ("https://serenasolutions.github.io/zephirum-lang/",
                "https://pypi.org/project/zephirum/"):
        try:
            st, _ = get(url, timeout=20)
            print(f"link {url[:48]:<48} {st}")
        except Exception as e:
            falhas.append(f"link quebrado {url}: {type(e).__name__}")

    print()
    if falhas:
        print("DIVERGENCIAS:")
        for f in falhas:
            print("  -", f)
        return 1
    print("TUDO CONFERE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

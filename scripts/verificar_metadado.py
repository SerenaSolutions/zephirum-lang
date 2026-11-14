#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Guard de metadado do ecossistema Qiskit.

Tres fontes descrevem o mesmo pacote e nenhuma delas obedece a outra:

  pyproject.toml                                  -> o que o fonte declara
  PyPI /pypi/zephirum/json                        -> o que o artefato publicado diz
  Qiskit/ecosystem resources/members/...          -> o que o bot do ecossistema escreveu

O bot le PyPI e reescreve o arquivo de membro sem nos consultar. Divergencia de
licenca em lista curada por terceiro nao e detalhe: e erro nosso exibido na vitrine
deles, e o conserto nao esta na nossa mao.

Regra de severidade:
  FALHA  licenca divergente; versao do arquivo de membro diferente da do PyPI;
         mesma versao com requires-python diferente; repositorio atras do PyPI.
  ALERTA fonte a frente do PyPI (release em preparo) ou requires-python
         divergente entre versoes distintas, que so se resolve publicando.
"""
from __future__ import annotations

import json
import pathlib
import sys
import urllib.request

try:  # tomllib so existe a partir do 3.11
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - caminho do 3.10
    tomllib = None

RAIZ = pathlib.Path(__file__).resolve().parents[1]
ECOSSISTEMA = ("https://raw.githubusercontent.com/Qiskit/ecosystem/main/"
               "resources/members/zephirum_b2b5fe46.toml")
PYPI = "https://pypi.org/pypi/zephirum/json"

ALIAS = {
    "apache 2.0": "Apache-2.0", "apache-2.0": "Apache-2.0", "apache 2": "Apache-2.0",
    "apache license 2.0": "Apache-2.0", "asl 2.0": "Apache-2.0",
    "mit": "MIT", "mit license": "MIT", "expat": "MIT",
}


def normalizar_licenca(valor) -> str | None:
    if valor is None:
        return None
    texto = str(valor).strip()
    if not texto or texto.lower() in ("none", "unknown", ""):
        return None
    return ALIAS.get(texto.lower(), texto)


def _buscar(url: str, tentativas: int = 3) -> bytes:
    ultimo = None
    for _ in range(tentativas):
        try:
            with urllib.request.urlopen(url, timeout=20) as r:
                return r.read()
        except Exception as e:  # noqa: BLE001 rede pode falhar de varias formas
            ultimo = e
    raise RuntimeError(f"fonte inacessivel: {url} ({ultimo})")


def _exige_tomllib() -> None:
    if tomllib is None:
        raise RuntimeError("tomllib exige Python 3.11+; o guard roda no job de 3.12")


def coletar_pyproject(caminho: pathlib.Path | None = None) -> dict:
    _exige_tomllib()
    dados = tomllib.loads((caminho or RAIZ / "pyproject.toml").read_text(encoding="utf-8"))
    projeto = dados["project"]
    licenca = projeto.get("license")
    if isinstance(licenca, dict):
        licenca = licenca.get("text") or licenca.get("file")
    return {"fonte": "pyproject", "version": projeto.get("version"),
            "license": normalizar_licenca(licenca),
            "requires_python": projeto.get("requires-python")}


def coletar_pypi(texto: bytes) -> dict:
    info = json.loads(texto)["info"]
    return {"fonte": "pypi", "version": info.get("version"),
            "license": normalizar_licenca(info.get("license_expression") or info.get("license")),
            "requires_python": info.get("requires_python")}


def coletar_ecossistema(texto: bytes) -> list[dict]:
    _exige_tomllib()
    dados = tomllib.loads(texto.decode("utf-8"))
    secoes = dados.get("pypi", [])
    if isinstance(secoes, dict):
        secoes = [secoes]
    return [{"fonte": f"ecossistema[{i}]", "version": s.get("version"),
             "license": normalizar_licenca(s.get("license")),
             "requires_python": s.get("requires_python")}
            for i, s in enumerate(secoes)]


def comparar(pyproject: dict, pypi: dict, membros: list[dict]) -> list[dict]:
    achados: list[dict] = []
    fontes = [pyproject, pypi, *membros]

    # 1. licenca: tem de ser uma so em todas as fontes que a declaram
    declaradas = {f["license"] for f in fontes if f["license"]}
    if len(declaradas) > 1:
        achados.append({"nivel": "FALHA", "campo": "license",
                        "detalhe": "; ".join(f"{f['fonte']}={f['license'] or '-'}" for f in fontes)})

    # 2. versao do arquivo de membro tem de seguir o PyPI, porque o bot copia de la
    for m in membros:
        if m["version"] != pypi["version"]:
            achados.append({"nivel": "FALHA", "campo": "version",
                            "detalhe": f"{m['fonte']}={m['version']} mas pypi={pypi['version']}"})

    # 3. repositorio contra o artefato publicado
    if pyproject["version"] == pypi["version"]:
        if pyproject["requires_python"] != pypi["requires_python"]:
            achados.append({"nivel": "FALHA", "campo": "requires-python",
                            "detalhe": (f"mesma versao {pyproject['version']} declara "
                                        f"pyproject={pyproject['requires_python']} e "
                                        f"pypi={pypi['requires_python']}: um dos dois mente "
                                        f"sobre onde o pacote instala")})
    else:
        try:
            atras = _versao(pyproject["version"]) < _versao(pypi["version"])
        except ValueError:
            atras = False
        achados.append({
            "nivel": "FALHA" if atras else "ALERTA", "campo": "version",
            "detalhe": (f"pyproject={pyproject['version']} vs pypi={pypi['version']}"
                        + (" (repositorio atras do publicado)" if atras else " (release em preparo)"))})
        if pyproject["requires_python"] != pypi["requires_python"]:
            achados.append({"nivel": "ALERTA", "campo": "requires-python",
                            "detalhe": (f"pyproject={pyproject['requires_python']} vs "
                                        f"pypi={pypi['requires_python']}: resolve na proxima publicacao")})
    return achados


def _versao(texto: str) -> tuple:
    partes = []
    for pedaco in str(texto).replace("-", ".").split("."):
        partes.append(int(pedaco) if pedaco.isdigit() else 0)
    return tuple(partes)


def main(argv: list[str]) -> int:
    try:
        pyproject = coletar_pyproject()
        pypi = coletar_pypi(_buscar(PYPI))
        membros = coletar_ecossistema(_buscar(ECOSSISTEMA))
    except Exception as e:  # noqa: BLE001
        print(f"::error::guard de metadado nao conseguiu ler as fontes: {e}")
        return 2

    print(f"pyproject   : {pyproject['version']} | {pyproject['license']} | {pyproject['requires_python']}")
    print(f"pypi        : {pypi['version']} | {pypi['license']} | {pypi['requires_python']}")
    for m in membros:
        print(f"{m['fonte']:12s}: {m['version']} | {m['license']} | {m['requires_python'] or '-'}")

    achados = comparar(pyproject, pypi, membros)
    falhas = [a for a in achados if a["nivel"] == "FALHA"]
    alertas = [a for a in achados if a["nivel"] == "ALERTA"]

    for a in falhas:
        print(f"::error file=pyproject.toml::{a['campo']} divergente — {a['detalhe']}")
    for a in alertas:
        print(f"::warning::({a['campo']}) {a['detalhe']}")
    if not achados:
        print("metadado consistente nas tres fontes")
    return 1 if falhas else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

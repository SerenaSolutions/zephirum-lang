"""Meta-testes de versao: o `pyproject.toml` e a fonte unica, os outros arquivos seguem.

Antes este arquivo fazia `assert` no nivel do modulo e nao declarava nenhuma funcao de
teste. Consequencia: o pytest contava zero testes, a esteira ficava verde sem verificar
nada, e quando a versao divergia o erro abortava a coleta da suite inteira em vez de
apontar um caso.
"""
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def _versao_do_pyproject() -> str:
    texto = (RAIZ / "pyproject.toml").read_text(encoding="utf-8")
    achado = re.search(r'^version\s*=\s*"([^"]+)"', texto, re.MULTILINE)
    assert achado, "pyproject.toml sem campo version"
    return achado.group(1)


def _versao_do_readme() -> str | None:
    texto = (RAIZ / "README.md").read_text(encoding="utf-8")
    achado = re.search(r"badge/version-(\d+\.\d+\.\d+)", texto)
    return achado.group(1) if achado else None


def _versao_do_changelog() -> str | None:
    texto = (RAIZ / "CHANGELOG.md").read_text(encoding="utf-8")
    achado = re.search(r"^##\s*\[([0-9][0-9A-Za-z.\-]*)\]", texto, re.MULTILINE)
    return achado.group(1) if achado else None


def test_versao_do_pyproject_e_semver():
    versao = _versao_do_pyproject()
    assert re.fullmatch(r"\d+\.\d+\.\d+", versao), f"versao fora de MAJOR.MINOR.PATCH: {versao}"


def test_badge_do_readme_acompanha_o_pyproject():
    esperado = _versao_do_pyproject()
    achado = _versao_do_readme()
    assert achado is not None, "README sem badge de versao no formato badge/version-X.Y.Z"
    assert achado == esperado, (
        f"README diz {achado} e pyproject diz {esperado}. "
        f"Rode: python scripts/sync_version.py"
    )


def test_changelog_tem_entrada_da_versao_atual():
    esperado = _versao_do_pyproject()
    achado = _versao_do_changelog()
    assert achado is not None, "CHANGELOG sem cabecalho no formato ## [X.Y.Z]"
    assert achado == esperado, (
        f"CHANGELOG abre em {achado} e pyproject diz {esperado}. "
        f"Rode: python scripts/sync_version.py"
    )

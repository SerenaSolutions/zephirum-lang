"""Uma versao so: pyproject, pacote e metadata nao podem divergir."""
import tomllib
from pathlib import Path

import zephirum

RAIZ = Path(__file__).resolve().parent.parent


def test_versao_do_pacote_igual_ao_pyproject():
    pyproject = tomllib.loads((RAIZ / "pyproject.toml").read_text(encoding="utf-8"))
    assert pyproject["project"]["version"] == zephirum.__version__

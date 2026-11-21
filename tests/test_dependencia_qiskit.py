"""O piso do Qiskit precisa conter as correcoes de seguranca do 2.6.1."""
import re
try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10 nao tem tomllib na stdlib
    import tomli as tomllib
from pathlib import Path

import qiskit

RAIZ = Path(__file__).resolve().parent.parent


def _piso() -> str:
    deps = tomllib.loads((RAIZ / "pyproject.toml").read_text(encoding="utf-8"))["project"]["dependencies"]
    alvo = [d for d in deps if d.startswith("qiskit>=")][0]
    return re.match(r"qiskit>=([0-9.]+)", alvo).group(1)


def _tupla(v: str) -> tuple:
    return tuple(int(x) for x in v.split("."))


def test_piso_do_qiskit_inclui_2_6_1():
    assert _tupla(_piso()) >= (2, 6, 1)


def test_instalado_nao_e_anterior_ao_piso():
    assert _tupla(qiskit.__version__) >= _tupla(_piso())

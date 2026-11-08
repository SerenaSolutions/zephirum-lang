# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Serena Quantum Solutions
"""Executa cada bateria estilo script como subprocesso e exige codigo de saida 0.

Motivo: essas baterias chamam sys.exit no nivel do modulo, o que interrompe a
coleta do pytest (INTERNALERROR / SystemExit). Rodando como subprocesso, elas
continuam valendo como teste e uma falha aparece como falha, nao como crash."""
import pathlib
import subprocess
import sys

import pytest

AQUI = pathlib.Path(__file__).parent
SCRIPTS = sorted(p.name for p in AQUI.glob("test_*.py")
                 if "sys.exit" in p.read_text(encoding="utf-8", errors="ignore")
                 and p.name not in ("test_baterias_script.py",))


@pytest.mark.parametrize("nome", SCRIPTS or ["<nenhum>"])
def test_bateria_script(nome):
    caminho = AQUI / nome
    assert caminho.exists(), f"bateria ausente: {nome}"
    r = subprocess.run([sys.executable, str(caminho)], capture_output=True, text=True, timeout=900)
    saida = (r.stdout or "")[-2000:] + (r.stderr or "")[-1000:]
    assert r.returncode == 0, f"{nome} saiu com {r.returncode}\n{saida}"

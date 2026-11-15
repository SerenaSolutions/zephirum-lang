import pytest
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Serena Quantum Solutions
"""Baterias escritas como script (sys.exit no import) sao excluidas da coleta direta
e executadas como subprocesso por tests/test_baterias_script.py."""
import pathlib

AQUI = pathlib.Path(__file__).parent
SCRIPTS = sorted(p.name for p in AQUI.glob("test_*.py")
                 if "sys.exit" in p.read_text(encoding="utf-8", errors="ignore")
                 and p.name not in ("test_baterias_script.py",))
collect_ignore = list(SCRIPTS)


@pytest.fixture
def sdk_qbraid_falso(monkeypatch):
    """Injeta um modulo `qbraid` minimo para exercitar as guardas de credencial.

    O adaptador recusa cedo com SDK_QBRAID_AUSENTE quando o SDK nao esta instalado.
    Os testes de credencial querem outro caminho (CREDENCIAL_AUSENTE, FALHA_AUTENTICACAO),
    que so e alcancavel depois do import. O falso nunca executa nada: recusa a chave."""
    import sys
    import types

    mod = types.ModuleType("qbraid")

    class QbraidProvider:
        def __init__(self, api_key=None):
            raise RuntimeError("autenticacao recusada (chave de teste)")

    mod.QbraidProvider = QbraidProvider
    monkeypatch.setitem(sys.modules, "qbraid", mod)
    return mod

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

# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Serena Quantum Solutions
"""O verificador independente aceita recibo integro e rejeita adulteracao."""
import json, subprocess, sys, pathlib

RAIZ = pathlib.Path(__file__).resolve().parents[1]
VERIF = RAIZ / "tools" / "zyql_verificar_recibo.py"


def _recibo_de(modulo_call):
    code = (
        "import json,sys; sys.path.insert(0,'src');"
        "from zyql_ten import s04_data_router as m;"
        "print(json.dumps(m.run([{'id':1},{'id':2}],['id'])))"
    )
    out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, cwd=RAIZ)
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout)


def _verificar(payload):
    return subprocess.run([sys.executable, str(VERIF)], input=json.dumps(payload),
                          capture_output=True, text=True)


def test_aceita_recibo_integro():
    r = _verificar(_recibo_de(None))
    assert r.returncode == 0, r.stderr
    assert "ATENDE" in r.stdout


def test_rejeita_saida_adulterada():
    payload = _recibo_de(None)
    payload["novos"] = 99
    r = _verificar(payload)
    assert r.returncode == 1
    assert "REPROVA" in r.stdout

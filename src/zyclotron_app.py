# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Serena Quantum Solutions
"""Zyclotron v0.2 — do manifesto ao app executavel.

Camada 2: recebe um blueprint, compila o manifesto (v0.1, intocado) e EMITE um
app Python autonomo, auditavel, que:
  1. carrega o proprio manifesto embutido e revalida a proveniencia SHA3-256;
  2. recusa (fail-closed) se a proveniencia nao casar;
  3. executa a decisao ZYQL e imprime veredito + recibo.

Nao altera o nucleo ZYQL. Nao inventa interface: entrega o artefato minimo
executavel, que e' o que a camada anterior prometia.
"""
from __future__ import annotations
import hashlib, json, pprint, zyclotron

VERSION = "0.2.0"

TEMPLATE = '''#!/usr/bin/env python3
# App derivado gerado por Zyclotron v0.2 — NAO EDITAR A MAO
import hashlib, json, sys
MANIFEST = {manifest}
MANIFEST_SHA3 = "{manifest_sha3}"

def canonical(v):
    return json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

def verificar():
    h = hashlib.sha3_256(canonical(MANIFEST).encode()).hexdigest()
    return h == MANIFEST_SHA3, h

def main():
    ok, h = verificar()
    if not ok:
        print(json.dumps({"verdict": "REFUSED", "reason": "MANIFEST_TAMPERED",
                           "expected": MANIFEST_SHA3, "got": h}))
        return 2
    print(json.dumps({"verdict": "1", "app": MANIFEST["name"],
                       "purpose": MANIFEST["purpose"],
                       "runtime": MANIFEST["runtime"],
                       "manifest_sha3_256": MANIFEST_SHA3,
                       "blueprint_sha3_256": MANIFEST["provenance"]["blueprint_sha3_256"],
                       "evidence": MANIFEST["provenance"]["evidence"],
                       "constraints": MANIFEST["provenance"]["constraints"]},
                     indent=1, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    sys.exit(main())
'''


def emit_app(blueprint):
    """Compila o manifesto e devolve (codigo_do_app, resultado_zyclotron)."""
    res = zyclotron.compile_derivative_app(blueprint)
    if res.decision != "1" or res.manifest is None:
        return None, res
    manifest = res.manifest
    sha = hashlib.sha3_256(
        json.dumps(manifest, ensure_ascii=False, sort_keys=True,
                   separators=(",", ":")).encode()).hexdigest()
    code = TEMPLATE.replace("{manifest}", pprint.pformat(manifest, sort_dicts=True, width=96))
    code = code.replace("{manifest_sha3}", sha)
    return code, res

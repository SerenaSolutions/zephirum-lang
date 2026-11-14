# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Serena Quantum Solutions
"""CLI do ZQ-GATE: decide antes de executar.
Uso: zqgate verify <receipt.json>   — verifica integridade SHA3-256 de um recibo
     zqgate version
"""
import sys

from zqea_canon import verificar_arquivo

def verify(path):
    res = verificar_arquivo(path)
    print(f"recibo: {path}")
    print(f"campo do selo: {res['campo'] or '(ausente)'}")
    print(f"regra do canon: {res['regra'] or '(nao identificada)'}")
    print(f"selo declarado: {res['declarado']}")
    print(f"selo calculado: {res['calculado']}")
    if res["integro"]:
        print("VEREDITO: 1 (recibo íntegro)")
        return 0
    motivo = "selo ausente" if res["motivo"] == "SEM_SELO" else "selo divergente"
    print(f"VEREDITO: 0 (adulterado — {motivo})")
    return 1

def main():
    if len(sys.argv) >= 3 and sys.argv[1] == "verify":
        sys.exit(verify(sys.argv[2]))
    if len(sys.argv) == 2 and sys.argv[1] == "version":
        from zqgate import __version__
        print("zq-gate", __version__, "— ASK FIRST. PROVE NEXT. COMPUTE LAST.")
        return
    print(__doc__)

if __name__ == "__main__":
    main()

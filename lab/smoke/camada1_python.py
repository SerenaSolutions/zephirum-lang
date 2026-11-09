# SPDX-License-Identifier: Apache-2.0
"""Camada 1 do roteiro: Python como base, sem IA ainda."""
import json, sys

def main():
    dados = {"tokens": 12, "temperatura": 0.2, "contexto": 8192}
    assert dados["temperatura"] <= 1.0
    print(json.dumps({"camada": 1, "ok": True, "base": "python", **dados}))
    return 0

if __name__ == "__main__":
    sys.exit(main())

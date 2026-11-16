"""CLI para a rodada avisar o STARGATE.

Uso:
    python tools/stargate_emitir.py --veredito REFUSED --motivo credencial_invalida
    python tools/stargate_emitir.py --veredito 1 --eliminadas 136130 --executadas 35292 --selo integro
    python tools/stargate_emitir.py --escoar
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# permite rodar como script (python tools/stargate_emitir.py) e como modulo
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.stargate import emitir, escoar_fila, montar_evento


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Emite evento de decisao para o STARGATE")
    p.add_argument("--veredito", choices=["1", "0", "REFUSED"])
    p.add_argument("--eliminadas", type=int, default=0)
    p.add_argument("--executadas", type=int, default=0)
    p.add_argument("--selo", choices=["integro", "rompido"], default="integro")
    p.add_argument("--motivo", default=None, help="motivo da recusa")
    p.add_argument("--segundos", type=float, default=0.0)
    p.add_argument("--url", default=None)
    p.add_argument("--fila", default=None)
    p.add_argument("--escoar", action="store_true", help="reenvia a fila e sai")
    a = p.parse_args(argv)

    if a.escoar:
        print(json.dumps(escoar_fila(a.url, a.fila), ensure_ascii=False))
        return 0
    if not a.veredito:
        p.error("informe --veredito ou --escoar")

    evento = montar_evento(
        a.veredito, eliminadas=a.eliminadas, executadas=a.executadas,
        selo=a.selo, motivo_recusa=a.motivo, segundos=a.segundos,
    )
    resultado = emitir(evento, a.url, a.fila)
    print(json.dumps(resultado, ensure_ascii=False))
    # nunca falha por causa da observabilidade
    return 0


if __name__ == "__main__":
    sys.exit(main())

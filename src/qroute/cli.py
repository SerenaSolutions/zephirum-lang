"""CLI do Q-ROUTE."""
import argparse, json, sys

from . import core, receipt


def main():
    ap = argparse.ArgumentParser(prog="qroute", description="Q-ROUTE — busca e decisao quantica de rotas (ZYQL)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run", help="avalia um mapa e decide")
    r.add_argument("mapa")
    r.add_argument("--budget", type=int, default=None)
    r.add_argument("--risk-max", type=float, default=None)
    r.add_argument("--iteracoes", type=int, default=None)
    r.add_argument("--seal", default=None)
    r.add_argument("--json", action="store_true")
    r.add_argument("--hardware", action="store_true", help="executa na QPU da IBM")
    r.add_argument("--backend", default=None, help="nome do backend IBM")
    r.add_argument("--dry-run", action="store_true", help="ensaio com backend falso (nao e QPU)")
    r.add_argument("--shots", type=int, default=1024)
    v = sub.add_parser("verify", help="verifica a integridade de um recibo")
    v.add_argument("recibo")
    a = ap.parse_args()

    if a.cmd == "run":
        saida = core.executa(a.mapa, a.budget, a.risk_max, a.iteracoes, a.seal, silencioso=a.json,
                             hardware=a.hardware, backend=a.backend, dry=a.dry_run, shots=a.shots)
        if a.json:
            print(json.dumps(saida, ensure_ascii=False, indent=1, default=str))
        return 0
    if a.cmd == "verify":
        res = receipt.verifica(a.recibo)
        print("recibo:", a.recibo)
        print("selo declarado:", res["declarado"])
        print("selo calculado:", res["calculado"])
        print("VEREDITO: 1 (recibo integro)" if res["integro"] else "VEREDITO: 0 (adulterado)")
        return 0 if res["integro"] else 1


if __name__ == "__main__":
    sys.exit(main())

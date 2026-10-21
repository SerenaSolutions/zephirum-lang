"""CLI do ZQ-GATE: decide antes de executar.
Uso: zqgate verify <receipt.json>   — verifica integridade SHA3-256 de um recibo
     zqgate version
"""
import sys, json, hashlib

def canonical(obj): return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))

def verify(path):
    rec = json.load(open(path))
    seal = rec.get("sha3_256")
    canon = {k: v for k, v in rec.items() if k != "sha3_256"}
    calc = hashlib.sha3_256(canonical(canon).encode()).hexdigest()
    ok = (seal == calc)
    print(f"recibo: {path}")
    print(f"selo declarado: {seal}")
    print(f"selo calculado: {calc}")
    print("VEREDITO: 1 (recibo íntegro)" if ok else "VEREDITO: 0 (adulterado)")
    return 0 if ok else 1

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

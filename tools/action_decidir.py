# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Serena Quantum Solutions
"""Decide a proportion from counts and write an auditable receipt."""
import argparse, json, math, hashlib, datetime

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shots", type=int, required=True)
    ap.add_argument("--counts", required=True)
    ap.add_argument("--threshold", type=float, required=True)
    ap.add_argument("--delta", type=float, default=0.05)
    ap.add_argument("--target", default="000")
    ap.add_argument("--receipt", required=True)
    a = ap.parse_args()
    counts = json.loads(a.counts)
    total = sum(counts.values())
    if total != a.shots or a.shots < 1 or any(v < 0 for v in counts.values()):
        rec = {"verdict": "REFUSED", "reason": "CONTRATO_INVALIDO"}
    elif not (0 < a.threshold < 1) or not (0 < a.delta < 1):
        rec = {"verdict": "REFUSED", "reason": "POLITICA_INVALIDA"}
    else:
        p = counts.get(a.target, 0) / a.shots
        eps = math.sqrt(math.log(2 / a.delta) / (2 * a.shots))
        veredito = "1" if p - eps > a.threshold else ("0" if p + eps < a.threshold else "INCONCLUSIVE")
        rec = {"verdict": veredito, "p_hat": round(p, 6), "epsilon": round(eps, 6),
               "threshold": a.threshold, "delta": a.delta, "shots": a.shots,
               "rule": "proporcao-v1",
               "input_commitment": hashlib.sha3_256(
                   json.dumps({"counts": counts, "shots": a.shots}, sort_keys=True).encode()).hexdigest(),
               "issued_at": datetime.datetime.now(datetime.timezone.utc).isoformat()}
    rec["receipt_hash"] = hashlib.sha3_256(
        json.dumps(rec, sort_keys=True).encode()).hexdigest()
    json.dump(rec, open(a.receipt, "w"), indent=1)
    print(f"veredito: {rec['verdict']}")

if __name__ == "__main__":
    main()

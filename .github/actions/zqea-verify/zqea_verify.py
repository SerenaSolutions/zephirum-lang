#!/usr/bin/env python3
"""Z-QEA receipt verifier — the official seal check.

Rule (declared in the receipt itself, field selo_regra):
  selo = SHA3-256 over canonical JSON of the receipt with the field
  selo_sha3_256 REMOVED from the input.
  canonical JSON = json.dumps(payload, sort_keys=True, ensure_ascii=True, default=str)

Exit codes: 0 = INTEGRAL (seal matches), 1 = BROKEN (seal mismatch /
missing / malformed receipt). In GitHub Actions, a broken seal fails the job —
nothing executes silently.
"""
import sys, os, json, hashlib

def canonical(payload):
    return json.dumps(payload, sort_keys=True, ensure_ascii=True, default=str)

def verify(receipt):
    if not isinstance(receipt, dict):
        return False, None, "receipt is not a JSON object"
    declared = receipt.get("selo_sha3_256")
    if not declared:
        return False, None, "receipt has no selo_sha3_256"
    payload = {k: v for k, v in receipt.items() if k != "selo_sha3_256"}
    recomputed = hashlib.sha3_256(canonical(payload).encode()).hexdigest()
    return declared == recomputed, recomputed, "ok" if declared == recomputed else "seal mismatch"

def main():
    if len(sys.argv) < 2:
        print("usage: zqea_verify.py <receipt.json>")
        return 2
    try:
        receipt = json.load(open(sys.argv[1]))
    except Exception as e:
        print("Z-QEA: RECEIPT MALFORMED —", e)
        return 1
    ok, recomputed, why = verify(receipt)
    print("selo declarado   :", receipt.get("selo_sha3_256"))
    print("selo recalculado  :", recomputed)
    print("Z-QEA: SELO ÍNTEGRO" if ok else f"Z-QEA: SELO ROMPIDO ({why})")
    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a") as f:
            f.write("status=" + ("INTEGRAL" if ok else "BROKEN") + "\n")
            f.write("seal=" + str(recomputed) + "\n")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())

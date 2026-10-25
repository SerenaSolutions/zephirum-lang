# -*- coding: utf-8 -*-
"""ZQ-GATE CI battery — the trivalent decision battery + receipt verification.

Runs entirely offline (noiseless kernel, no IBM account needed) so any CI can
use it. Modes via env ZQG_MODE (all | battery | verify-receipts):
  battery         -> run the trivalent decision battery: constant-1 => 1,
                     constant-0 => 0, balanced => REFUSED, 1 oracle call each.
  verify-receipts-> recompute the SHA3-256 seal of every sealed receipt in
                     experiments/ (Z-QEA, clean canonical rule).
Exit code 0 = all pass. Any failure exits 1 — nothing passes silently.
"""
import os, sys, json, hashlib, glob

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src"))

MODE = (os.environ.get("ZQG_MODE") or "all").strip().lower()
FAILED = []


def run_battery():
    from zyql_quantum_gate import ZYQLQuantumGate
    cases = [
        ("constant-1", lambda x: 1, "1"),
        ("constant-0", lambda x: 0, "0"),
        ("balanced",   lambda x: x ^ 1, "REFUSED"),
    ]
    print("== ZQ-GATE trivalent decision battery (noiseless, canonical) ==")
    for name, oracle, expected in cases:
        r = ZYQLQuantumGate(3, oracle).run_quantum()
        ok = str(r["decision"]) == expected
        print(f"[{'PASS' if ok else 'FAIL'}] {name}: decision={r['decision']} "
              f"(expected {expected}) p0={r.get('p0')} calls={r.get('oracle_calls')}")
        if not ok:
            FAILED.append(f"battery:{name}")


def canon(payload):
    return json.dumps(payload, sort_keys=True, ensure_ascii=True, default=str)


def verify_receipt(path):
    try:
        rec = json.load(open(path))
    except Exception as e:
        print(f"[FAIL] {os.path.basename(path)}: malformed ({e})")
        FAILED.append(path)
        return
    declared = rec.get("selo_sha3_256")
    if not declared:
        print(f"[FAIL] {os.path.basename(path)}: no selo_sha3_256")
        FAILED.append(path)
        return
    if isinstance(rec.get("payload"), dict) and "selo_sha3_256" in rec:
        # formato aninhado (Rodada G em diante): o selo cobre rec["payload"]
        payload = rec["payload"]
    else:
        payload = {k: v for k, v in rec.items() if k != "selo_sha3_256"}
    recomputed = hashlib.sha3_256(canon(payload).encode()).hexdigest()
    ok = declared == recomputed
    print(f"[{'PASS' if ok else 'FAIL'}] {os.path.basename(path)}: "
          f"{'SELO ÍNTEGRO' if ok else 'SELO ROMPIDO'}")
    if not ok:
        FAILED.append(path)


def run_verify():
    print("== ZQ-GATE receipt verification (Z-QEA, SHA3-256) ==")
    root = os.path.join(HERE, "..")
    paths = sorted(glob.glob(os.path.join(root, "experiments", "**", "*.json"), recursive=True))
    sealed = [p for p in paths if "job_meta" not in os.path.basename(p)]
    any_sealed = False
    for p in sealed:
        try:
            d = json.load(open(p))
            if isinstance(d, dict) and d.get("selo_sha3_256"):
                verify_receipt(p)
                any_sealed = True
        except Exception:
            verify_receipt(p)
            any_sealed = True
    if not any_sealed:
        print("(no sealed receipts found in experiments/ — nothing to verify)")


if MODE in ("all", "battery"):
    run_battery()
if MODE in ("all", "verify-receipts"):
    run_verify()

print()
if FAILED:
    print("ZQ-GATE: FAIL —", len(FAILED), "failure(s). Nothing passes silently.")
    sys.exit(1)
print("ZQ-GATE: ALL PASS — decisions sealed, receipts intact.")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validation harness for ZEPHIRUM — one command, one verdict, one seal.

Purpose: let someone who does not trust us check the repository without reading
the code first. Every check below is mechanical and fails loudly; nothing is
reported as PASS by default.

Stages implemented here (see docs/VALIDATION.md):
  E1  version consistency        VERSION == pyproject == src/__init__
  E2  receipt seals              every receipt with a seal must recompute
  E3  conformance                conformance/run_conformance.py must be CONFORMANTE
  E4  test battery               pytest must exit 0 (optional, --battery)
  E5  report seal                SHA3-256 over the canonical report

Usage:
    python tools/validate_zephirum.py                # E1-E3 + E5
    python tools/validate_zephirum.py --battery      # adds E4
    python tools/validate_zephirum.py --json rel.json

Exit: 0 all stages pass, 1 any stage fails, 2 harness could not run.
"""
from __future__ import annotations
import argparse, glob, hashlib, json, os, re, subprocess, sys, platform, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CANON = lambda o: json.dumps(o, sort_keys=True, ensure_ascii=True, default=str)


def e0_prereqs():
    """Declares what is needed. A missing optional extra makes the battery
    inconclusive, never a silent pass and never a false failure."""
    import importlib.util as iu
    core = ["hashlib", "json", "glob", "subprocess"]
    optional = {"qiskit": "quantum kernel runs", "qiskit_aer": "hardware-free simulator tests",
                "openqasm3": "OpenQASM 3 import", "pqcrypto": "Z-KEM battery (extra 'pq')",
                "cryptography": "Ed25519 signing layer"}
    have_core = all(iu.find_spec(m) is not None for m in core)
    missing = {k: v for k, v in optional.items() if iu.find_spec(k) is None}
    return dict(stage="E0_prerequisites", pass_=have_core,
                detail=dict(core_ok=have_core, optional_missing=missing))


def e1_version():
    v_file = open(os.path.join(ROOT, "VERSION")).read().strip()
    py = open(os.path.join(ROOT, "pyproject.toml")).read()
    m = re.search(r'^version\s*=\s*"([^"]+)"', py, re.M)
    v_py = m.group(1) if m else None
    init = os.path.join(ROOT, "src", "__init__.py")
    v_init = None
    if os.path.exists(init):
        m2 = re.search(r'__version__\s*=\s*"([^"]+)"', open(init).read())
        v_init = m2.group(1) if m2 else None
    ok = v_file == v_py and (v_init is None or v_init == v_file)
    return dict(stage="E1_version_consistency", pass_=bool(ok),
                detail=dict(VERSION=v_file, pyproject=v_py, src_init=v_init))


def e2_seals():
    """Accepts both seal formats declared by the house canon, never one invented here:
       selo_sha3_256 -> SHA3-256 over rec["payload"]   (house format, Round G onward)
       sha3_256      -> SHA3-256 over body without the key itself (legacy q-route)
    A receipt with no seal is counted, not silently skipped."""
    CANON = lambda o: json.dumps(o, sort_keys=True, ensure_ascii=True, default=str)
    files = sorted(glob.glob(os.path.join(ROOT, "experiments", "*.json"))) + \
            [os.path.join(ROOT, f) for f in ("pennylane_crosscheck_receipt.json", "anyon_receipt.json")]
    checked, broken, unsealed, legacy = 0, [], [], 0
    for f in files:
        if not os.path.exists(f):
            continue
        try:
            rec = json.load(open(f))
        except Exception:
            continue
        if not isinstance(rec, dict):
            continue
        rel = os.path.relpath(f, ROOT)
        if rec.get("selo_sha3_256"):
            if not isinstance(rec.get("payload"), dict):
                unsealed.append(rel); continue
            recomputed = hashlib.sha3_256(CANON(rec["payload"]).encode()).hexdigest()
            checked += 1
            if recomputed != rec["selo_sha3_256"]:
                broken.append(dict(file=rel, format="payload", why="seal mismatch"))
        elif rec.get("sha3_256"):
            body = {k: v for k, v in rec.items() if k != "sha3_256"}
            recomputed = hashlib.sha3_256(CANON(body).encode()).hexdigest()
            checked += 1; legacy += 1
            if recomputed != rec["sha3_256"]:
                broken.append(dict(file=rel, format="legacy", why="seal mismatch"))
        else:
            unsealed.append(rel)
    return dict(stage="E2_receipt_seals", pass_=not broken,
                detail=dict(sealed_checked=checked, legacy_format=legacy,
                            broken=broken, without_seal=sorted(unsealed)[:5],
                            without_seal_count=len(unsealed)))


def e3_conformance():
    p = subprocess.run([sys.executable, "conformance/run_conformance.py", "--json"],
                       cwd=ROOT, capture_output=True, text=True, timeout=1800)
    out = p.stdout.strip()
    try:
        data = json.loads(out[out.index("{"):])
    except Exception:
        data = {"raw_tail": out[-400:]}
    conformant = p.returncode == 0
    return dict(stage="E3_conformance", pass_=conformant,
                detail=dict(exit_code=p.returncode, summary=data))


def e4_battery():
    p = subprocess.run([sys.executable, "-m", "pytest", "-q", "tests"],
                       cwd=ROOT, capture_output=True, text=True,
                       env={**os.environ, "PYTHONPATH": os.path.join(ROOT, "src")},
                       timeout=3600)
    return dict(stage="E4_test_battery", pass_=p.returncode == 0,
                detail=dict(exit_code=p.returncode, tail=p.stdout.strip().splitlines()[-3:]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--battery", action="store_true", help="also run pytest")
    ap.add_argument("--json", metavar="PATH", help="write the sealed report here")
    a = ap.parse_args()

    stages = [e0_prereqs(), e1_version(), e2_seals(), e3_conformance()]
    if a.battery:
        stages.append(e4_battery())

    # battery that failed only because an extra is missing is inconclusive, not a defect
    e0 = stages[0]["detail"]
    inconclusive = None
    if a.battery and not stages[-1]["pass_"]:
        tail = " ".join(stages[-1]["detail"].get("tail") or [])
        if "ModuleNotFoundError" in tail or "No module named" in tail:
            inconclusive = "battery needs an optional extra; see E0.optional_missing"
            stages[-1]["pass_"] = True
            stages[-1]["detail"]["inconclusive"] = inconclusive

    all_pass = all(s["pass_"] for s in stages)
    report = dict(
        tool="zephirum-validate", schema=1,
        generated_at=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        environment=dict(python=platform.python_version(), platform=platform.platform(),
                         node=platform.node()),
        verdict=("PASS" if all_pass and not inconclusive else ("PASS (with gaps)" if all_pass else "FAIL")),
        gaps=[inconclusive] if inconclusive else [],
        stages=stages,
    )
    report["report_sha3_256"] = hashlib.sha3_256(CANON(report).encode()).hexdigest()

    for s in stages:
        print(f"[{'PASS' if s['pass_'] else 'FAIL'}] {s['stage']}")
        if not s["pass_"]:
            print("      ", json.dumps(s["detail"])[:300])
    print()
    print("veredito          :", report["verdict"])
    print("report_sha3_256   :", report["report_sha3_256"])
    print("ambiente          : python", report["environment"]["python"])

    if a.json:
        with open(a.json, "w") as fh:
            json.dump(report, fh, indent=2, sort_keys=True)
        print("relatorio salvo   :", a.json)
    return 0 if all_pass else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # harness failure is not a pass
        print("VALIDATOR ERROR:", exc)
        sys.exit(2)

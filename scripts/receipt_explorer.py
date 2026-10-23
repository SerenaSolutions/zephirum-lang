#!/usr/bin/env python3
"""Receipts explorer (issue #30): resume e verifica recibos Z-QEA.

Uso: python3 scripts/receipt_explorer.py caminho/recibo.json [mais.json ...]
Verifica a camada classica (SHA3-256) e, se houver assinatura ML-DSA-44,
informa a camada pos-quantica (verificacao completa via zqea-verify --strict-pq).
"""
import sys, os, json, hashlib

def canon(payload):
    if isinstance(payload, dict):
        return json.dumps(payload, sort_keys=True, ensure_ascii=True, default=str)

def explore(path):
    rec = json.load(open(path))
    print(f"\n== {os.path.basename(path)} ==")
    for k in ("missao", "tipo", "veredito", "provider"):
        if k in rec: print(f"  {k:<12}: {rec[k]}")
    if "agente" in rec: print(f"  agente       : {rec['agente'].get('nome')} v{rec['agente'].get('versao')}")
    if "entropia_quantica" in rec:
        e = rec["entropia_quantica"]
        print(f"  entropia     : {e.get('backend')} {e.get('shots')} shots (job {e.get('job_id')})")
    # camada classica
    declared = rec.get("selo_sha3_256")
    if not declared:
        print("  selo         : AUSENTE (sem camada classica!)"); return False
    payload = {k: v for k, v in rec.items() if k != "selo_sha3_256"}
    recomputed = hashlib.sha3_256(canon(payload).encode()).hexdigest()
    ok = declared == recomputed
    print(f"  selo SHA3-256: {'INTEGRO' if ok else 'ROMPIDO'} ({declared[:16]}...)")
    # camada pos-quantica
    apq = rec.get("assinatura_pq")
    if apq:
        print(f"  ML-DSA-44    : PRESENTE (alg={apq.get('alg','?')[:40]}..., pk embarcada)")
        print("  verificacao pos-quantica completa: zqea-verify --strict-pq")
    else:
        print("  ML-DSA-44    : ausente (recibo so classico; zqea-verify aceita como LEGACY_V1)")
    return ok

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    results = [explore(p) for p in sys.argv[1:]]
    print(f"\n{sum(results)}/{len(results)} recibos com selo integro")

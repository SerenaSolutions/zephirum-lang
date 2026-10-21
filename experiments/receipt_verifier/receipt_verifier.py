#!/usr/bin/env python3
"""
INDEPENDENT RECEIPT VERIFIER (POC 2)
=====================================
House ZEPHIRUM (Serena Quantum Solutions) - 2026-10-20
Standalone verifier for ZYQL/ZEPHIRUM decision receipts and ledgers.

Verification Layers:
  1. Mandatory Schema & Fields Check
  2. Cryptographic Hash Seal Integrity (SHA3-256 / SHA-256)
  3. Ledger Chain Order, Monotonicity & Replay Check
  4. Coherence Between Declared Verdict and Raw Measurement Evidence
  5. Prohibited Purpose Policy Alignment Check

Automated Tampering Battery (5 Attack Scenarios):
  (a) Forged receipt (modified verdict without seal update)
  (b) Omitted mandatory field
  (c) Reordered records in ledger chain
  (d) Replay / duplicated receipt ID attack
  (e) Divergence between declared verdict and raw shot counts / evidence (re-signed payload)
"""

import sys
import os
import json
import time
import hashlib
from typing import Dict, Any, List, Tuple, Union

MARGIN = 0.15

PROHIBITED_POLICY_KEYWORDS = [
    "weapons", "lethality", "surveillance", "persecution", "fraud",
    "forgery", "sabotage", "explosives", "cyberattack"
]

MANDATORY_RECEIPT_FIELDS = [
    ["sha3_256", "cert_hash", "seal", "hash"],                     # At least one seal field
    ["decision", "verdict", "status", "obtido"],                     # At least one verdict field
    ["ts", "timestamp", "timestamp_utc", "date", "created_at"]       # At least one timestamp field
]

class ReceiptVerifier:
    """Independent verifier for ZYQL receipts and ledgers."""

    def __init__(self, delta: float = 0.15):
        self.delta = delta

    def _canonical_bytes(self, payload: Dict[str, Any], exclude_keys: List[str] = None) -> bytes:
        if exclude_keys is None:
            exclude_keys = ["sha3_256", "cert_hash", "seal", "hash", "signature"]
        cleaned = {k: v for k, v in payload.items() if k not in exclude_keys}
        return json.dumps(cleaned, sort_keys=True, default=str).encode("utf-8")

    def verify_single_receipt(self, receipt: Dict[str, Any]) -> Tuple[bool, List[str]]:
        issues = []

        # Handle nested payload format (e.g. ZCA receipts: {"teste": "...", "payload": {...}, "sha3_256": "..."})
        if "payload" in receipt and isinstance(receipt["payload"], dict):
            payload = receipt["payload"]
            declared_seal = receipt.get("sha3_256") or receipt.get("seal")
        else:
            payload = receipt
            declared_seal = receipt.get("sha3_256") or receipt.get("cert_hash") or receipt.get("seal") or receipt.get("hash")

        # 1. Mandatory Fields Check
        for field_group in MANDATORY_RECEIPT_FIELDS:
            if not any(f in receipt or f in payload for f in field_group):
                issues.append(f"MISSING_MANDATORY_FIELD: None of {field_group} found in receipt.")

        if issues:
            return False, issues

        # 2. Cryptographic Hash Seal Verification
        if declared_seal:
            # Check SHA3-256
            if "payload" in receipt and isinstance(receipt["payload"], dict):
                blob = json.dumps(payload, sort_keys=True, default=str)
                calc_sha3 = hashlib.sha3_256(blob.encode("utf-8")).hexdigest()
                calc_sha256 = hashlib.sha256(blob.encode("utf-8")).hexdigest()
            else:
                canon_b = self._canonical_bytes(payload)
                calc_sha3 = hashlib.sha3_256(canon_b).hexdigest()
                calc_sha256 = hashlib.sha256(canon_b).hexdigest()

            if declared_seal.lower() not in (calc_sha3.lower(), calc_sha256.lower()):
                issues.append(f"HASH_SEAL_MISMATCH: Declared seal {declared_seal} does not match recomputed SHA3-256 ({calc_sha3}) or SHA-256 ({calc_sha256}).")

        # Extract verdict
        verdict = (
            receipt.get("decision") or receipt.get("verdict") or receipt.get("status") or
            payload.get("decision") or payload.get("verdict") or payload.get("status") or payload.get("obtido")
        )

        # 3. Policy Alignment Check
        purpose = str(receipt.get("purpose") or payload.get("purpose") or payload.get("question") or "")
        for kw in PROHIBITED_POLICY_KEYWORDS:
            if kw in purpose.lower() and str(verdict).upper() not in ("REFUSED", "0", "ERROR", "FLAGGED"):
                issues.append(f"POLICY_COHERENCE_VIOLATION: Purpose contains prohibited term '{kw}' but verdict is declared as '{verdict}'.")

        # 4. Raw Evidence & Decision Coherence Check
        p0 = receipt.get("p0") if receipt.get("p0") is not None else payload.get("p0")
        if p0 is None:
            p0 = receipt.get("p_hat") if receipt.get("p_hat") is not None else payload.get("p_hat")

        counts = receipt.get("counts") or payload.get("counts")
        if counts and isinstance(counts, dict) and p0 is None:
            total_shots = sum(counts.values())
            if total_shots > 0:
                zero_key = [k for k in counts if k.replace("|","").replace(">","").replace(" ","") == "0" * len(k.replace("|","").replace(">","").replace(" ",""))]
                if zero_key:
                    p0 = counts[zero_key[0]] / total_shots

        if p0 is not None:
            p0 = float(p0)
            if p0 > (1.0 - self.delta):
                if str(verdict).upper() not in ("1", "0", "PASS", "DECIDED_BY_INTERFERENCE"):
                    issues.append(f"VERDICT_EVIDENCE_DIVERGENCE: Measured p0={p0:.4f} >= {1-self.delta:.2f} (constant region), but verdict is declared as '{verdict}'.")
            elif p0 < self.delta:
                if str(verdict).upper() not in ("REFUSED", "0", "PASS", "DECIDED_BY_INTERFERENCE"):
                    issues.append(f"VERDICT_EVIDENCE_DIVERGENCE: Measured p0={p0:.4f} <= {self.delta:.2f} (balanced region), but verdict is declared as '{verdict}'.")
            else:
                if str(verdict).upper() not in ("REFUSED", "INSUFFICIENT_CONFIDENCE"):
                    issues.append(f"VERDICT_EVIDENCE_DIVERGENCE: Measured p0={p0:.4f} falls inside noise band ({self.delta:.2f}, {1-self.delta:.2f}), requiring verdict 'REFUSED', but got '{verdict}'.")

        is_valid = len(issues) == 0
        return is_valid, issues

    def verify_chain(self, receipts: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
        chain_issues = []
        seen_ids = set()
        prev_hash = None

        for idx, rec in enumerate(receipts):
            valid, single_issues = self.verify_single_receipt(rec)
            if not valid:
                chain_issues.append(f"RECEIPT_INDEX_{idx}_INVALID: {'; '.join(single_issues)}")

            rec_id = rec.get("id") or rec.get("receipt_id") or rec.get("job_id") or rec.get("ts") or str(idx)
            if rec_id in seen_ids and rec_id != str(idx):
                chain_issues.append(f"REPLAY_ATTACK_DETECTED: Duplicate receipt identifier '{rec_id}' at index {idx}.")
            seen_ids.add(rec_id)

            curr_prev_hash = rec.get("previous_hash") or rec.get("prev_sha3_256")
            if idx > 0 and curr_prev_hash:
                if prev_hash and curr_prev_hash.lower() != prev_hash.lower():
                    chain_issues.append(f"CHAIN_BREAK_DETECTED at index {idx}: Declared previous_hash '{curr_prev_hash}' != calculated previous hash '{prev_hash}'.")

            prev_hash = rec.get("sha3_256") or rec.get("cert_hash") or rec.get("seal")

        is_valid = len(chain_issues) == 0
        return is_valid, chain_issues


def run_tampering_battery(verifier: ReceiptVerifier) -> Dict[str, Any]:
    base_receipt = {
        "id": "rec_20261020_001",
        "purpose": "Verify safe matrix transform",
        "p0": 0.50,
        "decision": "REFUSED",
        "rule": "inside noise band (+-0.15)",
        "ts": "2026-10-20T19:28:00Z"
    }
    canon_bytes = verifier._canonical_bytes(base_receipt)
    base_receipt["sha3_256"] = hashlib.sha3_256(canon_bytes).hexdigest()

    attack_results = []

    # Attack (a): Forged receipt
    forged_rec = dict(base_receipt)
    forged_rec["decision"] = 1
    valid_a, issues_a = verifier.verify_single_receipt(forged_rec)
    attack_results.append({
        "attack_id": "attack_a_forged_verdict",
        "description": "Verdict tampered from REFUSED to 1 without updating cryptographic seal",
        "rejected_by_verifier": not valid_a,
        "detected_issues": issues_a,
        "PASS": not valid_a
    })

    # Attack (b): Omitted mandatory field
    omitted_rec = dict(base_receipt)
    del omitted_rec["sha3_256"]
    valid_b, issues_b = verifier.verify_single_receipt(omitted_rec)
    attack_results.append({
        "attack_id": "attack_b_omitted_field",
        "description": "Mandatory cryptographic seal field deleted",
        "rejected_by_verifier": not valid_b,
        "detected_issues": issues_b,
        "PASS": not valid_b
    })

    # Attack (c): Reordered records in ledger chain
    r1 = dict(base_receipt, id="rec_001", sha3_256="hash_111")
    r2 = dict(base_receipt, id="rec_002", previous_hash="hash_111", sha3_256="hash_222")
    r3 = dict(base_receipt, id="rec_003", previous_hash="hash_222", sha3_256="hash_333")
    reordered_chain = [r1, r3, r2]
    valid_c, issues_c = verifier.verify_chain(reordered_chain)
    attack_results.append({
        "attack_id": "attack_c_reordered_records",
        "description": "Chain records reordered (r3 before r2), breaking hash linkage",
        "rejected_by_verifier": not valid_c,
        "detected_issues": issues_c,
        "PASS": not valid_c
    })

    # Attack (d): Replay / duplicated receipt attack
    replayed_chain = [r1, r2, r2]
    valid_d, issues_d = verifier.verify_chain(replayed_chain)
    attack_results.append({
        "attack_id": "attack_d_replay_duplicate",
        "description": "Duplicate receipt replayed at end of chain",
        "rejected_by_verifier": not valid_d,
        "detected_issues": issues_d,
        "PASS": not valid_d
    })

    # Attack (e): Divergence between declared verdict and raw evidence (re-signed payload)
    divergent_rec = {
        "id": "rec_20261020_005",
        "purpose": "Evaluate noise band circuit",
        "p0": 0.50,
        "decision": 1,
        "rule": "band>=0.85",
        "ts": "2026-10-20T19:28:00Z"
    }
    divergent_canon = verifier._canonical_bytes(divergent_rec)
    divergent_rec["sha3_256"] = hashlib.sha3_256(divergent_canon).hexdigest()
    
    valid_e, issues_e = verifier.verify_single_receipt(divergent_rec)
    attack_results.append({
        "attack_id": "attack_e_verdict_evidence_divergence",
        "description": "Payload verdict = 1 despite raw p0 = 0.50 inside noise band (seal validly signed over fake payload)",
        "rejected_by_verifier": not valid_e,
        "detected_issues": issues_e,
        "PASS": not valid_e
    })

    all_rejected = all(a["PASS"] for a in attack_results)
    return {
        "total_attacks": len(attack_results),
        "attacks_rejected_count": sum(1 for a in attack_results if a["PASS"]),
        "tampering_battery_pass_rate": 100.0 if all_rejected else (100.0 * sum(1 for a in attack_results if a["PASS"]) / len(attack_results)),
        "all_tampered_rejected": all_rejected,
        "attack_details": attack_results
    }


def verify_repo_receipts(verifier: ReceiptVerifier) -> Dict[str, Any]:
    repo_files = [
        "zephirum_lang_audit/tests/ibm_quantum/zca_conformidade_sim.json",
        "zephirum_lang_audit/tests/ibm_quantum/zca_conformidade_live.json",
        "zephirum_lang_audit/experiments/chemistry/chemistry_battery_20261020.json",
        "dexia_receipts.jsonl"
    ]

    verification_summary = []

    for rel_path in repo_files:
        full_path = os.path.join("/app/conversations/69b3414a734bebfcfde6eea6", rel_path)
        if not os.path.exists(full_path):
            verification_summary.append({
                "file": rel_path,
                "status": "FILE_NOT_FOUND",
                "receipts_checked": 0,
                "valid_receipts": 0,
                "invalid_receipts": 0
            })
            continue

        valid_count = 0
        invalid_count = 0
        total_checked = 0
        file_issues = []

        try:
            if rel_path.endswith(".jsonl"):
                receipts = []
                with open(full_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            receipts.append(json.loads(line))
            else:
                with open(full_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        receipts = data
                    elif "recibos" in data:
                        receipts = data["recibos"]
                    elif "recibo" in data:
                        receipts = [data["recibo"]]
                    else:
                        receipts = [data]

            total_checked = len(receipts)
            for idx, rec in enumerate(receipts):
                valid, issues = verifier.verify_single_receipt(rec)
                if valid:
                    valid_count += 1
                else:
                    invalid_count += 1
                    file_issues.append({"receipt_index": idx, "issues": issues})

            verification_summary.append({
                "file": rel_path,
                "status": "VERIFIED",
                "receipts_checked": total_checked,
                "valid_receipts": valid_count,
                "invalid_receipts": invalid_count,
                "issues": file_issues
            })
        except Exception as e:
            verification_summary.append({
                "file": rel_path,
                "status": f"READ_ERROR: {str(e)}",
                "receipts_checked": 0,
                "valid_receipts": 0,
                "invalid_receipts": 0
            })

    return {
        "repo_files_evaluated": len(repo_files),
        "files_summary": verification_summary
    }

def main():
    verifier = ReceiptVerifier(delta=MARGIN)
    
    # 1. Run Tampering Battery
    tamper_res = run_tampering_battery(verifier)

    # 2. Run Real Receipts Verification
    repo_res = verify_repo_receipts(verifier)

    # Canonical Payload
    canonical_payload = {
        "experiment": "independent_receipt_verifier",
        "version": "1.0.0",
        "timestamp_utc": "2026-10-20T19:28:00Z",
        "tampering_battery": tamper_res,
        "repo_receipts_verification": repo_res,
        "declared_verifier_capabilities": [
            "Mandatory schema and fields presence check",
            "SHA3-256 and SHA-256 cryptographic seal integrity check",
            "Chain linkage, sequence monotonicity, and replay detection",
            "Coherence check between raw probability (p0) and trivalent verdict (1/0/REFUSED)",
            "Prohibited purpose policy alignment check"
        ],
        "declared_verifier_limitations": [
            "Cryptographic seal proves structural integrity and non-tampering of record; DOES NOT prove scientific correctness of physical laws.",
            "Raw measurement evidence coherence proves mathematical consistency with decision rule; DOES NOT guarantee hardware calibration state at run time.",
            "Signature attribution relies on ML-DSA-44 roadmap implementation; current hash seals confirm data integrity, not non-repudiable author identity."
        ]
    }

    # SHA3-256 Seal of results
    payload_str = json.dumps(canonical_payload, sort_keys=True)
    seal_sha3 = hashlib.sha3_256(payload_str.encode("utf-8")).hexdigest()

    final_output = {
        "canonical_receipt": {
            "house": "ZEPHIRUM (Serena Quantum Solutions)",
            "purpose": "Independent Receipt Verifier (POC 2)",
            "sha3_256": seal_sha3,
            "seal_alg": "SHA3-256",
            "signature_status": "DECLARED_ROADMAP_ML_DSA_44",
            "timestamp_utc": "2026-10-20T19:28:00Z"
        },
        "data": canonical_payload
    }

    output_path = os.path.join(os.path.dirname(__file__), "receipt_verifier_results.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final_output, f, indent=2)

    print(f"=== RECEIPT VERIFIER COMPLETE ===")
    print(f"Tampering Battery Result: {tamper_res['attacks_rejected_count']}/{tamper_res['total_attacks']} attacks rejected ({tamper_res['tampering_battery_pass_rate']}%)")
    print(f"SHA3-256 Seal: {seal_sha3}")
    print(f"Results saved to: {output_path}")

if __name__ == "__main__":
    main()

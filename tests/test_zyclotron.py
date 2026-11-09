# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Serena Quantum Solutions
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from zyclotron import compile_derivative_app


def blueprint():
    return {
        "name": "audit_app",
        "purpose": "audit a decision pipeline",
        "evidence": ["receipt-001"],
        "constraints": ["fail closed"],
        "alternatives": ["unverified route"],
        "capabilities": ["inspect", "verify"],
    }


def test_derivative_manifest_is_deterministic_and_auditable():
    a = compile_derivative_app(blueprint()).to_dict()
    b = compile_derivative_app(blueprint()).to_dict()
    assert a == b
    assert a["decision"] == "1"
    assert a["manifest"]["runtime"]["engine"] == "ZYQL"
    assert a["receipt"]["manifest_sha3_256"]


def test_missing_evidence_refuses_closed():
    bp = blueprint()
    bp["evidence"] = []
    result = compile_derivative_app(bp)
    assert result.decision == "REFUSED"
    assert result.receipt["refusal_reason"] == "MISSING_EVIDENCE"

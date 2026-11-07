"""Zyclotron: experimental derivative-app synthesis layer for ZYQL.

Zyclotron does not replace the ZYQL decision core. It compiles a validated
blueprint into a deterministic, auditable derivative-app manifest and carries
the input evidence, constraints, alternatives, and refusal conditions forward.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any, Mapping, Sequence

VERSION = "0.1.0"


class ZyclotronRefused(ValueError):
    """Raised when a blueprint cannot be compiled safely."""


@dataclass(frozen=True)
class ZyclotronResult:
    decision: str
    manifest: dict[str, Any] | None
    receipt: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {"decision": self.decision, "manifest": self.manifest,
                "receipt": self.receipt}


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"))


def _digest(value: Any) -> str:
    return hashlib.sha3_256(_canonical(value).encode("utf-8")).hexdigest()


def _strings(values: Any, field: str) -> list[str]:
    if values is None:
        return []
    if isinstance(values, str):
        values = [values]
    if not isinstance(values, Sequence) or isinstance(values, (bytes, bytearray)):
        raise ZyclotronRefused(f"{field} precisa ser uma lista de textos")
    result = [str(v).strip() for v in values if str(v).strip()]
    return result


def compile_derivative_app(blueprint: Mapping[str, Any]) -> ZyclotronResult:
    """Compile a blueprint into a derivative-app manifest.

    Required fields: ``name`` and ``purpose``. The compiler refuses empty
    evidence, missing constraints, duplicate capabilities, or invalid names.
    The output is deterministic for the same blueprint.
    """
    if not isinstance(blueprint, Mapping):
        raise ZyclotronRefused("blueprint precisa ser um objeto")
    name = str(blueprint.get("name", "")).strip()
    purpose = str(blueprint.get("purpose", "")).strip()
    if not name or not purpose:
        raise ZyclotronRefused("name e purpose são obrigatórios")
    if any(ch not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-" for ch in name):
        raise ZyclotronRefused("name contém caracteres não permitidos")

    evidence = _strings(blueprint.get("evidence"), "evidence")
    constraints = _strings(blueprint.get("constraints"), "constraints")
    alternatives = _strings(blueprint.get("alternatives"), "alternatives")
    capabilities = _strings(blueprint.get("capabilities"), "capabilities")
    if not evidence:
        return _refused(blueprint, "MISSING_EVIDENCE")
    if not constraints:
        return _refused(blueprint, "MISSING_CONSTRAINTS")
    if len(capabilities) != len(set(capabilities)):
        return _refused(blueprint, "DUPLICATE_CAPABILITY")

    normalized = {
        "name": name,
        "purpose": purpose,
        "evidence": evidence,
        "constraints": constraints,
        "alternatives": alternatives,
        "capabilities": capabilities,
    }
    source_hash = _digest(normalized)
    manifest = {
        "format": "zyclotron-derivative-app/v1",
        "zyclotron_version": VERSION,
        "id": f"app_{source_hash[:16]}",
        "name": name,
        "purpose": purpose,
        "capabilities": capabilities,
        "runtime": {"engine": "ZYQL", "verdicts": ["1", "0", "REFUSED"],
                    "fail_closed": True},
        "provenance": {"evidence": evidence, "constraints": constraints,
                        "alternatives_rejected": alternatives,
                        "blueprint_sha3_256": source_hash},
    }
    receipt = {"protocol": "ZyclotronReceipt/v1", "decision": "1",
               "source_sha3_256": source_hash,
               "manifest_sha3_256": _digest(manifest),
               "refusal_reason": None}
    return ZyclotronResult("1", manifest, receipt)


def _refused(blueprint: Mapping[str, Any], reason: str) -> ZyclotronResult:
    source_hash = _digest(dict(blueprint))
    return ZyclotronResult("REFUSED", None, {
        "protocol": "ZyclotronReceipt/v1", "decision": "REFUSED",
        "source_sha3_256": source_hash, "manifest_sha3_256": None,
        "refusal_reason": reason,
    })

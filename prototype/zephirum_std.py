#!/usr/bin/env python3
"""ZEPHIRUM normative conformance checker, standard v0.3 draft.

This module turns the language standard into an executable gate. It validates
source syntax and the normative contract before the reference NCA is called.
It does not claim self-hosting or replace the Python reference implementation.
"""
import json
import sys
from fractions import Fraction

from zephirum_lexer import parse_zephirum, ZephirumSyntaxError

STANDARD_VERSION = "0.3"
BLOCKS = {"ASK", "CONTRACT", "MODEL", "BUDGET", "REQUIRE"}
MODEL_TYPES = {"threshold_sum", "mean_partial", "constant_fold", "gauss_series"}


def _error(code, message):
    return {"code": code, "message": message}


def validate_source(source):
    errors = []
    try:
        blocks = parse_zephirum(source)
    except Exception as exc:
        return {"standard": STANDARD_VERSION, "valid": False,
                "errors": [_error("SYNTAX", str(exc))]}

    unknown_blocks = set(blocks) - BLOCKS
    for block in sorted(unknown_blocks):
        errors.append(_error("BLOCK_UNKNOWN", "bloco não reconhecido: %s" % block))

    if "ASK" not in blocks:
        errors.append(_error("ASK_REQUIRED", "bloco ASK obrigatório"))
    else:
        question = blocks["ASK"].get("question")
        if not question:
            errors.append(_error("QUESTION_REQUIRED", "ASK.question obrigatório"))

    if "CONTRACT" in blocks:
        contract = blocks["CONTRACT"]
        if "absolute_error" not in contract:
            errors.append(_error("CONTRACT_EXACTNESS",
                                 "CONTRACT.absolute_error obrigatório no perfil exacto"))
        elif contract["absolute_error"] != "0":
            errors.append(_error("CONTRACT_EXACTNESS",
                                 "o perfil certificado exige absolute_error: 0"))

    if "MODEL" in blocks:
        model = blocks["MODEL"]
        model_type = model.get("type")
        if not model_type:
            errors.append(_error("MODEL_TYPE_REQUIRED", "MODEL.type obrigatório"))
        elif model_type not in MODEL_TYPES:
            errors.append(_error("MODEL_UNSUPPORTED",
                                 "modelo não suportado no padrão v%s: %s" %
                                 (STANDARD_VERSION, model_type)))

    # Decimal literals are parsed by the reference lexer as Fraction, never float.
    # This check is intentionally executable evidence of the standard promise.
    try:
        from zephirum_lexer import eval_expr
        for line in source.splitlines():
            if ":" in line and any(ch.isdigit() for ch in line.split(":", 1)[1]):
                # Only evaluate literal-only expressions. Structured values remain
                # owned by the model parser and are not guessed here.
                value = line.split(":", 1)[1].strip()
                if value and all(ch in "0123456789.+-*/%() \t" for ch in value):
                    result = eval_expr(value)
                    if isinstance(result, float):
                        errors.append(_error("FLOAT_LITERAL", "literal decimal convertido a float"))
    except Exception:
        pass

    return {"standard": STANDARD_VERSION, "valid": not errors,
            "errors": errors, "blocks": sorted(blocks)}


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    source = open(argv[0], encoding="utf-8").read() if argv else sys.stdin.read()
    result = validate_source(source)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

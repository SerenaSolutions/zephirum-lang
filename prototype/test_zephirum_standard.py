#!/usr/bin/env python3
"""Executable conformance checks for the ZEPHIRUM language standard."""
from zephirum_std import validate_source, STANDARD_VERSION

VALID = """ASK:
    question: sum > 40
CONTRACT:
    absolute_error: 0
MODEL:
    type: threshold_sum
    terms: 3, 7, 12, 40
"""


def assert_valid(source):
    result = validate_source(source)
    assert result["valid"], result
    assert result["standard"] == STANDARD_VERSION


def assert_invalid(source, code):
    result = validate_source(source)
    assert not result["valid"], result
    assert code in {e["code"] for e in result["errors"]}, result


def main():
    assert_valid(VALID)
    assert_invalid("CONTRACT:\n    absolute_error: 0\n", "SYNTAX")
    assert_invalid(VALID.replace("absolute_error: 0", "absolute_error: 0.1"),
                   "CONTRACT_EXACTNESS")
    assert_invalid(VALID.replace("threshold_sum", "future_model"), "MODEL_UNSUPPORTED")
    assert_invalid(VALID.replace("MODEL:\n", "MODEL:\n    type: threshold_sum\nMODEL:\n"),
                   "SYNTAX")
    print("ZEPHIRUM standard v%s: conformance PASS" % STANDARD_VERSION)


if __name__ == "__main__":
    main()

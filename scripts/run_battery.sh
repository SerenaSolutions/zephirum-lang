#!/bin/sh
# Run the canonical rational test battery (CI parity: same command as .github/workflows/ci.yml)
set -e
cd "$(dirname "$0")/.."
python3 tests/test_canonical.py

# GEN1_BASELINE — ZEPHIRUM Scientific Kernel, Gen 1

Audited 2026-11-27 against `main`. Every statement points to code, test or document.
States: IMPLEMENTED_AND_TESTED (IT), IMPLEMENTED_NOT_FULLY_TESTED (INT), PARTIALLY_IMPLEMENTED (PI), DOCUMENTED_ONLY (DO), NOT_IMPLEMENTED (NI), UNKNOWN (U).

## 1. Public surface (real)

| Component | State | Evidence |
|---|---|---|
| Trivalent decision core | IT | `src/zephirum/__init__.py` — returns `1 / 0 / INCONCLUSIVE / REFUSED` with declared margin and rule id (`proporcao-v1`); refusal reasons are typed (`CONTAGENS_INVALIDAS`, `CONTAGEM_NAO_INTEIRA`, `SOMA_DIFERE_DOS_SHOTS`, `SHOTS_INVALIDO`) |
| Backend adapters | INT | `src/zephirum/adapters/qiskit_backend.py` (`disponivel`, `validar`, `construir`, `estado_exato`, `executar`, `verificar`), `qbraid_backend.py`, `cudaq_backend.py` |
| Q-route layer | PI | `src/qroute/{core,graph,grover,hardware,receipt}.py` |
| ZYQL-TEN stack | PI | `src/zyql_ten/s01..s07` (data validation, model guardian, pipeline control, data router, decision intelligence, compute router, AI governance) |
| Docker Core | IT | `docker/zephirum_core/{exact,cert,qasm3,zca,server}.py`, `docker/pipeline.py`, `docker/tests/test_zephirum_core.py` (merged via #142) |
| Core hardening 1.1 | IT (branch) | PR #153, `feat/zephirum-core-hardening`, 51 tests passing |
| Receipts (Z-QEA) | IT | `recibos/examples/hello_world.receipt.json`: `spec`, `modulo`, `data`, `modo`, `laboratorio`, `resultados`, `selo_regra`, `selo_sha3_256` |
| ML-DSA-44 signature | PI | declared BETA in `docs/MATURITY.md`; `docs/receipts.md` says "DECLARED ROADMAP" — **documents disagree** |
| Lisp parser `.zph` | PI | `src/zyql_lisp.py`, experimental per `docs/MATURITY.md` |

## 2. Test surface

52 test files in `tests/`. Baseline run on `main` (this environment): **4 collection errors, all environmental** (`ModuleNotFoundError: zephirum`, optional `qbraid`/`cudaq` adapters not installed). `docker/tests`: **51 passed** on the hardening branch, 25 passed on `main`.

## 3. Documented maturity vs. reality (discrepancies found)

1. `docs/MATURITY.md` marks `zyql_quantum_gate` as **PRODUÇÃO** while `README.md` frames the project as work in progress. Reconciliation required before any public maturity claim.
2. `docs/MATURITY.md` says ML-DSA-44 is **BETA**; `docs/receipts.md` says **DECLARED ROADMAP**. One statement must win.
3. No independent reproduction evidence exists in-repo (`CALL_FOR_TESTERS.md`, Discussion #141: 0 external reports).

## 4. Dependencies (declared)

`pyproject.toml`: `numpy>=1.26,<3`, `lark>=1.1,<2`, `qiskit>=2.6.1,<3`. Python >= 3.10. License Apache-2.0 (diverges from the earlier BSL/MIT hybrid instruction — founder decision pending).

## 5. Limits already declared by the project

No error correction (useful execution well below 20 qubits); hardware claims require job id + receipt; simulation must be labelled as simulation; hash proves integrity, not authorship nor truth.

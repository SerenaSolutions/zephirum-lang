# GEN1_ARCHITECTURE — six target components vs. what exists

Rule: reuse before creating. No module is created where an existing one can carry the responsibility.

| Target component | Carried today by | Gap |
|---|---|---|
| Scientific Interface | `src/zephirum/__init__.py` (Python API), `docker/zephirum_core/qasm3.py` (OpenQASM subset), `src/zyql_lisp.py` (`.zph`) | no single formal entry contract with version |
| Formalization Layer | partially `src/zyql_ten/s01_data_validation.py`, `docker/zephirum_core/exact.py` | no typed problem contract (domain, assumptions, constraints, tolerances) |
| VERITAS verification gate | `docker/zephirum_core/cert.py` (`emitir_certificado` / `verificar_certificado`), `server.py` validation | no separation between formal proof, structural check, numeric validation, experimental evidence |
| Hybrid Computational Orchestrator | `src/zyql_ten/s06_compute_router.py`, `src/qroute/core.py`, adapters | no declared backend capability contract; no explicit fallback policy record |
| Execution Engine | adapters (`qiskit`, `qbraid`, `cudaq`), `docker/pipeline.py`, `backends/ibm.py` | no post-execution normalization contract shared across backends |
| Z-QEA Evidence Engine | `docs/receipts.md`, `recibos/examples/*.json`, `src/qroute/receipt.py`, `zyql_ten/receipt.py` | receipt shape differs between layers; no single verifier across all producers |

## Decision

Gen 1 does **not** rewrite the runtime. It formalizes contracts around what exists and makes one end-to-end path verifiable: contract -> validation -> trivalent verdict -> backend selection -> execution -> receipt -> independent verification.

## Semantic rule (non-negotiable)

`1` = operational permission, `0` = operational prohibition, `REFUSED` = insufficient evidence. Never coerced to booleans. Epistemic dimension (PROVED / SUPPORTED / UNKNOWN) is recorded **separately** from the decision dimension and never inferred from it.

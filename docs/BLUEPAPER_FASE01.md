# BLUEPAPER · FASE 01 — Baseline verificado e gap analysis

**Data:** 2026-11-10 · **Escopo:** diretriz "ZYQL/ZEPHIRUM — Strategic Technical Evolution"
**Método:** auditoria do repositório `zephirum-lang` (código, testes, CI, licença, registros públicos).

## 1. Decisões de diretriz (travadas)

| Item | Diretriz dizia | Decisão | Motivo |
| --- | --- | --- | --- |
| Licença | "Preservar MIT" | **Apache-2.0 mantido** | Concessão explícita de patentes; já declarada no PyPI, Zenodo e catálogo Qiskit. Trocar para MIT enfraquece a proteção e desmente três registros públicos. |
| Numeração | "1.0 → 2.0" | **Pacote em 2.5.8; "1.0 → 2.0" vale para a especificação** | Renumerar para baixo quebraria PyPI, Zenodo e o catálogo. |
| Segunda sintaxe (PROBLEM/DECIDE/RETURN) | linguagem independente | **Descopada por ora** | O front-end é Lisp `.zph` (v2), com 26 exemplos e regressão própria. Duas superfícies públicas fragmentam a base. Reavaliar como superfície que compila para a forma canônica. |

## 2. Baseline verificado

- Versão: `2.5.8` (VERSION, pyproject e PyPI alinhados).
- Front-end: `src/zyql_lisp.py`, especificação em `docs/ZYQL_LISP_SPEC.md`, 26 programas `.zph`, `tests/test_lisp_regression.py`.
- Decisão: 11 arquivos; semântica trivalente congelada com contrato de campos.
- Recibo: selo SHA3-256 canônico (`src/qroute/receipt.py`), verificador público (`.github/actions/zqea-verify`), template de issue para verificação por terceiros.
- Qiskit: `src/zephirum/adapters/qiskit_backend.py`, `src/zyql_ten/qiskit_bridge.py`, `proofs_m1_s2_c3/qasm3_adapter/`.
- Testes: 57 arquivos. CI: 8 workflows (ci, conformance, coverage, codeql, dependency-review, regression-seal, ai-lab, cloud-lab).
- Registros: Zenodo concept DOI `10.5281/zenodo.23632019` (resolve para a versão mais recente), preprint `10.5281/zenodo.23330695`.

## 3. Lacunas por pilar

| Pilar | Estado | Lacuna |
| --- | --- | --- |
| 01 Core | parcial | sem gramática formal em arquivo (`.ebnf`); front-end monolítico |
| 02 Compiler | parcial | sem estágios separados (lexer/AST/semântica) como módulos |
| 03 Proof | **forte** | motor de prova não separado do motor de decisão |
| 04 Qiskit | parcial | apenas um backend; independência de fornecedor ainda é arquitetura, não código |
| 05 Validação | parcial | benchmarks permanentes e relatórios de baseline não formalizados |
| 06 Aplicações | parcial | 14 exemplos, nenhum dos três casos consolidados exigidos |

## 4. Executado nesta fase

- **Anti-replay no recibo** (severidade alta): nonce único de 16 bytes, sequência monotônica por corrente e `prev_sha3`, com `verifica_encadeamento()` e 4 testes (`tests/test_receipt_hardening.py`). Commit `78e0a2c`.

## 5. Números sem base reproduzível

As alegações da diretriz — 500.000 problemas, zero erros, 76,5% de redução computacional — **não têm ocorrência no repositório**. Não podem ir a documento público até existir dataset, baseline e relatório.

## 6. Próximos passos propostos

1. Formalizar a gramática em `docs/grammar/zyql.ebnf` a partir do parser atual (sem mudar sintaxe).
2. Separar `Decision Engine` e `Proof Engine` com interface estável e testes de contrato.
3. Escrever a errata do preprint sobre universalidade do conjunto de portas.
4. Consolidar três demonstrações com código, recibo e instruções de reprodução.

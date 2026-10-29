# Apps em producao (v1) — CPA-01 e QRS-01

Dois apps sobreviveram ao filtro da direcao (PUF e Policy Engine declinados em 2026-10-29).

## AuditKit — certificacao de entropia quantica (CPA-01)

`src/zyql_auditkit.py` · bateria: `tests/test_auditkit.py`

- Circuito: H em n qubits, medido -> n x shots bits por rodada.
- Testes declarados ANTES: monobit (z), runs (z), chi2 binario; alpha=0,01.
- Veredito trivalente: **1** certificado · **0** vies provado · **REFUSED** bits < 2048.
- Recibo selado SHA3-256 com counts + estatisticas + job_id.

**Hardware (2026-10-29, ibm_marrakesh, job `dbhpaomne4hc73bdbp7g`)**: 4096 bits,
z_monobit=-1,000, z_runs=-0,672, chi2=1,000 -> **1 certificado**.

## Quantum Regression Seal — gate de CI/CD (QRS-01)

`tools/regression_seal.py` · action: `.github/actions/regression-seal` · bateria: `tests/test_regression_seal.py`

- Compara a unitaria do circuito antes/depois do transformador, **ate fase global**.
- Pega o que a medicao nao pega: otimizacao que muda fase relativa (bug de fase 0,37 rad
  detectado; bug de porta rx(0,9) detectado; pipeline sao aprovado).
- Veredito: **1** selado · **0** regressao provada · **REFUSED** nao deu para compilar.
- Uso em outro repo: `uses: SerenaSolutions/zephirum-lang/.github/actions/regression-seal@main`

**Demo (2026-10-29)**: 3 circuitos de corpus; fase -> 0, porta -> 0, identidade -> 1.
Recibos em `experiments/qrs_20261029/`.

## Limites honestos

- CPA-01 valida a fonte de bits, nao a cadeia de custodia fisica do chip.
- QRS-01 compara unitarias exatas; circuitos com medida no meio exigem o espelho C+.

# Experimento: decisão auto-verificada em hardware — the provider_fez, 2026-10-29

Primeira execução da capacidade **self-verified device decision** (ver `docs/SELFVERIFIED.md`)
em QPU real, dentro do plano Open da a production superconducting QPU.

| Arquivo | Oráculo | Veredito | p0 | selfcheck | Lotes | job_id |
|---|---|---|---|---|---|---|
| `receipt_const1.json` | constante | **1** | 0.992 | 0.969 | 1/4 | `internal` |
| `receipt_balanced.json` | balanceado | **0** | 0.016 | 0.992 | 1/4 | `internal` |

- Circuitos por job: 4 lotes de decisão + 1 espelho (C†), 128 shots cada, n=3 qubits + ancilar.
- Custo: ~44 s de QPU no total.
- Selo: SHA3-256 sobre o payload (protocolo pré-declarado + contagens + veredito).
- Verificação: `python3 -c "import sys; sys.path.insert(0,'src'); from zyql_selfverified import verify_receipt; print(verify_receipt('experiments/selfcheck_the provider_fez_20261029/receipt_const1.json'))"`

Reprodução: `python3 -c "from zyql_selfverified import decide_selfverified; r=decide_selfverified('const1', qpu='the provider_fez', seal_path='selo.json')"` (exige `the provider_API_KEY` no ambiente).

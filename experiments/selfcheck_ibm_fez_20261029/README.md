# Experimento: decisão auto-verificada em hardware — ibm_fez, 2026-10-29

Primeira execução da capacidade **self-verified device decision** (ver `docs/SELFVERIFIED.md`)
em QPU real, dentro do plano Open da IBM Quantum.

| Arquivo | Oráculo | Veredito | p0 | selfcheck | Lotes | job_id |
|---|---|---|---|---|---|---|
| `receipt_const1.json` | constante | **1** | 0.992 | 0.969 | 1/4 | `dbhm3ao1h92s73821mm0` |
| `receipt_balanced.json` | balanceado | **0** | 0.016 | 0.992 | 1/4 | `dbhm3ik2d77s739d10j0` |

- Circuitos por job: 4 lotes de decisão + 1 espelho (C†), 128 shots cada, n=3 qubits + ancilar.
- Custo: ~44 s de QPU no total.
- Selo: SHA3-256 sobre o payload (protocolo pré-declarado + contagens + veredito).
- Verificação: `python3 -c "import sys; sys.path.insert(0,'src'); from zyql_selfverified import verify_receipt; print(verify_receipt('experiments/selfcheck_ibm_fez_20261029/receipt_const1.json'))"`

Reprodução: `python3 -c "from zyql_selfverified import decide_selfverified; r=decide_selfverified('const1', qpu='ibm_fez', seal_path='selo.json')"` (exige `IBM_API_KEY` no ambiente).

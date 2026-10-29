# Protocolos em hardware — ibm_marrakesh, 2026-10-29

| Protocolo | Medida | Resultado | job_id |
|---|---|---|---|
| P-10 fronteira clássica×hardware | TVD vs ideal, n=3..5 | 0.0139 / 0.0188 / 0.0183 | `dbhp6ks2d77s739d692g` |
| P-08 ZNE vs C† | p0 com e sem ZNE, n=4 | 0.0197 → **0.0116** (−41%); selfcheck 0.98 | `dbhp6ok2d77s739d6990` |

Reprodução: `python3 -c "from zyql_protocols import protocolo_p10; protocolo_p10(qpu='ibm_marrakesh', seal_path='s.json')"`

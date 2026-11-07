# Protocolos em hardware — the provider_marrakesh, 2026-10-29

| Protocolo | Medida | Resultado | job_id |
|---|---|---|---|
| P-10 fronteira clássica×hardware | TVD vs ideal, n=3..5 | 0.0139 / 0.0188 / 0.0183 | `internal` |
| P-08 ZNE vs C† | p0 com e sem ZNE, n=4 | 0.0197 → **0.0116** (−41%); selfcheck 0.98 | `internal` |

Reprodução: `python3 -c "from zyql_protocols import protocolo_p10; protocolo_p10(qpu='the provider_marrakesh', seal_path='s.json')"`

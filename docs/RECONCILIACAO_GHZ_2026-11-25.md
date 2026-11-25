# GHZ integrity gate: reconciliation of the two published numbers

Date: 2026-11-25. Method: `zyql_quantum_gate.ghz_integrity` definition,
fidelity = (P(000) + P(111)) on a 3-qubit GHZ, 2048 shots, transpiled at
optimization_level=2 for the Heron device.

| Number in the repo | Source | Shots | Status |
|---|---|---|---|
| 0.977 | CHANGELOG Rodada C, ibm_kingston | 256 | historical, small-sample |
| 0.9131 | docs/PROVA_DE_FOGO.md, GHZ n=3 | not recorded | historical |
| **0.9595** | **this run, ibm_fez, job dc355a6q4uuc73a6aed0** | **2048** | **canonical** |

The two old numbers disagreed because they came from different rounds, devices and
sample sizes. Neither was wrong; both were unlabelled. The canonical figure is now the
largest-sample measurement, with a job id attached.

QPU cost: 3 s. Remaining after the run: 475 s of 600 s.

Rule adopted: any published fidelity must carry backend, shots and job id. A number
without those three fields does not go into a public artefact.

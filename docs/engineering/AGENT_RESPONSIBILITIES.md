# Responsabilidades e fronteiras de arquivo (AGENT_RESPONSIBILITIES)

| Agente | Dominio | Arquivos de responsabilidade | Nunca toca |
|---|---|---|---|
| 00 chief-architect | coordenacao | docs/engineering/*, planejamento | codigo de produto |
| 01 veritas | matematica/logica | docs/ZSKC.md (pareceres), proofs | runtime |
| 02 quantum | circuitos/backends | conformance/, experiments/ | receipts |
| 03 hybrid | orquestracao | adapters, benchmarks | parser |
| 04 core | linguagem/runtime | src/, grammar | receipts |
| 05 red-team | testes adversariais | tests/adversarial/ | codigo de produto |
| 06 evidence | recibos/Z-QEA | receipts/, verificadores | matematica |
| 07 security | dependencias/CI | workflows, lockfiles | segredos (jamais) |
| 08 research | documentacao | docs/, CLAIMS.md | releases |

Delegacao vigente (issues abertas): WP2 corpus -> 05+04 (#146); WP5 precisao -> 01+03 (#147); WP1 adaptadores -> 02+03 (#148); WP3 VERITAS verifier -> 06+01 (#149); WP4 indice de evidencias -> 06 (#150); WP7 onboarding de testadores -> 08 (#151).

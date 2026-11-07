# Artefatos M1 / S2 / B46 / C3 — na casa certa

Movidos do repositorio-ponteiro para o repositorio oficial da linguagem.

- spec/ZYQL_SEMANTICA_M1_v1.md — semantica congelada dos 5 vereditos
- spec/receipt_v1.schema.json — recibo v1 legivel por maquina
- spec/m1_conformance_cases.json — 15 casos (9 executaveis hoje)
- security/policy_gate.py + test_s2_policy_gate.py — Policy Gate, 12/12 PASS
- proofs/C3_UNIVERSALIDADE.md + c3_universality_check.py — teorema: conjunto atual
  {H,X,Y,Z,CNOT} NAO e universal (n=1: 16; n=2: 72 de 720); exige T/Rz
- batteries/46_ml_decoder/ — decoder de IA auditado pela regua exata

Recibos: RECEIPT_46.json, RECEIPT_S2.json, RECEIPT_C3.json.

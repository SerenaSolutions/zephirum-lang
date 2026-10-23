# O núcleo quântico do ZEPHIRUM — o que é clássico e o que é quântico

Auditorias superficiais às vezes afirmam que "o ZEPHIRUM não tem núcleo quântico".
Este documento fixa a arquitetura real, verificável por anyone com os recibos.

## Arquitetura

**Camada clássica (host) — sim, é clássica, por design:**
- `src/zyql_lisp.py` — parser/interpretador Lisp (toda linguagem tem parser clássico)
- `src/battery_ci.py`, selagem Z-QEA — infraestrutura de recibos (SHA3-256 + ML-DSA-44)
- O *host* clássico monta, dispara e sela; não decide.

**Núcleo quântico (a decisão) — onde o veredito nasce:**
- `src/zyql_quantum_gate.py` — portas Deutsch-Jozsa trivalentes: um único oráculo
  (Uf|x> = (-1)^f(x)|x>) em regime de interferência; o veredito 1/0/REFUSED é LIDO da
  dominância estatística da medição (p0), não de um if clássico.
- `src/zquantum.py` — simulador state-vector para uso local/dev.
- Camada quântica opcional em OpenQASM 3 (regra da casa) e poliglota
  (Qiskit/Cirq/PennyLane/Braket concordam exatamente — ver SerenaSolutions/quantum-poc).

## Provas em silício (recibos selados, job IDs públicos)

1. **Rodada A** — ibm_fez (IBM Heron 156q), 512–16384 shots: vereditos trivalentes exatos.
2. **Rodada B** — ibm_kingston, shots 64/128/256/384, jobs reais:
   `dbdac41gv2cc738hnen0`, `dbdac47i0auc739521vg`, `dbdac4c24mrc73cl3ia0`,
   `dbdac4ni0auc73952200` — veredito `RODADA_B_VERIFICADA_TRIVALENTE_EXATO`,
   exato inclusive a 64 shots (recibo: `experiments/round_b_receipt.json`).
3. **Bateria trivalente em hardware** — job `dbbugbk24mrc73cif420` (3/3 PASS).
4. **Ánions S3** — fusão de par de qualquerons não-abelianos, ordem de trançado
   distinguível no silício (98,1% vs 95,8%, ibm_fez).
5. **Entropia quântica** — pool de 8192 bits medidos no ibm_marrakesh
   (job `dbcnmds24mrc73ck0p0g`), embutido na selagem dos recibos v2.

Todos verificáveis offline: `python3 scripts/receipt_explorer.py experiments/round_b_receipt.json`
(SHA3 recomputado + assinatura ML-DSA-44/FIPS 204 com chave pública embarcada).

## Onde o equívoco nasce

Se o auditor abrir só `zyql_lisp.py` (o parser) e `zquantum.py` (o simulador), vê software
clássico — correto, mas é o *host*. O veredito trivalente da casa nasce da interferência
medida (p0) e foi validado em processadores IBM Heron com job IDs selados
pós-quanticamente. Simulação é rotulada como simulação; hardware cita job. Nada executa
silenciosamente.

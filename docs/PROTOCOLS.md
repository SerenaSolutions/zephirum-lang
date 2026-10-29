# Protocolos para hardware IBM — defesa, filtro e execução

Triagem das 12 propostas (6 apps + 6 descobertas) para o plano Open da IBM Quantum.
Regra da casa: só entra em hardware o que tem protocolo declarado antes, orçamento
de shots explícito e recibo selado no fim.

## Apps (defesa e filtro)

| App | Defesa | Filtro | Estado |
|---|---|---|---|
| AuditKit (entropia certificada) | Recibo + witness substituem "confie que é aleatório" por evidência de viés < ε | B2B lento, exige piloto | especificado |
| Quantum Regression Seal (CI de compiladores) | Dor universal: miscompilação silenciosa; C† roda em 128 shots | pronto para demo de 1 página | **ativo** (selfcheck) |
| Quantum PUF (fingerprint de chip) | TVD como identidade física | exige baseline de calibração | parqueado |
| Policy Engine (bancos/farma) | witness como gate de compliance replayable | depende de adoção | especificado |
| Seguro de "vantagem quântica" | — | mercado inexistente | **morto** |
| Playground Enterprise | camada comercial do que já existe | depois de PMF | parqueado |

## Descobertas

| # | Protocolo | Viabilidade Open | Ação |
|---|---|---|---|
| P-07 | Refusal Topology (ruído não-markoviano) | 20 dias de coleta | issue + script |
| P-08 | ZNE vs C† no mesmo circuito | 1 job, ~8k shots | **rodar hoje** |
| P-09 | KCBS contextual com REFUSED | 5 qubits, 25 contextos | issue |
| P-10 | Fronteira MPS (n=12 local) vs hardware (n=3..5) | 1 job, ~12k shots | **rodar hoje** |
| P-11 | T-state com verificação C† | — | **DECLINADO (direção, 29/10)** |
| P-12 | Blind DJ (deleg. verificável, toy n=3) | — | **DECLINADO (direção, 29/10)** |

## Orçamento

Plano Open: 10 min de QPU/mês. Hoje: P-08 (4 circuitos × 2048) + P-10
(3 circuitos × 4096) ≈ 25k shots em 4-5 qubits — dentro do horário de fila baixa.
Regra de silêncio vale para o PR do ecossistema; nada aqui toca o qiskit/ecosystem.

## Defesa comum (por que isso é ciência e não demo)

1. **Protocolo antes da execução** — epsilon, alpha, shots e regra de parada são
   selados no recibo antes de qualquer job.
2. **Referência clássica honesta** — MPS/statevector dão a distribuição ideal;
   TVD mede o dispositivo contra ela, não contra si mesmo.
3. **Abstenção como resultado** — REFUSED é dado publicável, não fracasso.
4. **Reprodutibilidade** — job_id + selo SHA3 permitem re-verificação por terceiros.

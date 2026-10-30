# WORLD-3 — rodada revisada pela auditoria Nemotron (2026-10-29)

Pre-registro selado ANTES da execucao (protocolo + bandas + regra de agregacao).
Backend: ibm_marrakesh. 3 repeticoes independentes, 8192 shots, optimization_level=3,
controle SPAM por circuito idle, profundidade e portas 2q no recibo.

| Protocolo | Metricas (3 reps) | Veredito agregado |
|---|---|---|
| W-01 caminhada quantica | TVD 0.198 / 0.283 / 0.279; profundidade 320, 85 portas 2q | **REFUSED** |
| W-02 analogo HOM (sqrt-SWAP) | visibilidade 0.953 / 0.952 / 0.951; profundidade 16, 3 portas 2q | **1 CERTIFICADO** |
| W-03 Grover 3q | p 0.782 / 0.776 / 0.760 vs 0.125 classico (ideal 0.945) | **REFUSED** |
| SPAM (controle) | erro de leitura 1.07% / 1.10% / 0.89% | abaixo do limite 10% |

Jobs: dbhuqlg1h92s7382hn10 (rep1), dbhuqsmne4hc73bdm41g (rep2), dbhur1lep8hs73amuin0 (rep3).

Leitura honesta: W-02 e reprodutivel e certificado; W-01 falha por custo de roteamento
(85 portas 2q em 4 qubits); W-03 mostra amplificacao ~6x sobre o classico, mas abaixo da
banda de certificacao declarada (0.85) — fica como PROVISORIO, nao estabelecido.

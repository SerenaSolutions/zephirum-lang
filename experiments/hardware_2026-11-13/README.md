# Rodada em hardware — 2026-11-13

Job unico na IBM Quantum, backend `ibm_fez`, 2048 shots por circuito.
Conta: plano aberto. Estes recibos existem para que qualquer pessoa re-derive o
veredito a partir das contagens e confira o selo.

| circuito | contraste | p_hat | eps (Hoeffding, delta=0.05) | veredito |
|---|---|---|---|---|
| dj_constante | p(q0=1) | 0.0029 | 0.0300 | 0 |
| dj_balanceado | p(q0=1) | 0.9868 | 0.0300 | 1 |
| bell_Z | P(paridade igual) | 0.9458 | - | correlacionado |
| bell_X | P(paridade igual) | 0.9590 | - | correlacionado |

Regra aplicada: veredito 1 se p_hat - eps > 0.5; 0 se p_hat + eps < 0.5; REFUSED fora
disso. O selo e SHA3-256 do JSON canonico sem o campo selo_sha3_256.

Verificacao: `python tools/zqea_verify.py experiments/hardware_2026-11-13/recibo_*.json`

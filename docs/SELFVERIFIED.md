# Decisão auto-verificada no dispositivo (self-verified device decision)

**Capacidade nova do ZYQL (2026-10-29)** — a decisão trivalente executada **na QPU**, com a própria QPU certificando a execução.

Até aqui o runtime `decide()` decidia no kernel local (statevector); o hardware era usado em experimentos de shots fixos. Este módulo leva a semântica trivalente para o dispositivo com três garantias novas:

## 1. Auto-verificação (espelho C†)

O mesmo job inclui o circuito da decisão **e o seu inverso**. O estado final medido deve ser `|0…0⟩`; a taxa de zeros observada é a métrica de auto-verificação e vai carimbada no recibo como `selfcheck_p0`. Abaixo do limiar declarado (`selfcheck_min`, padrão 0.80) o resultado é **REFUSED** — a linguagem se abstém quando não consegue provar que executou o circuito pretendido.

## 2. Evidência sequencial com regra declarada

A decisão vai em lotes. A regra de parada (alpha-spending geométrico) é **declarada antes da execução**, no próprio recibo:

- `alpha_k = alpha / 2^k` por lote `k`
- fronteira `t_k = sqrt( ln(2/alpha_k) / (2·N_k) )`
- cruzar `0.5 ± t_k` decide; esgotar os lotes sem cruzar ⇒ **REFUSED (inconclusivo)**, sem retry silencioso.

## 3. Recibo auditável

O recibo carrega protocolo pré-declarado, contagens por lote, selfcheck, veredito, erro limite (Hoeffding), QPU e `job_id`, selado com SHA3-256 (integridade de conteúdo, não autoria).

## Semântica

Deutsch–Jozsa decide **constante vs balanceado**:

| Veredito | Significado |
|---|---|
| `1` | oráculo constante (f = 0 ou f = 1) |
| `0` | oráculo balanceado |
| `REFUSED` | selfcheck abaixo do limiar, ou evidência inconclusiva após os lotes |

## Resultado em hardware real (ibm_fez, 2026-10-29)

| Oráculo | Veredito | p0 | selfcheck | Lotes | Shots | job_id |
|---|---|---|---|---|---|---|
| constante | **1** | 0.992 | 0.969 | 1 | 128 | `dbhm3ao1h92s73821mm0` |
| balanceado | **0** | 0.016 | 0.992 | 1 | 128 | `dbhm3ik2d77s739d10j0` |

Recibos selados em `experiments/selfcheck_ibm_fez_20261029/`. Custo total: 2 jobs × 5 circuitos × 128 shots, ~44 s de QPU.

## Limites honestos

- Sem correção de erro: útil na banda de poucos qubits.
- Ruído correlacionado entre shots está **fora do escopo declarado**.
- O espelho verifica a execução (transpilação/roteamento/calibração), não a correção lógica do oráculo sintetizado.
- `REFUSED` é abstinência honesta, não erro: a linguagem prefere não decidir a decidir mal.

## Uso

```python
from zyql_selfverified import decide_selfverified

# local (Aer)
r = decide_selfverified(kind="const1", n=3, seal_path="selo.json")

# hardware real
r = decide_selfverified(kind="balanced", n=3, qpu="ibm_fez", seal_path="selo_hw.json")
print(r.verdict, r.p0, r.selfcheck_p0, r.job_id)
```

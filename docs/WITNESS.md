# Refusal Witness — abstenção com prova

A pergunta que todo resultado quântico esconde: **"o dispositivo executou o que eu pedi?"**
Esta primitiva responde com semântica trivalente e recibo selado.

## Semântica

| Veredito | Significado |
|---|---|
| **1** CERTIFICADO | A TVD entre a distribuição ideal (referência exata via statevector) e a medida no dispositivo cabe em `epsilon`, com confiança `1-alpha`. Decisões subsequentes são sustentáveis. |
| **0** REPROVADO | A TVD **prova** desvio além de `epsilon`. O dispositivo não executou o pretendido — qualquer veredito dele não é sustentável. |
| **REFUSED** | Evidência insuficiente: o intervalo estatístico cruza `epsilon`. Não afirma fidelidade nem desvio. **Mais shots são necessários** — a abstenção dirige a aquisição de evidência. |

Limite declarado **antes** da execução (Hoeffding + união sobre K saídas):

```
delta = sqrt(K * ln(2/alpha) / (2*N))
upper = tvd_hat + delta ;  lower = max(0, tvd_hat - delta)
upper <= epsilon -> 1   |   lower > epsilon -> 0   |   senão -> REFUSED
```

## Uso

```python
from zyql_witness import witness, verify_receipt
r = witness("balanced", shots=8192, qpu="ibm_marrakesh", seal_path="selo.json")
# Witness(verdict='1', mode='CERTIFICADO', tvd=0.0198, delta=0.0509, ...)
verify_receipt("selo.json")  # -> True
```

## Prova em hardware (2026-10-29)

| Dispositivo | Shots | TVD | delta | Janela | ε | Veredito | job_id |
|---|---|---|---|---|---|---|---|
| ibm_fez | 4096 | 0.0317 | 0.0719 | [0.000, 0.104] | 0.10 | **REFUSED** | `dbhn296ne4hc73bd7u1g` |
| ibm_marrakesh | 8192 | 0.0198 | 0.0509 | [0.000, 0.071] | 0.10 | **1 CERTIFICADO** | `dbhn8hs2d77s739d32lg` |

O primeiro voo **absteve-se** com a evidência disponível; o segundo, com o dobro de shots,
certificou. Esse é o desenho funcionando: recusar quando não sabe, e não adivinhar.

## Limites honestos

- O delta é conservador (Hoeffding + união): a banda pode ser apertada com testes
  exatos (qui-quadrado) — trabalho futuro.
- A referência ideal cobre circuitos simuláveis por statevector (≤ ~20 qubits).
  Para circuitos maiores, a referência deve vir do backend MPS.
- TVD mede fidelidade de **distribuição**, não de fase global nem de coerência entre execuções.

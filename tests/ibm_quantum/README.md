# Suíte de Conformidade ZCA — IBM Quantum

Estado de maturidade: **IMPLEMENTADO** (validado em hardware real e simulador).

Suite de conformidade do ZCA (Zephirum Compilation Algorithm) para o degrau
quântico da escada certificada do kernel ZYQL. Executa quatro testes e emite
recibo de integridade por teste (SHA3-256 do payload, job_id, backend, shots,
p_hat, banda, margem, decisão e regra aplicada).

## Protocolo (régua da casa)

| Teste | Cena | Veredito esperado |
| :--- | :--- | :--- |
| 1 | DJ constante | `0` (fora da banda, inferior) |
| 2 | DJ balanceada | `1` (fora da banda, superior) |
| 3 | Controle Bell Phi+ (bases Z e X) | correlação em ambas as bases ≥ 0.70 |
| 4 | Sentinela de drift | janelas 1ª/2ª metade do job |

Resultado por teste: `PASS` / `FLAGGED` — nunca escondido. A sentinela de drift
sinaliza assimetria entre janelas do job (ruído de leitura assimétrico típico de
hardware real); um alerta de drift não invalida o veredito quando a estimativa
inteira permanece fora da banda declarada.

## Uso

```bash
# simulador local (sem dependência externa)
python3 tests/ibm_quantum/zca_conformidade_ibm.py

# hardware real (requer qiskit-ibm-runtime e conta IBM Quantum)
QISKIT_IBM_TOKEN=... python3 tests/ibm_quantum/zca_conformidade_ibm.py --live
```

O token é lido exclusivamente de variável de ambiente (`QISKIT_IBM_TOKEN` ou
`API_KEY`). Nunca comitar tokens.

## Evidências

- `zca_conformidade_sim.json` — recibos da validação em simulador local (4/4 PASS).
- `zca_conformidade_live.json` — recibos da validação em hardware real:
  backend `ibm_fez` (156 qubits), 4 PASS / 0 FLAGGED, com disparo da sentinela
  de drift no teste 2 mantendo o veredito (2026-10-13).
- `zca_live_20261013.log` — log de execução da rodada live.

## Recibo de integridade do conjunto

SHA3-256 dos arquivos desta pasta no momento da submissão — ver commit
associado. Cada recibo interno carrega seu próprio SHA3-256 do payload.

## Gap vs referência

Suite cobre os degraus quânticos do kernel (DJ, Bell, drift). Não cobre ainda:
cláusulas v1.3 (K-SHADOW, K-BUDGET, K-GAP, K-CAL), camada ZCA/NEXA de
eliminação, nem circuitos com mais de 156 qubits. Maturidade dos degraus não
cobertos: ESPECIFICAÇÃO.

Autoria: Serena Solutions.

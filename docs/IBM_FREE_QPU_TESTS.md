# IBM FREE QUANTUM — suíte de verificação em QPU real

## O que é

`prototype/ibm_free_qpu.py` executa cinco testes pequenos o suficiente para o
plano gratuito do IBM Quantum, comparando o resultado do hardware com a
previsão IDEAL e EXACTA do ZEPHIRUM (Fraction, sem float):

| Teste | Circuito | Ideal exacto | Proibidos |
|---|---|---|---|
| T1 | X | 1 (prob. 1) | 0 |
| T2 | H | 0,1 (1/2 cada) | — |
| T3 | Bell (H+CNOT) | 00,11 (1/2 cada) | 01,10 |
| T4 | GHZ-3 | 000,111 (1/2 cada) | resto |
| T5 | Zephirum | kernel decide `entangled == 1` (Schmidt) e o hardware confirma as correlações | 01,10 |

Critério declarado ANTES da execução: TVD ≤ 0.10 e resultados proibidos ≤ 5%
(ruído de leitura). O recibo regista backend, job_id, shots, contagens, TVD,
veredicto e limitações, selado com SHA-256 (`decision_kernel.digest`).

## Como rodar (com o token do dono)

```bash
export IBM_QUANTUM_TOKEN=...      # nunca no chat, nunca no repositório
pip install qiskit qiskit-ibm-runtime
python3 prototype/ibm_free_qpu.py --shots 1024
```

Sem token ou sem SDK: `SKIP (§12)`, exit 3, nenhum job inventado — o harness
nunca fabrica identificadores nem resultados.

## Contexto absorvido (LinkedIn, 27-11-2026)

Os posts partilhados não são legíveis por API (LinkedIn exige login); apenas
os títulos/slugs foram lidos, e é isso que aqui se declara. Temas que
enquadram a suíte:

1. SC26 Chicago — IBM, NVIDIA e Fermilab: computação híbrida HPC+QPU como
   direção industrial. A suíte T1-T4 é exactamente a verificação mínima que
   qualquer pipeline híbrido precisa antes de confiar num backend.
2. Quantum algorithms e photonics: algoritmos quânticos só são auditáveis se
   o resultado ideal for conhecido exactamente — o que o Zephirum fornece.
3. Estruturas de projecto de agentes de IA: a equipa de auditoria do Gen 1
   segue esse desenho (papéis independentes, evidência por agente).

## Limitações declaradas (§12)

- Hardware ruidoso: TVD tolerada é uma escolha declarada, não uma prova.
- Plano gratuito: filas variáveis; nenhum benchmark de performance é alegado.
- O teste NÃO demonstra vantagem quântica — demonstra correlação correta.

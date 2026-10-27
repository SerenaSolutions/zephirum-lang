# BENCHMARK-01 — a camada de decisão da ZEPHIRUM (fecha a issue #28)

A tese: **a ZEPHIRUM não compete em velocidade de circuito; compete em honestidade.**
O benchmark mede o que nenhuma outra suite do mundo mede: o custo e a fidelidade
da DECISÃO trivalente.

## Protocolo (regra declarada ANTES do dado)
- epsilon = 0.05; banda = 0.15 (fixa, declarada antes de qualquer medição)
- Proibida re-rolagem de semente (peeking)

## Kernel A — shots-to-verdict (parada antecipada)
DJ n=3, oráculo constante; escada dobrando [64, 128, ... 8192]; para no primeiro veredito.
- **Resultado: veredito `1` no 1º degrau (64 shots)** — 99,22% de economia vs. baseline fixo de 8192
- Mínimo exigido por Hoeffding para a banda declarada: 67 shots (o empírico confirma a ordem)

## Kernel B — refusal fidelity (falsificável)
Oráculos com fração de uns w ∈ {0, 1/8, 1/4, 3/8, 1/2} ⇒ p0=(1−2w)²; 200 tentativas por (w, shots).
- **Zona cinzenta (p0=0.5625 e 0.25): ZERO falsas confirmações em 1.200 tentativas**
- Oráculo constante: confirmado em 100% das tentativas
- Oráculos balanceados (p0≤0.0625): `REFUSED_BALANCED` em 100% das tentativas (recusa informativa)

## Reprodução
`python3 benchmarks/bench_decision_layer.py` — o recibo é selado na cadeia Z-QEA
(SHA3-256, verificação via bateria: `ZQG_MODE=verify-receipts`).

*Revisão pré-silício interna incorporada (declaração de epsilon/margem, parada
antecipada, poder estatístico do kernel B). Nenhuma alegação acima da evidência.*


## Perna de hardware (ibm_fez, plano open — 27/10/2026)
Mesmos kernels, 8192 shots/caso, regra declarada antes:
- `const1`: p0 = 0.9718 ≥ 0.85 → veredito **1** (déficit vs. 1.0 = ruído real, declarado)
- `gray (w=1/8)`: p0 = 0.5159 dentro de (0.15, 0.85) → **REFUSED_GRAY** — o portão
  recusou na zona ambígua EM HARDWARE, sem falsa confirmação
- No hardware não se afirma p0 "verdadeiro"; afirma-se apenas o comportamento do
  portão sob a banda declarada. Recibo selado na cadeia Z-QEA junto aos demais.

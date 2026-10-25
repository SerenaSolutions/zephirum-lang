# -*- coding: utf-8 -*-
"""Métrica m50 — compromisso público de melhoria do modo de falha dominante.

**Modo de falha dominante do ciclo ZEPHIRUM → QPU (evidência da Rodada H,
24/10/2026): decoerência correlacionada.** GHZ de profundidade 16 no
supercondutor devolveu fidelidade 0.6118 < guarda 0.80 → REFUSED
DEVICE_DECOHERED, com curva de decoerência visível (n=12 → 0.7595;
n=16 → 0.6118). Leitura trivalente e latência de selo não produziram
recusas na mesma rodada: decoerência é a única falha que escala com a
profundidade do problema — é o muro entre a casa e circuitos maiores.

## A métrica única

    m = 1 − F_GHZ(16)

Infidelidade do estado GHZ de 16 qubits sob protocolo selado, **medição
crua de hardware (sem mitigação)** — mitigação é reportada à parte e não
entra no m.

- **Baseline selado:** m₀ = 0.3882 (24/10/2026, recibo c8182223 encadeado
  na cadeia Z-QEA; backend identificado dentro do recibo selado)
- **Compromisso:** m ≤ 0.194 (queda de 50%) até 25/04/2027
- **Bônus embutido:** F_GHZ(16) ≥ 0.806 significa que o REFUSED de hoje
  vira ACCEPTED **com o mesmo protocolo** — zero espaço para mudar regra
  no meio do caminho.

## Protocolo (selado antes de cada medição)

1. `protocol_seal` da spec: circuito GHZ-16, shots, epsilon, banda
   Hoeffding, stopping rule fixa.
2. Execução no hardware; `stopping_rule_check` amarra o recibo de
   execução ao protocolo selado (H11).
3. Fidelidade reportada pelo runtime; m = 1 − F; recibo Z-QEA encadeado.
4. Cada medição entra no registro com data, m e link do recibo — a curva
   responde com dados, não com opinião.

## Falsificabilidade

Se em 25/04/2027 a cadeia de recibos não mostrar m ≤ 0.194, o
compromisso **falhou publicamente** — e a linha do recibo estará lá para
qualquer um verificar. Nenhum número de marketing: só medição selada.

# Auditoria de hardware real — 16/11/2026

Job `dbtk8ob2kf8s73c990jg` no QPU `ibm_marrakesh` (156 qubits, supercondutor), 1024 shots por circuito, primitiva `sampler` V2, circuitos transpilados para os portões nativos do alvo (`cz, id, rx, rz, rzz, sx, x`).

## O que foi executado

| Circuito | Profundidade | Concordância entre bits | Intervalo exato (95%) | Veredito ao limiar 0,90 | Recibo |
|---|---|---|---|---|---|
| Bell (2 qubits) | 1 CZ | 92.48% | 0.9069 a 0.9402 | INCONCLUSIVE | verifica: True |
| GHZ-6 (6 qubits) | 5 CZ | 78.91% | 0.7628 a 0.8137 | 0 | verifica: True |

Diferencial de profundidade: **13.57 pontos percentuais** entre 1 CZ e 5 CZ.

## O que isso prova, e o que não prova

Prova que o decisor funciona com dado sujo de hardware real. Com 92,48% de concordância e erro padrão de 0.0424, o limite inferior fica em 0.9069, abaixo do limiar de 0,90. O sistema devolveu `INCONCLUSIVE` em vez de afirmar `1`. Essa é a propriedade que interessa: na fronteira, o ZEPHIRUM recusa em vez de exagerar.

Prova também que a deterioração com profundidade é mensurável e entra no recibo: 13,57 pontos percentuais a menos em GHZ-6, com o veredito caindo para `0`, ou seja, o hardware não sustenta o limiar declarado.

Não prova equivalência semântica da linguagem, que é medida de software (item 1 da bateria, contra Cirq, fidelidade 1,0). Não prova custo de fila paga, porque o plano é gratuito. Não prova nada sobre outro provedor.

## Defeito encontrado no caminho

O núcleo chama o terceiro valor de `INCONCLUSIVE` e 38 módulos chamam de `REFUSED`. O STARGATE aceita apenas `{1, 0, REFUSED}`. Com este job, o terceiro valor saiu do núcleo em dado real e seria recusado pelo painel. É inconsistência de vocabulário, com impacto direto em observabilidade.

## Como reproduzir

```
python experiments/prova_2026_11_16/hardware/ibm.py     # cliente da API v1
python experiments/prova_2026_11_16/prova.py            # bateria de software
```

Credencial: `IBM_API_KEY` no ambiente. O Cloudflare da IBM bloqueia a assinatura TLS do `urllib` (erro 1010); o cliente usa `curl`.

## Estado da auditoria completa

11 itens PASS em software, 1 falha real (vocabulário do terceiro valor), 5 bloqueados por dependerem de gente ou de contrato. Hardware: 1 job real, 2 circuitos, 2 recibos verificados.

# Power analysis da agregacao trivalente (3 repeticoes)

Calculado por Monte Carlo em `tools/power_analysis.py` (20.000 experimentos de 3 repeticoes,
8192 shots, alpha = 0,05). Todos os numeros abaixo saem da execucao, nao de estimativa.

## As duas regras

| Regra | Como certifica |
|---|---|
| **R1** (a que os recibos refletem) | estimativa da media passa da banda |
| **R2** (a da testemunha Deutsch-Jozsa) | intervalo inteiro fica do lado certo da banda |

## W-02 visibilidade (banda: V >= 0,70) — delta = 0,0212 com K = 2

| V verdadeiro | P(certificar) R1 | P(certificar) R2 |
|---|---|---|
| 0,69 | 0,0000 | 0,0000 |
| **0,70 (na banda)** | **0,1205** | 0,0000 |
| 0,72 | 1,0000 | 0,0658 |
| 0,75 | 1,0000 | 1,0000 |
| 0,90 | 1,0000 | 1,0000 |

## W-01 TVD (banda: TVD <= 0,10) — delta = 0,0600 com K = 16

| TVD verdadeiro | P(certificar) R1 | P(certificar) R2 |
|---|---|---|
| 0,06 | 1,0000 | 0,0000 |
| 0,09 | 0,9975 | 0,0000 |
| **0,10 (na banda)** | **0,1273** | 0,0000 |
| 0,12 | 0,0000 | 0,0000 |

## O que isso prova

**R1 nao tem garantia de cobertura.** Um dispositivo exatamente na banda certifica em 12% das
vezes (W-02) e 13% (W-01). Nao e "poder alto": e ausencia de garantia. Nenhum alpha foi
declarado nos recibos do WORLD-3, e essa e a falha estatistica real do experimento.

**R2 com Hoeffding e conservador demais para TVD.** Com K = 16 (4 qubits), delta = 0,06: para
certificar TVD <= 0,10 seria preciso estimativa <= 0,04. Com 8192 shots, W-01 **nunca** poderia
certificar sob R2. Para caber num vao de 0,04 seriam necessarios
`ceil(16*ln(40)/(2*0,04^2)) = 18.444 shots`, cerca de 2,25x o usado.

## O que o protocolo passa a declarar

1. **alpha = 0,05** explicito, por repeticao, e regra de agregacao AND nas 3.
2. **Regra de veredito = R2** (intervalo), nao estimativa pontual. E o que a testemunha DJ ja faz.
3. **W-02:** potência de 1,00 a partir de V = 0,75; nada certifica abaixo de 0,72. Isso e
   declarado, nao escondido. O 0,952 medido esta muito acima da zona de duvida.
4. **W-01:** com a banda de 0,10 e 8192 shots, certificacao e impossivel sob R2. Ou se sobe
   para 18.444 shots, ou se troca Hoeffding por bootstrap com justificativa empirica. Enquanto
   isso, a banda de 0,10 para W-01 deve ser retirada do texto como inalcancavel no desenho atual.

## Correcao ao parecer do Nemotron-3 Ultra

| Item do parecer | Verificacao | Situacao |
|---|---|---|
| delta = 0,0173 para alpha = 0,05 | `sqrt(ln(2/0,05)/(2*8192))` = **0,0150**; com K=2, 0,0212 | **errado** |
| Modela limiar deslocado por delta como "a regra" | nossos recibos usam estimativa pontual contra a banda | **regra trocada** |
| sigma de TVD por aproximacao binomial | TVD nao e proporcao; variancia vem de bootstrap | **metodo inadequado** |
| "power analysis inexistente" | confirmado | **correto** |
| "com n=3 a regra aceitaria >30% de falha em >65% dos casos" | R1 na banda certifica 12-13%, nao 65% | **numero errado, direcao certa** |

A direcao do alerta dele estava certa: sem alpha declarado e sem regra intervalar, o
"certificado" do W-02 nao tem base estatistica formal. Os numeros, nao.

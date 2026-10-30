# Capítulo 3 — Hipótese: precisamos computar isto?
*ZEPHIRUM — A Computação Antes da Execução | Parte I: A Pergunta*

## 3.1 Nível 1 — Um juiz antes do disparo

Se a observação do capítulo 2 está correta, a pergunta seguinte é inevitável: por que não consultar um juiz de necessidade antes de disparar a execução?

A hipótese deste livro é que esse juiz pode existir como parte formal, verificável e barata da própria linguagem. Com isso, a pergunta de engenharia muda de lugar: deixa de ser "qual máquina resolve isto mais rápido?" e passa a ser "isto precisa ser executado, e por quê?".

## 3.2 Nível 2 — Enunciado e compromissos

**Hipótese.** Para uma classe mensurável de perguntas de engenharia, existe um procedimento que decide, com custo muito inferior ao da execução, se a execução é necessária — e esse procedimento pode ser formalizado, tipado e auditado.

Três compromissos decorrem do enunciado, e cada um tem consequência de projeto:

- **honestidade** — quando o juiz não sabe, ele declara que não sabe; não escolhe entre sim e não por conveniência. Consequência: o sistema precisa de um terceiro valor, o que motiva o capítulo 10.
- **auditabilidade** — cada veredito deixa recibo verificável por terceiro, com integridade e autoria. Consequência: capítulo 12.
- **economicidade** — o juiz precisa custar menos do que economiza. Consequência: a escada de custo do capítulo 11 e o NetBenefit do capítulo 15.

Os três compromissos são conflitantes em tensão real: um juiz mais rigoroso custa mais e recusa mais; um juiz mais barato erra mais. O contrato do capítulo 8 é o instrumento que explicita essa troca em vez de escondê-la.

## 3.3 Nível 3 — A objeção da indecidibilidade

O leitor formado em teoria da computação reconhecerá o problema imediatamente: em geral, decidir se uma computação é necessária é indecidível, por redução ao problema da parada [3]. A hipótese, tomada sem qualificação, seria falsa.

A resposta é a qualificação, e ela é o coração do livro: **não se decide no caso geral; decide-se sob contrato**. A tolerância $\varepsilon$ e o orçamento $B$ restringem a jurisdição a um subconjunto no qual a decisão é possível. Formalmente, o juiz resolve

$$ d^{*} \;=\; \arg\min_{d \in M}\; c(d) \quad \text{sujeito a} \quad \delta(d) \le \varepsilon,\;\; c(d) \le B $$

onde $c(d)$ é o custo e $\delta(d)$ o risco do decisor $d$. Se o conjunto viável é vazio, o veredito é REFUSED. A existência de $d^{*}$ não é garantida; a honestidade sobre sua inexistência, sim.

Essa formulação tem precedente direto na lógica de três valores de Kleene [4], no tratamento de informação incompleta em bancos de dados [5] e na disciplina de certificados executáveis [6]. O que se propõe aqui é o uso dessas três tradições como contrato de primeira classe numa linguagem executável.

## 3.4 Como a hipótese pode ser falsificada

Uma hipótese que não pode falhar não é hipótese. Três previsões são testáveis, e o capítulo 6 descreve o teste de cada uma:

| Previsão | Teste | Resultado observado |
|---|---|---|
| decisões honestas não erram | 500 problemas com verdade calculada à parte | 0 respostas erradas em 471 decididas |
| certificados não podem ser forjados | 20 certificados adulterados | 20 rejeitados |
| a recusa aparece quando deve | casos sem informação suficiente | 29 recusas declaradas |

Se qualquer previsão falhasse, a arquitetura deveria ser abandonada na forma atual. O capítulo 6 relata o que falhou parcialmente, inclusive o que doeu: o custo de execução em três casos ficou acima do previsto, e o NetBenefit agregado, embora positivo, não foi positivo em todos os casos.

## Exercícios

1. Por que a honestidade é requisito de projeto, e não virtude opcional, num juiz de necessidade?
2. Enuncie um caso em que o juiz contratual responderia "não precisa executar" e outro em que responderia REFUSED. O que muda no sistema entre os dois?
3. A hipótese seria falsa sem a cláusula "sob contrato". Explique a redução ao problema da parada que sustenta essa afirmação.

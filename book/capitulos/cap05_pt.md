# Capítulo 5 — Anterioridade: as vinte linhas que já existiam
*ZEPHIRUM — A Computação Antes da Execução | Parte II: O Tribunal da Ciência*

## 5.1 Nível 1 — O tribunal

Antes de dizer "isto é novo", um livro honesto senta no banco dos réus. Este capítulo é o tribunal. O veredito, antecipado: **quase todas as peças, isoladas, já existiam**. O que se propõe é a composição — e o capítulo 7 delimita o que ela acrescenta e o que não acrescenta.

## 5.2 Nível 2 — Inventário, sem ornamentos

| # | Linha existente | O que já faz | Referência |
|---|---|---|---|
| 1 | avaliação preguiçosa | adia a computação até o valor ser necessário | [35] |
| 2 | curto-circuito booleano | evita avaliar o segundo operando | linguagens C e derivadas |
| 3 | propagação de restrições | poda domínios antes de buscar | década de 1960 em diante |
| 4 | lógica ternária de Kleene | propaga "desconhecido" sem contaminar | [4] |
| 5 | NULL relacional | representa ausência em bancos de dados | [5] |
| 6 | proof-carrying code | anexa prova verificável ao código | [6] |
| 7 | compilador verificado | garante preservação semântica | [7] |
| 8 | IR de compilador | separa camadas com verificação | [8] |
| 9 | linguagens quânticas de alto nível | tipam qubits e medição | [9, 33] |
| 10 | OpenQASM 3 | assembly quântico padronizado | [10] |
| 11 | Qiskit | compilação e execução em hardware real | [11] |
| 12 | early exit / branch and bound | abandona ramos sem solução | literatura de otimização |
| 13 | decisão condicionada por medição | controle clássico sobre circuito | [9, 10] |
| 14 | mitigação de erro (ZNE) | extrapola a ruído zero | [19] |
| 15 | simulação por MPS | simula estados pouco emaranhados | [20] |
| 16 | intervalos de confiança exatos | quantifica incerteza de proporção | [26, 27] |
| 17 | controle de falsa descoberta | corrige comparações múltiplas | [29] |
| 18 | hash criptográfico e assinatura | integridade e autoria | [23, 25] |
| 19 | audiência de recibos append-only | ordem temporal auditável | prática de ledger |
| 20 | verificação independente de resultado | terceiro reexecuta e confere | [6, 7] |

Os algoritmos que justificaram o campo — Deutsch-Jozsa [12], Grover [13] e Shor [14] — aparecem aqui como referência de escala, não como objeto de reivindicação.

Nenhuma dessas linhas, isolada, entrega um juiz de necessidade **tipado na linguagem, contratual, com abstenção declarada e recibo verificável em cada decisão**.

## 5.3 Nível 3 — O critério de novidade

A literatura de métodos científicos distingue invenção, composição e integração. Invenção introduz um mecanismo inexistente; composição combina mecanismos conhecidos produzindo propriedade emergente; integração apenas reúne peças sem propriedade nova.

A posição defendida neste livro é a de **composição**, e ela se sustenta em uma propriedade que nenhuma das vinte linhas tem sozinha: o veredito de necessidade é parte do contrato da linguagem, e a abstenção é valor de primeira classe com motivo auditável. Um leitor cético pode argumentar que a propriedade é engenharia, não ciência. O capítulo 14 responde com números, inclusive os desfavoráveis.

## 5.4 O que a anterioridade obriga

O inventário impõe três obrigações ao projeto, e todas estão refletidas no restante do livro:

1. **não reivindicar primazia** sobre técnicas isoladas — daí o capítulo 7 existir;
2. **citar a dívida** em cada capítulo em que uma técnica alheia for usada;
3. **provar o que afirma** sobre a composição, com experimento e recibo, não com retórica.

## Exercícios

1. Escolha três linhas do inventário e explique por que nenhuma resolve sozinha o problema do juiz de necessidade.
2. Qual é a diferença entre proof-carrying code [6] e o recibo desta arquitetura? O que a segunda tem que a primeira não tem?
3. Discuta: composição com propriedade emergente é ciência ou engenharia? Defenda as duas posições em um parágrafo cada.

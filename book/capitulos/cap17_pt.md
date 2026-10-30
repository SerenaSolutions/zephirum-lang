# Capítulo 17 — Futuro: neutralidade tecnológica como método
*ZEPHIRUM — A Computação Antes da Execução | Parte V: O Horizonte*

## 17.1 Nível 1 — O quântico como consequência

A pergunta natural, ao final de um livro sobre computação quântica, é: quando o quântico vence? Este livro responde de modo desconfortável para os dois lados da expectativa: **quando o contrato mandar**.

## 17.2 Nível 2 — Os quatro horizontes

| Horizonte | O que muda | O que a arquitetura já suporta |
|---|---|---|
| hoje | QPU ruidosa, poucos qubits, custo alto | recusa declarada, mitigação [19], simulação [20] |
| curto prazo | correção de erro parcial, mais profundidade | bandas por protocolo, recibos com métricas de sistema |
| médio prazo | vantagem em nichos (química, otimização) [21, 22, 31, 32] | seleção por contrato, NetBenefit como critério |
| longo prazo | tolerância a falhas | decisão já desacoplada do modelo de execução |

A coluna da direita é a tese do capítulo: a arquitetura não aposta em um horizonte. Ela decide qual usar.

## 17.3 Nível 2 — Padrões como porta institucional

Um projeto isolado não vira infraestrutura. Três caminhos existem, e o livro declara a ordem de prioridade:

1. **OpenQASM 3** [10] — já adotado, com conformidade verificada; é a via de menor atrito e maior alcance;
2. **QIR e interoperabilidade de baixo nível** — reduz dependência de um fornecedor único;
3. **catálogos de ecossistema** — visibilidade, sem promessa de adoção.

A ordem é deliberada: primeiro o que é verificável tecnicamente, depois o que depende de terceiros.

## 17.4 Nível 3 — O que falta para virar infraestrutura

Quatro condições, e nenhuma é técnica:

1. **terceiro independente** capaz de reproduzir um resultado a partir do recibo, sem contato com o autor;
2. **caso de uso com número público** — custo antes e depois, com banda declarada;
3. **especificação estável** do formato de recibo, versionada e publicada;
4. **governança** do formato, para que não dependa de uma pessoa.

Sem a quarta, o formato morre com o autor; é o modo mais comum de um bom mecanismo desaparecer.

## Exercícios

1. Por que a neutralidade tecnológica é método, e não modéstia?
2. Qual das quatro condições é a mais difícil de obter, e por quê?
3. Descreva um caso de uso com número público que testaria a tese econômica do livro.

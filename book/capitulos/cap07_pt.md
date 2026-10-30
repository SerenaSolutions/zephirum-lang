# Capítulo 7 — O que sobrou: a composição como contribuição
*ZEPHIRUM — A Computação Antes da Execução | Parte II: O Tribunal da Ciência*

## 7.1 Nível 1 — A pergunta honesta

Depois do tribunal do capítulo 5, resta uma pergunta: se todas as peças existiam, o que este livro oferece?

A resposta é uma composição com contrato. Não o motor de um carro novo — o projeto do chassi que faz rodas existentes andarem juntas na direção certa. Um chassi não é pouco: sem ele, cada roda é um projeto isolado.

## 7.2 Nível 2 — A frase obrigatória de honestidade

**Nenhuma peça isolada desta linguagem é inédita; a contribuição é a integração contratual de decisão, tipagem, certificado e auditoria em uma única linguagem executável, com vereditos honestos e recibo verificável em cada decisão.**

Quatro propriedades emergem dessa integração, e só dela:

1. **tipagem da pergunta, não do estilo** — o programador não escolhe entre preguiça e clareza; declara o contrato e o sistema resolve;
2. **juiz como cidadão de primeira classe** — a decisão de necessidade não é hack de biblioteca, é construção da linguagem;
3. **auditabilidade por terceiro** — cada veredito é reproduzível e verificável sem confiança no autor (capítulo 12);
4. **honestidade sintática** — a recusa está na gramática, não em comentário ou convenção.

A quarta propriedade é a mais frágil e a mais valiosa. Ela é frágil porque pode ser contornada por quem escreve o programa; é valiosa porque torna a abstenção um resultado **registrado**, não uma omissão.

## 7.3 Nível 3 — Consequências de projeto

A composição altera três coisas concretas no desenho de linguagens.

**Primeiro**, desloca a fronteira entre compilador e runtime. O contrato viaja com o programa até a execução, e o runtime devolve o custo real, fechando o laço que o capítulo 14 mede. Em termos de projeto, isso significa que o custo não é propriedade estática: é resultado observado e registrado.

**Segundo**, transforma erro em valor. Sistemas de tipos clássicos representam incerteza como exceção; aqui a incerteza é valor com motivo, o que permite composição: uma decisão recusada pode alimentar outra decisão, sem captura de exceção.

**Terceiro**, introduz a prova como cidadã de primeira classe na cadeia de ferramentas. O verificador não é auditoria externa posterior: é parte do produto, e o capítulo 12 detalha sua separação do gerador.

## 7.4 O que um cético diria

*"Isso é engenharia de software com nomes novos."* Em parte, sim. A resposta não é retórica: se for apenas engenharia, deve produzir medição — e produz, no capítulo 14, com números que incluem falhas.

*"A composição não é propriedade emergente, é soma."* É a objeção mais forte deste capítulo. A réplica é que a soma das cinco peças sem contrato não gera abstenção auditável: gera erro silencioso ou exceção. A emergência está na quarta propriedade, e ela é testável — o capítulo 6 tenta exatamente isso.

## Exercícios

1. Reescreva a frase obrigatória de honestidade sem trair o sentido.
2. Das quatro propriedades emergentes, qual é a mais frágil? Por quê?
3. "Engenharia, não ciência": defenda e ataque a frase, um parágrafo cada.

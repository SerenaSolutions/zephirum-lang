# Capítulo 4 — A jornada do zero: śūnya, ṣifr, zephirum
*ZEPHIRUM — A Computação Antes da Execução | Parte I: A Pergunta*

## 4.1 Nível 1 — Uma palavra que atravessou três continentes

O zero que se usa hoje tem passaporte carimbado muitas vezes. Nasceu na Índia como **śūnya**, o vazio. Atravessou o mundo árabe como **ṣifr**. Os mercadores italianos o transformaram em **zefiro**, e o zefiro virou *zero* em português e *cifra* em matemática [34].

O nome desta linguagem vem desse ponto intermediário da viagem: **Zephirum** é o zero quando ainda era uma ideia em trânsito, antes de virar símbolo estabilizado.

## 4.2 Nível 2 — Por que nomear uma linguagem com o nome do zero

Porque o zero é a primeira resposta da história que significou "não é preciso contar nada aqui". Ele é a ausência que dispensa a operação. Um juiz de necessidade é, na prática, um produtor sistemático de zeros: emite "não execute" com a naturalidade com que o aritmético emite 0.

Há uma segunda razão, técnica. Em linguagens formais sérias, um valor distinto marcando *indefinido* evita a confusão entre falso e desconhecido: a lógica ternária de Kleene tem UNKNOWN [4], o modelo relacional tem NULL [5], VHDL tem o estado 'X', e as linguagens funcionais têm Maybe/Option. O capítulo 10 mostra que o terceiro valor desta linguagem, **REFUSED**, cumpre esse papel com uma diferença: carrega motivo legível por máquina, e não apenas ausência.

## 4.3 Nível 3 — O zero como numeral de segunda ordem

Do ponto de vista da história da notação, a invenção do zero é a invenção de um numeral de **segunda ordem**: I, II, III descrevem presenças; 0 descreve uma propriedade do sistema de numeração — a posição vazia. É uma mudança de tipo, não de quantidade [34].

A mesma mudança de tipo aparece aqui. Os valores 0 e 1 são respostas **sobre o mundo**; REFUSED é uma resposta **sobre a decisão** — um meta-valor que informa o que o sistema sabe sobre o próprio ato de decidir. Essa distinção é o que separa esta arquitetura de um tratamento de erro: erro é falha do programa; abstenção é resultado do método.

| Camada | O que o valor afirma | Exemplo |
|---|---|---|
| objeto | propriedade do mundo | "a porta está aberta" |
| decisão | estado do conhecimento do sistema | "não há evidência suficiente para afirmar" |

Sem valor de segunda ordem, o sistema é forçado a mentir quando não sabe — e a mentira é indistinguível da verdade no registro. Com ele, a ignorância fica registrada, datada e auditável.

## 4.4 Nota de nomenclatura

O livro usa três nomes que o leitor encontrará no repositório [R1]: **ZEPHIRUM** (a linguagem e o projeto), **ZYQL** (o núcleo de decisão trivalente) e **Z-QEA** (a camada de recibos). A escolha não é decorativa: separa o que é linguagem, o que é decisão e o que é prova, permitindo evoluir cada camada sem renomear as outras.

## Exercícios

1. Explique, com suas palavras, a diferença entre "falso" e "desconhecido" e por que ela exige um valor próprio.
2. Dê um exemplo de sistema em que a ausência de um valor de segunda ordem produz registro falso.
3. Por que o livro separa os nomes ZEPHIRUM, ZYQL e Z-QEA em vez de usar um só?

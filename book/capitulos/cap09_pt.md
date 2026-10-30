# Capítulo 9 — A linguagem: ASK, CONTRACT, MODEL, BUDGET, REQUIRE
*ZEPHIRUM — A Computação Antes da Execução | Parte III: A Arquitetura*

## 9.1 Nível 1 — Escrever a promessa mais antiga da engenharia

Uma linguagem de programação é um modo de escrever promessas que uma máquina cumpre. Esta linguagem escreve a mais antiga das promessas de engenharia: **só gaste se for necessário**.

## 9.2 Nível 2 — O bloco de pergunta

A unidade central é o bloco **PRASHNA** — do sânscrito *praśna*, "pergunta", a língua em que o zero nasceu śūnya. Em torno dele, as cinco cláusulas do capítulo 8 tornam-se palavras reservadas:

```
prashna "a soma excede 1e9?"
  ask      soma(lista) > 1e9
  model    {algebrico, classico}
  budget   B = 0.01 USD
  require  veredito + certificado
```

O programa lê como contrato assinado. Não há cláusula opcional: orçamento ausente é erro de compilação, não omissão tolerada. Essa rigidez é deliberada — o capítulo 8 mostrou que o contrato é o que torna a decisão possível.

## 9.3 Nível 2 — Tipagem semântica T1–T6

Seis regras de tipo carregam o comportamento do sistema:

| Regra | Enunciado | Impede |
|---|---|---|
| T1 | valor colapsado não evolui | usar resultado medido como se fosse coerente |
| T2 | dupla medição do mesmo qubit não compila | reutilização indevida de estado |
| T3 | operação unitária preserva norma | normalização inválida |
| T4 | veredito é valor, não exceção | tratar abstinência como falha |
| T5 | certificado acompanha a decisão que o exige | veredito órfão de prova |
| T6 | contrato é fechado antes da execução | mudar a banda depois de ver o resultado |

T6 é a regra mais importante do livro, e a menos comum em linguagens. Ela proíbe o comportamento que o capítulo 14 documenta como falha real: escolher a regra de decisão depois de conhecer os dados.

## 9.4 Nível 3 — Semântica operacional resumida

A execução de um bloco PRASHNA segue cinco passos: (i) avaliação das cláusulas; (ii) consulta ao juiz com o conjunto de decisores admissíveis; (iii) execução do degrau selecionado, se houver; (iv) emissão do veredito com motivo, em caso de recusa; (v) selagem do recibo. Os passos (ii) e (v) são obrigatórios; (iii) é condicional.

A gramática completa, em Lark, está no Apêndice A; a versão corrente é a 1.3.1, que corrigiu a leitura de números negativos — defeito encontrado em QPU real, não em teste de bancada (capítulo 14).

## 9.5 Interoperabilidade

O compilador emite OpenQASM 3 [10], que é o padrão de fato do setor, e desde a versão 1.4 importa QASM 3 de volta, com verificação de ida e volta. A escolha é deliberada: uma linguagem que só fala consigo mesma não é linguagem, é brinquedo. A conformidade é verificada no CI do repositório [R1] e o resultado está no capítulo 14.

## Exercícios

1. Escreva um bloco PRASHNA para uma pergunta da sua área, com $\varepsilon$, $B$ e $M$ explícitos.
2. Por que T6 (contrato fechado antes da execução) é uma regra de tipo, e não uma convenção de estilo?
3. O que se perde ao emitir OpenQASM 3 em vez de um formato binário próprio?

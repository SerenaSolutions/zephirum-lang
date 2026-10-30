# Capítulo 16 — Resultados: o que os números dizem, e o que ainda não dizem
*ZEPHIRUM — A Computação Antes da Execução | Parte IV: O Teste*

## 16.1 Nível 1 — A síntese em uma página

Depois de seis capítulos de arquitetura e três de teste, o que se pode afirmar? Este capítulo responde em uma tabela, com a disciplina de separar evidência de expectativa.

## 16.2 Nível 2 — O que está estabelecido

| Resultado | Valor | Base |
|---|---|---|
| decisões erradas no experimento de falsificação | 0 em 471 decididas | capítulo 6, recibo por decisão |
| certificados forjados aceitos | 0 em 20 | capítulo 6 |
| computação eliminada com certificado | 79,2% (2.995 de 3.784 unidades) | capítulo 6 |
| certificação em hardware real | W-02 com IC [0,947; 0,957] acima da banda 0,70 | capítulo 14 |
| recusas declaradas em hardware real | W-01 e W-03 | capítulo 14 |
| detecção de adulteração, remoção e reordenação | 4 de 4 ataques | capítulo 12 |
| conformidade OpenQASM 3 | 24 de 24 circuitos | capítulo 13 |
| sobrecarga do laço de controle | 11,147× o tempo de porta | capítulo 2 |

## 16.3 Nível 2 — O que os números não dizem

Três leituras seriam abusivas e não são feitas neste livro.

**Primeira: "o sistema é mais rápido que a prática corrente".** Não foi medido contra carga real de produção. O ganho medido é de eliminação de computação em problemas sintéticos, não de tempo de parede em sistema industrial.

**Segunda: "o hardware é bom".** O CHSH com $S=2{,}07\pm0{,}12$ não demonstra violação de Bell. O que se demonstra é que o sistema registrou a incerteza em vez de arredondá-la.

**Terceira: "a arquitetura está validada".** Validação exige terceiro independente. O que existe é reprodutibilidade local e verificação criptográfica do registro.

## 16.4 Nível 3 — A leitura correta do conjunto

O conjunto de evidências sustenta uma afirmação estreita e sólida: **é possível construir um sistema que decide quando não sabe, registra a decisão de forma verificável, e resiste a ataques de adulteração ao próprio registro.** Essa afirmação é demonstrável hoje, no repositório público, com 13 testes adversariais e 24 circuitos conformes.

A afirmação ampla — que esse sistema entrega vantagem econômica em produção — permanece hipótese. O capítulo 17 descreve o que seria necessário para testá-la.

## Exercícios

1. Escolha um resultado da tabela e descreva o experimento que o derrubaria.
2. Por que a segunda leitura abusiva ("o hardware é bom") é tentadora, e por que ela é falsa?
3. Escreva, em duas frases, a afirmação estreita que o conjunto sustenta.

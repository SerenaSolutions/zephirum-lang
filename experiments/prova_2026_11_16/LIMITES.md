# Limites declarados

## O que esta bateria NÃO prova

1. Nada sobre hardware real. Não houve QPU nesta rodada, por credencial inválida.
2. Nada sobre custo de fila paga.
3. Nada sobre avaliação por terceiro. Nenhuma pessoa de fora compilou um programa.
4. A equivalência foi medida em um circuito (Bell), não no corpus inteiro. Ampliar é trabalho pendente, e a meta do pré-registro é 100% do corpus.

## O que ela prova

1. O decisor não emite certificado falso em 2.000 casos adversariais, contra referência de terceiro.
2. O intervalo exato concorda com Clopper-Pearson do scipy a 3,4e-13.
3. O recibo é sensível a adulteração em qualquer um dos 7 campos testados.
4. O veredito não se inverte ao variar shots.
5. O exportador QASM 3, comparado com Qiskit, tem fidelidade 1,0 no caso medido.

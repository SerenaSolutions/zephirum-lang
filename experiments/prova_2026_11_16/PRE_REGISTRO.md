# Pré-registro — prova da linguagem

Escrito antes de qualquer rodada em hardware, e vale como compromisso: se o critério não for atingido, o resultado é negativo, não é reajuste de meta.

## O que conta como prova

1. Equivalência semântica: fidelidade de processo igual a 1,0 contra Qiskit em 100% da amostra. Uma divergência já reprova.
2. Round-trip da IR: exportar e reimportar sem perda de estrutura em 100% dos programas do corpus.
3. Falsificação: zero certificado falso em 2.000 casos adversariais, com verdade independente por biblioteca de terceiro (scipy).
4. Determinismo: mesma entrada, mesmo `receipt_hash`, em duas execuções.
5. Recusa: recibo intacto aceito, cada campo adulterado rejeitado.
6. Falha segura: nenhuma entrada inválida produz veredito 1 ou 0.

## O que reprova a linguagem

1. Qualquer divergência semântica contra Qiskit no corpus.
2. Qualquer certificado falso que o verificador independente aceite.
3. Qualquer adulteração de recibo que passe.
4. Inversão entre 1 e 0 ao variar o número de shots.

## O que não conta como prova

1. Rodar o mesmo circuito mais vezes no plano free.
2. Resultado de hardware sem recibo verificável.
3. Testemunho interno sem código de terceiro reproduzindo.

## Prazo

Revisão do critério somente com justificativa escrita e anterior à rodada. Rodada em hardware entra depois da equivalência fechada, e só nos pontos de fronteira que o certificado previu.

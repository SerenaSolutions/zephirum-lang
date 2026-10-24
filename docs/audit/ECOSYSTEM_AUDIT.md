# Auditoria adversarial interna (24/10/2026)

Resposta aos 4 pontos levantados pela revisao do Qiskit Ecosystem (issue #1431)
e pelo auditor externo. Regra da casa: encontrar a falha antes do revisor.

## 1. A logica trivalente e necessaria? (sim, e mensuravel)

Demo executavel: `python3 experiments/adversarial_refused_demo.py`
(20.000 julgamentos, 256 shots, epsilon=0.05, margem Hoeffding do proprio nucleo)

Resultado: diante de oraculos com verdade conhecida (constante-1, constante-0,
balanceado) e ruido de leitura, a decisao BINARIA FORCADA (limiar p0=0.5) produz
~33% de alegacoes ERRADAS por ser obrigada a responder no cinzento. O ZYQL troca
essa classe inteira de erro por RECUSA: 0,00% de alegacao errada em todos os
niveis de ruido testados (0-30%). Custo declarado: cobertura (recusa honesta
quando o ruido empurra caso conclusivo pra banda; a 30% de ruido recusa ~100%).
REFUSED e necessario exatamente onde o binario erra por design.

## 2. Os experimentos sao reproduziveis? (verificados do zero)

O job QEC da Rodada F-rev (dbehrdngdj9s73flr1ng, ibm_kingston, 2048 shots)
foi REABERTO e recomputado a partir das contagens cruas, independentemente do
recibo selado:
- controle (|0> + X, sem codigo): 2034/2048 = erro fisico 99,32%
- codificado + bit-flip injetado: maioria erra 30/2048 = erro logico 1,46%
- codificado limpo: 40 flips espontaneos corrigidos pela maioria, base = 0
Os numeros batem com o recibo (99,32% / 1,46%). Reproducao: qualquer conta IBM
Quantum com `QiskitRuntimeService` pode reabrir o job pelo ID acima.

## 3. A alegacao QEC se sustenta? (sustenta, com frase corrigida)

ACHADO DA AUDITORIA (nosso, antes do revisor): a frase publica "injected 99%
bit-flip error" podia sugerir um canal aleatorio de 99% em TODOS os qubits.
O experimento real injeta UM bit-flip DETERMINISTICO no qubit do meio - a classe
de erro para a qual o codigo de repeticao foi projetado. O erro fisico de 99,3%
e o que o MESMO flip causa sem codigo (medido no controle). A alegacao correta e
precisa: "o codigo de repeticao corrigiu na base Z, em hardware real, seu flip
de 1 qubit (erro fisico medido 99,3%), deixando 1,5% de erro logico residual".
FRASE CORRIGIDA em: SPEAKER_KIT.md, posts_2026-10-24.py, qiskit_community_post.md.
Limitacao declarada: nao e teste de estresse multi-qubit nem canal aleatorio.

## 4. Compatibilidade Qiskit e demonstravel? (sim, executavel)

Suite completa: 34/34 testes passando (pytest, <1s) em ambiente com qiskit 2.6.0
+ qiskit-ibm-runtime 0.50.0 (SamplerV2, channel ibm_quantum_platform) +
qiskit-qasm3-import (fontes OpenQASM 3 carregadas via qasm3.load no quantum-poc,
concordancia exata entre 6 SDKs com recibo selado). CI verde em todos os pushes.

## Veredito da auditoria interna

Numeros do silicio: confirmados do zero. Alegacoes publicas: 1 frase corrigida.
Nenhuma outra divergencia entre recibo selado e recomputacao independente.

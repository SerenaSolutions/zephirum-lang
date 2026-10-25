# RODADA H — especificacao dos jobs de QPU (confronto em silicio IBM)

Pre-requisito: credenciais IBM Quantum ativas na sessao de execucao.
Cada job deve registrar: backend, base de medida, shots, job ID e recibo
Z-QEA encadeado na Rodada G. Protocolo selado ANTES do envio (zyql_robust.protocol_seal).

## H1-QPU — correlacao entre shots (leitura temporal)
Executar GHZ4 com leitura em lotes TEMPORAIS separados (8 lotes de 256 shots).
Saidas por lote alimentam correlation_verdict; lag-1 acima do limiar =>
veredito de independencia RECUSADO para a amostra (ruido drift do QPU).
Esperado: correlacao fraca, mas a HIPOTESE passa a ser medida, nao assumida.

## H2-QPU — protocolo selado + executar o DJ da porta de confianca
Selo com epsilon=0.05, shots=2048, family=1; executar ZYQLQuantumGate(4, f_constante);
veredito publicado com o SELO no recibo. Qualquer re-execucao exige protocolo novo.

## H3-QPU — ZNE com folding manual em decaimento real
GHZ5 com folding manual g=1,3,5 (CX dobrados), 3 jobs, fidelidades por ponto.
zne_verdict decide MITIGATED ou REFUSED com base no guard; registrar os 3 job IDs.

## H4-QPU — kernel concentrado sob ruido real
Feature map RY(pi*x) em 4 qubits, kernel_matrix de 4 pontos x,y; medir em 2 backends
com T1/T2 diferentes (ex.: fez vs kingston); kernel_concentration_verdict por backend.
Esperado honesto: backend mais ruidoso se aproxima mais do valor uniforme 2^-4.

## H5-QPU — GHZ n=16 no hardware vs MPS
Fidelidade GHZ16 medida (job) contra MPS exato chi=8 no simulador local;
mps_truncation_verdict com a referencia. Quebra o teto n=12 da Rodada G se fidelidade > threshold.

## H6-QPU — curva de decaimento do gradiente no silicio
parameter-shift medido (base X) para L=1,2,4,8 em n=4; variancia por profundidade
alimenta train_verdict; registrar a curva completa no recibo (McClean 2018 no hardware).

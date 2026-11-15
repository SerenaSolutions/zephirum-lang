# Instancias disponiveis: leitura de arquitetura (15/11/2026)

Fonte: metadata do qBraid Runtime, conta da Serena. Nada aqui e estimativa; todo campo vem
do proprio provedor. Onde o provedor nao informa, o campo aparece como nao declarado.

## Panorama

1. 33 dispositivos cadastrados, 19 utilizaveis no momento da leitura.
2. 18 seguem modelo de portas (gate_model) e 1 e analogico: QuEra Aquila, 256 atomos.
3. Apenas 4 declararam conjunto de portas nativo: as quatro variantes de IonQ Forte, com 34 portas.
4. Apenas 1 declarou modelo de ruido explicito.
5. Sobre simuladores: 9 disponiveis, incluindo tensor network com 500 qubits (qbraid gpu-tn) e
   density matrix de 17 qubits (AWS dm1).

## Consequencia para o ZEPHIRUM

A heterogeneidade real nao esta no numero de qubits: esta na ausencia de contrato declarado.
Quinze dos dezenove dispositivos nao dizem quais portas aceitam, e dezoito nao dizem nada sobre
ruido. Um compilador que assume portas universais acerta por sorte no simulador e falha no
hardware. A regra do adaptador passa a ser: sem declaracao, nao executa; declara recusa.

Segunda consequencia: 256 atomos analogicos nao sao 256 qubits de porteira. Aquila nao entra
pela mesma interface e nao deve aparecer em comparacao de fidelidade com gate model.

## Custo declarado (unidade nao confirmada pelo provedor)

1. AWS roda com perTask 30.0 e, no IonQ, perShot 8.0.
2. Rigetti direto cobra por minuto: 12000.0 por minuto.
3. Simuladores qbraid: 0.0 por tarefa e por tiro; gpu-sv e gpu-tn cobram 5.0 por minuto.
4. Dispositivos openquantum: todos com preco 0.0 nos tres campos.

A unidade nao esta declarada no metadata. Sem confirmacao, esses numeros servem para ordenar
prioridade, nao para orcar. Nao cite valores em moeda sem confirmar a unidade.

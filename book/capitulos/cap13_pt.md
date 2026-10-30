# Capítulo 13 — Os quatro pilares e o inventário real do sistema
*ZEPHIRUM — A Computação Antes da Execução | Parte III: A Arquitetura*

## 13.1 Nível 1 — Um prédio de quatro andares

Uma linguagem não é apenas gramática. É um prédio de quatro andares: a linguagem que se escreve, o compilador que traduz, o simulador que ensaia e o runtime que entrega no hardware. Aqui os quatro são projetados juntos, com um corredor transversal que os conecta.

## 13.2 Nível 2 — Os pilares

- **Language** — gramática com as cinco cláusulas do contrato, o terceiro valor e o bloco PRASHNA; palavras reservadas em português com notação matemática.
- **Compiler** — tradução para OpenQASM 3 [10], validação das regras T1–T6 e emissão do recibo; desde 1.4, importa QASM 3 de volta com verificação de ida e volta.
- **Simulator** — ensaio barato: produto de estados matricial [20] e extrapolação a ruído zero [19] antes do palco caro.
- **Runtime** — execução final em clássico, paralelo ou QPU, sempre com as três métricas de sistema no recibo.

O **NEXA-IR** é a representação intermediária transversal: toda passagem entre pilares é registrada e auditável. Nenhum pilar fala com outro por baixo do pano. A inspiração é a tradição de IR de compilador [8]: cada camada evolui isolada, e a verificação é independente por camada.

## 13.3 Nível 2 — Inventário real do código

O pacote publicado na versão 2.1.2 [R2] contém 25 módulos de topo. O inventário abaixo não é aspiracional: é o que existe.

| Grupo | Módulos | Função |
|---|---|---|
| núcleo trivalente | `zqgate`, `battery_ci`, `zyql_witness`, `shot_auditor` | decisão, bateria de CI, abstenção com prova, controle de campanha |
| linguagem | `zyql_lisp`, `oq3`, `quantum_types` | interpretador, transpilador QASM 3, tipos quânticos |
| runtime e sistema | `zkernel`, `zquantum`, `zyql_runtime` | escalonador, camada de sistema, runtime de produção |
| criptografia do recibo | `zqea_sig`, `zqea_kem` | assinatura ML-DSA-44, sigilo ML-KEM-768 |
| simulação | `zyql_mps`, `zyql_zne`, `zyql_selfverified` | MPS, ruído zero, dispositivo auto-verificado |
| interoperabilidade | `zyql_cirq` | paridade de veredito com Cirq |
| camadas aplicadas | `zyqml_core`, `zyql_llm_compress`, `zyql_rag_layer` | aprendizado variacional, compressão, camada neural |
| robustez | `zyql_robust`, `zyql_auditkit` | guardas adversariais, entropia com recibo |
| experimentos selados | `zyql_protocols`, `zyql_world3`, `zyql_worldscale` | P-08, P-10, rodadas WORLD |

A tabela tem uma consequência de leitura: o projeto é maior que o capítulo 11 sugere, e menor que o entusiasmo sugere. Vinte e cinco módulos não significam vinte e cinco produtos; significam uma arquitetura em construção, com dívida técnica declarada no capítulo 15.

## 13.4 Nível 3 — Conformidade com o padrão

O compilador emite OpenQASM 3 e o CI verifica a ida e volta. O resultado observado em 30/10/2026: **24 circuitos conformes em 24 avaliados**. Quando o importador de QASM não está disponível no ambiente, o CI faz degradação explícita em vez de silenciosa: marca a verificação como não executada, e não como aprovada.

Essa distinção — *não executado* diferente de *aprovado* — é a mesma disciplina do terceiro valor aplicada ao próprio processo de teste. Um sistema que trata ausência de verificação como aprovação é exatamente o que este livro critica.

## Exercícios

1. Por que uma IR auditável reduz o custo de verificação por camada?
2. O CI marca "não executado" quando falta o importador. Descreva o efeito de tratar esse estado como "aprovado".
3. Escolha dois módulos do inventário e explique o que aconteceria se fossem fundidos em um só.

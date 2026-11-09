# Plano de convergência: ZYQL ZEPHIRUM em C++, Python e Qiskit

Versão 1.0, 09/11/2026. Executa a correção dos itens reprovados na auditoria e
define a separação de responsabilidade entre as três linguagens.

## Divisão de responsabilidade

**C++ decide o que é numérico e verificável por máquina.** `cpp/zyql_verdict.cpp`
expõe duas funções: `zyql_rota`, que devolve 1 clássico, 2 quântico ou 0 recusado,
e `zyql_veredito`, que aplica a banda de erro sobre p0 e devolve 1, 0 ou 2. É o
núcleo que não pode depender do interpretador.

**Python orquestra.** Provedores de evidência, recibos, política e a cola entre
módulos vivem em `src/zyql_ten/`. Python não decide sozinho: ele chama o núcleo.

**Qiskit mede.** Circuito, `Statevector` e `transpile` fornecem as três métricas de
sistema: qubits programáveis, profundidade e throughput. Onde não há QPU, o campo
declara a origem local em vez de fingir medição de hardware.

## Fases

**Fase 1, concluída hoje.** Recibo SHA3 em todos os dez módulos com verificação de
integridade, motivo de recusa declarado em todos os dez, terceira métrica no
adaptador, saída única de dez linhas, piso de Python em 3.11, versões
independentes de gramática e de contrato de recibo.

**Fase 2, núcleo nativo.** O C++ já cobre rota e veredito com concordância provada
contra a implementação Python numa grade de casos. O próximo passo é mover a
canonicalização do recibo para C++ e manter em Python apenas a assinatura ML-DSA.

**Fase 3, verificador independente.** É o requisito RF-10, ainda aberto, e o único
que não se resolve com código nosso: exige terceiro executando o verificador sem
confiar no autor.

**Fase 4, produto.** Embrulhar o roteador em API, persistir recibos e publicar SLA
de latência e custo por operação. Só depois dos gates anteriores.

## Regra de ouro

Nenhuma fase abre a seguinte por decisão interna. Cada uma exige artefato
verificável, e o artefato é sempre o mesmo: teste que falha quando a promessa não
é cumprida.

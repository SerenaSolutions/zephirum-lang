# Matriz de fornecedores com nivel de evidencia

Niveis: E0 identificado; E1 integracao de software testada; E2 simulador validado;
E3 hardware real executado; E4 recibo integro com proveniencia verificavel;
E5 aprovacao comercial e licenciamento.

Nenhum fornecedor e apresentado como integrado so porque aceita uma linguagem.

| Fornecedor | Nivel | Evidencia no projeto | Bloqueio | Proximo passo |
| --- | --- | --- | --- | --- |
| IBM Qiskit | E3 (E4 parcial) | 4 PASS no ibm_fez, SHA3 conferido | job_id amarrado depois da execucao (proveniencia reconstruida) | capturar job_id na submissao e assinar o recibo |
| IBM Quantum (hardware) | E3 | rodada Bell 4096 tiros, paridade 0,9446 | cota do plano open e fila | proximo experimento com mitigacao de leitura |
| PennyLane | E2 | mesmo Bell em default.qubit, paridade 1,0000 | sem QPU propria | comparar apos mitigacao |
| Cirq | E2 | Deutsch-Jozsa identico ao Qiskit (paridade 1e-9) | sem hardware Google | manter como referencia |
| qBraid | E1 (adaptador pronto) | `src/zephirum/adapters/qbraid_backend.py`, recusa declarada | credencial recusada pelo servico | token valido do qBraid |
| Intel (IQS) | E1 | IQS adotado como referencia independente de simulacao | sem acesso ao SDK completo | confirmar licenca e canal de acesso |
| Intel (hardware) | E0 | nenhuma execucao | acesso restrito a grupos aprovados | pedido formal de acesso |
| AWS Braket | E0 | nenhuma integracao | nada iniciado | adaptador OpenQASM 3 por dispositivo |
| Microsoft QIR | E0 | nenhuma integracao | nada iniciado | backend QIR e estimativa de recursos |
| OpenAI / Gemini | E1 | camada de IA com modo deterministico | chaves nao autenticaram | chave valida e saida citavel |

Regra: subir de nivel exige evidencia nova registrada em recibo, nao declaracao.

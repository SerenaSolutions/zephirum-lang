# Submissao para revisao: ZEPHIRUM no qBraid com Intel Quantum SDK

## O que se submete

Pacote `zephirum` (PyPI, Apache-2.0), documentacao publica e o repositorio privado sob
acesso restrito. Idioma unico de entrada: contrato `qubits` + `gates`. O adaptador qBraid
ja existe e recusa com motivo quando nao ha credencial, em vez de simular escondido.

## O que o projeto entrega ao ambiente

1. Decisao trivalente com cota declarada e recibo SHA3 conferivel.
2. Adaptadores por provedor, com o mesmo contrato de programa.
3. Recibo com backend, shots, forma do circuito no alvo e hash do programa.
4. Nenhuma alegacao de hardware sem recibo de hardware.

## Checklist de revisao

1. Licenca Apache-2.0 declarada (PEP 639) e LICENSE no wheel.
2. Dependencias fixadas: numpy, lark, qiskit; extras hardware, interop, api, pq, test, docs.
3. Instalacao limpa verificada em venv sem credencial de nuvem.
4. Suite local: testes de contrato, praticas de servico e integridade de recibo.
5. Adaptador qBraid em `src/zephirum/adapters/qbraid_backend.py`.
6. Nivel de evidencia atual na matriz: qBraid E1, Intel IQS E1.

## Perguntas objetivas

Para o qBraid: qual device identifica o Intel Quantum SDK no plano gratuito; se o envio
de circuito Qiskit exige transpilacao previa; e qual o caminho de revisao para publicar
um adaptador de linguagem na plataforma.

Para a Intel: se o SDK completo tem canal de acesso para empresa brasileira; sob qual
licenca; e se o IQS compilado localmente pode ser citado como ambiente de referencia.

## O que nao sera alegado

Que IQS seja backend oficial do SDK; que ML-DSA prove correcao do calculo; que simulacao
seja hardware. Cada uma dessas frases fica fora do material de submissao.

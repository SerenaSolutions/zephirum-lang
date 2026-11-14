# Rodada com as 16 praticas (14/11/2026)

Programa: Bell Phi+ escrito no contrato da linguagem (H, CX).
Comando: `PYTHONPATH=src python3 experiments/qpu_16pilares.py`

O script aplica as 16 praticas e grava recibo conferivel. O resultado desta data saiu em
simulador porque a conta IBM recusou a credencial: `InvalidAccountError: Unable to retrieve
instances`. O recibo marca `origem: simulador` em vez de fingir hardware.

Para rodar em QPU de verdade falta apenas credencial com instancia ativa da IBM Quantum.
Com a chave valida no ambiente (`IBM_QUANTUM_TOKEN`), o mesmo comando executa no backend
menos ocupado da lista permitida e grava `origem: qpu`.

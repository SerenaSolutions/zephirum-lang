# Runbook de Reprodução Independente — Bateria Química ZEPHIRUM

**Casa ZEPHIRUM — Guia de Reprodução por Terceiros (POC 4 & 5)**

Este documento fornece instruções passo a passo para auditores e revisores externos reproduzirem o benchmark público e independente da bateria de química quântica da Casa ZEPHIRUM com sementes fixas e versões travadas.

---

## 1. Requisitos de Ambiente

- **Sistema Operacional:** Linux (Ubuntu 22.04 LTS / Debian 12) ou macOS
- **Python:** Versão `3.10` ou superior (`3.10.x` / `3.11.x` / `3.12.x`)
- **Gerenciador de Pacotes:** `pip` e `virtualenv`

---

## 2. Passo a Passo de Instalação (Dependências Travadas)

### Passo 2.1: Criar e Ativar Ambiente Virtual
```bash
python3 -m venv venv_zephirum
source venv_zephirum/bin/activate
pip install --upgrade pip
```

### Passo 2.2: Instalar Pacotes com Versões Exatas
Crie um arquivo `requirements.txt` com o seguinte conteúdo:
```text
numpy==2.4.6
pyscf==2.14.0
qiskit==2.6.0
qiskit-nature==0.8.0
qiskit-algorithms==0.3.0
```

E execute a instalação:
```bash
pip install -r requirements.txt
```

### Passo 2.3: Validar as Versões Instaladas
Execute no terminal para confirmar que o ambiente está com as versões exatas:
```bash
python3 -c "import numpy, pyscf, qiskit, qiskit_nature; print('numpy:', numpy.__version__); print('pyscf:', pyscf.__version__); print('qiskit:', qiskit.__version__); print('qiskit_nature:', qiskit_nature.__version__)"
```
**Saída esperada:**
```text
numpy: 2.4.6
pyscf: 2.14.0
qiskit: 2.6.0
qiskit_nature: 0.8.0
```

---

## 3. Estrutura dos Arquivos

Certifique-se de que a estrutura dos diretórios está organizada da seguinte forma:
```text
zephirum_lang_audit/experiments/
├── chemistry/
│   ├── SPEC.md
│   ├── chemistry_battery.py
│   ├── chem_H2.json
│   ├── chem_LiH.json
│   ├── chem_H2O.json
│   ├── chem_NH3.json
│   └── chemistry_battery_20261020.json
└── benchmark_public/
    ├── RUNBOOK.md
    ├── verify.py
    └── RESULTS.md
```

---

## 4. Execução do Script de Verificação (`verify.py`)

Navegue até o diretório `benchmark_public/` e execute o script de verificação:

```bash
cd zephirum_lang_audit/experiments/benchmark_public/
python3 verify.py 1
```

### O que o script faz:
1. Fixa as sementes globais (`SEED = 42`).
2. Lê os dados de referência publicados em `../chemistry/chemistry_battery_20261020.json`.
3. Executa o cálculo FCI do PySCF para $H_2$, $LiH$, $H_2O$ e $NH_3$.
4. Mapeia o Hamiltoniano para qubits via Jordan-Wigner e executa diagonalização exata (`NumPyMinimumEigensolver`).
5. Avalia o VQE com `StatevectorEstimator`, `EfficientSU2(reps=1)` e `COBYLA(maxiter=120)`.
6. Valida o erro de mapeamento ($|E_{\text{mapped}} - E_{\text{FCI}}| < 1.0 \times 10^{-8} \text{ Ha}$) e a coincidência das energias.
7. Emite o status `PASS`/`FAIL` por molécula e o hash SHA-256 do resultado canônico do benchmark.

---

## 5. Teste do Protocolo de Determinismo

Para comprovar que o protocolo é 100% determinístico e reproduzível, execute o script duas vezes consecutivas e compare os hashes canônicos emitidos:

```bash
python3 verify.py 1
python3 verify.py 2
```

### Critério de Determinismo:
- **Ambas as rodadas devem imprimir `PASS` para todas as moléculas ($H_2$, $LiH$, $H_2O$, $NH_3$).**
- **O Hash Canônico SHA-256 de ambas as rodadas deve ser rigorosamente IDÊNTICO:**
  `b79ed17e46752823839d3a501c465b61149a1016b217e2bab568db4fa991ce59`

---

## 6. Solução de Problemas / FAQ

- **Warning de Depreciação no Qiskit:**  
  O uso da classe `EfficientSU2` pode gerar um aviso informativo de depreciação no Qiskit 2.6.0. O script `verify.py` silencia este aviso para manter o output limpo.
- **Tempo de Execução:**  
  O tempo total de execução para as 4 moléculas é de aproximadamente 1,5 a 2 minutos em hardware moderno de 4 cores.

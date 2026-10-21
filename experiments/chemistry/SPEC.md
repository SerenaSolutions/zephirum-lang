# Especificação Completa da Bateria Química ZEPHIRUM (POC 4 & 5)

**Casa ZEPHIRUM — Auditoria Linguística & Computacional**  
**Data:** 20 de Outubro de 2026  
**Recibo Global da Bateria (SHA-256):** `85c20bc9a0bd0c7e35b698f10e59ce9052a895a00ae8843b2f1f59db16b22070`  
**Etiqueta de Simulação:** `DECLARED_CLASSICAL` (Statevector Simulation)

---

## 1. Visão Geral & Propósito

Esta especificação define rigorosamente o protocolo computacional da **Bateria de Química Quântica ZEPHIRUM**, contemplando quatro moléculas fundamentais da natureza: **$H_2$** (Hidrogênio), **$LiH$** (Hidreto de Lítio), **$H_2O$** (Água) e **$NH_3$** (Amônia).

A bateria estabelece a validação formal em dois níveis de prova:
1. **Prova Matemática do Mapeamento Qubit:** Equivalência exata entre a energia de estado fundamental do FCI (*Full Configuration Interaction*) em espaço eletrônico contínuo/discretizado e a diagonalização exata do Hamiltoniano mapeado via transformação Jordan-Wigner em espaço de spin.
2. **Prova Variacional (VQE):** Execução do algoritmo VQE (*Variational Quantum Eigensolver*) com ansatz e otimizador travados para aferição de convergência variacional e rastreamento da limitação de profundidade.

---

## 2. Stack de Software e Versões Travadas

| Pacote | Versão Travada | Função no Pipeline |
|---|---|---|
| **Python** | `3.10+` | Runtime do benchmark |
| **PySCF** | `2.14.0` | Driver Hartree-Fock (RHF) e referência quântica exata FCI |
| **Qiskit** | `2.6.0` | Framework quântico e primitivas de simulação (`StatevectorEstimator`) |
| **Qiskit-Nature** | `0.8.0` | Construção de Hamiltonianos de segunda quantização e mapeador Jordan-Wigner |
| **NumPy** | `2.4.6` | Computação numérica e diagonalização de matrizes |
| **Qiskit-Algorithms** | `0.3.0` | Solver exato (`NumPyMinimumEigensolver`), VQE e otimizador `COBYLA` |

---

## 3. Especificação Molecular & Geometrias Exatas

Todas as geometrias moleculares estão definidas em Ångström ($\text{\AA}$), em coordenadas cartesianas exatas:

1. **$H_2$ (Hidrogênio molecular)**
   - Base: `STO-3G`
   - Geometria cartesiana ($\text{\AA}$): `"H 0.0 0.0 0.0; H 0.0 0.0 0.735"`
   - Qubits Jordan-Wigner: **4 qubits**
   - Energia Repulsão Nuclear: `0.71996899 Hartree`

2. **$LiH$ (Hidreto de Lítio)**
   - Base: `STO-3G`
   - Geometria cartesiana ($\text{\AA}$): `"Li 0.0 0.0 0.0; H 0.0 0.0 1.595"`
   - Qubits Jordan-Wigner: **12 qubits**
   - Energia Repulsão Nuclear: `0.99531764 Hartree`

3. **$H_2O$ (Água)**
   - Base: `STO-3G`
   - Geometria cartesiana ($\text{\AA}$): `"O 0.0 0.0 0.117; H 0.0 0.757 -0.470; H 0.0 -0.757 -0.470"`
   - Qubits Jordan-Wigner: **14 qubits**
   - Energia Repulsão Nuclear: `9.18825842 Hartree`

4. **$NH_3$ (Amônia)**
   - Base: `STO-3G`
   - Geometria cartesiana ($\text{\AA}$): `"N 0.0 0.0 0.0; H 0.0 0.937 0.381; H 0.812 -0.469 0.381; H -0.812 -0.469 0.381"`
   - Qubits Jordan-Wigner: **16 qubits**
   - Energia Repulsão Nuclear: `11.95930477 Hartree`

---

## 4. Formulação Matemática & Protocolos de Cálculo

### 4.1 Método de Referência Exato (FCI do PySCF)
- **Cálculo de Campo Autoconsistente (SCF):** Restricted Hartree-Fock (`scf.RHF(mol)`).
- **FCI Kernel:** Solver Full Configuration Interaction (`fci.FCI(mf)`).
- **Energia Total de Referência:** $E_{\text{FCI}} = E_{\text{eletrônica, FCI}} + E_{\text{nuc}}$.

### 4.2 Mapeamento Jordan-Wigner & Diagonalização Exata
- **Operador de Segunda Quantização:** Gerado via `PySCFDriver(atom=geom, basis="sto3g", unit=DistanceUnit.ANGSTROM)`.
- **Mapeador de Spin:** `JordanWignerMapper().map(ham.second_q_op())`.
- **Eigensolver Quântico Exato:** `NumPyMinimumEigensolver().compute_minimum_eigenvalue(qubit_op)`.
- **Inclusão da Repulsão Nuclear:** $E_{\text{mapped}} = \text{Re}(\lambda_{\min}(H_{\text{qubit}})) + E_{\text{nuc}}$, onde $E_{\text{nuc}} = \text{ham.nuclear\_repulsion\_energy}$.

### 4.3 Algoritmo Variacional (VQE)
- **Primitiva de Avaliação:** `StatevectorEstimator` (simulação de vetor de estado pura sem ruído de amostragem).
- **Ansatz Variacional:** `EfficientSU2(num_qubits, reps=1)` (camadas SU(2) com entrelançamento linear/circular de profundidade 1).
- **Otimizador:** `COBYLA(maxiter=120)` (Constrained Optimization BY Linear Approximation, limitado a 120 iterações em ambiente sandbox).
- **Ponto Inicial Documentado:** Vector determinístico $\mathbf{\theta}_0 = [0.05, 0.05, \dots, 0.05]^T$ com tamanho igual a `ansatz.num_parameters`.
- **Energia VQE Total:** $E_{\text{VQE}} = \text{Re}(\langle \psi(\mathbf{\theta}^*) | H_{\text{qubit}} | \psi(\mathbf{\theta}^*) \rangle) + E_{\text{nuc}}$.

---

## 5. Criterologia de Aceitação & Tolerâncias Numéricas Declaradas

Para que o benchmark declare estado **PASS**, as seguintes tolerâncias devem ser estritamente satisfeitas:

1. **Tolerância de Mapeamento Jordan-Wigner:**
   $$\text{Erro de Mapeamento} = |E_{\text{mapped}} - E_{\text{FCI}}| < 1.0 \times 10^{-8} \text{ Hartree}$$
   *(Demonstra que a representação em qubits é matematicamente isomórfica ao Hamiltoniano molecular contínuo).*
2. **Coincidência com Valores Referenciados:**
   - $|E_{\text{FCI, calculado}} - E_{\text{FCI, publicado}}| < 1.0 \times 10^{-6} \text{ Hartree}$
   - $|E_{\text{mapped, calculado}} - E_{\text{mapped, publicado}}| < 1.0 \times 10^{-6} \text{ Hartree}$
   - $|E_{\text{VQE, calculado}} - E_{\text{VQE, publicado}}| < 1.0 \times 10^{-5} \text{ Hartree}$

---

## 6. Tabelas de Resultados de Referência Publicados

| Molécula | Qubits (JW) | Repulsão Nuclear (Ha) | $E_{\text{FCI}}$ PySCF (Ha) | $E_{\text{mapped}}$ Qubit (Ha) | Erro Mapeamento (Ha) | $E_{\text{VQE}}$ (Ha) | Erro VQE (Ha) | SHA-256 Recibo Individual |
|---|---|---|---|---|---|---|---|---|
| **H2** | 4 | 0.71996899 | -1.13730604 | -1.13730604 | 0.00000000 | -1.114371 | 0.022935 | `bebd2978c90a851b0f14f0e6e6514ecb2185228f25f7b0f708f5f65fdd1808a1` |
| **LiH** | 12 | 0.99531764 | -7.88240193 | -7.88240193 | 0.00000000 | -7.253225 | 0.629177 | `c8fd8c626c8b82a2c2b2fabd6f54713ac4d7fb965ef4190bc1046b94833684dd` |
| **H2O** | 14 | 9.18825842 | -75.01264712 | -75.01264712 | 0.00000000 | -67.944430 | 7.068217 | `4f20c1b4e07b1b858231342b803069377919dfaf31a91b3e6d93fa8bd71b5871` |
| **NH3** | 16 | 11.95930477 | -55.51908560 | -55.51908560 | 0.00000000 | -50.258387 | 5.260698 | `4716c2ff7c18c5ba36a668289522d2e9de02c7fc030b2f34848ee565333b0788` |

**Recibo de Integridade Global da Bateria (SHA-256):**  
`85c20bc9a0bd0c7e35b698f10e59ce9052a895a00ae8843b2f1f59db16b22070`

---

## 7. Declaração Honest de Limitações

Em conformidade com as diretrizes de integridade científica da Casa ZEPHIRUM:

1. **Classificação do Benchmark (`DECLARED_CLASSICAL`):**  
   Todas as execuções foram realizadas via simulação clássica de vetor de estado (`StatevectorEstimator`). Não se alega execução em hardware quântico físico (QPU) nesta bateria.
2. **Limitação de Profundidade do Ansatz VQE:**  
   O ansatz utilizado (`EfficientSU2`, `reps=1`, 120 iterações COBYLA) é um ansatz heurístico raso configurado para restrições de tempo de execução em sandbox. Ansätze quimicamente precisos (como UCCSD) exigem recursos computacionais adicionais.
3. **Execução em Hardware Quântico Real:**  
   A migração destas provas para QPUs físicas da IBM é o objetivo declarado da solicitação de **IBM Quantum Credits**, não constituindo alegação do presente relatório.

# Chemistry battery — nature-derived molecules

FCI reference (PySCF) x Jordan-Wigner mapping (an industry-standard quantum SDK) x variational pipeline.
STO-3G basis. Simulation labeled DECLARED_CLASSICAL (statevector).

| Molecule | Qubits (JW) | FCI (Ha) | Mapped (Ha) | Mapping error |
|---|---|---|---|---|
| H2  | 4  | -1.137306 | -1.137306 | 0.0 |
| LiH | 12 | -7.882402 | -7.882402 | < 1e-10 |
| H2O | 14 | -75.012647 | -75.012647 | 0.0 |
| NH3 | 16 | -55.519086 | -55.519086 | 0.0 |

Run: `python3 chemistry_battery.py H2 LiH H2O NH3`
Battery receipt (SHA-256 over canonical results): 85c20bc9a0bd0c7e...
VQE limitation declared: shallow ansatz (depth 1, 120 sandbox iterations);
chemistry-grade ansaetze (UCCSD) and hardware execution are future work.

## QPU testimony — H2 (primeira execução em hardware de um sistema químico)

Registro: `h2_qpu_testimony_20261016/` · maturidade EXPERIMENTAL

| Item | Valor |
|---|---|
| Sistema | H2 / STO-3G / redução de paridade 2 qubits / R = 0.75 Å |
| Clássico pré-registrado (eletrônica) | -1.8514 Ha (sha256 5b0cb79d…, selado antes da submissão) |
| Hardware medido (eletrônica) | -1.7862 Ha · delta +0.0652 Ha |
| FCI independente (PySCF) | -1.8427 Ha · delta +0.0565 Ha |
| Veredito | VALIDADO_DENTRO_TOLERANCIA (±0.10 Ha pré-registrado) |
| Execução | ibm_marrakesh · job_id db9agfgc77vs73815bgg · 3 circuitos × 400 shots |

As duas rotas clássicas divergem em 0.0087 Ha (coeficientes publicados vs FCI no geométrico
exato); ambas ficam dentro da tolerância. Ponto aberto registrado, não mascarado.

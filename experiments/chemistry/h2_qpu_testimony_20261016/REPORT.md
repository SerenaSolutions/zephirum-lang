# H2 — decisão clássica testemunhada em hardware real
Data do experimento: 2026-10-16 · Portado ao canônico: 2026-11-26 · Maturidade: EXPERIMENTAL

## Por que este arquivo existe
A bateria `chemistry_battery.py` declara explicitamente: "hardware execution are future work".
Este registro é a primeira execução em QPU de um sistema químico no projeto — fecha essa
lacuna para o H2, no padrão de evidência da casa: decidir em clássico primeiro, gastar
hardware só no resíduo, selar recibo com job_id + backend + shots.

## Desenho (pré-registrado ANTES da submissão)
- Sistema: H2, STO-3G, redução de paridade 2 qubits, R = 0.75 Å
- Hamiltoniano: coeficientes publicados da redução 2 qubits (O'Malley et al., PRX 6, 031007, 2016)
- Decisão clássica (FATO): E_eletronica = -1.8514 Ha · E_total = -1.1457 Ha
  (diagonalização exata; reconstrução de Pauli verificada exata em sandbox)
- Hipótese pré-registrada: hardware reproduz E_eletronica dentro de ±0.10 Ha
- Pré-registro selado: sha256 5b0cb79da54cd511… (antes de qualquer submissão)

## Execução
- 3 circuitos × 400 shots (bases Z, X, Y), vetor fundamental exato (StatePreparation 2 qubits)
- backend: ibm_marrakesh · job_id: db9agfgc77vs73815bgg · shots totais: 1200
- Contagens Z dominadas pelo setor esperado (380/400)
- Expectativas XX/YY medidas: -0.265 / -0.230 (previsto: -0.2277)

## Resultado
| Quantidade | Valor (Ha) |
|---|---|
| Clássico pré-registrado (eletrônica) | -1.8514 |
| Hardware medido (eletrônica) | -1.7862 |
| Delta vs pré-registro | +0.0652 → **VALIDADO_DENTRO_TOLERANCIA** |
| FCI independente (PySCF, mesmo geométrico) | -1.8427 |
| Delta vs FCI | +0.0565 → dentro da tolerância |

## Reconciliação honesta (INFERÊNCIA)
As duas rotas clássicas divergem em 0.0087 Ha: coeficientes publicados (R=0.75 Å da tabela
original) vs FCI PySCF no geométrico exato. Ambas as referências ficam dentro da tolerância
pré-registrada em relação ao hardware. O veredito não muda; a origem da divergência
(arredondamento de coeficientes na tabela publicada ou diferença sutil de geométrico) fica
registrada como ponto aberto — não foi mascarada.

## O que isto NÃO é
- Não é vantagem quântica: H2 é exatamente decidível em clássico (o gate o recusou duas vezes, corretamente).
- Não é descoberta de molécula: é testemunho de hardware com recibo, o padrão de evidência
  que antecede qualquer alegação de fronteira.
- Vantagem quântica em química permanece HIPÓTESE/PREVISÃO.

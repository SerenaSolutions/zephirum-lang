# GEN1_BASELINE — Fotografia técnica do repositório (evidence before velocity)

Repositório real: https://github.com/SerenaSolutions/zerum
Commit de referência: ca82d6f (arXiv preprint) + incremento do orquestrador
Data do levantamento: 2026-11-27

## 1. Dimensão do código

- 44 módulos Python em `prototype/`, ~8.096 linhas.
- 1 verificador independente em C (`prototype/verifier_indep/`, conforme conformance v0.3).
- Suíte de conformidade executável: `prototype/conformance_v03.py` (baterias PASS integrais).

## 2. Componentes confirmados por inspeção

| Módulo | Responsabilidade real |
|---|---|
| `zephirum_lexer.py` | Lexer da linguagem |
| `zephirum.py` / `nexa_core.py` | Parser e núcleo de decisão (ASK/CONTRACT/MODEL) |
| `zephirum_ir.py` | Representação intermédia |
| `zephirum_vm.py` | VM de bytecode orçamentada |
| `zephirum_runtime.py` | Runtime |
| `zephirum_simulator.py` | Simulador |
| `zephirum_transpiler.py` / `_multi.py` | Transpilação (Python, C, Java, C#) |
| `verify_certificate.py` | Verificador independente (Python) |
|  `prototype/verifier_indep/` | Verificador independente (C, sem código partilhado) |
| `decision_kernel.py` | Digest canónico (SHA-256) e base dos recibos |
| `zephirum_trust.py` / `test_trust.py` | Camada de confiança |
| `zephirum_isolate.py` | Isolamento de processos |
| `qsim_gateway.py` | Produto: portão quântico (prova antes de pagar QPU) |
| `ai_layer.py` | Camada de IA (declarada, escopo separado) |

Famílias de decisão implementadas no núcleo (`nexa_core.py`): expressão,
soma com limiar (`_threshold_sum`), média parcial (`_mean_partial`),
Laplace (`_laplace`), determinante (`_det`), geométrica (`_geo`),
emaranhamento de 2 qubits (`_entangle`).

## 3. Matriz de alegações — documentos externos vs realidade

Os três documentos colados (ChatGPT, 27/11) descrevem um projeto diferente.
Verificação feita contra o repositório:

| Alegação dos documentos | Realidade verificada |
|---|---|
| Repositório `SerenaSolutions/zephirum-lang` | `SerenaSolutions/zerum` |
| Linguagem chamada ZYQL | Linguagem chama-se ZEPHIRUM |
| Fonte em Lisp `.zph` | Programa ASK/CONTRACT/MODEL, sem Lisp |
| `docs/FACTS.md`, `MATURITY.md`, `receipts.md` | Não existem |
| Recibos com SHA3-256 | SHA-256 (`decision_kernel.digest`) |
| Assinatura ML-DSA-44 | Não existe no repositório |
| Valores `1 / 0 / REFUSED` | `TRUE / FALSE / Z` (Z = UNKNOWN, §12) |
| Integração Qiskit como dependência | Confronto tri-SDK documentado (`docs/QINTEROP.md`), SDK opcional |

Conclusão (CORRIGIDA em 2026-11-27, 11h45 UTC — verificação via API GitHub):
os documentos externos NÃO descrevem um projeto imaginado. Descrevem um
SEGUNDO repositório real da mesma organização: `SerenaSolutions/zephirum-lang`
(criado 2026-10-12, PR #145 mergeado, push em 2026-11-27T11:37Z, 2 stars,
pacote PyPI `zephirum` v2.5.9 com 1.282 downloads no último mês, núcleo
ZYQL 1/0/REFUSED). Este baseline descreve o OUTRO repositório — a linhagem
deste workspace (`SerenaSolutions/zephirum`, núcleo ASK/CONTRACT/MODEL,
TRUE/FALSE/Z, SHA-256).

Existem, portanto, DUAS linhagens ZEPHIRUM com semânticas distintas.
Consolidação é decisão do fundador (ver pauta da reunião).

## 4. Estado de maturidade (declarado vs verificado)

- Verificado: conformidade v0.3 com baterias PASS integrais, incluindo
  verificador C (400/400), certificados forjados rejeitados (5/5),
  transpilador multi-alvo com veredictos e hashes idênticos, gateway 40/40.
- Não verificado: replicação independente por terceiros; hardware quântico
  real nunca foi executado; revisão matemática externa pendente.

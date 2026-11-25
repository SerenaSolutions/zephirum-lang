# Equipe de agentes — ZEPHIRUM Scientific Kernel Gen 1

**Repositório:** `SerenaSolutions/zephirum-lang`  
**Branch de trabalho:** `feat/gen1-scientific-kernel-baseline`  
**Diretrizes:** HYBRID · FOUNDER-LED · Proof → Compute  
**Estado:** plano de coordenação configurado; agentes especializados não foram iniciados por esta interface.

## Limite operacional

A interface disponível nesta sessão não oferece mecanismo para criar ou iniciar agentes Copilot independentes. Portanto, os sete papéis abaixo são frentes de trabalho configuradas, não agentes que já tenham sido executados. O agente coordenador não atribuirá a si próprio uma revisão independente nem registrará como concluída uma tarefa que não realizou.

O agente coordenador pode executar as frentes em sequência, usando este quadro como checklist, ou entregar o plano a agentes reais quando disponíveis. Resultados, alterações e testes só serão marcados após evidência verificável.

## Papéis e entregáveis

| ID | Papel | Escopo de inspeção/trabalho | Entrega exigida | Estado |
|---|---|---|---|---|
| A1 | Auditoria do kernel | `src/`, entrypoints, APIs públicas, dependências, CI e documentação normativa | Inventário com caminhos/símbolos; testes e comandos de reprodução; lacunas identificadas | PENDENTE — auditoria inicial parcial já registrada no baseline |
| A2 | Matemática e semântica | `src/zyql_runtime.py`, `src/zyql_quantum_gate.py`, `src/zephirum/__init__.py`, `docs/FACTS.md`, `docs/MATURITY.md` e testes relacionados | Mapa de `1`/`0`/`REFUSED` e estados complementares; separar validação, prova, cálculo e experimento; registrar questões estatísticas pendentes | PENDENTE — não equivale a revisão matemática independente |
| A3 | Orquestração híbrida | `src/qroute/`, `src/zkernel.py`, contratos e chamadas de execução | Proposta de despacho por capacidades declaradas, seleção explícita e política fail-closed/fallback; diagrama do fluxo real versus proposto | PENDENTE — não implementar roteamento amplo antes dos contratos e testes |
| A4 | Backends e execução | `src/zephirum/adapters/`, `src/zquantum.py`, Qiskit/Aer, qBraid, CUDA-Q, CUDA-Q e hardware nos testes | Matriz por backend: classe (CPU/simulador/hardware), operações, limites, dependências, disponibilidade, falhas e testes existentes | PENDENTE — presença de adaptador não conta como validação de hardware |
| A5 | Evidências e recibos | `src/zqea_canon.py`, `src/zqea_sig.py`, `src/qroute/receipt.py`, recibos runtime/adaptadores e `docs/SPEC_Z-QEA_v1.0.md` | Inventário de formatos/canonicalizações/verificadores, fixtures e plano de compatibilidade; limites de hash/assinatura/cadeia/âncora | PENDENTE — não propor formato concorrente antes da matriz |
| A6 | Testes adversariais e segurança | `tests/`, `tests/hardware_live/`, CI, entrada/credenciais/recibos e caminhos de fallback | Baseline de testes executada; casos adversariais reproduzíveis; resultados separados em aprovado/reprovado/não executado | PENDENTE — não usar mocks como prova de hardware |
| A7 | Documentação científica | Documentos Gen 1, README, `docs/FACTS.md`, `docs/MATURITY.md`, claims e limitações | RFCs aditivas, claims vinculadas a código/teste, limitações e guia de reprodução | PENDENTE — alterações de alegações de maturidade requerem decisão humana |

## Dependências e ordem de trabalho

1. **A1** completa a fotografia e confirma os paths/símbolos antes de afirmar cobertura integral.
2. **A2 e A5** podem inspecionar sem alterar implementação; sinalizam questões semânticas e formatos incompatíveis.
3. **A4 e A3** mapeiam capacidades reais; A3 não deve presumir recursos não demonstrados por A4.
4. **A6** executa a suíte existente e registra o baseline antes de qualquer alteração funcional; testes específicos novos podem ser propostos depois da leitura dos contratos.
5. **A7** consolida os resultados comprovados em RFC/documentação, mantendo proposta e implementação claramente diferenciadas.
6. O coordenador integra alterações pequenas em branch isolada, verifica colisões, executa regressão e reporta limitações. Nenhuma frente pode aprovar cientificamente a própria alegação sem revisão independente.

## Regras de governança e integração

- Nenhum merge em `main`, release ou alteração de credenciais.
- Nenhuma alteração pública de semântica, contratos ou formato de recibo sem análise de migração e gate humano.
- Não remover testes para obter aprovação; preservar e diagnosticar falhas.
- Não declarar execução QPU sem job real e evidência; não converter fallback em simulação silenciosa.
- Nenhuma afirmação de garantia estatística enquanto a pendência de `adaptive_margin_family` em `docs/MATURITY.md` não estiver resolvida com revisão apropriada.
- Toda conclusão deve apontar para arquivos, símbolos, testes e comando executável; “não executado” não significa aprovado.
- Toda contribuição de agente real deverá informar arquivos examinados, mudanças feitas, testes, resultados, limitações e riscos.

## Quadro de acompanhamento inicial

| Frente | Responsável operacional nesta sessão | Progresso verificável |
|---|---|---|
| A1 Auditoria | Coordenador Copilot | Parcial; evidências iniciais em `GEN1_BASELINE.md` e `GEN1_COMPONENT_INVENTORY.md` |
| A2 Semântica | Não iniciado | Nenhum parecer independente |
| A3 Orquestração | Não iniciado | Nenhum código de orquestração Gen 1 implementado |
| A4 Backends | Não iniciado além da inspeção inicial dos adaptadores citados no baseline | Nenhuma validação remota/hardware nesta sessão |
| A5 Recibos | Inspeção inicial parcial pelo coordenador | Nenhum formato novo ou migração executados |
| A6 Testes/segurança | Não iniciado | Suíte não executada nesta sessão |
| A7 Documentação | Coordenador Copilot | Baseline inicial e este quadro de equipe registrados |

**Próxima tarefa executável:** completar A1/A5 com inventário de recibos, adaptadores, diretórios científicos e testes; depois A6 deve executar `python3 -m pytest -q` em ambiente apropriado e registrar a saída literal. Até lá, a implementação de contratos permanece proposta, não código validado.

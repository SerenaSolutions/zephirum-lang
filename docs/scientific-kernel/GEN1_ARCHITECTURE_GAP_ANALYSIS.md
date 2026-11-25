# GEN1_ARCHITECTURE_GAP_ANALYSIS — proposta versus estado observado

**Base analisada:** `main` em `880d567f42542c2a8c4114aec013f751940126c3`.  
**Propósito:** mapear responsabilidades sem insinuar que a arquitetura Gen 1 já está implementada.

## Resumo

O repositório já oferece linguagem/runtime de decisão, simulação local, caminhos de integração com Qiskit e provedores, roteamento Q-ROUTE e múltiplas formas de recibo. O principal gap não é ausência total de peças: é falta de contratos e fronteiras unificadas entre peças distintas, mais a necessidade de demonstrar compatibilidade, capacidade e evidência em cada fluxo. Não se recomenda reescrever runtime, criar outro simulador ou introduzir um recibo concorrente antes do inventário e dos testes.

| Componente Gen 1 | Evidência preexistente | Gap específico | Incremento seguro proposto |
|---|---|---|---|
| Scientific Interface | `.zph` (`src/zyql_lisp.py`); API de `zephirum.decidir`; CLI `zyql-decide`; circuito declarativo Qiskit | Entradas não compartilham um contrato científico versionado que represente hipótese, restrição, evidência esperada e política de execução | Documentar um envelope não vinculante e mapear conversões sem mudar API; escolher um caso vertical pequeno após aprovação de compatibilidade. |
| Formalization Layer | Validação de entradas do runtime e de circuitos | Regras são locais a cada função; não há evidência de formalização universal/domínio-tipado | Começar por schema/validador estrito de uma operação piloto, sem assumir provas gerais nem adicionar hipóteses. |
| VERITAS | `ConfigError`, validação de circuito, classificação de recusa e verificadores de recibo | Mistura potencial de validação estrutural, regra estatística e prova; `adaptive_margin_family` tem revisão pendente declarada | Registrar tipo de evidência e escopo para cada check; manter `REFUSED`; não renomear semântica nem chamar gate de provador. |
| Hybrid Orchestrator | Q-ROUTE combina análise clássica, cálculo de Grover e caminho opcional de hardware; `zkernel` registra backend | Não identificado um seletor genérico baseado em operação/capacidade/limites/custo/evidência, nem modelo comum de fallback | Extrair primeiro contrato de capacidade a partir dos adaptadores existentes; execução somente quando backend explícito e compatível. Sem fallback por padrão. |
| Execution Engine | `QCircuit`, Qiskit Aer local, adaptadores qBraid/CUDA-Q e rotas de hardware | Diferença entre simulator/local/provider deve aparecer uniforme nos resultados; limites declarados e operações dos adaptadores divergem | Criar tabela de conformidade e testes de capacidades; identificar resultado pelo backend real; sem execução remota em baseline. |
| Z-QEA Evidence Engine | SHA3, verificadores e formatos assinados/encadeados estão presentes | Trilhas e canonicalizações coexistem; nem todo recibo tem mesmo nível de autoria/cadeia/âncora; recibo não demonstra validade científica | Fazer corpus de amostras e verificar cada formato com o verificador correto. Não alterar formato nem aplicar assinatura automaticamente antes de migração. |

## Fluxo operacional que existe hoje (recorte)

No caminho `zyql_runtime.decide`, a entrada é validada, um `ZYQLQuantumGate` é criado e a execução usa `QCircuit` em `src/zquantum.py`; a saída pode ser convertida em `Verdict` e selada opcionalmente. O rótulo da implementação é simulação local, não QPU. Separadamente, `qroute.core.executa` avalia um mapa, pode solicitar execução pelo módulo `qroute.hardware` e pode gerar recibo Q-ROUTE. O adaptador `zephirum.adapters.qiskit_backend.executar` usa Aer local; os caminhos qBraid/CUDA-Q têm outras condições. Estes fluxos não constituem por si sós um único orquestrador.

## Lacunas transversais / bloqueios de alegação

1. **Adequação computacional:** disponibilidade de backend não basta. A seleção deve considerar problema e declaração do backend; hoje a evidência inspecionada não demonstra um seletor geral com esses critérios.
2. **Compatibilidade de semântica:** `REFUSED`, `INCONCLUSIVE` e recusa com motivo aparecem em áreas distintas. O kernel precisa preservar o contrato legado em vez de colapsar estados ou converter em booleano.
3. **Estatística:** há várias regras e configurações; `docs/MATURITY.md` assinala a revisão matemática pendente de `adaptive_margin_family`. Não estabelecer garantia familiar nova nesta etapa.
4. **Hardware:** presença de adaptador, teste unitário ou caminho dry-run não é prova de job real. A documentação do próprio `docker/README.md` afirma que naquele sandbox não houve submissão real.
5. **Recibos:** SHA3 assegura integridade desde o selo, não autoria nem verdade do resultado. Assinatura também não valida a experiência; Z-QEA v1.0 declara essas fronteiras.
6. **Maturidade:** README, MATURITY e receipts devem ser reconciliados com teste executável e estado de integração, sem reclassificar como estável por decisão do agente.

## Decisões de arquitetura recomendadas

- Reutilizar `zyql_runtime`, `zephirum.adapters`, `qroute` e Z-QEA como implementações candidatas, não criar módulos duplicados com nomes VERITAS/Z-QEA apenas para refletir o diagrama.
- Manter CPU clássica como referência de validação do protótipo e simulador explicitamente identificado; “híbrido” deve significar despacho documentado, não alegação de vantagem.
- Não conectar QPU nem executar chamadas de rede neste incremento; primeiro testar contrato de capacidade e caminhos de recusa.
- Contrato novo, se aprovado, deverá ser aditivo e versionado; API legada preservada até cobertura de migração demonstrar equivalência.

## Critérios mínimos para sair do gap analysis

- Inventário de todos os formatos de recibo e de seus verificadores, com fixtures.
- Matriz de operações por backend e testes de recusa para capacidade não declarada.
- Testes de contrato antes de execução, execução identificada como local/simulada/remota e fallback proibido por padrão.
- Revisão independente da derivação estatística antes de alegar garantia.
- CI completa executada e reportada; execução real em QPU só pode ser atestada por recibo, job ID e protocolo verificáveis.

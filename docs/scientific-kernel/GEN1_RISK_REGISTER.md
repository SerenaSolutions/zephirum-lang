# GEN1_RISK_REGISTER — riscos, controles e evidências pendentes

| ID | Risco | Evidência/causa no repositório | Impacto | Controle/ação | Estado |
|---|---|---|---|---|---|
| R-01 | Contratos paralelos e incompatíveis | APIs diferentes em `src/zyql_runtime.py`, `src/zephirum/__init__.py`, adaptadores e `src/qroute/core.py` | Resultado, erro ou evidência podem ter semânticas distintas | Inventariar campos e consumidores; adotar contrato aditivo, versionado, somente após testes | Aberto |
| R-02 | Coerção ou confusão entre estados | `Verdict` no runtime, `REFUSED` com motivo, `INCONCLUSIVE` em outras interfaces | Incerteza vira conclusão incorreta | Matriz semântica e testes; proibir conversão implícita e preservar motivo | Aberto |
| R-03 | Alegação estatística além da prova | `adaptive_margin_family` documentada em `src/zyql_quantum_gate.py`; pendência expressa em `docs/MATURITY.md` | Falsa confiança/decisão científica | Não usar como garantia até derivação e revisão independente; manter limitação pública | Aberto, bloqueio de alegação |
| R-04 | Simulação rotulada como hardware | `src/zephirum/adapters/qiskit_backend.py::executar` usa `AerSimulator`; outras rotas podem ser remotas | Evidência experimental inválida | Campo de tipo/origem obrigatório e testes de roteamento; nada de fallback implícito | Aberto |
| R-05 | Capacidades de backend presumidas | Adaptadores possuem conjuntos de operações/limites próprios; qBraid lê metadata e CUDA-Q consulta targets | Operação rejeitada tardiamente ou malformada | Matriz por operação, validação anterior ao despacho e recusa se capacidade desconhecida | Aberto |
| R-06 | Fallback silencioso ou custo inesperado | `qroute.executa` permite hardware/dry; no geral falta política única observada | Execução não autorizada, custo de QPU | Fallback desativado por padrão; chamada remota exige configuração e autorização explícitas | Aberto |
| R-07 | Integridade confundida com correção/autoria | Z-QEA define hash, assinatura, cadeia e âncora; especificação exclui correção matemática/fidelidade | Alegação enganosa sobre verdade ou autoria | Rotular classes de evidência; explicitar limites em recibos e documentos | Mitigação documental; validar implementações |
| R-08 | Incompatibilidade de recibos | `src/zqea_canon.py` aceita estilos/campos legados; runtime/qroute/adaptadores emitem formas diversas | Verificador pode recusar legado ou aceitar dado inadequado | Corpus de fixtures e teste por versão; sem formato concorrente | Aberto |
| R-09 | Cobertura/estado de CI desconhecido nesta tarefa | `.github/workflows/ci.yml` declara matriz extensa; testes não executados no agente | Regressão não detectada | Executar suíte baseline e verificar último CI; reportar falhas sem removê-las | Aberto |
| R-10 | Falsa afirmação de QPU validada | Adaptadores e documentação não equivalem a submissão real; `docker/README.md` diz que sandbox não submeteu job | Alegação experimental sem procedência | Não alegar validação; exigir job ID/dados/recibo verificado e protocolo | Aberto |
| R-11 | Segredo exposto ou execução remota insegura | Adaptadores aceitam chaves/token como entrada; não houve auditoria de serviço/credenciais nesta rodada | Acesso não autorizado/custo/vazamento | Revisar secret handling, logs e escopo; jamais gravar credenciais em recibo | Aberto |
| R-12 | Maturidade contraditória | README, `docs/MATURITY.md`, `docs/receipts.md` e `docs/FACTS.md` têm escopos/declarações que precisam ser conciliados | Usuários interpretam beta como produção ou vice-versa | Fazer matriz de alegações baseada em código/testes, manter linguagem cautelosa | Aberto |
| R-13 | Auditoria incompleta | Inventário parcial; `zyql_science`, SDK, C++, workflows e recibos não foram lidos integralmente | Gap relevante não identificado | Completar inspeção antes de RFC ou implementação | Aberto |
| R-14 | Falsa evidência de teste | Nenhum comando foi executado neste ciclo; escrita no GitHub não oferece shell/test runner | Documentos podem parecer validados quando não foram | Marcar claramente “não executado”; rodar suíte/CI em etapa com ambiente disponível | Controlado por declaração |

## Regras de escalonamento

- **Exige decisão do fundador:** mudança incompatível em API, semântica de veredito, regra estatística, recibo, maturidade ou publicação de alegação experimental.
- **Bloqueia alegação científica:** qualquer risco em aberto que afete validade/garantia do claim correspondente.
- **Pode avançar sem decisão irreversível:** inspeção, testes aditivos, documentação de limites, matriz de capacidades e testes de recusa.

## Resultado inicial

Estado global: **BLOCKED_BY_ARCHITECTURAL_RISKS** para implementação ampla do kernel, por falta de inventário integral/contrato comum e testes executados neste ciclo. Trabalho de auditoria, especificação aditiva e testes independentes permanece executável.

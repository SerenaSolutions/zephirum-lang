# GEN1_IMPLEMENTATION_PLAN — fases incrementais e gates

**Status:** plano inicial a partir do baseline; não afirma fases já concluídas.  
**Princípios:** compatibilidade, alteração reversível, evidência e nenhuma execução remota implícita.

## Fase 0 — Baseline verificável (em andamento)

**Atividades:** inventário de módulos/APIs/recibos, documentação e testes; registrar commit-base.  
**Saída:** baseline, inventário, gap analysis, plano e riscos.  
**Gate:** toda afirmação de implementação apontar a código/teste; lacunas explícitas.  
**Estado neste ciclo:** cinco documentos de referência preparados; inspeção parcial e testes não executados. Não fechar Fase 0 ainda.

## Fase 1 — Conformidade de contratos legados

1. Ler contratos e implementações Q-ROUTE, adaptadores, `zyql_science`, SDK, C++ e API.
2. Levantar recibos reais do repositório, identificar canonicalização/campo de selo e testar verificadores offline.
3. Executar a suíte e CI relevante; registrar baseline de falhas antes de alterar código.
4. Especificar equivalências de `1`, `0`, `REFUSED` e estados adicionais, sem coerção booleana.

**Saída:** matriz de compatibilidade e conjunto de fixtures de conformidade.  
**Gate:** nenhuma decisão pública de formato/semântica feita sem testes de regressão e aprovação humana quando incompatível.

## Fase 2 — Contrato de execução mínimo (RFC)

Especificar, como proposta e antes da implementação: `ScientificProblem`, `ExecutionRequest`, `BackendCapability`, `ScientificVerdict`, `EvidenceRecord` e `ExecutionReceipt`. A proposta deve distinguir validação estrutural, prova formal, validação numérica e observação experimental. Identificar campos obrigatórios e extensões legadas; definir versão, erro e política de fallback.

**Saída:** RFC e corpus válido/inválido.  
**Gate:** verificação de compatibilidade com APIs existentes e revisão humana para mudanças públicas.

## Fase 3 — Caminho clássico de referência

Escolher uma única operação determinística e pequena, com domínio e saída verificáveis. Integrar um backend clássico de referência somente após confirmar que não duplica um solver existente. Validar contrato antes do despacho; recusar operação ou capacidade não declarada.

**Saída:** teste ponta a ponta repetível e proveniência da execução.  
**Gate:** comportamento inválido recusa antes da execução; seed/versão/entrada rastreáveis, se aplicáveis.

## Fase 4 — Simulador quântico explícito

Integrar um simulador existente (candidato: `src/zquantum.py` ou Qiskit Aer) por interface de capacidade restrita. Registrar `backend_type=simulator`, dependência e parâmetros. Comparar apenas operações para as quais exista referência clássica adequada. Fallback para simulador sempre requer autorização explícita.

**Saída:** execução simulada identificada e testes reproduzíveis.  
**Gate:** prova por teste de que solicitação de hardware não vira simulador silenciosamente; nenhuma alegação de vantagem.

## Fase 5 — Evidência e verificadores

Consolidar inventário antes de mexer em recibos. Reusar Z-QEA e verificadores existentes, criar testes de adulteração, JSON não finito, cadeia, formatos legados e resultado inconsistente. Documentar níveis de integridade/autoria/encadeamento/âncora, sem confundi-los com validade científica.

**Saída:** teste de auditoria offline e documentação de limitações.  
**Gate:** recibos antigos continuam verificáveis sob regras anteriores; mudança incompatível exige versão/migração.

## Fase 6 — Preparação de hardware (sem submissão automática)

Auditar integração de cada provedor, credenciais e política de custos/limites. Implementar apenas adaptador solicitado/selecionado e teste de recusa sem credencial. Nenhum token em fonte/log/recibo. Não usar mocks como evidência de hardware real.

**Saída:** documentação operacional e caminho de recusa seguro.  
**Gate para experiência:** aprovação humana, protocolo pré-declarado, acesso seguro e capacidade disponível. Publicação exige job real, dados e recibo, inclusive resultados negativos.

## Fase 7 — Consolidação

Executar regressão completa, conformance, verificadores de documentos/alegações e revisão externa necessária. Corrigir documentação para refletir código e testes; não publicar release nem alterar `main` sem autorização.

## Critérios de conclusão da Gen 1 (não satisfeitos por criar documentos)

- Contrato versionado e validado antes do despacho.
- Veredito trivalente preservado, incluindo incerteza e motivo.
- Backend escolhido conforme capacidade demonstrada e problema; sem fallback implícito.
- Caminhos clássico e simulado identificáveis e reprodutíveis.
- Recibo verificável sem confundir hash com prova/autoria.
- Testes de compatibilidade, adulteração, falha e recusa aprovados.
- Hardware apenas se evidência real disponível e publicada com limitações.
- CI executada; revisão humana/externa conforme risco.

## Próxima execução autorizada

Completar a auditoria dos módulos e recibos enumerados em `GEN1_COMPONENT_INVENTORY.md`, executar `python3 -m pytest -q` no ambiente apropriado e coletar CI recente. Não implementar contrato ou modificar runtime até conhecer falhas de base e aprovar interfaces públicas.

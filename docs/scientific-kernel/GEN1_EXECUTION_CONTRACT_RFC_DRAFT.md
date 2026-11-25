# RFC proposta — contrato aditivo mínimo de execução Gen 1

**Status:** proposta para revisão externa; não implementada.  
**Compatibilidade:** não modifica API pública nem formatos de recibo nesta RFC.  
**Base de evidência:** revisão estática do commit `642074c33de2f6a065a9a30098fcacc48d07c020`.  
**Princípio:** manter `1`, `0`, `REFUSED`; separar prova, decisão, cálculo e classe de evidência.

## 1. Problema

O repositório possui interfaces de execução distintas: `zyql_runtime.decide`, circuito declarativo dos adaptadores, Q-ROUTE, ZYQL Science e ZYSDK. Validação estrutural e verificações de recibo existem, mas não formam um contrato comum. Esta RFC propõe apenas um envelope mínimo que pode ser mapeado aos caminhos existentes após aprovação e testes; não define runtime novo.

## 2. Vocabulário

- **Proof/check result:** resultado de um verificador identificado, escopado ao conteúdo, premissas e regra informados. Um check estrutural não é prova formal.
- **Decision verdict:** `1` (aceito segundo regra identificada), `0` (rejeitado segundo regra identificada), `REFUSED` (não há base para decidir/continuar segundo política). Nenhum valor é booleano implícito.
- **Execution state:** `NOT_STARTED`, `EXECUTED`, `FAILED`, `REFUSED`.
- **Epistemic status:** `FORMALLY_VERIFIED`, `STRUCTURALLY_VALIDATED`, `NUMERICALLY_EVALUATED`, `EXPERIMENTALLY_OBSERVED`, `ASSUMED`, `UNKNOWN`.
- **Evidence class:** integrity, proof/check, numerical, experimental, provenance. Uma classe não prova outra.

## 3. Estruturas conceituais

JSON ilustrativo, não compromisso de formato serializado:

```json
{
  "contract_version": "gen1-draft-1",
  "problem": {
    "problem_id": "caller-supplied-id",
    "operation": "registered-operation-name",
    "domain": "declared-domain",
    "inputs": {},
    "assumptions": [],
    "constraints": []
  },
  "request": {
    "allowed_backends": ["classical_cpu"],
    "requested_mode": "compute",
    "fallback_allowed": false,
    "evidence_requirements": []
  }
}
```

Backend capability, proof/check record, decision e receipt são modelos lógicos separados. O wire-format definitivo só poderá ser escolhido depois da matriz de adaptação/recibos e revisão de compatibilidade.

## 4. Interfaces propostas

As assinaturas são pseudocódigo normativo para discussão, não API implementada.

```text
validate_problem(problem) -> ValidationResult
verify_evidence(problem, evidence) -> ProofCheckResult
list_capabilities() -> list[BackendCapability]
select_backend(problem, request, capabilities) -> RouteDecision
execute(problem, request, selected_backend) -> ExecutionResult
verify_receipt(receipt) -> ReceiptIntegrityResult
```

### 4.1 `BackendCapability`

Campos mínimos conceituais: `backend_id`, `execution_kind` (`classical_cpu`, `classical_gpu`, `quantum_simulator`, `quantum_hardware`, `analytical`), `operations`, `limits`, `precision`, `dependency_versions`, `availability`, `failure_modes`, `evidence_origin`.

A disponibilidade é um dado de capacidade operacional, não uma justificativa de adequação. Ausência de uma operação/limite necessário deve impedir despacho com código/motivo explícito.

### 4.2 `ProofCheckResult`

`status`: `VERIFIED`, `NOT_VERIFIED`, `INDETERMINATE`; `verifier_id` e versão; `proof_kind`; compromissos/hash do problema e premissas; regra/escopo; motivo. Não mapear `NOT_VERIFIED` para `0`: prova ausente/inaplicável não é refutação.

### 4.3 `RouteDecision`

Contém `status`, backend selecionado ou ausência, justificativa, capacidades consultadas, política de fallback e estado de execução inicial. Nenhum fallback automático se `fallback_allowed=false`. Não trocar hardware pedido por simulator, nem simulator por hardware, silenciosamente.

### 4.4 `ExecutionResult`

Contém `execution_state`, backend efetivamente utilizado, identidade/versão/target, versão do programa/código, parâmetros (incluindo seed se aplicável), dados brutos, resultado normalizado, erro/recusa, `verdict` legado quando produzido por regra compatível e epistemic status. Falha de backend nunca vira resultado científico.

### 4.5 `Receipt`

RFC não cria schema de recibo. A camada deve reusar/adaptar os formatos existentes sem alterá-los até que um inventário de produtores, verificadores e fixtures defina migração. Separar campos conceituais de integridade/hash, autenticidade/assinatura, proveniência/encadeamento e evidência científica. Hash não certifica autor, matemática ou hardware.

## 5. Ordem do fluxo Proof → Decision → Compute

1. Validar sintaxe, esquema, tipos, domínios, limites e premissas declaradas. Falha: `REFUSED`/erro de contrato segundo o adaptador legado; não despachar.
2. Verificar evidências/certificados disponíveis com verificador explícito e verificar escopo/compromisso de entradas. Não há prova não implica resultado falso.
3. Aplicar política: certificado válido pode autorizar/evitar somente operação que o certificado cobre; sem prova, computação só continua se modo experimental/calculacional estiver permitido e registrado.
4. Selecionar capacidade adequada; disponibilidade sozinha não é critério. Compatibilidade ausente: recusa antes do despacho.
5. Executar apenas no backend solicitado/selecionado. Fallback somente com opt-in anterior ao início.
6. Validar pós-condições/resultado com regra identificada; não converter simulação em observação física.
7. Registrar recibo no formato legado compatível e adicionar evidência semanticamente identificada apenas por estratégia de migração aprovada.

## 6. Erros e recusas

A interface conceitual distingue:

- `INVALID_CONTRACT`: shape/tipo/domínio incorreto.
- `PRECONDITION_FAILED`: condição obrigatória demonstradamente violada.
- `PROOF_UNAVAILABLE`: evidência de prova ausente/não verificável; só interrompe se a política requer prova.
- `CAPABILITY_UNDECLARED` / `CAPABILITY_INCOMPATIBLE`: backend não pode provar suporte ao requisito.
- `BACKEND_UNAVAILABLE`: backend explicitamente pedido indisponível.
- `EXECUTION_FAILED`: backend falhou; nenhum resultado emite veredito positivo.
- `INSUFFICIENT_EVIDENCE`: execução/dados insuficientes; preservar `REFUSED`.

Os códigos são nomes para futura compatibilidade, não erros já existentes.

## 7. Critérios de conformidade e testes necessários

Antes de implementação, construir testes que falhem sem:

1. resolução de contrato, tipos e domínio antes do despacho;
2. manutenção exata de `Verdict.PERMIT`, `.DENY`, `.REFUSED` sem `bool()` coercitivo em adaptadores;
3. serialização explícita dos enums para wire values legados e recusa de JSON implícito não definido;
4. prova/check associada a hash/escopo exato das entradas;
5. distinção de prova inválida, ausente e indeterminada;
6. incompatibilidade de backend antes de execução;
7. solicitação de hardware que não possa completar em simulator no caminho de fallback;
8. fallback autorizado somente por campo explícito e registrado;
9. falha do backend que não seja convertida em `1`/`0`;
10. recibos legados verificados com seus verificadores, sem alteração de canonicalização;
11. recibo adulterado rejeitado, incluindo campos de resultado, parâmetros e origem;
12. modo experimental identificado como simulação/observação conforme o backend;
13. reexecução determinística para a operação/seed definida;
14. OpenAI chat incapaz de solicitar hardware ou assinatura por ferramenta (`api/zyql_chat.py` já define hardware/sign falsos; teste de regressão necessário).

### Semântica Enum — questão a testar, não presumir

Como `Verdict` é `enum.Enum` comum, é esperado pela semântica Python que os membros sejam truthy por padrão, inclusive `Verdict.DENY`; `Verdict.PERMIT == True` e `Verdict.DENY == False` são comparações de `Enum` por identidade e não devem ser assumidas equivalentes. JSON padrão não serializa automaticamente membros de `Enum` comum. Esses pontos não foram executados nesta sessão; adicionar testes reproduzíveis antes de decidir política. Não mudar `Enum` para `IntEnum` sem análise, pois isso pode introduzir coerções numéricas.

## 8. Migração/compatibilidade

- Sem alteração nos retornos públicos em primeira etapa.
- Criar adaptadores puros entre envelope proposto e APIs legadas somente após fixtures e equivalência testada.
- Preservar campos e hashes de recibos históricos; nunca recalcular com novo algoritmo e sobrescrever registros.
- Mudanças incompatíveis de wire schema exigem versão nova, período de coexistência e verificador de migração.
- A RFC não habilita execução remota nem altera credenciais.

## 9. Decisões que exigem revisão humana

- Semântica canônica de `0` versus recusa em domínios científicos diversos.
- Qual prova/certificado é suficiente para eliminar ou autorizar computação.
- Regra estatística e garantias familiares.
- Quais operações entram na primeira versão do contrato.
- Política de execução remota, custo e gestão de credenciais.
- Evolução dos formatos de recibo e representação serializada de verdict.

**Solicitação à revisão externa:** validar se a separação `ProofCheckResult` / `RouteDecision` / `ExecutionResult` resolve a ambiguidade sem sugerir prova matemática geral, e avaliar os testes propostos, em particular recusa distinta de refutação e semântica Python de `Enum`.

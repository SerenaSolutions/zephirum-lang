# Auditoria — álgebra de decisões trivalentes + validação em QPU

**Data:** 08/11/2026 · **Executor da implementação:** Superagent (Antigravity com cota esgotada, HTTP 429)
**Pré-registro:** `docs/PRE_REGISTRO_ALGEBRA_QPU.json` (selo `34e6fcd020b3aa02`, assinatura ML-DSA-44 verificada)
**Evidência de hardware:** job `dboh76oqtr0c738crlng`, backend `ibm_marrakesh`, p0 = 0,9720 em 2000 shots

## Achados

**A1 — colisão de selo (crítico, corrigido).** `conjuncao(1,1)` e `disjuncao(1,1)` produziam o
**mesmo** selo SHA3-256, porque o operador não entrava na forma canônica. Dois programas
distintos com o mesmo recibo. Corrigido: `op` gravado no nó e serializado; teste de não-colisão
adicionado. Este é o tipo de falha que só aparece quando se tenta quebrar o próprio código.

**A2 — previsão inicial errada (registrado).** Eu supus que 200 shots com 7 decisões recusariam.
A margem rigorosa ali é +0,3813: **não** recusa. A fronteira real, calculada, é `shots <= 14`.
O pré-registro foi corrigido **antes** da execução, não depois de ver o resultado.

**A3 — poder insuficiente recusa, nunca aprova.** Programa de 7 decisões com `eps=0,01` e
`shots=10` devolveu `REFUSED` com motivo `FAMILY_EXCEEDS_SHOTS` em hardware real. Nenhum
caminho do código converte recusa em aprovação (verificado por leitura e por teste).

**A4 — dependência em fim de vida (aberto).** `SamplerV2` está depreciado no
`qiskit-ibm-runtime` 0.50+ (instalado: 0.51.0), com remoção prevista em três meses. O script
`experiments/algebra_qpu_validation.py` precisa migrar para `qiskit_ibm_runtime.Sampler`
(client-side). Enquanto não migrar, a reprodutibilidade do recibo depende de versão fixada.

**A5 — limite declarado da validação.** O que foi provado é a **aritmética do orçamento** contra
estatística de hardware: a decisão única foi medida, o programa composto recusou onde a conta
manda. Não é alegação de vantagem física sobre outros frameworks, e não substitui validação
externa por terceiro.

## Estado do ciclo

| Etapa | Estado |
|---|---|
| 1. Missão escrita | concluída (`docs/MISSAO_ALGEBRA_TRIVALENTE.md`) |
| 2. Implementação | concluída por mim; Antigravity bloqueado por cota até ~14/11 |
| 3. Auditoria | concluída, 1 defeito crítico corrigido (A1) |
| 4. QPU IBM | concluída, job `dboh76oqtr0c738crlng`, 6/6 previsões confirmadas |
| 5. Devolver ao Antigravity | **bloqueada** (429, reset em ~141 h) |
| 6. Segunda auditoria | pendente da etapa 5 |

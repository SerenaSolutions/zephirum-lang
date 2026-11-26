# Ciclo operacional (AGENT_WORKFLOW)

DISCOVERY -> PLAN -> DELEGATE -> IMPLEMENT -> TEST -> ADVERSARIAL REVIEW -> EVIDENCE -> DOCUMENT -> PULL REQUEST

Cada tarefa entrega: objetivo, arquivos alterados, justificativa tecnica, testes executados, resultado, limitacoes, riscos, evidencias, estado padronizado de conclusao.

Regras:
- Branch especifica por tarefa; integracao por Pull Request.
- Main protegida: 4 status checks obrigatorios. Nao contornar protecoes.
- Merge na main exige aprovacao humana.
- Estado de conclusao usa o vocabulario padronizado da casa (IMPLEMENTADO, TESTADO, REPRODUZIDO_INDEPENDENTEMENTE, FORMALMENTE_VERIFICADO, EXPERIMENTAL, ESPECIFICACAO, NAO_VERIFICADO, BLOQUEADO).

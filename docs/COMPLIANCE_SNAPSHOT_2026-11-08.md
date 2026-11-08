# Posição de compliance — plataforma e ecossistema ZEPHIRUM
**Data:** 08/11/2026 · **Escopo:** repositório `zephirum-lang`, API, cobrança, recibos, publicação
**Método:** verificação no código e nos documentos locais. Nada aqui é certificação de terceiro.

| Área | Situação | Evidência | Próximo passo |
|---|---|---|---|
| Licença | CONFORME | `LICENSE` Apache-2.0 | — |
| Cabeçalho SPDX no código | **NÃO CONFORME** | 0 de 201 arquivos `.py` com `SPDX-License-Identifier` | adicionar em lote |
| Política de privacidade (LGPD) | **PARCIAL** | `PRIVACY.md` §7 afirma "não coleta dados pessoais por padrão"; `api/billing.py:97,116` guarda `email` da sessão e da conta | corrigir a política para declarar o tratamento do e-mail de cobrança, base legal e retenção |
| Política de segurança | PARCIAL | `SECURITY.md` tem canal privado, sem prazo de resposta declarado | declarar SLA (ex.: 5 dias úteis) |
| Cadeia de custódia de recibos | CONFORME (local) | lock + `fsync` + `os.replace`; teste com 24 threads sem elo duplicado | enviar ao remoto |
| Autoria x integridade | CONFORME (local) | `/verify` separa `integridade` (SHA3) de `autoria_verificada` (ML-DSA-44) | enviar ao remoto |
| Cobrança | CONFORME (local) | só `checkout.session.completed` + `payment_status=paid` + valor e moeda conferidos | enviar ao remoto |
| Escrita do interpretador | CONFORME (local) | `seal` confinado a `ZYQL_RECEIPT_DIR` por realpath | enviar ao remoto |
| Limite de taxa | CONFORME (local) | cota por IP antes da autenticação + por chave depois; expiração e teto | enviar ao remoto |
| Gate de CI | CONFORME (local) | `pytest tests -q` na esteira | enviar ao remoto |
| Cobertura de testes | CONFORME | 159 aprovados | — |
| Segredos no repositório | CONFORME | varredura por `sk_live_`, `whsec_`, chave privada: nenhum achado | — |
| Fixação de dependências | **PARCIAL** | `qiskit>=2.6,<3` com teto; `numpy` e `lark` sem teto | fixar faixa |
| Alegação de garantia estatística | **NÃO CONFORME** | margem de testes múltiplos sem derivação válida demonstrada | não apresentar como garantia até decisão |
| Contagem de consultas ao oráculo | CONFORME (local) | recibo declara tabela de verdade e sondas | enviar ao remoto |
| API em C declarada | **NÃO CONFORME** | `src/zephirum.h` sem nenhum `.c` | remover promessa |
| Versão única | CONFORME (local) | 4 fontes em 2.5.7 | enviar ao remoto |
| Endosso externo | CONFORME | nenhuma menção a aprovação ou homologação de IBM/Qiskit | manter |
| Estado do remoto | **CRÍTICO** | `main` remota em `54b1051`; 3 commits de correção só em local | publicar ou declarar |
| Serviço público em operação | NÃO VERIFICÁVEL AQUI | sem acesso à infraestrutura de produção | confirmar com o responsável |

## Riscos em ordem

1. **Remoto desatualizado.** Duas auditorias externas encontraram os mesmos problemas porque leram a `main` pública. Enquanto os 3 commits não sobem, a posição real do repositório continua vulnerável em 9 pontos.
2. **Alegação estatística.** É o único item que pode virar problema de reputação científica, não só de código.
3. **Privacidade contraditória.** A política nega coleta de dado pessoal; a cobrança guarda e-mail. Em LGPD isso é declaração inexata ao titular.
4. **Promessa de API em C** sem implementação.
5. **SPDX ausente** em 100% dos arquivos Python.

## Decisões pendentes do responsável
- Publicar os 3 commits no remoto (recomendado).
- Aprovar a rederivação da margem de testes múltiplos.
- Autorizar remoção do `zephirum.h`.
- Autorizar correção do `PRIVACY.md` e do SLA em `SECURITY.md`.

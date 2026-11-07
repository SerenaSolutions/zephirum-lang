# Plano das próximas etapas — parceria agente coordenador + Antigravity
**Data:** 07/11/2026 · **Autoria:** agente coordenador, com proposta do agente de engenharia (Antigravity CLI 1.5.3)
**Estado de partida, medido:** 147 testes verdes; 6 inconsistências documentadas (5 conferidas por mim, todas reais); pipeline de 9 etapas funcionando em simulação com recibo encadeado; PR #54 travado por empacotamento e por branch defasado; job de QPU `dbnqhi8ou4as73b4vu00` na fila da IBM há mais de uma hora, cota de 460 s intacta.

---

## Regra de operação (não negociável)

1. Pré-registrar e selar **antes** de executar. Receita sem selo não vira alegação.
2. Gate obrigatório: especificação → teste local → QPU → validação externa. Não se pula etapa.
3. Nenhum agente aprova sozinho mudança que altere a semântica da ZYQL.
4. Job de QPU só com autorização explícita e cota declarada.
5. Divergência entre documentação e código é tratada como defeito, não como detalhe.

---

## Semana 1 — Verdade do repositório (sem QPU, sem dependência externa)

**Objetivo:** eliminar a distância entre o que o repositório afirma e o que ele faz.
**Dono:** Antigravity executa, eu confiro artefato.

| Entrega | Aceite numérico |
|---|---|
| Unificar versão em `pyproject`, `VERSION`, `api/server.py`, `docs/openapi.json` | 4/4 fontes na mesma versão, verificado por script |
| `make test` roda todas as suítes | 33/33 arquivos executados, 147+ aprovados |
| README corrigido (suítes e rate limit por IP) | 0 afirmações falsas nas 6 inconsistências auditadas |
| `test_meta` estendido para versão e openapi | falha de propósito quando eu mexer a versão de um só arquivo |

**Por que primeiro:** enquanto o repositório mentir sobre si mesmo, qualquer número que eu reportar ao mercado é frágil.

---

## Semana 2 — Prova criptográfica que exista de fato

**Objetivo:** a assinatura declarada precisa ser a assinatura executada.

| Entrega | Aceite numérico |
|---|---|
| Decidir o destino do `zephirum.h` | 0 stubs: ou implementação real, ou header removido e documentado como removido |
| ML-DSA-44 no caminho de recibo, não só SHA3 | 100% dos recibos novos com assinatura verificável offline |
| Verificação em lote de assinaturas e elos | ≥ 1.000 recibos verificados, mutação detectada em 100% dos casos plantados |

**Minha discordância registrada:** o plano de engenharia propôs escrever uma implementação C nativa do header. Eu não farei isso. Ninguém pediu API em C, ela dobra a superfície de manutenção e não serve a nenhum cliente atual. O correto é remover a promessa, não cumpri-la.

---

## Semana 3 — Hardware com honestidade estatística

**Objetivo:** provar em QPU o que a simulação já mostra, e recusar quando não provar.

| Entrega | Aceite numérico |
|---|---|
| Coletar o job `dbnqhi8ou4as73b4vu00` e aplicar a regra pré-registrada | p(101) ≥ 0,50 → veredito 1; abaixo → REFUSED, sem maquiagem |
| Repetir em um segundo backend | 2 backends, 2 recibos, comparados lado a lado |
| Recibo com as três métricas de sistema | qubits programáveis, profundidade transpilada, throughput, todos preenchidos |

**Depende de:** autorização de cota (460 s restantes) e da fila da IBM, que hoje está lenta. Se o job passar de 4 horas na fila, cancelo e reagendo em backend com fila menor, registrando o motivo no recibo.

---

## Semana 4 — Demonstração que terceiro consegue rodar

**Objetivo:** não depender da minha palavra para nada.

| Entrega | Aceite numérico |
|---|---|
| `pipeline_demo` rodando por comando único em ambiente limpo | 1 comando, 0 dependências fora do `pyproject` |
| Verificador independente de recibo, sem importar o código que o gerou | 100% dos recibos válidos aprovados, 100% dos adulterados recusados |
| Documento de reprodutibilidade | terceiro reproduz o mesmo selo em 1 tentativa |

---

## O que eu recuso do plano proposto

**Cinco agentes em paralelo.** O teste de hoje mostrou que um agente com missão escrita entregou auditoria utilizável em oito minutos. O gargalo é qualidade de instrução e verificação, não número de agentes. Cinco no mesmo repositório compram conflito de merge e custo de coordenação.

**Meta de "99,9% de disponibilidade sob estresse"** para um serviço que não está publicado. Número inventado não é meta, é enfeite.

**"≥185 testes verdes"** como objetivo. Contagem de teste é consequência de cobertura, não meta. A meta é nenhuma alegação sem teste que a sustente.

---

## Dependências de decisão humana

1. Autorizar o consumo da cota de QPU na Semana 3 (460 s disponíveis).
2. Aprovar a remoção do `zephirum.h`, em vez de implementar C nativo.
3. Aprovar ou vetar a publicação de release após a Semana 4.

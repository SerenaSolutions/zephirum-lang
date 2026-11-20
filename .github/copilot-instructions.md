# Instruções para o GitHub Copilot neste repositório

Este repositório é o ecossistema ZYQL / Zephirum. Leia antes de propor código.

## Regra de ouro

Nenhuma alegação sem recibo. Toda afirmação técnica precisa apontar um recibo (SHA3-256 + ML-DSA-44),
um `job_id` de QPU, ou um teste que a reproduza. Se não houver, escreva "não demonstrado".

## Gates obrigatórios, nesta ordem

1. especificação escrita
2. teste local (sem QPU, sem crédito)
3. execução em QPU ou hardware real
4. validação externa

Nunca pule etapa. Nunca apresente resultado de etapa 2 como se fosse etapa 3.

## Estilo de contribuição

- Português do Brasil em documentação e mensagens de commit.
- Sem dependências externas novas no pacote `zephirum` (exceção: `pyproject.toml` declara o mínimo).
- Sem código copiado de terceiros. O ecossistema é proprietário.
- Testes antes de qualquer mudança de API. Suíte atual: `pytest -q`.
- Toda interface com PR segue `docs/REVISAO_PR.md` (6 regras).
- Não invente números. Números citados vivem em `book/qa/numeros.json`; o gate acusa divergência.

## Vocabulário do projeto

- **ZYQL**: linguagem/decididor trivalente, veredito em 1, 0 ou REFUSED.
- **Recibo**: registro selado de uma decisão, com hash encadeado ao anterior.
- **REFUSED**: recusa explícita, auditável. É resultado legítimo, não falha.
- **WORLD-3**: experimento em hardware IBM com três protocolos (HOM, caminhada, Grover).

## Ao gerar código

Prefira funções pequenas, tipadas, com erro explícito em vez de exceção silenciosa.
Recusa e erro devem ser distinguíveis no retorno. Nunca engula exceção.

## Invariantes de engenharia (valem acima de estilo)

1. Proof -> Compute: nenhum cálculo roda antes da prova/eliminação.
2. Trivalente `1` / `0` / `REFUSED`. Nunca converter `REFUSED` em booleano, nunca
   substituir por heurística quando falta prova.
3. Aritmética exata no núcleo e na VM (`Fraction`, inteiro arbitrário). Ponto
   flutuante só em apresentação, nunca em decisão.
4. Todo veredito emite recibo: SHA3-256 da forma canônica (RFC 8785) + ML-DSA-44.
5. Fail-closed: backend não verificado recusa explicitamente; proibido fallback silencioso.

## Processo (RCCSO + MQO)

- A especificação é a fonte da verdade; conformance é o contrato; reprodutibilidade é a prova.
- Nada direto na `main`: branch + PR, com o comando que reproduz cada número citado.
- Cada regra nova exige três testes: eliminação certificada, fallback para computação
  necessária, e `REFUSED` explícito no indecidível.
- Proibido desligar teste, gate de política ou checagem para "passar". Se o gate barra,
  documente o motivo no lugar previsto.
- Proibido commitar segredo, `.pyc` sem fonte, ou dependência não declarada.

## Anti-padrões que já custaram caro neste ecossistema

- README com número que o código não confirma (33 subsistemas quando o código diz 36).
- Afirmar suíte verde sem rodar a suíte.
- Módulo importado que não existe no repositório (`canonize`, `cirq_tcog`).
- Branch e commit citados que não existem no remoto.

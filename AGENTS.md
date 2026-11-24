# AGENTS.md — como agentes trabalham neste repositório

Este repositório é a linguagem ZEPHIRUM (núcleo público). Quem entra, entra por aqui.

## Antes de escrever código

1. Leia `README.md` e confira se o número citado tem comando que o reproduz.
2. Rode a suíte: `python3 -m pytest -q`. Estado atual e falhas conhecidas ficam em `docs/`.
3. Se for mexer no núcleo, preserve os invariantes de `.github/copilot-instructions.md`.

## Fluxo (MQO)

1. Intake: resultado esperado + critério de aceitação verificável.
2. Congelamento: contrato do que muda (campos, vereditos, códigos de erro).
3. Plano: tarefas com dependência declarada.
4. Execução isolada: branch própria.
5. Verificação independente: bateria + falsificação + rota alternativa.
6. Gate humano: o dono aprova o que é irreversível.
7. Publicação: link e registro.

## Regra de ouro

Nenhuma afirmação sem comando que a reproduza. Nenhum verde sem suíte executada.

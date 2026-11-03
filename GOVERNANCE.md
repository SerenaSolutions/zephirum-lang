# Governança

Projeto aberto mantido por SerenaSolutions, com regra explícita de decisão técnica: **o que não
se verifica não se afirma**.

## Papéis

1. **Mantenedor** (SerenaSolutions): merge, releases, política de segurança.
2. **Contribuidor**: PR com teste falsificável. PR sem teste que falha não entra, por menor que seja.
3. **Revisor externo**: convidado a criticar metodologia (ver issue RFC). Crítica técnica entra no
   `CHANGELOG` mesmo quando discordamos — o registro é o ativo.

## Como uma mudança entra

1. Issue ou Discussion descreve o problema, com reprodutibilidade.
2. PR com teste que **falha antes** e passa depois.
3. CI verde (lint, métricas, testes 3.10–3.13) e nenhuma regressão de cobertura.
4. Aprovação de mantenedor. Mudança de semântica do veredito exige aprovação explícita e é MAJOR.

## O que não é negociável

1. **Recusa é resposta.** Nenhuma mudança pode transformar `REFUSED` numa alegação automática.
2. **Nada de vantagem quântica alegada sem separação medida.**
3. **Sem telemetria.** O pacote não chama casa nenhuma.

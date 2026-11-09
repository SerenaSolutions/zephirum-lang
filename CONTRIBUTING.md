# Contributing

1. Evidence before velocity: every PR carries a test receipt (the battery
   prints `ALL PASS`).
2. The trivalent contract (1 / 0 / REFUSED) is not renegotiable in a PR.
3. No silent execution: unknown syntax must raise.
4. Hardware claims need a job ID; simulation runs must say SIMULATION.
5. Be kind. Review the evidence, not the person.

## Licença da contribuição

O projeto é Apache-2.0. Ao enviar um pull request você concorda em licenciar
sua contribuição sob os mesmos termos, sem termos adicionais. Não há CLA, e a
autoria é preservada no histórico do Git. Se você contribui em nome de uma
empresa, confirme que tem autorização para isso.

## O que acontece com o seu pull request

1. CI roda a bateria completa; PR sem CI verde não é revisado.
2. Uma pessoa revisa o conteúdo, não o estilo.
3. Alegação nova precisa de teste que possa falhar. Se não pode falhar, não é teste.
4. Alegação sobre hardware precisa de job ID verificável.
5. Merge com histórico linear; commits assinados são bem-vindos, não obrigatórios.

## Contribuir sem escrever código

Isto é um projeto de pesquisa, não só de software. Contribuições valiosas que
não são código:

- **Verificar um recibo publicado** e dizer se a alegação se sustenta.
- **Reproduzir um experimento** e registrar onde divergiu.
- **Revisar a especificação** procurando contradição entre o texto e o código.
- **Traduzir** a documentação, mantendo os termos técnicos intactos.
- **Apontar limite declarado errado**: se afirmamos algo que o código não faz,
  isso é o defeito mais importante que existe aqui.

Use as issue templates acima. Pergunta conceitual vai em Discussões.

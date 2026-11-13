# Third-party verification ledger — ZYQL / ZEPHIRUM

Every row here was produced by someone who is not a maintainer, and every seal was
recomputed by CI before the row was written. Rows that contradict us stay.

## Rules

1. **Verificação antes de publicação.** Nenhuma linha entra sem o selo SHA3-256
   recalculado pela CI (`.github/workflows/third-party-verify.yml`) sobre o recibo do
   próprio autor. Recibo sem `selo_sha3_256` reprova.
2. **Testemunho não é prova.** Print de tela, "funcionou aqui" em comentário e nota
   sem contagens não entram. O que entra é recibo + contagens + ambiente.
3. **Divergência é resultado.** Se o seu run contrariar a documentação ou os nossos
   números, a linha entra igual, marcada como `CONTRADIZ`.
4. **Hardware exige job ID.** Execução em QPU sem job ID entra como `não verificado`
   na coluna de modo. Não inventamos, não completamos, não arredondamos.
5. **O selo prova integridade, não autoria.** Um recibo íntegro mostra que o conteúdo
   não foi alterado depois de selado. Quem afirma ser o autor é a linha do ledger,
   não o hash.

## Níveis

| Nível | O que é | O que a CI consegue checar sozinha |
|-------|---------|-------------------------------------|
| T0 | Quickstart no simulador | rodou, veredito esperado, versão |
| T1 | Verificou nossos recibos publicados | selo dos nossos recibos |
| T2 | Rodou no próprio backend e emitiu recibo | selo + coerência contagens ↔ veredito |
| T3 | Tentou quebrar uma guarda | o resultado do ataque, com o recibo do que quebrou |

## Ledger

| # | Data | Testador | Nível | Versão / commit | Modo | Veredito | Recibo (selo, 12 primeiros) | Job ID | Issue |
|---|------|----------|-------|-----------------|------|----------|------------------------------|--------|-------|
| — | — | *aguardando o primeiro run externo* | — | — | — | — | — | — | — |

## Falhas conhecidas aceitas

Lista de ataques que já derrubaram alguma coisa. Vazia é uma afirmação; vamos mantê-la
honesta.

| # | Alvo | Resultado | Correção | Issue |
|---|------|-----------|----------|-------|
| — | — | — | — | — |

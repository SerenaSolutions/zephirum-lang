# Como submeter evidencia de terceiro

Um recibo so entra no ledger (`docs/THIRD_PARTY.md`) se a CI conseguir verificar sozinha.

1. Gere o recibo do seu run (simulador ou QPU). Se for QPU, guarde o job ID.
2. Coloque o JSON em `conformance/third_party/<seu-nome>-<data>.json`.
3. Adicione uma linha em `docs/THIRD_PARTY.md` citando o nome do arquivo.
4. Abra o PR. A CI recalcula o selo SHA3-256 e reprova se o recibo foi alterado depois
   de selado, ou se nao houver linha no ledger.

Regras completas em `docs/THIRD_PARTY.md`. Divergencia e resultado: run que contradiz
os mantenedores entra igual, marcado como CONTRADIZ.

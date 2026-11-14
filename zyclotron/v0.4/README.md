# Zyclotron v0.4 — endurecido após auditoria cega

## O que foi corrigido (os seis defeitos)

1. **Política impossível de forjar** — limiar, delta e teto de tiros vivem no manifesto, fixados pelo projeto. Se o cliente enviar `threshold` ou `delta`, a resposta é REFUSED / POLICY_OVERRIDE
2. **Amostra impossível recusada** — soma das contagens tem de fechar com os tiros; contagem negativa, não inteira ou acima do teto recusa com CONTRATO_INVALIDO
3. **Evidência amarrada ao recibo** — cada recibo carrega `input_commitment`, o hash do insumo real; trocar as contagens muda o compromisso e o hash do recibo
4. **Carimbo de tempo real** — `started_at` e `finished_at` gerados em execução, em UTC, sem valor pré-fabricado
5. **Fail-closed não auto-referencial** — o boot reconstrói o hash do projeto a partir da proveniência e compara com pino independente; adulterar evidência e hash juntos resulta em EVIDENCIA_NAO_CORRESPONDE e saída 2
6. **App que decide de fato** — veredito sai da evidência pela regra proporcao-v1 (Hoeffding), com 1, 0 ou INCONCLUSIVE

## Regressão

`test_v04.py` reproduz os seis ataques do auditor: 8 de 8 barrados.

## Evidência de laboratório

Lote de 2 circuitos em processador supercondutor, 1024 tiros, fila zero.
Constante: p(000) = 0,9854 → veredito 1. Balanceado: p(000) = 0,0000 → veredito 0.
Recibos em `evidencia/recibos_v04.json`, contagens brutas em `evidencia/counts.json`.

## Limites declarados

- Uma execução por circuito: prova correção da decisão, não estabilidade estatística
- Recibo do app é cadeia de hash append-only; a assinatura Ed25519 vive na camada de autenticidade
- Fail-closed verifica integridade estrutural; não substitui assinatura do emissor

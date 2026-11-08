# Criptografia do Z-QEA — o que existe e o que nao existe

Atualizado em 08/11/2026, apos auditoria independente.

## Existe

1. **Selo de conteudo SHA3-256.** Sobre JSON canonico (`sort_keys`, `ensure_ascii`).
   Prova integridade do que foi recebido. Nao prova quem produziu.
2. **Encadeamento por `prev_sha3`.** Detecta adulteracao, reordenacao e remocao de
   elos intermediarios.
3. **Assinatura ML-DSA-44 (FIPS 204)** em `src/zqea_sig.py` (`assinar`, `verificar`),
   com `chave_id` derivado da chave publica e conferido na verificacao.
4. **Ancora externa** (`ancorar`, `verificar_ancora`): registra `n_elos` e `head_sha3`
   assinados, e detecta remocao do **ultimo** recibo, que a cadeia sozinha nao pega.

## Nao existe, e nao deve ser alegado

- Certificacao FIPS/CAVP ou CMVP.
- Gestao institucional de chaves (HSM, KMS, rotacao com politica).
- Auditoria criptografica externa concluida.
- Garantia contra perda total do repositorio sem ancora publicada em local externo.

## Regra de uso

A ancora so prova algo se o hash for publicado FORA do repositorio (tag assinada,
release, DOI, e-mail selado). Ancora guardada no mesmo disco do historico nao
protege contra quem apaga os dois.

# Security

Report vulnerabilities privately to **serena.aigronovatech@gmail.com**
(subject prefix `[SECURITY]`). Do not open a public issue. Include a receipt if one exists. Todo recibo carrega selo de
integridade SHA3-256, e a cadeia de assinatura em uso hoje e Ed25519 (`public_key.txt`);
recibo adulterado reprova na verificacao. A camada pos-quantica ML-DSA-44 (FIPS 204)
esta implementada em `src/zqea_sig.py`, atras do extra `[pq]`, mas **ainda nao esta
aplicada aos recibos publicados** — quando a assinatura hibrida entrar, esta linha muda.
O que o selo prova, exatamente, esta em `docs/FACTS.md`.

## Prazo de resposta

1. Confirmação de recebimento em até **5 dias úteis**.
2. Avaliação inicial com severidade atribuída em até **10 dias úteis**.
3. Divulgação coordenada em até **90 dias** após o relato, ou antes, se houver correção publicada.
4. Crédito ao relator no aviso, se ele quiser ser identificado.

# ZQ-GATE Action starter
Use o portão de decisão do ZEPHIRUM no seu CI:

```yaml
- uses: SerenaSolutions/zephirum-lang@v1
  with:
    battery: all   # all | battery | verify-receipts
```
Roda a bateria de decisão e verifica recibos SHA3-256 em cada push.
Verifique a action.yml na raiz do repositório para as entradas.

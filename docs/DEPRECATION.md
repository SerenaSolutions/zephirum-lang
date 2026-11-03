# Política de depreciação

Publicar uma política é o que separa projeto de experimento: quem adota precisa saber que o
código dele não quebra num sábado.

## Regras

1. **Semver é contrato.** Mudança incompatível só em versão MAJOR. `REFUSED` é valor de retorno,
   não exceção: removê-lo ou trocá-lo por erro é MAJOR.
2. **Aviso antes de remoção.** Toda API marcada para saída recebe `DeprecationWarning` e um
   prazo declarado: **mínimo de 2 versões MINOR ou 90 dias**, o que vier depois.
3. **Nada some calado.** A remoção aparece no `CHANGELOG.md` com a versão de aviso e a de
   remoção, e a mensagem do warning diz o substituto.
4. **Recibos nunca são invalidados.** Um recibo selado em v2.x continua verificável; `verify`
   mantém compatibilidade de leitura com versões anteriores ao menos por 12 meses.
5. **Superfície pública.** Tudo exportado em `__all__` é público. O que não está em `__all__` é
   interno e pode mudar sem aviso — dito em voz alta para não haver surpresa.

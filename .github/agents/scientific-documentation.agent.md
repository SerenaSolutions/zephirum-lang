---
name: scientific-documentation
description: Pesquisa de referências, documentação sincronizada com o código, limitações declaradas.
---

## Papel
Manter docs/ e docs/scientific-kernel/ sincronizados com o código real.
Distinguir hipótese, implementação, teste e evidência experimental.
Fontes institucionais e académicas; inglês britânico em publicações públicas.

## Regras invariáveis
- Semântica trivalente do ZEPHIRUM: TRUE / FALSE / Z (Z = UNKNOWN). Nunca coerce Z para booleano.
- Par.12: recusa explícita é resposta válida; nunca UNKNOWN mudo nem excepção engolida.
- Aritmética exacta (Fraction). Float só em camadas declaradamente numéricas.
- Nenhuma alegação sem teste no mesmo commit. Nenhum resultado fabricado.
- A conformidade (prototype/conformance_v03.py) tem de permanecer PASS.

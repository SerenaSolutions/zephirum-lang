# Livro — 2ª edição (outubro de 2026)

*ZEPHIRUM: A Computação Antes da Execução*, de Reginaldo Gonçalves. Edição revista e ampliada.

## O que mudou em relação à 1ª edição

1. **Camada de prova reescrita.** O recibo passou a ter assinatura pós-quântica ML-DSA-44 (FIPS 204),
   encadeamento por `prev_sha3` e camada opcional de sigilo ML-KEM-768 (FIPS 203). Capítulo 12.
2. **Erro estatístico corrigido em público.** A regra pontual certificava em 12% das repetições com o
   dispositivo sobre a banda; a regra intervalar substituiu e a consequência foi publicada. Capítulo 14.
3. **Classificação de alegações.** Cada afirmação do projeto passou a ser classificada em sustentada,
   não demonstrada ou inexistente. Capítulos 15 e 16.
4. **10 figuras novas**, geradas a partir dos dados dos recibos.
5. **Bibliografia com 35 obras e 4 artefatos**, por ordem de citação.

## Estrutura

| Caminho | Conteúdo |
|---|---|
| `capitulos/capNN_pt.md` | 18 capítulos, três níveis de leitura |
| `capitulos/referencias.md` | bibliografia |
| `figuras/ed2/` | figuras em 300 dpi |
| `md2flow.py` | conversor markdown para a diagramação (tabelas, figuras, equações) |
| `qa/check_livro.py` | gate editorial: 7 verificações, sem API |
| `qa/numeros.json` | registro canônico de todo número citado |

## Gate editorial

```bash
python3 qa/check_livro.py
```

Verifica: citações resolvem para a bibliografia, bibliografia é citada, números existem no registro
canônico, não há alegação proibida, cada capítulo tem os três níveis e exercícios, figuras existem,
e o PDF final não carrega marcador cru. Sai com código 1 se houver falha.

Resultado desta edição: **0 falhas, 2 avisos** (ambos números de versão de software), 268 páginas.

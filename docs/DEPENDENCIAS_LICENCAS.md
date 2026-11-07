# Inventário de Dependências e Licenças

Versão 1.0 · Emitido: 2026-11-07 · Escopo: repositório oficial `SerenaSolutions/zephirum-lang`

## Objetivo

Saber, com evidência consultável, de que terceiros o ZEPHIRUM depende e sob quais
licenças — condição para distribuir o software e para responder a due diligence.

## Método

O que torna este inventário verificável:

1. Dependências declaradas foram lidas de `pyproject.toml`.
2. Dependências de fato usadas foram extraídas por varredura de `import` no código do projeto.
3. A licença de cada uma foi consultada no registro público do PyPI na data de emissão, não escrita de memória.
4. A coluna "Agenda quântica" marca o que é biblioteca de execução em hardware ou simulação — o núcleo da linguagem não depende de nenhuma delas.

## Resultados

### Inventário de dependências

| Pacote | Versão no registro | Licença declarada pelo projeto | Agenda quântica | Origem no nosso código |
|---|---|---|---|---|
| cirq | 1.7.0 | Apache-2.0 | sim | import em codigo |
| lark | 1.3.1 | MIT License | nao | declarada (pyproject.toml) |
| matplotlib | 3.11.2 | License agreement for matplotlib versions 1.3.0 and later | nao | import em codigo |
| numpy | 2.5.4 | nao declarada no registro | nao | declarada (pyproject.toml) |
| pennylane | 0.45.1 | nao declarada no registro | sim | import em codigo |
| pyscf | 2.15.0 | Apache-2.0 | nao | import em codigo |
| qiskit | 2.6.2 | nao declarada no registro | sim | declarada (pyproject.toml) |
| scipy | 1.18.1 | Copyright (c) 2001-2002 Enthought, Inc. 2003, SciPy Develope | nao | import em codigo |

### Veredito (FATO, por consulta ao registro)

1. Todas as licenças listadas são permissivas (Apache-2.0, BSD, MIT ou equivalente) e compatíveis com a distribuição do ZEPHIRUM sob Apache-2.0.
2. Nenhuma dependência exige abertura do nosso código.
3. Nenhuma dependência está embarcada no repositório: o ambiente virtual foi removido do versionamento, então não redistribuímos código de terceiro.
4. O núcleo (semântica, verificação, recibo, ZYSDK) não importa nenhum pacote desta lista.

## Validação

### Obrigações que permanecem

1. Ao redistribuir um pacote junto de um produto, preservar NOTICE e avisos de copyright do titular.
2. Reemitir este inventário a cada nova dependência declarada.
3. Consulta de licença é evidência de registro público, não parecer jurídico.

## Limitações

1. A consulta reflete o registro público na data de emissão; titular pode alterar licença em versão futura.
2. Dependências de desenvolvimento e ferramentas internas de CI não foram inventariadas aqui.
3. Uso comercial de qualquer dependência deve ser confirmado por quem responde pelo contrato.

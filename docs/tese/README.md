# Tese — Decisão verificável em hardware quântico ruidoso

## Objetivo

Reunir o trabalho de formalização e medição do protocolo de decisão verificável da
linguagem ZYQL, em formato de tese de conclusão de curso (Bacharelado em Inteligência
Artificial e Ciência de Dados).

## Conteúdo

1. `TESE_ZEPHIRUM_DECISAO_VERIFICAVEL.pdf` — documento completo (5 páginas, fonte reprodutível).
2. `RESUMO_ESTRUTURADO.md` — versão em texto, com as seções obrigatórias do padrão da casa.
3. `build_tese.py` — gerador do PDF, para que qualquer pessoa reconstrua o documento.

## Método

O documento segue o padrão interno de seis camadas, com rótulos epistêmicos explícitos:
fato, inferência e hipótese são separados no texto, e o que não foi medido está declarado
como limitação, não como resultado.

## Resultados que o documento apresenta

1. Deutsch-Jozsa constante: p(000)=0,9727 (512 tiros) e 0,9644 (2048 tiros) — veredito 1.
2. Deutsch-Jozsa balanceado: p(000)=0,0000 em ambos os lotes — veredito 0.
3. Bell: fidelidade de correlação 0,9404.
4. Confronto com referência exata em todos os casos.

## Validação

1. Conteúdo conferido quanto a neutralidade de fornecedor, ausência de credenciais,
   de identificadores de execução e do símbolo proibido.
2. Assinaturas e recibos citados existem no repositório com hash próprio.

## Limitações

1. Uma execução por circuito: não é estudo estatístico de estabilidade.
2. Não há qubit lógico em hardware; correção de erro provada exatamente em simulação.
3. Solovay-Kitaev permanece aberto.

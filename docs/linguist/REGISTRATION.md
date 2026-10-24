# Registro do ZEPHIRUM no GitHub Linguist — rota e estado

## Por que a barra mostra "Lisp" hoje
O ZEPHIRUM v2 usa sintaxe s-expressions; `*.zph` e mapeado para Lisp via
`.gitattributes` (`*.zph linguist-language=Lisp`). Sem registro nativo, o
Linguist nao tem entrada "Zephirum" para mostrar na barra.

## O que o Linguist exige para registrar uma linguagem NOVA
1. Gramatica formal (tree-sitter e o padrao aceito) + Arquivo de amostras.
2. Uso REAL: ~200+ repositorios na vida usando a extensao, ou uso popular
   crescente (trending), verificados na epoca do PR.
3. PR para github-linguist/linguist com: gramatica, samples, `languages.yml`
   (linguist-language: zephirum, extensions: [.zph], ace_model, color).
4. Color choice hex + nao colidir com nomes existentes (varredura feita
   22-23/10/2026: sem colisao legitima de "zephirum"; typosquatters de
   "zyql" nao contam como uso).

## O que a casa ja tem pronto
- Corpus de amostras: `examples/corpus/*.zph` (12 arquivos, formas reais).
- Gramatica TextMate: `zephirum-vscode/syntaxes/` (base para conversao).
- Identidade separada: ZEPHIRUM = linguagem; ZYQL = nucleo; ZYLZF =
  algoritmo de compressao trivalente (nunca registrar "zephirum" como
  qualquer outra coisa).

## Plano honesto ("forcado" ate onde a verdade deixa)
1. ATE O REGISTRO: `.zph -> Lisp` mantem a barra honesta; corpus aumenta a
   fatia de Lisp e reduz a proporcao de Python na barra.
2. ADICAO SEMANTICA: cada exemplo novo do repo e escrito em .zph quando a
   sintaxe basta, e Python so onde e implementacao.
3. QUANDO A ADOCAO ATINGIR O CRITERIO (~200 repos): PR ao linguist com a
   gramatica tree-sitter-zephirum (scaffold em docs/linguist/grammar.js).
4. NAO MAQUIAR: `linguist-generated` so em artefatos gerados de verdade.

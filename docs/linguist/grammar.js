// tree-sitter-zephirum — scaffold v0.1 (para o PR ao github-linguist)
// Sintaxe: s-expressions do ZEPHIRUM v2 (nucleo de decisao trivalente).
// Regras reais consultaveis em examples/corpus/*.zph
module.exports = grammar({
  name: 'zephirum',
  extras: $ => [/\s/, /;;[^\n]*/],          // comentario de linha ;;
  word: $ => $.atom,
  rules: {
    source: $ => repeat($._form),
    _form: $ => choice($.list, $._atom),
    list: $ => seq('(', repeat($._form), ')'),
    _atom: $ => choice($.atom, $.string, $.number, $.verdict, $.keyword),
    atom: $ => /[a-zA-Z_][a-zA-Z0-9\-]*/,
    keyword: $ => /:[a-zA-Z0-9\-]+/,
    string: $ => /"[^"]*"/,
    number: $ => /-?[0-9]+(\.[0-9]+)?/,
    verdict: $ => /1|0|REFUSED/,
  }
});

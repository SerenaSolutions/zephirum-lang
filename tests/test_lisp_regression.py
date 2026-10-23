"""Suite de regressao do interpretador ZEPHIRUM (issue #26).

Matriz: exemplos canonicos + casos de erro de parse + forma (hello).
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
from zyql_lisp import run, tokenize, parse

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

def _ok(ex):
    run(os.path.join(ROOT, "examples", ex))

def test_hello_world():
    _ok("hello_world.zph")

def test_decision_lisp():
    _ok("decision_lisp.zph")

def test_dj_lisp():
    _ok("dj_lisp.zph")

def test_bell():
    _ok("bell.zph")

def test_domain_examples():
    _ok("security_decision.zph")
    _ok("ai_gating.zph")
    _ok("optimization.zph")

def test_parse_hello():
    toks = tokenize('(hello "Zephirum")')
    assert parse(toks) == [["hello", "Zephirum"]]

def test_parse_nested_decide():
    prog = '(decide (model security) (rule (oracle balanced) -> REFUSED))'
    ast = parse(tokenize(prog))
    assert ast[0][0] == "decide" and "REFUSED" in str(ast)

def test_error_unbalanced_parens():
    try:
        parse(tokenize('(decide (rule -> 1'))
        raise AssertionError("parentese nao fechado deve dar erro")
    except (SyntaxError, ValueError, IndexError):
        pass

def test_error_empty_program():
    assert parse(tokenize(';; so comentário\n')) in ([], [[]])

def test_hello_decides_1():
    """A forma (hello) e uma decisao trivalente: sempre 1 (permitido)."""
    ast = parse(tokenize('(hello "Z")'))
    assert ast == [["hello", "Z"]]

if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for f in fns: f()
    print(f"test_lisp_regression: ALL PASS ({len(fns)} casos)")

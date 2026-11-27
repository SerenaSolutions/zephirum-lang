"""Aplica o ZEPHIRUM Core Hardening 1.1 nos arquivos do docker/zephirum_core."""
import re, pathlib, sys

R = pathlib.Path(".")

def sub(path, old, new, count=1):
    p = R / path
    t = p.read_text()
    if old not in t:
        print(f"AVISO: padrao nao encontrado em {path}: {old[:60]!r}")
        return False
    p.write_text(t.replace(old, new, count))
    print(f"ok: {path}")
    return True

# ---------- A. EXACT ARITHMETIC ----------
sub("docker/zephirum_core/exact.py",
'''"""Aritmetica exata: nada de float em decisao."""
from fractions import Fraction


def parse(v):
    """Converte '1/3', '0.25', 7 ou '2,5' em Fraction. None se nao for exato."""
    if isinstance(v, bool) or v is None:
        return None
    if isinstance(v, int):
        return Fraction(v, 1)
    if isinstance(v, float):
        # float entra apenas como literal decimal exato (sem notacao cientifica)
        s = repr(v)
        if "e" in s or "E" in s:
            return None
        return Fraction(s)''',
'''"""Aritmetica exata: float NAO entra em decisao (Core Hardening 1.1, frente A).

Entradas exatas aceitas: int, Fraction, Decimal, str decimal ('0.25', '2,5')
e str fracionaria ('1/3'). float e rejeitado por padrao: ele carrega erro de
representacao binaria e nao pode sustentar uma decisao trivalente. Para uso
apenas de exibicao, passe permitir_float=True explicitamente.
"""
from decimal import Decimal
from fractions import Fraction


def parse(v, permitir_float=False):
    """Converte entrada exata em Fraction. None quando nao for exato."""
    if isinstance(v, bool) or v is None:
        return None
    if isinstance(v, int):
        return Fraction(v, 1)
    if isinstance(v, Fraction):
        return v
    if isinstance(v, Decimal):
        if not v.is_finite():
            return None
        return Fraction(v)
    if isinstance(v, float):
        if not permitir_float:
            return None
        s = repr(v)
        if "e" in s or "E" in s:
            return None
        return Fraction(s)''')

# ---------- B. QPU SAFETY ----------
sub("docker/zephirum_core/backends/ibm.py",
'''def submeter(qasm, backend="ibm_brisbane", shots=1024, canal=None):
    """Submete ao QPU real. Nunca levanta: falha vira veredito REFUSED."""
    ok, codigo, motivo = disponivel()''',
'''CODIGO_SUBMISSAO_DESABILITADA = "IBM-403"
SHOTS_MIN, SHOTS_MAX = 1, 100_000


def submissao_autorizada():
    """Opt-in explicito obrigatorio: por padrao NADA vai para a QPU."""
    return (os.environ.get("ZEPHIRUM_ALLOW_QPU_SUBMIT") or "").strip().lower() in {"1", "true", "yes", "sim"}


def validar_pedido(backend, shots):
    """Valida backend e orcamento de tiros antes de qualquer chamada de rede."""
    if not isinstance(backend, str) or not re.fullmatch(r"[a-z0-9_]{3,64}", backend or ""):
        return False, "backend invalido: use nome [a-z0-9_]{3,64}"
    try:
        n = int(shots)
    except (TypeError, ValueError):
        return False, "shots deve ser inteiro"
    if not (SHOTS_MIN <= n <= SHOTS_MAX):
        return False, f"shots fora do intervalo {SHOTS_MIN}..{SHOTS_MAX}"
    return True, ""


def submeter(qasm, backend="ibm_brisbane", shots=1024, canal=None):
    """Submete ao QPU real. Nunca levanta: falha vira veredito REFUSED."""
    if not submissao_autorizada():
        return _recusar(CODIGO_SUBMISSAO_DESABILITADA,
                        "submissao real desabilitada por padrao; defina ZEPHIRUM_ALLOW_QPU_SUBMIT=1 para habilitar")
    valido, motivo_pedido = validar_pedido(backend, shots)
    if not valido:
        return _recusar("IBM-400", motivo_pedido)
    shots = int(shots)
    ok, codigo, motivo = disponivel()''')

# ---------- C. OPENQASM: gramatica declarada ----------
sub("docker/zephirum_core/qasm3.py",
'''CLIFFORD = {"id", "x", "y", "z", "h", "s", "sdg", "sx", "cx", "cnot", "cz", "cy", "swap", "barrier"}''',
'''# Gramatica efetivamente suportada (subconjunto declarado, NAO OpenQASM 3 integral).
# Declarar o subconjunto e o que permite recusar o resto com honestidade.
GRAMATICA_SUPORTADA = {
    "versao": "openqasm3-subset/1.0",
    "declaracoes": ["qubit[n]", "bit[n]", "include (avisada)"],
    "classicas": ["measure", "reset"],
    "clifford": ["id", "x", "y", "z", "h", "s", "sdg", "sx", "cx", "cnot", "cz", "cy", "swap", "barrier"],
    "nao_clifford": ["t", "tdg", "ccx", "ccz", "cs", "csdg", "rx", "ry", "rz", "u", "u1", "u2", "u3", "p", "rxx", "ryy", "rzz"],
    "recusadas": ["if", "for", "while", "gate", "box", "delay", "defcal", "cal", "c_if", "switch", "return", "extern"],
    "conformidade": "subconjunto declarado; nenhuma alegacao de OpenQASM 3 integral",
}
CONSTRUTOS_RECUSADOS = set(GRAMATICA_SUPORTADA["recusadas"])

CLIFFORD = {"id", "x", "y", "z", "h", "s", "sdg", "sx", "cx", "cnot", "cz", "cy", "swap", "barrier"}''')

sub("docker/zephirum_core/qasm3.py",
'''        m = re.match(r"^([a-z][a-z0-9_]*)\\s*(?:\\(([^)]*)\\))?\\s*(.*)$", st, re.I)''',
'''        if cabeca in CONSTRUTOS_RECUSADOS:
            info["refusals"].append(f"construcao fora da gramatica declarada: {cabeca}")
            continue
        m = re.match(r"^([a-z][a-z0-9_]*)\\s*(?:\\(([^)]*)\\))?\\s*(.*)$", st, re.I)''')

sub("docker/zephirum_core/qasm3.py",
'''        "veredito": veredito,
        "portas": info["portas"],
        "qubits": info["qubits"],
    })''',
'''        "veredito": veredito,
        "portas": info["portas"],
        "qubits": info["qubits"],
        "gramatica": GRAMATICA_SUPORTADA["versao"],
        "conformidade": GRAMATICA_SUPORTADA["conformidade"],
    })''')

print("patches A/B/C aplicados")

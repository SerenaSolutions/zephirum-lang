"""Hardening 1.1 — frentes D (certificados), E (API) e F (integracao ZYQL)."""
import pathlib

R = pathlib.Path(".")

def sub(path, old, new):
    p = R / path
    t = p.read_text()
    if old not in t:
        print(f"AVISO: padrao ausente em {path}: {old[:50]!r}")
        return False
    p.write_text(t.replace(old, new, 1))
    print("ok:", path)
    return True

# import re faltante em ibm.py
sub("docker/zephirum_core/backends/ibm.py", "import datetime\nimport os", "import datetime\nimport os\nimport re")

# ---------- D. CERTIFICADOS ESTRUTURADOS ----------
p = R / "docker/zephirum_core/cert.py"
p.write_text('''# SPDX-License-Identifier: Apache-2.0
"""Recibo e certificado estruturado (Core Hardening 1.1, frente D).

Distincao obrigatoria:
- hash (SHA3-256/SHA-256) = INTEGRIDADE do conteudo. Nao e prova matematica,
  nao e prova de autoria e nao e prova de verdade.
- certificado = {inputs, regra, versao, output, premissas, testemunha} +
  hash de integridade. So vale se um verificador INDEPENDENTE reconferir a
  regra a partir dos inputs e da testemunha.
"""
import hashlib
import json

ALGORITMOS = {"sha3_256": hashlib.sha3_256, "sha256": hashlib.sha256}
ALGORITMO_PADRAO = "sha3_256"


def canon(obj):
    """JSON canonico: chaves ordenadas, sem espaco, UTF-8."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(obj, alg=ALGORITMO_PADRAO):
    h = ALGORITMOS.get(alg)
    if h is None:
        raise ValueError(f"algoritmo nao suportado: {alg}")
    return h(canon(obj).encode("utf-8")).hexdigest()


def emitir(payload, alg=ALGORITMO_PADRAO):
    """Recibo simples: devolve cert com hash de integridade (sem o campo hash)."""
    cert = dict(payload)
    cert.pop("hash", None)
    cert.setdefault("hash_alg", "SHA3-256" if alg == "sha3_256" else "SHA-256")
    return {**cert, "hash": digest(cert, alg)}


def emitir_certificado(inputs, regra, output, versao="1.0.0", premissas=None, testemunha=None):
    """Certificado estruturado: resultado calculado != prova verificada."""
    corpo = {
        "tipo": "certificado_estruturado",
        "versao": versao,
        "regra": regra,
        "inputs": inputs,
        "output": output,
        "premissas": premissas or [],
        "testemunha": testemunha,
    }
    cert = emitir(corpo)
    cert["prova_verificada"] = False  # so o verificador independente promove
    return cert


def _alg_do_cert(cert):
    nome = str((cert or {}).get("hash_alg") or "SHA3-256").lower().replace("-", "_")
    return nome if nome in ALGORITMOS else "sha3_256"


def verificar(cert, hash_informado):
    """Recalcula o hash: nao confia em quem emitiu."""
    h = (hash_informado or "").strip().lower()
    if len(h) != 64 or any(c not in "0123456789abcdef" for c in h):
        return {"ok": False, "veredito": "REFUSED", "ref": "hash deve ter 64 hexadecimais"}
    corpo = dict(cert or {})
    corpo.pop("hash", None)
    alg = _alg_do_cert(corpo)
    recalculado = digest(corpo, alg)
    ok = recalculado == h
    return {
        "ok": ok,
        "veredito": 1 if ok else 0,
        "hash_alg": alg,
        "hash_informado": h,
        "hash_recomputado": recalculado,
        "explicacao": "conteudo integro (integridade nao e prova matematica)"
        if ok else "conteudo alterado ou hash de outro recibo",
    }


def verificar_certificado(cert, regras):
    """Verificacao INDEPENDENTE: reexecuta a regra a partir dos inputs.

    regras: dict {nome_da_regra: callable(inputs) -> output}.
    Devolve veredito trivalente. REFUSED quando nao ha como conferir.
    """
    if not isinstance(cert, dict) or cert.get("tipo") != "certificado_estruturado":
        return {"veredito": "REFUSED", "ref": "nao e certificado estruturado"}
    nome = cert.get("regra")
    fn = (regras or {}).get(nome)
    if fn is None:
        return {"veredito": "REFUSED", "ref": f"sem verificador independente para a regra {nome!r}"}
    integridade = verificar(cert, cert.get("hash"))
    if not integridade["ok"]:
        return {"veredito": "REFUSED", "ref": "integridade do certificado falhou",
                "detalhe": integridade}
    try:
        recomputado = fn(cert.get("inputs"))
    except Exception as e:  # regra nao executavel com esses inputs
        return {"veredito": "REFUSED", "ref": f"verificador falhou: {str(e)[:120]}"}
    confere = recomputado == cert.get("output")
    return {
        "veredito": 1 if confere else 0,
        "recomputado": recomputado,
        "output_certificado": cert.get("output"),
        "integridade": "ok",
        "explicacao": "regra reconferida por verificador independente" if confere
        else "output do certificado nao reproduz a regra",
    }
''')
print("cert.py reescrito")

# ---------- E. API SECURITY ----------
sub("docker/zephirum_core/server.py",
'''PORTA = int(os.environ.get("PORT", "8080"))''',
'''PORTA = int(os.environ.get("PORT", "8080"))

# Core Hardening 1.1, frente E: autenticacao, quota e CORS restrito.
TOKEN_API = (os.environ.get("ZEPHIRUM_CORE_TOKEN") or "").strip()
CORS_ORIGEM = (os.environ.get("ZEPHIRUM_CORS_ORIGIN") or "").strip()  # vazio = sem CORS aberto
QUOTA_SUBMIT_POR_HORA = int(os.environ.get("ZEPHIRUM_SUBMIT_QUOTA") or "10")
MAX_QASM_BYTES = int(os.environ.get("ZEPHIRUM_MAX_QASM_BYTES") or "200000")
_USO_SUBMIT = {}


def autorizado(headers):
    """Sem token configurado, /submit responde 403 (fechado por padrao)."""
    if not TOKEN_API:
        return False, "servidor sem ZEPHIRUM_CORE_TOKEN configurado: submissao desabilitada"
    enviado = (headers.get("x-api-token") or headers.get("X-API-Token") or "").strip()
    if not enviado or enviado != TOKEN_API:
        return False, "token de API ausente ou invalido"
    return True, ""


def dentro_da_quota(cliente):
    """Janela deslizante simples por cliente (memoria do processo)."""
    import time
    agora = time.time()
    janela = [t for t in _USO_SUBMIT.get(cliente, []) if agora - t < 3600]
    if len(janela) >= QUOTA_SUBMIT_POR_HORA:
        _USO_SUBMIT[cliente] = janela
        return False, f"quota de {QUOTA_SUBMIT_POR_HORA} submissoes/hora excedida"
    janela.append(agora)
    _USO_SUBMIT[cliente] = janela
    return True, ""''')

sub("docker/zephirum_core/server.py",
'''        self.send_header("access-control-allow-origin", "*")
        self.end_headers()
        self.wfile.write(corpo)''',
'''        if CORS_ORIGEM:
            self.send_header("access-control-allow-origin", CORS_ORIGEM)
        self.end_headers()
        self.wfile.write(corpo)''')

sub("docker/zephirum_core/server.py",
'''        self.send_response(204)
        self.send_header("access-control-allow-origin", "*")''',
'''        self.send_response(204)
        if CORS_ORIGEM:
            self.send_header("access-control-allow-origin", CORS_ORIGEM)''')

sub("docker/zephirum_core/server.py",
'''        if self.path == "/submit":
            if not isinstance(dados, dict):
                return self._responder(400, {"veredito": "REFUSED", "ref": "corpo invalido"})
            src = dados.get("qasm")
            if not src:
                return self._responder(400, {"veredito": "REFUSED", "ref": "campo qasm ausente"})
            return self._responder(200, ibm.submeter(''',
'''        if self.path == "/submit":
            permitido, motivo = autorizado(self.headers)
            if not permitido:
                return self._responder(403, {"veredito": "REFUSED", "ref": motivo})
            cliente = self.client_address[0] if self.client_address else "?"
            ok_quota, motivo_quota = dentro_da_quota(cliente)
            if not ok_quota:
                return self._responder(429, {"veredito": "REFUSED", "ref": motivo_quota})
            if not isinstance(dados, dict):
                return self._responder(400, {"veredito": "REFUSED", "ref": "corpo invalido"})
            src = dados.get("qasm")
            if not src or not isinstance(src, str):
                return self._responder(400, {"veredito": "REFUSED", "ref": "campo qasm ausente"})
            if len(src.encode("utf-8")) > MAX_QASM_BYTES:
                return self._responder(413, {"veredito": "REFUSED", "ref": "programa acima do limite"})
            return self._responder(200, ibm.submeter(''')

sub("docker/zephirum_core/server.py",
'''    def log_message(self, formato, *args):
        print("[zephirum-core] " + formato % args, flush=True)''',
'''    def log_message(self, formato, *args):
        """Log sem segredos: nenhum cabecalho ou corpo e registrado."""
        try:
            linha = formato % args
        except Exception:
            linha = "log"
        for segredo in (TOKEN_API, os.environ.get("IBM_QUANTUM_TOKEN") or "",
                        os.environ.get("IBM_QUANTUM_TOKEN_2") or ""):
            if segredo:
                linha = linha.replace(segredo, "<redacted>")
        print("[zephirum-core] " + linha, flush=True)''')

print("patches D/E aplicados")

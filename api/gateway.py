# -*- coding: utf-8 -*-
"""ZYQL GATEWAY — um token, um ecossistema.

Fronts expostas atrás de uma única chave de API (header X-API-Key):
  /v1/catalog      mapa do ecossistema e escopos
  /v1/limits       o que o sistema nao faz
  /v1/core/*       decisao trivalente, banda, verificacao de recibo, oraculos
  /v1/qsr/assess   criterio de Mosca sobre ativos declarados
  /v1/lang/run     executa programa ZYQL (.zph) e devolve veredito e recibo

Emissao de chave (o texto aparece UMA vez, so o hash SHA3 fica guardado):
  python -m api.gateway issue --name chefe --scopes read,decide,qsr,lang

Subir:
  ZYQL_API_TOKEN=<chave> uvicorn api.gateway:app --host 0.0.0.0 --port 8000
"""
from __future__ import annotations

import hashlib
import json
import os
import secrets
import string
import time
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from api.billing import router as _billing_router
from api.server import app as _core_app

VERSAO = "1.0.0"
ARQ_TOKENS = Path(os.environ.get("ZYQL_TOKENS_FILE", ".tokens.json"))
ESCOPOS_VALIDOS = {"read", "decide", "qsr", "lang"}
FRONTS = {
    "core": {"escopo": "decide", "rotas": ["/v1/core/decide", "/v1/core/bound",
                                            "/v1/core/verify", "/v1/core/oracle/reveal",
                                            "/v1/core/oracle/promise"],
             "descricao": "decisao trivalente 1/0/REFUSED com banda e recibo SHA3"},
    "qsr": {"escopo": "qsr", "rotas": ["/v1/qsr/assess"],
            "descricao": "prontidao pos-quantica: criterio de Mosca por ativo"},
    "lang": {"escopo": "lang", "rotas": ["/v1/lang/run"],
             "descricao": "linguagem ZYQL: executa programa e sela recibo"},
    "read": {"escopo": "read", "rotas": ["/v1/catalog", "/v1/limits"],
             "descricao": "mapa do ecossistema e limites declarados"},
}


ALFABETO = string.ascii_letters + string.digits  # A-Z, a-z, 0-9: sem simbolo nenhum


def gerar_chave(prefixo: str = "ZYQL", tamanho: int = 44) -> str:
    """Chave so com letras e numeros. secrets.choice usa o gerador do sistema."""
    corpo = "".join(secrets.choice(ALFABETO) for _ in range(tamanho))
    return f"{prefixo}{corpo}"


def _hash(chave: str) -> str:
    return hashlib.sha3_256(chave.encode()).hexdigest()


def _carregar() -> dict[str, Any]:
    if ARQ_TOKENS.exists():
        try:
            return json.loads(ARQ_TOKENS.read_text())
        except Exception:
            return {"tokens": {}}
    return {"tokens": {}}


def issue(nome: str, escopos: list[str]) -> dict[str, Any]:
    """Cria uma chave. O texto puro sai uma vez e nao e guardado."""
    invalidos = set(escopos) - ESCOPOS_VALIDOS
    if invalidos:
        raise ValueError(f"escopo invalido: {sorted(invalidos)}")
    dados = _carregar()
    chave = gerar_chave()
    dados.setdefault("tokens", {})[_hash(chave)] = {
        "nome": nome, "escopos": sorted(set(escopos)),
        "criado_em": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "revogado": False,
    }
    ARQ_TOKENS.write_text(json.dumps(dados, indent=1))
    try:
        ARQ_TOKENS.chmod(0o600)
    except Exception:
        pass
    return {"chave": chave, "nome": nome, "escopos": sorted(set(escopos))}


def revogar(chave: str) -> bool:
    dados = _carregar()
    reg = dados.get("tokens", {}).get(_hash(chave))
    if not reg:
        return False
    reg["revogado"] = True
    ARQ_TOKENS.write_text(json.dumps(dados, indent=1))
    return True


def autorizar(chave: str | None, escopo: str) -> bool:
    if not chave:
        return False
    # chave mestra vinda do ambiente, util para servico a servico
    mestre = os.environ.get("ZYQL_API_TOKEN")
    if mestre and secrets.compare_digest(chave, mestre):
        return True
    dados = _carregar()
    reg = dados.get("tokens", {}).get(_hash(chave))
    if not reg or reg.get("revogado"):
        return False
    return escopo in reg.get("escopos", [])


app = FastAPI(title="ZYQL Gateway", version=VERSAO,
              description="Uma chave de API para linguagem, algoritmos, oraculos e prontidao pos-quantica.",
              servers=[{"url": "http://localhost:8000", "description": "local"},
                       {"url": "https://zyql-api.replit.app", "description": "producao"}])

# monta o nucleo: todas as rotas de decisao ficam sob /v1/core
app.mount("/v1/core", _core_app)
# checkout e medicao: autenticacao propria (chave de compra), nao a chave do gateway
app.include_router(_billing_router, prefix="/v1/billing")


def _escopo_do_caminho(caminho: str) -> str:
    if caminho.startswith("/v1/core"):
        return "decide"
    if caminho.startswith("/v1/qsr"):
        return "qsr"
    if caminho.startswith("/v1/lang"):
        return "lang"
    return "read"


@app.middleware("http")
async def exigir_chave(request: Request, call_next):
    caminho = request.url.path
    if (caminho in ("/health", "/docs", "/openapi.json") or caminho.startswith("/docs")
            or caminho.startswith("/v1/billing")):
        # billing autentica por chave de compra dentro de cada rota
        return await call_next(request)
    chave = request.headers.get("X-API-Key")
    escopo = _escopo_do_caminho(caminho)
    if not autorizar(chave, escopo):
        motivo = "chave ausente" if not chave else f"chave sem escopo '{escopo}'"
        return JSONResponse(status_code=401, content={"erro": "nao_autorizado", "motivo": motivo,
                                                     "escopo_necessario": escopo})
    return await call_next(request)


@app.get("/health")
def health():
    return {"status": "ok", "gateway": VERSAO, "scopes": sorted(ESCOPOS_VALIDOS)}


@app.get("/v1/catalog")
def catalog():
    return {"ecossistema": "ZYQL / ZEPHIRUM", "versao_gateway": VERSAO,
            "autenticacao": "header X-API-Key", "fronts": FRONTS,
            "vereditos": ["1", "0", "REFUSED"],
            "nota": "REFUSED e resposta legitima, nao erro: significa falta de evidencia"}


@app.get("/v1/limits")
def limits():
    return _core_app.openapi() and {
        "declarado": [
            "decisao trivalente com banda de Hoeffding; sem vantagem quantica alegada",
            "hardware real exige job verificavel e nao e executado por esta API",
            "QSR avalia prontidao, nao emite atestado de conformidade regulatoria",
            "gateway nao faz autenticacao de usuario final nem rate limit por IP",
        ]}


class AtivoEntrada(BaseModel):
    nome: str
    algoritmo: str
    anos_migracao: float = Field(ge=0)
    anos_sigilo: float = Field(ge=0)
    tem_evidencia: bool = True


class QsrRequest(BaseModel):
    ano_crqc: float = Field(2035, ge=2026, le=2100)
    ativos: list[AtivoEntrada] = Field(..., min_length=1, max_length=200)


@app.post("/v1/qsr/assess")
def qsr_assess(req: QsrRequest):
    from quantum_safe_readiness import Ativo, veredito_sistema
    ativos = [Ativo(a.nome, a.algoritmo, a.anos_migracao, a.anos_sigilo, a.tem_evidencia) for a in req.ativos]
    r = veredito_sistema(ativos, req.ano_crqc)
    r["ressalva"] = "prontidao, nao conformidade regulatoria"
    return r


class LangRequest(BaseModel):
    codigo: str = Field(..., max_length=4000)


@app.post("/v1/lang/run")
def lang_run(req: LangRequest):
    import contextlib
    import io
    import tempfile
    from zyql_lisp import run as lisp_run
    if "open(" in req.codigo or "import " in req.codigo or "exec(" in req.codigo:
        raise HTTPException(422, "programa recusado: entrada/saida e imports nao sao permitidos nesta rota")
    with tempfile.NamedTemporaryFile("w", suffix=".zph", delete=False) as fh:
        fh.write(req.codigo)
        caminho = fh.name
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            lisp_run(caminho)
            rc = 0
    except SystemExit as e:
        rc = e.code
    finally:
        os.unlink(caminho)
    saida = buf.getvalue()
    return {"codigo_saida": rc, "saida": saida[-4000:]}


def main(argv: list[str] | None = None) -> int:
    import sys
    argv = argv if argv is not None else sys.argv[1:]
    if not argv:
        print(__doc__)
        return 2
    cmd = argv[0]
    if cmd == "issue":
        nome, escopos = "padrao", ["read"]
        if "--name" in argv:
            nome = argv[argv.index("--name") + 1]
        if "--scopes" in argv:
            escopos = [e.strip() for e in argv[argv.index("--scopes") + 1].split(",") if e.strip()]
        r = issue(nome, escopos)
        print("chave emitida (guarde agora, nao aparece de novo):")
        print(r["chave"])
        print("escopos:", r["escopos"])
        return 0
    if cmd == "revoke":
        if len(argv) < 2:
            print("uso: python -m api.gateway revoke <chave>")
            return 2
        ok = revogar(argv[1])
        print("revogada" if ok else "chave nao encontrada")
        return 0 if ok else 1
    if cmd == "list":
        dados = _carregar().get("tokens", {})
        for h, reg in dados.items():
            print(f"{h[:16]}... | {reg['nome']:20} | {','.join(reg['escopos']):28} | "
                  f"{reg['criado_em']} | {'REVOGADA' if reg.get('revogado') else 'ativa'}")
        if not dados:
            print("nenhuma chave nomeada emitida")
        return 0
    print(f"comando desconhecido: {cmd}")
    return 2

if __name__ == "__main__":
    raise SystemExit(main())

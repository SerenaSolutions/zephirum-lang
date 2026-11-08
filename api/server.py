# -*- coding: utf-8 -*-
"""ZYQL DECISION API — superfície REST do núcleo trivalente (v2.5.0).

Aqui a matemática fica exposta, não decorada. Cada endpoint devolve a conta
junto com a resposta: banda de Hoeffding, shots usados, erro máximo declarado,
hipóteses assumidas e o recibo selado. Se o pedido não tem resolução
estatística para a afirmação, a resposta é REFUSED com motivo — nunca um
número inventado.

Rotas:
  GET  /health              estado e limites declarados
  GET  /limits              o que o sistema NÃO faz (limites honestos)
  POST /bound               álgebra de Hoeffding: banda, shots necessários, família
  POST /decide              veredito trivalente 1 / 0 / REFUSED + recibo SHA3-256
  POST /verify              verificação offline do recibo (detecta adulteração)
  POST /oracle/reveal       Bernstein–Vazirani: máscara oculta em 1 consulta
  POST /oracle/promise      auditoria da promessa com testemunha

Física declarada: simulação exata de vetor de estado (sem ruído de hardware).
Execução em QPU real exige job ID verificável e por isso NÃO é feita por esta
API — o pedido com `hardware=true` é recusado explicitamente, não simulado em
silêncio.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import threading
import sys
from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/src")

from zyql_oracle_id import audit_promise, identify_2bit, reveal_linear
from zyql_quantum_gate import ZYQLQuantumGate, adaptive_margin, adaptive_margin_family

APP_VERSION = "2.5.6"
MAX_N = 8                    # fase-oráculo simulada: 2^n amplitudes
MAX_SHOTS = 100_000

app = FastAPI(
    title="ZYQL Decision API",
    version=APP_VERSION,
    description="Decisão trivalente com banda derivada e recibo verificável offline.",
    servers=[
        {"url": "http://localhost:8000", "description": "desenvolvimento local"},
        {"url": "https://zyql-api.replit.app", "description": "produção (trocar pela URL real do serviço)"},
    ],
)

ORACLES = {
    "const1": (lambda x: 1, "constant"),
    "const0": (lambda x: 0, "constant"),
    "parity": (lambda x: x & 1, "balanced"),
}


# ------------------------------------------------------------------ modelos
class BoundRequest(BaseModel):
    epsilon: float = Field(0.05, gt=0.0, lt=0.5, description="erro máximo de família")
    shots: int | None = Field(None, gt=0, le=MAX_SHOTS)
    margin: float | None = Field(None, gt=0.0, lt=0.5)
    family: int = Field(1, ge=1, le=1000)


class DecideRequest(BaseModel):
    oracle: Literal["const1", "const0", "parity"] = "const1"
    n: int = Field(3, ge=1, le=MAX_N)
    shots: int = Field(2048, gt=0, le=MAX_SHOTS)
    epsilon: float = Field(0.05, gt=0.0, lt=0.5)
    family: int = Field(1, ge=1, le=1000)
    seed: int = 1701
    hardware: bool = False
    sign: bool = False          # assinatura pós-quântica ML-DSA-44 (mais lenta)


class VerifyRequest(BaseModel):
    receipt: dict


class RevealRequest(BaseModel):
    mask: int = Field(..., ge=0)
    n: int = Field(3, ge=1, le=MAX_N)


class PromiseRequest(BaseModel):
    truth_table: list[int] = Field(..., min_length=2, max_length=256)


# ------------------------------------------------------------------ util
def _corpo_sem_assinatura(rec: dict) -> dict:
    """O selo cobre o conteudo; a assinatura e o identificador da chave ficam de fora."""
    fora = {"selo_sha3_256", "assinatura", "algoritmo", "chave_id", "chave_publica", "assinatura_pq"}
    return {k: v for k, v in rec.items() if k not in fora}


_CAMINHO_CHAVE = os.environ.get("ZYQL_SIGN_KEY", ".zyql_sig_key.json")


def _chave_de_assinatura() -> tuple:
    """Par ML-DSA persistido (0600). Gera na primeira vez; nao vaza a privada em log."""
    import base64
    import json as _json
    import zqea_sig
    try:
        with open(_CAMINHO_CHAVE) as fh:
            d = _json.load(fh)
        return base64.b64decode(d["publica"]), base64.b64decode(d["privada"])
    except Exception:
        pk, sk = zqea_sig.keypair()
        try:
            desc = os.open(_CAMINHO_CHAVE, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
            with os.fdopen(desc, "w") as fh:
                _json.dump({"publica": base64.b64encode(pk).decode(),
                            "privada": base64.b64encode(sk).decode()}, fh)
        except Exception:
            pass
        return pk, sk


def _seal(receipt: dict) -> str:
    corpo = {k: v for k, v in receipt.items() if k != "selo_sha3_256"}
    return hashlib.sha3_256(
        json.dumps(corpo, sort_keys=True, ensure_ascii=True, default=str).encode()
    ).hexdigest()


ARQ_CORRENTE = os.environ.get("ZYQL_CHAIN_FILE", ".chain.json")


def _ler_corrente() -> dict:
    try:
        with open(ARQ_CORRENTE) as fh:
            return json.load(fh)
    except Exception:
        return {"elo": 0, "ultimo": "genesis"}


_CADEIA_LOCK = threading.Lock()


def _correntear(recibo: dict) -> str:
    """Encadeia o recibo ao anterior antes de selar: prova ordem e ausencia de remocao."""
    with _CADEIA_LOCK:  # P2-1: leitura-escrita atomica; sem elo duplicado
        est = _ler_corrente()
        recibo["prev"] = est.get("ultimo", "genesis")
        recibo["elo"] = int(est.get("elo", 0)) + 1
        selo = _seal(recibo)
        recibo["selo_sha3_256"] = selo
        tmp = ARQ_CORRENTE + ".tmp"
        with open(tmp, "w") as fh:
            json.dump({"elo": recibo["elo"], "ultimo": selo}, fh)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, ARQ_CORRENTE)  # troca atomica
    return selo


def _shots_necessarios(epsilon: float, margin: float, family: int = 1) -> int:
    """Hoeffding inverso: quantos shots para garantir banda <= margin.

    m = sqrt(ln(2/eps')/(2S))  ⇒  S = ln(2/eps') / (2 m²),  eps' = eps/k
    """
    eps_linha = epsilon / max(family, 1)
    if not (0.0 < eps_linha < 1.0):
        raise HTTPException(422, "epsilon/family fora de (0,1)")
    return int(math.ceil(math.log(2.0 / eps_linha) / (2.0 * margin * margin)))


# ------------------------------------------------------------------ rotas
@app.get("/health")
def health():
    return {
        "status": "ok",
        "app": "ZYQL Decision API",
        "version": APP_VERSION,
        "verdicts": ["1", "0", "REFUSED"],
        "physics": "simulação exata de vetor de estado (sem ruído de QPU)",
        "max_n": MAX_N,
        "max_shots": MAX_SHOTS,
    }


@app.get("/limits")
def limits():
    return {
        "declarado": [
            "n <= 8 na fase-oráculo simulada (2^n amplitudes em memória)",
            "sem correção de erro quântico; nenhuma vantagem alegada sobre clássico",
            "banda de Hoeffding cobre erro AMOSTRAL, não viés sistemático de readout",
            "hardware real exige job ID verificável e não é executado por esta API",
            "recusa (REFUSED) é resposta de primeira classe, não exceção",
        ],
        "nao_alegado": [
            "vantagem computacional quântica",
            "detecção de oráculos adversariais fora da classe promise",
            "ausência de memória no ambiente (ver gate BLP do núcleo)",
        ],
    }


@app.post("/bound")
def bound(req: BoundRequest):
    """Álgebra da banda. Devolve a conta, não só o número."""
    if req.shots is None and req.margin is None:
        raise HTTPException(422, "informe shots ou margin")
    saida = {"epsilon": req.epsilon, "family": req.family,
             "epsilon_por_teste": req.epsilon / max(req.family, 1)}
    if req.shots is not None:
        m = adaptive_margin_family(req.epsilon, req.shots, req.family)
        saida["shots"] = req.shots
        saida["margin"] = m
        saida["resolvivel"] = m > 0
        if m <= 0:
            saida["motivo"] = "FAMILY_EXCEEDS_SHOTS"
    if req.margin is not None:
        saida["shots_necessarios"] = _shots_necessarios(req.epsilon, req.margin, req.family)
    saida["formula"] = "m = sqrt(ln(2/(eps/k)) / (2S))"
    return saida


def _run(oracle_key: str, n: int, shots: int, epsilon: float, family: int, seed: int):
    f, classe = ORACLES[oracle_key]
    gate = ZYQLQuantumGate(n, f)
    return gate.run_quantum(shots=shots, seed=seed, epsilon=epsilon, family=family), classe


@app.post("/decide")
def decide(req: DecideRequest):
    """Veredito trivalente com recibo selado."""
    if req.hardware:
        raise HTTPException(
            409,
            "hardware=true recusado: esta API não executa em QPU. O caminho honesto "
            "é o script de hardware do repositório, que devolve job ID verificável.",
        )
    res, classe = _run(req.oracle, req.n, req.shots, req.epsilon, req.family, req.seed)
    veredito = res["decision"]
    recibo = {
        "versao_api": APP_VERSION,
        "oraculo": req.oracle,
        "classe_esperada": classe,
        "n": req.n,
        "shots": req.shots,
        "epsilon": req.epsilon,
        "family": req.family,
        "seed": req.seed,
        "banda": res.get("error_bound_value") or res.get("margin")
        or adaptive_margin_family(req.epsilon, req.shots, req.family),
        "p0": res.get("p0"),
        "veredito": veredito,
        "motivo": res.get("refusal_reason") or res.get("mode"),
        "fisica": "statevector_exato",
        "hipoteses": ["amostras independentes", "erro amostral <= epsilon"],
    }
    recibo["selo_sha3_256"] = _correntear(recibo)
    if req.sign:
        # P2-2 (v2.5.8): assinatura ML-DSA real, com a implementacao que existe (zqea_sig).
        try:
            import base64
            import zqea_sig
            pk_b, sk_b = _chave_de_assinatura()
            # a chave publica entra no corpo ANTES de assinar, senao a assinatura
            # cobriria um corpo diferente do que o verificador reconstroi (P2-2)
            recibo["chave_publica"] = base64.b64encode(pk_b).decode()
            recibo = zqea_sig.assinar(recibo, sk_b, pk_b)
            recibo["selo_sha3_256"] = _seal(_corpo_sem_assinatura(recibo))
        except Exception as e:                     # indisponibilidade declarada, nunca escondida
            recibo["assinatura_pq"] = {"erro": f"indisponivel: {type(e).__name__}"}
    return {"verdict": veredito, "p0": res.get("p0"), "margin": recibo["banda"],
            "shots": req.shots, "epsilon": req.epsilon, "family": req.family,
            "mode": res.get("mode"), "reason": recibo["motivo"], "receipt": recibo}


@app.post("/verify")
def verify(req: VerifyRequest):
    """Verificação offline: recomputa o selo e denuncia adulteração."""
    rec = dict(req.receipt)
    rec_integral = dict(req.receipt)   # a assinatura cobre o recibo COM o selo: verificar sobre o original
    selo = rec.pop("selo_sha3_256", None)
    if not selo:
        return {"ok": False, "reason": "SEAL_MISSING"}
    corpo = _corpo_sem_assinatura(rec)  # mesma regra usada ao selar (P2-2)
    esperado = hashlib.sha3_256(
        json.dumps(corpo, sort_keys=True, ensure_ascii=True, default=str).encode()
    ).hexdigest()
    ok = esperado == selo
    # P2-2 (v2.5.8): integridade do hash NAO e autoria. A assinatura e verificada de fato.
    autoria = None
    if rec.get("assinatura"):
        try:
            import base64
            import zqea_sig
            pk = base64.b64decode(rec_integral.get("chave_publica", ""))
            autoria = bool(zqea_sig.verificar(rec_integral, pk)) if pk else False
        except Exception:
            autoria = False
    return {"ok": ok, "reason": None if ok else "SEAL_MISMATCH",
            "seal_recomputado": esperado[:16] + "...",
            "integridade": "hash_ok" if ok else "hash_divergente",
            "autoria_verificada": autoria,
            "assinatura_presente": bool(rec.get("assinatura")),
            "chave_id": rec.get("chave_id"),
            "assinatura_pq": "assinatura_pq" in rec}


@app.post("/oracle/reveal")
def oracle_reveal(req: RevealRequest):
    """Bernstein–Vazirani: a função escondida, em uma consulta."""
    if req.mask >= (1 << req.n):
        raise HTTPException(422, f"mascara {req.mask} nao cabe em {req.n} bits")
    return reveal_linear(req.mask, req.n)


@app.post("/oracle/promise")
def oracle_promise(req: PromiseRequest):
    """A promessa vale? Se não, devolve a testemunha da violação."""
    total = len(req.truth_table)
    n = total.bit_length() - 1
    if 1 << n != total:
        raise HTTPException(422, "truth_table precisa ter 2^n entradas")
    tabela = {x: req.truth_table[x] for x in range(total)}
    return {"audit": audit_promise(tabela), "identify": identify_2bit(tabela) if n == 2 else None}

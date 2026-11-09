# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Serena Quantum Solutions
"""v2.6.0 — ALGEBRA DE DECISOES TRIVALENTES.

Fecha o intervalo entre decidir uma vez e decidir em sequencia: operadores
compõem decisoes e propagam, junto com o veredito, o ORCAMENTO DE ERRO do
programa inteiro. `k` deixa de ser numero digitado e passa a ser contado
da propria expressao.

Semantica (identica a do nucleo, nao estendida):
    1        evidencia sustenta a afirmacao
    0        evidencia sustenta a negacao
    REFUSED  evidencia insuficiente; nunca convertido em 1 nem em 0

Recusa contamina para cima: um componente recusado torna a composicao
recusada, salvo quando outro componente ja decide (0 em conjuncao).
"""
import json
from zqea_sig import sha3_256
from zyql_quantum_gate import adaptive_margin_family

UM = 1
ZERO = 0
RECUSA = "REFUSED"

MOTIVO_FAMILIA = "FAMILY_EXCEEDS_SHOTS"


class Decisao:
    """No da algebra: folha (decisao medida) ou composicao."""

    __slots__ = ("veredito", "epsilon", "shots", "refusal_reason", "filhos", "recibo_selo", "op")

    def __init__(self, veredito, epsilon, shots, refusal_reason=None, filhos=(), recibo_selo=None, op=None):
        if veredito not in (UM, ZERO, RECUSA):
            raise ValueError("veredito precisa ser 1, 0 ou 'REFUSED'; recebido %r" % (veredito,))
        if not isinstance(epsilon, (int, float)) or not (0.0 < epsilon < 1.0):
            raise ValueError("epsilon precisa estar em (0,1); recebido %r" % (epsilon,))
        if not isinstance(shots, int) or shots < 1:
            raise ValueError("shots precisa ser inteiro >= 1; recebido %r" % (shots,))
        if veredito == RECUSA and not (refusal_reason or "").strip():
            raise ValueError("veredito REFUSED exige refusal_reason nao vazio")
        self.veredito = veredito
        self.epsilon = float(epsilon)
        self.shots = shots
        self.refusal_reason = refusal_reason
        self.filhos = tuple(filhos)
        self.recibo_selo = recibo_selo
        self.op = op

    def __repr__(self):
        return "Decisao(%r, eps=%g, shots=%d, k=%d)" % (
            self.veredito, self.epsilon, self.shots, n_testes(self))


def _recusa(motivo, base):
    return Decisao(RECUSA, base.epsilon, base.shots, refusal_reason=motivo, filhos=base.filhos)


def _folhas(no):
    if not no.filhos:
        return [no]
    saida = []
    for f in no.filhos:
        saida.extend(_folhas(f))
    return saida


def n_testes(no):
    """Numero de decisoes independentes que a expressao consome."""
    return len(_folhas(no))


def epsilon_familia(no):
    """Erro familiar exato sob independencia: 1 - prod(1 - eps_i).

    Reduz-se a 1 - (1 - eps)^k quando as folhas tem o mesmo epsilon.
    """
    return _erro_familiar(_folhas(no))


def _cabe_no_orcamento(folhas):
    """k vereditos exigem margem rigorosa > 0 em cada folha."""
    k = len(folhas)
    for f in folhas:
        if adaptive_margin_family(f.epsilon, f.shots, family=k, modo="rigorous") <= 0:
            return False
    return True


def _erro_familiar(folhas):
    """1 - prod(1 - eps_i), limitado abaixo de 1 para caber em (0,1)."""
    prod = 1.0
    for f in folhas:
        prod *= (1.0 - f.epsilon)
    return min(1.0 - 1e-9, 1.0 - prod)


def _compor(veredito, motivo, a, b, op):
    """O no composto declara o erro do CONJUNTO, nunca o de uma folha."""
    filhos = (a, b)
    folhas = _folhas(Decisao(UM, a.epsilon, a.shots, filhos=filhos))
    eps_fam = _erro_familiar(folhas)
    if veredito != RECUSA and not _cabe_no_orcamento(folhas):
        return Decisao(RECUSA, eps_fam, a.shots, refusal_reason=MOTIVO_FAMILIA,
                       filhos=filhos, op=op)
    return Decisao(veredito, eps_fam, a.shots, refusal_reason=motivo, filhos=filhos, op=op)


def conjuncao(a, b):
    """1 somente se ambas 1. Qualquer 0 decide 0. Recusa propaga o motivo."""
    if a.veredito == RECUSA and b.veredito == RECUSA:
        return _compor(RECUSA, "%s + %s" % (a.refusal_reason, b.refusal_reason), a, b, "conj")
    if a.veredito == ZERO or b.veredito == ZERO:
        return _compor(ZERO, None, a, b, "conj")
    if a.veredito == RECUSA:
        return _compor(RECUSA, a.refusal_reason, a, b, "conj")
    if b.veredito == RECUSA:
        return _compor(RECUSA, b.refusal_reason, a, b, "conj")
    return _compor(UM, None, a, b, "conj")


def disjuncao(a, b):
    """1 se qualquer 1. So e 0 se ambas 0. Recusa propaga o motivo."""
    if a.veredito == RECUSA and b.veredito == RECUSA:
        return _compor(RECUSA, "%s + %s" % (a.refusal_reason, b.refusal_reason), a, b, "disj")
    if a.veredito == UM or b.veredito == UM:
        return _compor(UM, None, a, b, "disj")
    if a.veredito == RECUSA:
        return _compor(RECUSA, a.refusal_reason, a, b, "disj")
    if b.veredito == RECUSA:
        return _compor(RECUSA, b.refusal_reason, a, b, "disj")
    return _compor(ZERO, None, a, b, "disj")


def negacao(a):
    if a.veredito == RECUSA:
        return Decisao(RECUSA, a.epsilon, a.shots, refusal_reason=a.refusal_reason, filhos=a.filhos, op="neg")
    return Decisao(UM if a.veredito == ZERO else ZERO, a.epsilon, a.shots, filhos=a.filhos, op="neg")


def sequencia(*decisoes):
    """Conjuncao n-aria: o programa so segue se todas sustentarem."""
    if not decisoes:
        raise ValueError("sequencia exige ao menos uma decisao")
    atual = decisoes[0]
    for prox in decisoes[1:]:
        atual = conjuncao(atual, prox)
    return atual


def forma_canonica(no):
    if not no.filhos:
        return {"tipo": "folha", "veredito": no.veredito,
                "epsilon": round(no.epsilon, 12), "shots": no.shots,
                "motivo": no.refusal_reason}
    return {"tipo": no.op or "comp", "veredito": no.veredito,
            "motivo": no.refusal_reason,
            "filhos": [forma_canonica(f) for f in no.filhos]}


def recibo_da_expressao(no):
    """Recibo verificavel: mesma expressao => mesmo selo SHA3-256."""
    forma = forma_canonica(no)
    canon = json.dumps(forma, sort_keys=True, separators=(",", ":"))
    return {
        "n_testes": n_testes(no),
        "epsilon_familia": round(epsilon_familia(no), 12),
        "veredito": no.veredito,
        "refusal_reason": no.refusal_reason,
        "forma": forma,
        "selo_sha3_256": sha3_256(canon),
    }


def verificar_recibo(no, recibo):
    return recibo_da_expressao(no)["selo_sha3_256"] == recibo.get("selo_sha3_256")

# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Serena Quantum Solutions
"""Canon Z-QEA e verificacao unificada de selo SHA3-256.

Existe por um defeito real: o interpretador sela com a regra da casa
(``json.dumps(sort_keys=True, ensure_ascii=True, default=str)``) e grava o selo
em ``selo_sha3_256``, enquanto verificadores antigos procuravam ``sha3_256`` e
usavam separadores compactos. O resultado era o pior possivel: um recibo
integro, verificado por quem o recebeu, respondia "adulterado".

Regra: existe UMA regra normativa (a da casa). As duas variantes historicas
continuam aceitas para nao invalidar recibos ja publicados. Aceitar variantes
nao enfraquece a deteccao: qualquer alteracao de conteudo muda o hash em todas
elas, e o campo do selo nunca entra no calculo.

Uso:
    from zqea_canon import verificar_arquivo
    res = verificar_arquivo("recibo.json")
    res["integro"], res["regra"], res["declarado"], res["calculado"]
"""
import hashlib
import json

# Nomes de campo ja usados em recibos publicados, do mais recente ao mais antigo.
CAMPOS_SELO = ("selo_sha3_256", "sha3_256", "seal", "selo")

# Estilos de canonizacao, na ordem em que devem ser tentados.
REGRAS = ("casa", "compacto", "compacto_ascii")


def canon(payload, regra="casa"):
    """Serializa um recibo sem o campo do selo segundo uma regra declarada."""
    if regra == "casa":
        return json.dumps(payload, sort_keys=True, ensure_ascii=True, default=str)
    if regra == "compacto":
        return json.dumps(payload, sort_keys=True, ensure_ascii=False,
                          separators=(",", ":"), default=str)
    if regra == "compacto_ascii":
        return json.dumps(payload, sort_keys=True, ensure_ascii=True,
                          separators=(",", ":"), default=str)
    raise ValueError(f"regra desconhecida: {regra}")


def selo_declarado(rec):
    """Devolve (campo, valor) do selo, ou (None, None) se nao houver selo."""
    for campo in CAMPOS_SELO:
        valor = rec.get(campo)
        if isinstance(valor, str) and len(valor) == 64:
            return campo, valor
    return None, None


def verificar(rec):
    """Verifica a integridade de um recibo ja carregado.

    Retorna dict com: integro, regra, campo, declarado, calculado, motivo.
    """
    campo, declarado = selo_declarado(rec)
    if not declarado:
        return {"integro": False, "regra": None, "campo": None, "declarado": None,
                "calculado": None, "motivo": "SEM_SELO"}
    corpo = {k: v for k, v in rec.items() if k != campo}
    calculado = None
    for regra in REGRAS:
        calculado = hashlib.sha3_256(canon(corpo, regra).encode()).hexdigest()
        if calculado == declarado:
            return {"integro": True, "regra": regra, "campo": campo,
                    "declarado": declarado, "calculado": calculado, "motivo": "OK"}
    return {"integro": False, "regra": None, "campo": campo, "declarado": declarado,
            "calculado": calculado, "motivo": "SELO_DIVERGENTE"}


def verificar_arquivo(caminho):
    with open(caminho, encoding="utf-8") as f:
        return verificar(json.load(f))

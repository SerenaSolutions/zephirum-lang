# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Serena Quantum Solutions
"""ZEPHIRUM — ponto de entrada publico.

Antes desta versao o pacote instalava dezenas de modulos com prefixo `zyql_` e
nenhum modulo de topo chamado `zephirum`, entao `import zephirum` falhava. Este
modulo fecha essa lacuna e oferece a API minima para comecar.

Exemplo:
    >>> from zephirum import decidir
    >>> decidir({"000": 964, "111": 60}, shots=1024, threshold=0.9)
    {'verdict': 'INCONCLUSIVE', ...}
"""
from __future__ import annotations

import hashlib
import json
import math

__version__ = "2.5.8"
__all__ = ["decidir", "verificar_recibo", "modulos", "__version__"]


def _canon(v):
    return json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _sha3(v):
    return hashlib.sha3_256(_canon(v).encode("utf-8")).hexdigest()


def decidir(counts, shots=None, threshold=0.5, delta=0.05, target_key="000"):
    """Regra proporcao-v1 com limite de Hoeffding.

    Devolve veredito 1, 0, INCONCLUSIVE ou REFUSED, com a margem declarada e o
    compromisso do insumo. Nunca adivinha: quando as barras se cruzam, recusa
    afirmar; quando o contrato e invalido, recusa executar.
    """
    if not isinstance(counts, dict):
        return {"verdict": "REFUSED", "reason": "CONTAGENS_INVALIDAS", "rule": "proporcao-v1"}
    try:
        limpo = {str(k): int(v) for k, v in counts.items()}
    except (TypeError, ValueError):
        return {"verdict": "REFUSED", "reason": "CONTAGEM_NAO_INTEIRA", "rule": "proporcao-v1"}
    if any(v < 0 for v in limpo.values()):
        return {"verdict": "REFUSED", "reason": "CONTAGEM_NEGATIVA", "rule": "proporcao-v1"}
    total = sum(limpo.values())
    shots = total if shots is None else int(shots)
    if shots <= 0:
        return {"verdict": "REFUSED", "reason": "SHOTS_INVALIDO", "rule": "proporcao-v1"}
    if total != shots:
        return {"verdict": "REFUSED", "reason": "SOMA_DIFERE_DOS_SHOTS",
                "soma": total, "shots": shots, "rule": "proporcao-v1"}
    if not (0.0 < float(threshold) < 1.0) or not (0.0 < float(delta) < 1.0):
        return {"verdict": "REFUSED", "reason": "POLITICA_FORA_DE_FAIXA", "rule": "proporcao-v1"}
    p = limpo.get(target_key, 0) / shots
    eps = math.sqrt(math.log(2 / float(delta)) / (2 * shots))
    if p - eps > float(threshold):
        v = "1"
    elif p + eps < float(threshold):
        v = "0"
    else:
        v = "INCONCLUSIVE"
    recibo = {"verdict": v, "p_hat": round(p, 6), "epsilon": round(eps, 6),
              "threshold": float(threshold), "delta": float(delta), "shots": shots,
              "target_key": target_key, "rule": "proporcao-v1",
              "input_commitment": _sha3({"counts": limpo, "shots": shots})}
    recibo["receipt_hash"] = _sha3(recibo)
    return recibo


def verificar_recibo(recibo):
    """Confere se o recibo foi alterado depois de emitido."""
    if not isinstance(recibo, dict) or "receipt_hash" not in recibo:
        return False
    corpo = {k: v for k, v in recibo.items() if k != "receipt_hash"}
    return _sha3(corpo) == recibo["receipt_hash"]


def modulos():
    """Lista os modulos publicos disponiveis no pacote instalado."""
    import pkgutil
    return sorted(m.name for m in pkgutil.iter_modules() if m.name.startswith("zyql_"))

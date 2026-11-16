"""Cliente do STARGATE: emite evento de decisão sem nunca derrubar quem chamou.

Regra de ouro: observabilidade não pode ser o motivo de a rodada falhar. Se o
STARGATE estiver inacessível, o evento vai para a fila local e a execução segue.
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

FILA_PADRAO = Path("receipts") / "stargate_fila"
VEREDITOS = {"1", "0", "REFUSED"}
SELOS = {"integro", "rompido"}


def montar_evento(
    veredito: str,
    *,
    eliminadas: int = 0,
    executadas: int = 0,
    selo: str = "integro",
    motivo_recusa: str | None = None,
    segundos: float = 0.0,
) -> dict[str, Any]:
    if veredito not in VEREDITOS:
        raise ValueError(f"veredito fora de {sorted(VEREDITOS)}: {veredito!r}")
    if selo not in SELOS:
        raise ValueError(f"selo fora de {sorted(SELOS)}: {selo!r}")
    evento: dict[str, Any] = {
        "veredito": veredito,
        "eliminadas": max(0, int(eliminadas)),
        "executadas": max(0, int(executadas)),
        "selo": selo,
        "segundos": max(0.0, float(segundos)),
    }
    if motivo_recusa:
        evento["motivo_recusa"] = motivo_recusa
    return evento


def enviar(evento: dict[str, Any], url: str, timeout: float = 5.0) -> tuple[bool, str]:
    """Devolve (entregue, detalhe). Nunca levanta exceção de rede."""
    dados = json.dumps(evento).encode()
    req = urllib.request.Request(
        url.rstrip("/") + "/evento", data=dados,
        headers={"content-type": "application/json"}, method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            corpo = json.loads(resp.read() or b"{}")
            if resp.status in (200, 202) and corpo.get("aceito") is not False:
                return True, "entregue"
            return False, f"recusado: {corpo.get('erro', resp.status)}"
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        return False, f"inacessivel: {type(e).__name__}"
    except json.JSONDecodeError:
        return True, "entregue (resposta sem JSON)"


def enfileirar(evento: dict[str, Any], pasta: Path, motivo: str) -> Path:
    pasta.mkdir(parents=True, exist_ok=True)
    carimbo = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f")
    alvo = pasta / f"{carimbo}.json"
    # dois eventos no mesmo microssegundo nao podem sobrescrever um ao outro
    sufixo = 1
    while alvo.exists():
        alvo = pasta / f"{carimbo}-{sufixo}.json"
        sufixo += 1
    alvo.write_text(json.dumps({"evento": evento, "motivo_falha": motivo}, indent=2))
    return alvo


def emitir(
    evento: dict[str, Any],
    url: str | None = None,
    pasta_fila: Path | None = None,
    timeout: float = 5.0,
) -> dict[str, Any]:
    """Tenta entregar; se não conseguir, enfileira. Devolve o que aconteceu."""
    url = url or os.environ.get("STARGATE_URL", "")
    pasta = Path(pasta_fila or os.environ.get("STARGATE_FILA") or FILA_PADRAO)
    if not url:
        caminho = enfileirar(evento, pasta, "STARGATE_URL nao configurada")
        return {"estado": "enfileirado", "motivo": "sem URL", "arquivo": str(caminho)}
    entregue, detalhe = enviar(evento, url, timeout)
    if entregue:
        return {"estado": "entregue", "detalhe": detalhe}
    caminho = enfileirar(evento, pasta, detalhe)
    return {"estado": "enfileirado", "motivo": detalhe, "arquivo": str(caminho)}


def escoar_fila(
    url: str | None = None,
    pasta_fila: Path | None = None,
    timeout: float = 5.0,
) -> dict[str, int]:
    """Reenvia o que ficou na fila. Remove só o que foi aceito."""
    url = url or os.environ.get("STARGATE_URL", "")
    pasta = Path(pasta_fila or os.environ.get("STARGATE_FILA") or FILA_PADRAO)
    enviados = restantes = 0
    if not url or not pasta.exists():
        return {"enviados": 0, "restantes": len(list(pasta.glob("*.json"))) if pasta.exists() else 0}
    for arq in sorted(pasta.glob("*.json")):
        try:
            conteudo = json.loads(arq.read_text())
            evento = conteudo.get("evento", conteudo)
        except json.JSONDecodeError:
            continue
        entregue, _ = enviar(evento, url, timeout)
        if entregue:
            arq.unlink()
            enviados += 1
        else:
            restantes += 1
    return {"enviados": enviados, "restantes": restantes}

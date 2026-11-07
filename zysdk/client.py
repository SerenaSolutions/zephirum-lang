#!/usr/bin/env python3
"""ZYSDK — o SDK do ZEPHIRUM. Zero dependencia de terceiros.

Por que isto existe: falar com hardware quantico nao exige SDK de fornecedor.
Exige HTTPS, JSON e OpenQASM 3 — tres coisas que a biblioteca padrao ja tem.
O SDK alheio trazia 40 MB, versao travada, licenca de terceiro e fornecedor
dentro do nosso codigo. Aqui a fronteira e' um contrato de rede, nao um pacote.

O que permanece inevitavel (declarado, nao escondido):
  o CONTRATO da API de quem tem a maquina. Autenticacao, formato do trabalho e
  nomes de campo sao do provedor. Isso e' servico, nao biblioteca. Trocar de
  provedor = trocar um adaptador de 30 linhas, nao reescrever o projeto.
"""
from __future__ import annotations
import json, ssl, time, urllib.request, urllib.error
from dataclasses import dataclass, field

VERSAO = "0.1.0"
QASM3 = "OpenQASM 3.0"  # formato de transito; o produto nao depende de SDK alheio


class ErroDeProvedor(RuntimeError):
    """Falha de rede ou de contrato. Nunca carrega credencial na mensagem."""


def _redigir(texto: str) -> str:
    import re
    return re.sub(r"(?i)(token|apikey|api_key|authorization|bearer)([=:\s\"']+)([A-Za-z0-9_\-\.]{6,})",
                  r"\1\2[REDIGIDO]", str(texto))


@dataclass
class Contagem:
    """Resultado cru do dispositivo, sem interpretacao."""
    tiros: int
    contagens: dict = field(default_factory=dict)

    def proporcao(self, alvo: str) -> float:
        total = sum(self.contagens.values()) or 1
        return self.contagens.get(alvo, 0) / total


class Provedor:
    """Interface. Todo fornecedor implementa isto; o resto do produto nao conhece marca."""
    nome = "abstrato"

    def enviar(self, qasm3: str, tiros: int) -> str: raise NotImplementedError
    def estado(self, job: str) -> str: raise NotImplementedError
    def resultado(self, job: str) -> Contagem: raise NotImplementedError


class ProvedorREST(Provedor):
    """Cliente generico. Sem SDK, sem dependencia, sem marca no codigo.

    contrato:  POST {base}/jobs   {"program": <qasm3>, "shots": n}  -> {"id": "..."}
               GET  {base}/jobs/{id}                               -> {"status": "...", "counts": {...}}
    """

    def __init__(self, base: str, token: str, nome: str = "generico", timeout: float = 30.0, tls_minimo=True):
        if not base.startswith("https://"):
            raise ErroDeProvedor("transporte inseguro: exigido https")
        self.base, self.nome, self.timeout = base.rstrip("/"), nome, timeout
        self._token = token
        self._ctx = ssl.create_default_context() if tls_minimo else None

    def _req(self, caminho: str, dados=None):
        url = self.base + caminho
        corpo = json.dumps(dados).encode() if dados is not None else None
        req = urllib.request.Request(url, data=corpo, method="POST" if corpo else "GET")
        req.add_header("Authorization", f"Bearer {self._token}")
        req.add_header("Content-Type", "application/json")
        req.add_header("User-Agent", f"ZEPHIRUM-ZYSDK/{VERSAO}")
        try:
            with urllib.request.urlopen(req, timeout=self.timeout, context=self._ctx) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            raise ErroDeProvedor(f"HTTP {e.code} em {caminho}: {_redigir(e.read()[:200])}") from None
        except Exception as e:
            raise ErroDeProvedor(f"falha de rede em {caminho}: {_redigir(e)}") from None

    def enviar(self, qasm3: str, tiros: int) -> str:
        d = self._req("/jobs", {"program": qasm3, "shots": int(tiros)})
        if "id" not in d:
            raise ErroDeProvedor("contrato violado: resposta sem id")
        return d["id"]

    def estado(self, job: str) -> str:
        return self._req(f"/jobs/{job}").get("status", "DESCONHECIDO")

    def resultado(self, job: str) -> Contagem:
        d = self._req(f"/jobs/{job}")
        if "counts" not in d:
            raise ErroDeProvedor(f"contrato violado em resultado: {_redigir(list(d))}")
        return Contagem(tiros=sum(d["counts"].values()), contagens=dict(d["counts"]))

    def esperar(self, job: str, limite_s: float = 600, intervalo_s: float = 5) -> Contagem:
        t0 = time.monotonic()
        while time.monotonic() - t0 < limite_s:
            e = self.estado(job)
            if e in ("DONE", "CONCLUIDO", "COMPLETED"):
                return self.resultado(job)
            if e in ("ERROR", "CANCELLED", "FALHA"):
                raise ErroDeProvedor(f"execucao terminou em {e}")
            time.sleep(intervalo_s)
        raise ErroDeProvedor("limite de espera excedido (job segue na fila)")


class ProvedorLocal(Provedor):
    """Simulador proprio: mesma interface, zero rede. Padrao do projeto."""
    nome = "local-exato"

    def __init__(self, simulador):
        self.sim = simulador
        self._ultimo = {}

    def enviar(self, qasm3: str, tiros: int) -> str:
        jid = f"local-{len(self._ultimo)+1}"
        self._ultimo[jid] = self.sim(qasm3, tiros)
        return jid

    def estado(self, job: str) -> str:
        return "DONE" if job in self._ultimo else "DESCONHECIDO"

    def resultado(self, job: str) -> Contagem:
        c = self._ultimo[job]
        return Contagem(tiros=sum(c.values()), contagens=dict(c))


def registro():
    """Mapa de adaptadores. Acrescentar fornecedor = acrescentar funcao de fabrica aqui."""
    return {"rest": ProvedorREST, "local": ProvedorLocal}

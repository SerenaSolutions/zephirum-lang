# SPDX-License-Identifier: Apache-2.0
"""Adaptador IBM Quantum — plano free.

Regras da casa:
- Fail-closed: sem token, sem backend ou sem qiskit-ibm-runtime, devolve REFUSED com codigo.
- Nao gasta cota a toa: circuito so-Clifford e recusado para QPU (simulador classico resolve).
- Toda submissao emite recibo com job_id, backend e hash do programa.
"""
import datetime
import os
import re

from ..cert import emitir
from ..qasm3 import decidir as decidir_qasm

CODIGO_SEM_TOKEN = "IBM-401"
CODIGO_SEM_LIB = "IBM-503"
CODIGO_SEM_BACKEND = "IBM-404"
CODIGO_COTA = "IBM-429"
CODIGO_CLIFFORD = "IBM-422"


def _agora():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _recusar(codigo, motivo, extra=None):
    saida = {"veredito": "REFUSED", "codigo": codigo, "motivo": motivo, "emitido_utc": _agora()}
    if extra:
        saida.update(extra)
    return saida


def _token():
    """Aceita os nomes que o cofre da plataforma usa, em ordem de preferencia."""
    for nome in ("IBM_QUANTUM_TOKEN", "IBM_API_TOKEN", "IBM_API_TOKEN_2"):
        valor = (os.environ.get(nome) or "").strip()
        if valor:
            return valor
    return ""


def disponivel():
    """Diz se ha como falar com a IBM, sem tocar na rede."""
    token = _token()
    if not token:
        return False, CODIGO_SEM_TOKEN, "IBM_QUANTUM_TOKEN ausente no ambiente"
    try:
        import qiskit_ibm_runtime  # noqa: F401
    except Exception:
        return False, CODIGO_SEM_LIB, "qiskit-ibm-runtime nao instalado na imagem"
    return True, "", ""


def portao_de_cota(qasm):
    """Barra o que nao precisa de QPU. Devolve (permitido, analise)."""
    analise = decidir_qasm(qasm)
    if analise.get("veredito") == 1:
        return False, {
            "codigo": CODIGO_CLIFFORD,
            "motivo": "circuito apenas Clifford: simulavel classicamente, nao gaste cota de QPU",
            "analise": analise.get("analise"),
        }
    if analise.get("veredito") == "REFUSED":
        return False, {
            "codigo": "IBM-400",
            "motivo": "programa fora do subconjunto: " + str(analise.get("ref") or analise.get("motivo")),
            "analise": analise.get("analise"),
        }
    return True, {"analise": analise.get("analise"), "motivo_analise": analise.get("motivo")}


CODIGO_SUBMISSAO_DESABILITADA = "IBM-403"
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
    ok, codigo, motivo = disponivel()
    if not ok:
        return _recusar(codigo, motivo)

    permitido, info = portao_de_cota(qasm)
    if not permitido:
        return _recusar(info["codigo"], info["motivo"], {"analise": info.get("analise")})

    try:
        from qiskit import QuantumCircuit
        from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
        from qiskit.qasm3 import loads as carregar_qasm3
    except Exception as e:  # biblioteca quebrada na imagem
        return _recusar(CODIGO_SEM_LIB, f"falha ao importar qiskit: {str(e)[:120]}")

    token = _token()
    try:
        kwargs = {"channel": canal or os.environ.get("IBM_QUANTUM_CHANNEL", "ibm_quantum")}
        instancia = (os.environ.get("IBM_QUANTUM_INSTANCE") or "").strip()
        if instancia:
            kwargs["instance"] = instancia
        servico = QiskitRuntimeService(token=token, **kwargs)
        alvo = servico.backend(backend)
    except Exception as e:
        return _recusar(CODIGO_SEM_BACKEND, f"backend '{backend}' indisponivel: {str(e)[:140]}")

    try:
        circuito = carregar_qasm3(qasm)
        if not isinstance(circuito, QuantumCircuit):
            return _recusar("IBM-400", "QASM3 nao produziu circuito")
        circuito.measure_all()
        amostrador = Sampler(alvo)
        trabalho = amostrador.run([circuito], shots=shots)
        job_id = trabalho.job_id()
        resultado = trabalho.result()
        contagens = resultado[0].data.meas.get_counts()
    except Exception as e:
        return _recusar("IBM-500", f"falha na execucao: {str(e)[:160]}")

    cert = emitir({
        "hash_alg": "SHA-256",
        "emitido_utc": _agora(),
        "motor": "zephirum-ibm/1.0.0",
        "backend": backend,
        "job_id": job_id,
        "shots": shots,
        "canal": canal or os.environ.get("IBM_QUANTUM_CHANNEL", "ibm_quantum"),
    })
    return {"veredito": 1, "job_id": job_id, "backend": backend, "shots": shots,
            "contagens": contagens, "cert": cert}


def ensaio(qasm, backend="simulador"):
    """Caminho sem QPU: valida o programa e devolve o que seria enviado."""
    permitido, info = portao_de_cota(qasm)
    return {
        "veredito": "ENSAIO" if permitido else "REFUSED",
        "backend_alvo": backend,
        "permitido_para_qpu": permitido,
        "detalhe": info.get("motivo") or info.get("motivo_analise"),
        "analise": info.get("analise"),
        "emitido_utc": _agora(),
    }

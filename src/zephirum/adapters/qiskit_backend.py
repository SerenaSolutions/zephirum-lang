# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Serena Quantum Solutions
"""Adaptador oficial Qiskit — camada 2 (transito), nao nucleo.

Por que existe: o ecossistema em que o projeto entrou usa SDK proprio. O ZYQL
precisa conversar com ele sem se casar com ele. Este modulo traduz um programa
ZYQL declarativo em circuito nativo, executa em simulador local e devolve
resultado com recibo verificavel por hash SHA3-256.

Garantias:
  * Importacao preguicosa: importar este modulo nunca quebra o nucleo, mesmo
    sem o SDK instalado.
  * Aritmetica inteira na contagem de tiros; nenhum float decide veredito.
  * Recibo amarrado ao conteudo: alterar contagens invalida a verificacao.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

ADAPTADOR = "qiskit"
VERSAO_ADAPTADOR = "1.0"

# Operacoes suportadas: nome ZYQL -> metodo do circuito nativo.
OPERACOES_SIMPLES = {
    "h": "h", "x": "x", "y": "y", "z": "z",
    "s": "s", "sdg": "sdg", "t": "t", "tdg": "tdg",
}

OPERACOES_PARAMETRICAS = {"rx": "rx", "ry": "ry", "rz": "rz"}

OPERACOES_DUAS = {"cx": "cx", "cz": "cz", "swap": "swap"}


class AdaptadorIndisponivel(RuntimeError):
    """SDK externo ausente. Mensagem diz o que instalar, sem quebrar o nucleo."""


class ProgramaInvalido(ValueError):
    """Programa ZYQL fora do contrato aceito pelo adaptador."""


def disponivel() -> bool:
    """Diz se o SDK esta instanciavel, sem propagar excecao."""
    try:
        _sdk()
        return True
    except AdaptadorIndisponivel:
        return False


def _sdk():
    try:
        import qiskit  # noqa: F401  (importacao preguicosa e proposital)
    except Exception as erro:  # pragma: no cover - depende do ambiente
        raise AdaptadorIndisponivel(
            "SDK externo nao instalado. Instale com: pip install 'zephirum[ecossistema]'"
        ) from erro
    return qiskit


def validar(programa: dict[str, Any]) -> dict[str, Any]:
    """Valida o contrato do programa e devolve copia normalizada."""
    if not isinstance(programa, dict):
        raise ProgramaInvalido("programa deve ser um objeto com 'qubits' e 'gates'")

    qubits = programa.get("qubits")
    if not isinstance(qubits, int) or qubits < 1 or qubits > 24:
        raise ProgramaInvalido("qubits deve ser inteiro entre 1 e 24")

    portas = programa.get("gates")
    if not isinstance(portas, list) or not portas:
        raise ProgramaInvalido("gates deve ser lista nao vazia")

    normalizadas = []
    for indice, porta in enumerate(portas):
        if not isinstance(porta, dict):
            raise ProgramaInvalido(f"porta {indice} nao e objeto")
        op = str(porta.get("op", "")).lower()
        alvos = porta.get("qubits")
        if not isinstance(alvos, list) or not alvos:
            raise ProgramaInvalido(f"porta {indice} sem 'qubits'")
        for alvo in alvos:
            if not isinstance(alvo, int) or alvo < 0 or alvo >= qubits:
                raise ProgramaInvalido(f"porta {indice}: qubit {alvo} fora de 0..{qubits - 1}")

        if op in OPERACOES_SIMPLES:
            if len(alvos) != 1:
                raise ProgramaInvalido(f"porta {indice}: '{op}' usa 1 qubit")
        elif op in OPERACOES_PARAMETRICAS:
            if len(alvos) != 1:
                raise ProgramaInvalido(f"porta {indice}: '{op}' usa 1 qubit")
            if "theta" not in porta or not isinstance(porta["theta"], (int, float)):
                raise ProgramaInvalido(f"porta {indice}: '{op}' exige 'theta' numerico")
        elif op in OPERACOES_DUAS:
            if len(alvos) != 2:
                raise ProgramaInvalido(f"porta {indice}: '{op}' usa 2 qubits")
        else:
            raise ProgramaInvalido(f"porta {indice}: operacao '{op}' nao suportada")

        normalizadas.append({"op": op, "qubits": list(alvos), **({"theta": porta["theta"]} if "theta" in porta else {})})

    return {"qubits": qubits, "gates": normalizadas}


def construir(programa: dict[str, Any]):
    """Traduz programa ZYQL em circuito nativo. Ordem das portas e preservada."""
    _sdk()
    from qiskit import QuantumCircuit

    normalizado = validar(programa)
    circuito = QuantumCircuit(normalizado["qubits"])
    for porta in normalizado["gates"]:
        op, alvos = porta["op"], porta["qubits"]
        if op in OPERACOES_SIMPLES:
            getattr(circuito, OPERACOES_SIMPLES[op])(alvos[0])
        elif op in OPERACOES_PARAMETRICAS:
            getattr(circuito, OPERACOES_PARAMETRICAS[op])(porta["theta"], alvos[0])
        else:
            getattr(circuito, OPERACOES_DUAS[op])(alvos[0], alvos[1])
    return circuito


def estado_exato(programa: dict[str, Any]) -> dict[str, complex]:
    """Amplitudes exatas. Serve para comparar simulacao com previsao teorica."""
    _sdk()
    from qiskit.quantum_info import Statevector

    vetor = Statevector.from_instruction(construir(programa))
    return {str(chave): complex(valor) for chave, valor in vetor.to_dict().items()}


def _hash_conteudo(payload: dict[str, Any]) -> str:
    canonico = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha3_256(canonico.encode("utf-8")).hexdigest()


def executar(programa: dict[str, Any], shots: int = 1024, seed: int = 0) -> dict[str, Any]:
    """Executa no simulador local e devolve contagens com recibo selado.

    Nada e enviado a hardware externo: esta funcao e deterministica e local.
    """
    _sdk()
    if not isinstance(shots, int) or shots < 1 or shots > 1_000_000:
        raise ProgramaInvalido("shots deve ser inteiro entre 1 e 1000000")
    if not isinstance(seed, int) or seed < 0:
        raise ProgramaInvalido("seed deve ser inteiro nao negativo")

    from qiskit import transpile
    from qiskit_aer import AerSimulator

    circuito = construir(programa)
    medicao = circuito.copy()
    medicao.measure_all()

    backend = AerSimulator(seed_simulator=seed)
    compilado = transpile(medicao, backend=backend, seed_transpiler=seed)
    bruto = backend.run(compilado, shots=shots, seed_simulator=seed).result().get_counts()

    contagens = {str(k): int(v) for k, v in bruto.items()}
    total = sum(contagens.values())
    if total != shots:
        raise RuntimeError(f"contagem inconsistente: {total} tiros medidos de {shots} pedidos")

    corpo = {
        "adaptador": ADAPTADOR,
        "versao_adaptador": VERSAO_ADAPTADOR,
        "programa": validar(programa),
        "shots": shots,
        "seed": seed,
        "contagens": contagens,
        "total": total,
    }
    corpo["recibo"] = _hash_conteudo({k: v for k, v in corpo.items() if k != "recibo"})
    return corpo


def verificar(recibo: dict[str, Any]) -> dict[str, Any]:
    """Recalcula o hash do recibo. Contagem adulterada reprova aqui."""
    corpo = {k: v for k, v in recibo.items() if k != "recibo"}
    esperado = _hash_conteudo(corpo)
    confere = esperado == recibo.get("recibo")

    inconsistencia = None
    if sum(int(v) for v in corpo.get("contagens", {}).values()) != corpo.get("total"):
        inconsistencia = "soma das contagens difere do total declarado"
        confere = False

    return {
        "valido": confere,
        "hash_calculado": esperado,
        "hash_declarado": recibo.get("recibo"),
        "inconsistencia": inconsistencia,
    }

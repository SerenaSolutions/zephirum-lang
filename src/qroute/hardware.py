"""Q-ROUTE na QPU: monta o Grover, transpila para o backend e submete a IBM.

O recibo de hardware carrega job_id, backend, shots, contagens brutas e o
intervalo de confianca da probabilidade medida — sem esses campos nao ha alegacao."""
import math
import os

from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import MCPhaseGate


def monta(n_qubits, marcados, iteracoes):
    qc = QuantumCircuit(n_qubits, n_qubits)
    qc.h(range(n_qubits))
    for _ in range(iteracoes):
        for m in marcados:                      # oraculo: inverte a fase de cada rota viavel
            for q in range(n_qubits):
                if not (m >> q) & 1:
                    qc.x(q)
            qc.append(MCPhaseGate(math.pi, n_qubits - 1), range(n_qubits))
            for q in range(n_qubits):
                if not (m >> q) & 1:
                    qc.x(q)
        qc.h(range(n_qubits))                   # difusao
        qc.x(range(n_qubits))
        qc.append(MCPhaseGate(math.pi, n_qubits - 1), range(n_qubits))
        qc.x(range(n_qubits))
        qc.h(range(n_qubits))
    qc.measure(range(n_qubits), range(n_qubits))
    return qc


def p_marcados(counts, marcados, shots=None):
    alvo = {"{:0{n}b}".format(m, n=n) for m in marcados} if False else None
    total = sum(counts.values())
    soma = 0
    for bits, c in counts.items():
        limpo = bits.replace(" ", "")
        if int(limpo, 2) in marcados:
            soma += c
    p = soma / total if total else 0.0
    n = total or shots or 1
    erro = 1.96 * math.sqrt(max(p * (1 - p), 0) / n)      # IC 95% normal
    return {"p_medido": round(p, 6), "shots": total,
            "ic95": [round(max(0.0, p - erro), 6), round(min(1.0, p + erro), 6)]}


ORDEM_TOKEN = ("IBM_QUANTUM_TOKEN", "IBM_QUANTUM_TOKEN_2", "IBM_QUANTUM_TOKEN_3",
               "IBM_QUANTUM_TOKEN_4", "IBM_QUANTUM_TOKEN_5")


_ESCOLHIDO = {}


def _token():
    """Escolhe a chave mais recente que REALMENTE autentica.

    O ambiente ganha sufixo _N a cada rotacao, e nem toda chave nova e valida
    (chave revogada, copia truncada). Testar por numero quebra a execucao sem aviso."""
    if _ESCOLHIDO:
        return _ESCOLHIDO["tok"], _ESCOLHIDO["nome"]
    nomes = [n for n in reversed(ORDEM_TOKEN) if os.environ.get(n)]
    if not nomes:
        return None, None
    from qiskit_ibm_runtime import QiskitRuntimeService
    for nome in nomes:
        try:
            QiskitRuntimeService(channel="ibm_quantum_platform",
                                 token=os.environ[nome]).usage()
        except Exception as e:
            print("aviso: %s nao autentica (%s); tentando a anterior" % (nome, type(e).__name__))
            continue
        _ESCOLHIDO.update(tok=os.environ[nome], nome=nome)
        return _ESCOLHIDO["tok"], nome
    return None, None


def _servico(token=None, crn=None):
    """Conecta na IBM; se o CRN salvo estiver obsoleto, cai para a instancia automatica.

    CRN velho no ambiente ja quebrou duas execucoes — agora e tratado como aviso,
    nao como falha: a conta aberta e selecionada sozinha."""
    from qiskit_ibm_runtime import QiskitRuntimeService
    from qiskit_ibm_runtime.exceptions import IBMInputValueError
    tok = token or _token()[0]
    inst = crn or os.environ.get("IBM_QUANTUM_CRN") or None
    if inst:
        try:
            return QiskitRuntimeService(channel="ibm_quantum_platform", token=tok, instance=inst)
        except IBMInputValueError:
            print("aviso: CRN salvo nao existe mais nesta conta; usando a instancia aberta")
    return QiskitRuntimeService(channel="ibm_quantum_platform", token=tok)


def executa(n_qubits, marcados, iteracoes, shots=1024, backend=None, token=None, crn=None):
    from qiskit_ibm_runtime import SamplerV2
    svc = _servico(token, crn)
    if backend:
        bk = svc.backend(backend)
    else:
        cands = svc.backends(operational=True, simulator=False)
        bk = min(cands, key=lambda b: b.status().pending_jobs)
    qc = monta(n_qubits, marcados, iteracoes)
    tqc = transpile(qc, bk, optimization_level=3)
    sampler = SamplerV2(mode=bk)
    job = sampler.run([tqc], shots=shots)
    res = job.result()
    dados = res[0].data
    reg = list(dados.keys())[0]
    counts = getattr(dados, reg).get_counts()
    m = p_marcados(counts, marcados, shots)
    return {
        "modo": "HARDWARE IBM QUANTUM",
        "backend": bk.name,
        "job_id": job.job_id(),
        "shots_pedidos": shots,
        "qubits_fisicos_trabalho": n_qubits,
        "profundidade_transpilada": tqc.depth(),
        "portas_2q": sum(1 for i in tqc.data if len(i.qubits) == 2),
        "contagens": {k.replace(" ", ""): v for k, v in counts.items()},
        **m,
    }


def dry_run(n_qubits, marcados, iteracoes, shots=1024):
    """Ensaio sem credencial: backend falso com ruido real de calibracao da IBM."""
    from qiskit_ibm_runtime.fake_provider import FakeMarrakesh
    bk = FakeMarrakesh()
    qc = monta(n_qubits, marcados, iteracoes)
    tqc = transpile(qc, bk, optimization_level=3)
    from qiskit_aer import AerSimulator
    sim = AerSimulator.from_backend(bk)
    counts = sim.run(tqc, shots=shots).result().get_counts()
    m = p_marcados(counts, marcados, shots)
    return {"modo": "ENSAIO (backend falso, ruido de calibracao IBM, NAO e QPU)",
            "backend": "FakeMarrakesh", "job_id": None,
            "shots_pedidos": shots, "profundidade_transpilada": tqc.depth(),
            "portas_2q": sum(1 for i in tqc.data if len(i.qubits) == 2),
            "contagens": {k.replace(" ", ""): v for k, v in counts.items()}, **m}

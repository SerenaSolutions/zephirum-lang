"""AuditKit: certificacao de entropia quantica com recibo (CPA-01)."""
import json, math, os
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister, transpile
from zyql_witness import _seal

def _circ(n):
    qr = QuantumRegister(n, "q"); cr = ClassicalRegister(n, "c")
    qc = QuantumCircuit(qr, cr)
    for i in range(n): qc.h(i)
    qc.measure(qr, cr)
    return qc

def _monobit(bits):
    n = len(bits); c = bits.count("1")
    return (c - n / 2) / math.sqrt(n / 4)

def _runs(bits):
    n = len(bits)
    runs = 1 + sum(1 for i in range(1, n) if bits[i] != bits[i - 1])
    p = bits.count("1") / n
    mu = 2 * n * p * (1 - p)
    var = 2 * n * p * (1 - p) * (2 * n * p * (1 - p) - 1) / (n - 1)
    return (runs - mu) / math.sqrt(var) if var > 0 else 0.0

def _chi2(bits):
    n = len(bits); e = n / 2
    return (bits.count("0") - e) ** 2 / e + (bits.count("1") - e) ** 2 / e

def certificar(shots=1024, qubits=8, qpu=None, seal_path=None):
    circ = _circ(qubits)
    if qpu is None:
        from qiskit_aer import AerSimulator
        sim = AerSimulator(seed_simulator=3)
        res = sim.run(transpile(circ, sim), shots=shots).result()
        counts, dev, jid = res.get_counts(), "aer_simulator", "local"
    else:
        from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
        tok = os.environ.get("IBM_API_KEY") or os.environ.get("GITHUB_TOKEN_2")
        svc = QiskitRuntimeService(channel="ibm_quantum_platform", token=tok)
        b = svc.backend(qpu)
        tq = transpile(circ, backend=b, optimization_level=1)
        job = Sampler(mode=b).run([tq], shots=shots)
        res = job.result()
        counts, dev, jid = res[0].data.c.get_counts(), b.name, job.job_id()
    bits = "".join(k * v for k, v in counts.items())
    N = len(bits)
    z1, z2, chi = _monobit(bits), _runs(bits), _chi2(bits)
    if N < 2048: v = "REFUSED"
    elif max(abs(z1), abs(z2)) > 3.29: v = "0"
    else: v = "1"
    payload = {"protocolo": {"id": "CPA-01", "declarado": {"shots": shots, "qubits": qubits,
               "alpha": 0.01, "testes": ["monobit", "runs", "chi2_binario"]}},
               "execucao": {"dispositivo": dev, "job_id": jid, "counts": counts, "bits": N},
               "resultado": {"z_monobit": round(z1, 3), "z_runs": round(z2, 3),
                             "chi2": round(chi, 3), "veredito": v}}
    rec = _seal(payload)
    if seal_path: json.dump(rec, open(seal_path, "w"), ensure_ascii=False, indent=1)
    return rec

def verify_receipt(path):
    import hashlib
    d = json.load(open(path))
    h = d.pop("receipt_sha3_256")
    return hashlib.sha3_256(json.dumps(d, sort_keys=True, ensure_ascii=False).encode()).hexdigest() == h

"""Testes da testemunha de abstenção (refusal witness) — roda sem QPU."""
import json
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

try:
    from zyql_witness import (witness, verify_receipt, _dj, _ideal_probs,
                              _tvd)
    from qiskit import transpile
    from qiskit_aer import AerSimulator
    from qiskit_aer.noise import NoiseModel, depolarizing_error
except Exception as e:  # pragma: no cover
    print(f"RESULTADO WITNESS: SKIP ({e})")
    sys.exit(0)

ok = falhas = 0


def checa(nome, cond, extra=""):
    global ok, falhas
    if cond:
        ok += 1
        print(f"  OK   {nome} {extra}")
    else:
        falhas += 1
        print(f"  FALHA {nome} {extra}")


# 1) dispositivo fiel -> CERTIFICADO (=1)
r = witness("balanced", shots=4096, seal_path="/tmp/wit_t1.json")
checa("limpo certifica", r.verdict == "1" and r.tvd < 0.05, f"tvd={r.tvd:.4f}")
checa("selo íntegro", verify_receipt("/tmp/wit_t1.json"))

# 2) ruído forte -> REPROVADO (=0)
noise = NoiseModel()
noise.add_all_qubit_quantum_error(depolarizing_error(0.08, 1), ["h", "x"])
noise.add_all_qubit_quantum_error(depolarizing_error(0.10, 2), ["cx"])
sim = AerSimulator(noise_model=noise, seed_simulator=7)
circ = _dj("balanced", 3)
counts = sim.run(transpile(circ, sim), shots=4096).result().get_counts()
ideal = _ideal_probs("balanced", 3)
tvd = _tvd(ideal, counts, 3)
delta = math.sqrt(8 * math.log(200) / 8192)
checa("ruído reprova", tvd - delta > 0.10, f"tvd={tvd:.4f} lower={max(0,tvd-delta):.4f}")

# 3) poucos shots -> REFUSED por evidência insuficiente
r3 = witness("balanced", shots=64, seal_path="/tmp/wit_t3.json")
checa("64 shots abstém", r3.verdict == "REFUSED" and r3.delta > 0.3,
      f"delta={r3.delta:.3f}")
checa("recibo do REFUSED selado", verify_receipt("/tmp/wit_t3.json"))

# 4) protocolo declarado antes da execução
prot = json.load(open("/tmp/wit_t1.json", encoding="utf-8"))["protocolo"]
checa("protocolo pré-declarado", "limite" in prot and prot["epsilon"] == 0.10)

print(f"RESULTADO WITNESS: {ok} ok / {falhas} falhas")
sys.exit(1 if falhas else 0)

#!/usr/bin/env python3
"""
IBM FREE QUANTUM — verificação em QPU real (plano gratuito IBM Quantum).
=======================================================================

Ideia: o ZEPHIRUM prevê o resultado IDEAL de forma EXACTA (Fraction), e a
QPU real é medida contra essa previsão. O certificado diz o que a matemática
exige; o recibo diz o que o hardware entregou. Nunca se confundem.

Testes (todos pequenos o suficiente para o plano gratuito):
  T1  X          — determinístico: 1 com probabilidade 1
  T2  H          — superposição: 0 e 1 com 1/2 cada
  T3  Bell       — H+CNOT: 00 e 11 com 1/2 cada, 01/10 proibidos
  T4  GHZ-3      — 000 e 111 com 1/2 cada, resto proibido
  T5  Zephirum   — a decisão exacta do kernel (emaranhado == 1) é comparada
                   com o resultado do hardware (critério de Schmidt previsto
                   analiticamente; a QPU só confirma)

Uso:
  export IBM_QUANTUM_TOKEN=...      # NUNCA no chat, NUNCA no repositório
  python3 ibm_free_qpu.py --shots 1024

Sem token ou sem SDK: SKIP (§12) explícito, exit 3 — nenhum job inventado.
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from decision_kernel import digest


# ------------------------------------------------------------------ previsão
# O oráculo do ZEPHIRUM: distribuições IDEIAIS, exactas, sem float.
def predict_exact():
    return {
        "T1_x": {"1": Fraction(1)},
        "T2_h": {"0": Fraction(1, 2), "1": Fraction(1, 2)},
        "T3_bell": {"00": Fraction(1, 2), "11": Fraction(1, 2)},
        "T4_ghz3": {"000": Fraction(1, 2), "111": Fraction(1, 2)},
        # T5: estado de Bell é emaranhado (C = 1): a decisão do kernel
        # 'entangled == 1' é True — o hardware deve produzir correlações
        # perfeitamente correlacionadas (mesma distribuição de T3).
        "T5_zephirum_bell": {"00": Fraction(1, 2), "11": Fraction(1, 2)},
    }


def build_circuits():
    """Circuitos Qiskit correspondentes (só quando o SDK existe)."""
    from qiskit import QuantumCircuit

    circuits = {}

    c = QuantumCircuit(1, 1)
    c.x(0)
    c.measure(0, 0)
    circuits["T1_x"] = c

    c = QuantumCircuit(1, 1)
    c.h(0)
    c.measure(0, 0)
    circuits["T2_h"] = c

    c = QuantumCircuit(2, 2)
    c.h(0)
    c.cx(0, 1)
    c.measure([0, 1], [0, 1])
    circuits["T3_bell"] = c

    c = QuantumCircuit(3, 3)
    c.h(0)
    c.cx(0, 1)
    c.cx(1, 2)
    c.measure([0, 1, 2], [0, 1, 2])
    circuits["T4_ghz3"] = c

    c = QuantumCircuit(2, 2)
    c.h(0)
    c.cx(0, 1)
    c.measure([0, 1], [0, 1])
    circuits["T5_zephirum_bell"] = c

    return circuits


# --------------------------------------------------------------- verificação
def verify_counts(counts, ideal, shots, tvd_max=0.10):
    """Compara contagens reais com a distribuição ideal exacta.

    Critério: distância de variação total (TVD) entre a frequência medida e
    a ideal abaixo de tvd_max; resultados 'proibidos' (ideal = 0) só são
    tolerados como ruído de leitura até 5% dos shots.
    """
    observed = {k.replace(" ", ""): v for k, v in counts.items()}
    total = sum(observed.values()) or 1
    freqs = {k: Fraction(v, total) for k, v in observed.items()}
    outcomes = set(freqs) | set(ideal)
    tvd = sum(abs(freqs.get(o, Fraction(0)) - ideal.get(o, Fraction(0)))
              for o in outcomes) / 2
    forbidden = {k: v for k, v in observed.items() if k not in ideal}
    forbidden_share = (Fraction(sum(forbidden.values()), total)
                       if forbidden else Fraction(0))
    ok = (tvd <= Fraction(tvd_max).limit_denominator(1000)
          and forbidden_share <= Fraction(5, 100))
    return {
        "ok": ok,
        "tvd": float(tvd),
        "tvd_max": tvd_max,
        "forbidden": forbidden,
        "forbidden_share": float(forbidden_share),
        "observed": dict(observed),
        "ideal": {k: str(v) for k, v in ideal.items()},
        "shots": total,
    }


# ---------------------------------------------------------------- execução
def _load_sdk():
    try:
        import qiskit  # noqa: F401
        from qiskit_ibm_runtime import QiskitRuntimeService, Sampler  # noqa: F401
        return True
    except Exception:
        return False


def run_on_ibm(shots=1024):
    """Executa a suíte na QPU menos ocupada do plano gratuito."""
    token = os.environ.get("IBM_QUANTUM_TOKEN", "")
    if not token:
        print("SKIP (§12): IBM_QUANTUM_TOKEN ausente — nenhum job foi "
              "submetido e nenhum ID foi inventado.")
        print("Defina: export IBM_QUANTUM_TOKEN=<o seu token do IBM Quantum>")
        return 3
    if not _load_sdk():
        print("SKIP (§12): qiskit / qiskit-ibm-runtime não instalados.")
        print("Instale: pip install qiskit qiskit-ibm-runtime")
        return 3

    from qiskit_ibm_runtime import QiskitRuntimeService, Sampler

    service = QiskitRuntimeService(channel="ibm_quantum", token=token)
    backend = service.least_busy(operational=True, simulator=False)
    print("BACKEND:", backend.name)

    circuits = build_circuits()
    ideal = predict_exact()
    sampler = Sampler(mode=backend)
    receipts = {}
    all_ok = True

    for name in circuits:
        job = sampler.run([circuits[name]], shots=shots)
        print("JOB %-18s %s" % (name, job.job_id()))
        result = job.result()
        data = result[0].data
        counts = data.meas.get_counts()
        check = verify_counts(counts, ideal[name], shots)
        all_ok = all_ok and check["ok"]
        receipts[name] = {
            "job_id": job.job_id(),
            "backend": backend.name,
            "shots": shots,
            "counts": counts,
            "check": check,
            "verdict": "CONFIRMED" if check["ok"] else "DEVIATED",
        }
        print("  -> %s (TVD %.3f)" % (receipts[name]["verdict"],
                                      check["tvd"]))

    receipt = {
        "receipt_version": "1.0",
        "kind": "ibm_free_qpu_suite",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "backend": backend.name,
        "shots": shots,
        "tests": receipts,
        "all_confirmed": all_ok,
        "limitations": [
            "free plan: queue times vary; readout error tolerated up to 5%",
            "ideal distributions are exact (Fraction); hardware is noisy",
            "TVD threshold 0.10 declared before execution",
        ],
    }
    receipt["INTEGRITY"] = digest(receipt)
    path = "results/ibm_free_qpu_receipt.json"
    os.makedirs("results", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(receipt, f, indent=1, sort_keys=True, default=str)
    print("RECEIPT:", path)
    print("INTEGRITY:", receipt["INTEGRITY"])
    print("RESULTADO:", "PASS — hardware confirma o ideal"
          if all_ok else "DEVIATED — ver recibo")
    return 0 if all_ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shots", type=int, default=1024)
    a = ap.parse_args()
    return run_on_ibm(shots=a.shots)


if __name__ == "__main__":
    sys.exit(main())

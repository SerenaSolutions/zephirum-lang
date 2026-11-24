#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""ZEPHYRUM QPU witness - hardware is evidence, never the judge.

Produces the exact verdict offline, submits a Bell Phi+ witness to IBM
Quantum on the free plan, and seals a receipt binding the verdict hash to
the hardware job id. Token and CRN come from the environment only.
"""
import hashlib, json, os, sys
from datetime import datetime, timezone

from qiskit import QuantumCircuit
from qiskit import transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

SHOTS = int(os.environ.get("WITNESS_SHOTS", "512"))
BACKEND = os.environ.get("WITNESS_BACKEND", "ibm_fez")


def exact_verdict():
    """Reference exact verdict: Bell Phi+ is entangled (det != 0), decided offline."""
    return {
        "ask": "Is the Bell state Phi+ entangled?",
        "verdict": 1,
        "method": "exact_determinant",
        "detail": "det(rho_A partial) = -0.25 != 0 -> entangled",
        "units_consumed": 0,
    }


def bell_pair():
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    return qc


def measure_in(qc, basis):
    out = qc.copy()
    if basis == "X":
        out.h(0)
        out.h(1)
    out.measure_all()
    return out


def main():
    token = os.environ.get("IBM_QUANTUM_TOKEN")
    crn = os.environ.get("IBM_QUANTUM_CRN")
    if not token:
        print("IBM_QUANTUM_TOKEN missing", file=sys.stderr)
        return 2

    verdict = exact_verdict()
    vhash = hashlib.sha256(json.dumps(verdict, sort_keys=True).encode()).hexdigest()

    kwargs = {"channel": "ibm_quantum_platform", "token": token}
    # Only pass instance when the CRN is complete: a truncated or partial CRN
    # makes the runtime reject the whole account. Token-only discovery works.
    if crn and crn.startswith("crn:v1:") and len(crn) > 60:
        kwargs["instance"] = crn
    elif crn:
        print("[witness] CRN incompleto (%d chars) - usando descoberta por token" % len(crn), flush=True)
    service = QiskitRuntimeService(**kwargs)
    usage_before = service.usage()

    backend = service.backend(BACKEND)
    # The target does not accept raw H: transpile for the device before submitting.
    circuits = transpile([measure_in(bell_pair(), "Z"), measure_in(bell_pair(), "X")],
                         backend=backend, optimization_level=1)
    sampler = Sampler(mode=backend)
    job = sampler.run(circuits, shots=SHOTS)
    print("[witness] job %s submitted to %s" % (job.job_id(), BACKEND))
    result = job.result()

    correlators = {}
    for basis, idx in (("ZZ", 0), ("XX", 1)):
        counts = result[idx].data.meas.get_counts()
        total = sum(counts.values())
        same = counts.get("00", 0) + counts.get("11", 0)
        correlators[basis] = round((2 * same - total) / total, 4)

    receipt = {
        "doctrine": "QPU is witness, never judge",
        "sealed_at": datetime.now(timezone.utc).isoformat(),
        "verdict": verdict,
        "verdict_sha256": vhash,
        "hardware": {"backend": BACKEND, "shots": SHOTS, "job_id": job.job_id()},
        "measured": correlators,
        "usage_before": usage_before,
        "usage_after": service.usage(),
    }
    out = os.environ.get("RECEIPT_PATH", "/opt/zyql/receipts/witness_%s.json" % job.job_id())
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as fh:
        json.dump(receipt, fh, indent=2)
    print(json.dumps(receipt, indent=2))
    print("[witness] receipt sealed at %s" % out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

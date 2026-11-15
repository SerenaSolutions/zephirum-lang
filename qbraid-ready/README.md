# ZEPHIRUM

Quantum language and runtime for auditable decisions. Every execution returns a trivalent
verdict (1, 0 or REFUSED) with a declared statistical bound and a sealed SHA3-256 receipt
that anyone can verify.

## What the notebook covers

1. Install and import the runtime.
2. Produce a verdict from measurement counts, with the bound stated.
3. Verify the sealed receipt and detect any alteration.
4. Run a three-case battery: Bell parity, constant Deutsch-Jozsa, balanced Deutsch-Jozsa.

## Launch on qBraid

Open `zephirum_qbraid.ipynb` in qBraid Lab and run the cells. No credential is needed:
the runtime is local and deterministic.

## Running locally

    pip install -r requirements.txt
    jupyter lab zephirum_qbraid.ipynb

## What it does not claim

A receipt proves integrity of the record, not correctness of the calculation, and not
execution on hardware. Hardware execution is reported separately, with backend and job id.

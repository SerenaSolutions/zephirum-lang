# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Serena Quantum Solutions
"""Rodada fresca de prova de conceito na QPU (2026-11-05)."""
import hashlib, json, sys, time
from pathlib import Path
AQUI = Path(__file__).parent
sys.path.insert(0, str(AQUI.parent.parent / "src"))
import os
from qroute import hardware as hw
tok, nome = hw._token()
os.environ["IBM_API_KEY"] = tok  # rodada_mundial le desse nome
from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit import transpile
from zyql_worldscale import walk, hom, grover, rodada_mundial

PROTO = {"id": "POC-20261105", "data": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
         "shots": 8192, "circuitos": ["W-01_caminhada", "W-02_HOM", "W-03_grover101"],
         "bandas": {"W-01_tvd": [0.20, 0.35], "W-02_vis": [0.8, 0.5], "W-03_p": [0.85, 0.70]},
         "chave": nome}
PROTO["sha3_protocolo"] = hashlib.sha3_256(json.dumps(PROTO, sort_keys=True).encode()).hexdigest()
(AQUI / "protocolo_poc.json").write_text(json.dumps(PROTO, indent=1))
print("protocolo selado:", PROTO["sha3_protocolo"][:24], flush=True)

svc = QiskitRuntimeService(channel="ibm_quantum_platform", token=tok)
b = svc.least_busy(operational=True, simulator=False)
print("backend:", b.name, flush=True)
rec = rodada_mundial(shots=8192, qpu=b.name, seal_path=str(AQUI / "poc_20261105.json"))
r = rec["resultado"]
print("W-01 tvd:", r["W-01"]["tvd"], r["W-01"]["veredito"], flush=True)
print("W-02 vis:", r["W-02"]["visibilidade"], r["W-02"]["veredito"], flush=True)
print("W-03 p  :", r["W-03"]["p_marcado"], r["W-03"]["veredito"], flush=True)
print("job:", rec["execucao"]["job_id"], flush=True)

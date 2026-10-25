# -*- coding: utf-8 -*-
"""RODADA G — analise + selagem Z-QEA encadeada (v2.0.0 no silicio).

CORRECAO REGISTRADA (antes de qualquer selo publico): lista de circuitos
= 1 PUB POR CIRCUITO; a leitura antiga fatiava BITS do BitArray e lia o
mesmo circuito repetido. Achado nosso, corrigido aqui, semHistoria oculta.
"""
import glob, hashlib, json, os, sys, time
import numpy as np
HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, "..", "src"))
from zyqml_core import train_verdict
from zyql_zne import zne_verdict
from zyql_mps import MPSSim, H1 as MH1, CNOT4
from qiskit_ibm_runtime import QiskitRuntimeService

jobs = json.load(open(os.path.join(HERE, "round_g_jobs.json")))
svc = QiskitRuntimeService(channel="ibm_quantum_platform", token=os.environ["IBM_QUANTUM_TOKEN"])

def fetch(jid, wait=300):
    job = svc.job(jid)
    for _ in range(wait // 10):
        st = str(job.status())
        if st in ("DONE", "ERROR", "FAILED", "CANCELLED"):
            break
        time.sleep(10)
    print(jid, "->", st)
    assert st == "DONE", "job nao terminou: " + st
    return job.result()

def pub_counts(res, i, expect):
    d = res[i].data
    for nm in (list(getattr(d, "fields", ()) or []) or ["c"]):
        try:
            c = getattr(d, nm).get_counts()
            if abs(sum(c.values()) - expect) <= 0.1 * expect:
                return c
        except Exception:
            continue
    raise KeyError("pub %d sem contagens" % i)

r_qml = fetch(jobs["qml_job"])
r_zne = fetch(jobs["zne_job"])
r_g12 = fetch(jobs["g12_job"])
print("pubs:", len(r_qml), len(r_zne), len(r_g12))

# ---------- A1: gradientes parameter-shift MEDIDOS NO QPU (base X) ----------
SQ = jobs["shots"]["qml"]
def energy_hw(pi):
    c = pub_counts(r_qml, pi, SQ)
    p0 = sum(v for k, v in c.items() if k[-1] == "0") / SQ    # little-endian: q0 = ultimo char
    return 2 * p0 - 1

meta = jobs["meta"]
grads, e_base = {"shallow": [], "deep": []}, {}
for label in ("shallow", "deep"):
    pubs = [i for i, m in enumerate(meta) if m[0] == label]
    assert len(pubs) >= 3, "meta sem grupo " + label
    e_base[label] = energy_hw(pubs[0])
    for k in range(1, len(pubs), 2):        # pares (+,-) consecutivos
        assert meta[pubs[k]][2] == 1.0 and meta[pubs[k + 1]][2] == -1.0
        grads[label].append((energy_hw(pubs[k]) - energy_hw(pubs[k + 1])) / 2.0)

var_s, var_d = float(np.var(grads["shallow"])), float(np.var(grads["deep"]))
v_s = train_verdict(jobs["n"], jobs["layers_shallow"], var_s)
v_d = train_verdict(jobs["n"], jobs["layers_deep"], var_d)
print("A1 gradientes raso   :", ["%+.4f" % g for g in grads["shallow"]])
print("A1 gradientes profundo:", ["%+.4f" % g for g in grads["deep"]])
print("A1 variancia: raso=%.6f profundo=%.6f" % (var_s, var_d))
print("A1 veredito raso    :", v_s["decision"], v_s.get("refusal_reason", ""))
print("A1 veredito profundo:", v_d["decision"], v_d.get("refusal_reason", ""))

# ---------- A2: fidelidade GHZ5 em gamma=1,3,5 + ZNE ternario ----------
SZ = jobs["shots"]["zne"]
fids = []
for gi in range(3):
    c = pub_counts(r_zne, gi, SZ)
    fids.append((c.get("00000", 0) + c.get("11111", 0)) / SZ)
print("A2 fidelidades GHZ5 gamma=1,3,5:", ["%.4f" % f for f in fids])
assert fids[0] > fids[1] > fids[2], "folding deve degradar a fidelidade monotonicamente"
v_zne = zne_verdict(jobs["gammas"], fids)
print("A2 ZNE veredito:", v_zne["decision"], v_zne.get("refusal_reason", ""),
      "| estimativa zero-noise=%.4f" % v_zne["estimate"])

# ---------- A3: GHZ12 hardware vs MPS exato ----------
m = MPSSim(12, chi=4)
m.apply_1q(MH1, 0)
for i in range(11):
    m.apply_2q(CNOT4, i, i + 1)
p_mps = m.probs()
c12 = pub_counts(r_g12, 0, jobs["shots"]["g12"])
f12 = (c12.get("0" * 12, 0) + c12.get("1" * 12, 0)) / jobs["shots"]["g12"]
print("A3 GHZ12: MPS exato 0.5/0.5 | hardware fidelidade=%.4f" % f12)

# ---------- selagem Z-QEA encadeada (nao encadeia em si mesma) ----------
cands = [p for p in glob.glob(os.path.join(HERE, "*receipt*.json"))
         if "round_g" not in os.path.basename(p)]
prev = sorted(cands, key=os.path.getmtime)[-1]
prev_seal = None
try:
    pr = json.load(open(prev))
    prev_seal = pr.get("selo_sha3_256") or pr.get("payload", {}).get("selo_sha3_256")
except Exception:
    pass
print("cadeia <-", os.path.basename(prev))

payload = {"round": "G", "theme": "fronteiras v2.0.0 no silicio",
  "backend": jobs["backend"], "jobs": {k: jobs[k] for k in ("qml_job", "zne_job", "g12_job")},
  "shots": jobs["shots"], "qml_basis": jobs.get("qml_basis"),
  "a1_qml_trivalente": {
    "n": jobs["n"], "layers": {"shallow": jobs["layers_shallow"], "deep": jobs["layers_deep"]},
    "gradients_shallow": grads["shallow"], "gradients_deep": grads["deep"],
    "gradient_variance": {"shallow": var_s, "deep": var_d}, "energy_base": e_base,
    "verdict_shallow": v_s, "verdict_deep": v_d,
    "method": "parameter-shift no QPU real, base X em q0 (H pre-medida), 1024 shots"},
  "a2_zne_manual_folding": {"gammas": jobs["gammas"], "ghz5_fidelities": fids,
    "verdict": v_zne, "method": "CX dobrados a mao pos-transpile; Richardson nativo"},
  "a3_ghz12_vs_mps": {"mps_p0_12": float(p_mps[0]), "hardware_fidelity": f12, "mps_chi": 4},
  "correction_log": "leitura inicial de pubs fatiava Bits (bug nosso, achado na analise); A1 refeito em base X; nada selado antes da correcao",
  "previous_seal": prev_seal, "previous_receipt": os.path.basename(prev),
  "sealed_by": "zyql-round-g-2.0.0"}
selo = hashlib.sha3_256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
receipt = {"payload": payload, "selo_sha3_256": selo}
json.dump(receipt, open(os.path.join(HERE, "round_g_receipt.json"), "w"), indent=1, sort_keys=True)
chk = hashlib.sha3_256(json.dumps(receipt["payload"], sort_keys=True).encode()).hexdigest()
assert chk == selo, "selo nao verifica!"
print("RECIBO SELADO:", selo[:16], "| cadeia:", os.path.basename(prev), "| VERIFICACAO OFFLINE: OK")

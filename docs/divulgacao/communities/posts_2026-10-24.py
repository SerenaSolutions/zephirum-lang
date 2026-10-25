import json, os, urllib.request

T = os.environ['GITHUB_TOKEN']

MITIQ = {
  "repo": "MDEwOlJlcG9zaXRvcnkyMzY3MDY4ODE=",
  "cat": "MDE4OkRpc2N1c3Npb25DYXRlZ29yeTMyMTE4NjU0",  # Show and tell
  "title": "Show and tell: a trivalent decision core on three IBM Heron QPUs - repetition-code correction, CHSH violation, and declared adaptive margins",
  "body": """Hello Unitary Fund community! Sharing results from a small research language we've been validating on hardware, hoping for feedback from the error-mitigation folks here.

We built **ZYQL**, a trivalent exact-decision core (part of the ZEPHIRUM language): it reads verdicts **1 / 0 / REFUSED** from Deutsch-Jozsa interference, with statistical margins declared per verdict (adaptive Hoeffding bound), and a GHZ-state gate that interrogates the processor's coherence before accepting any verdict. Every run is sealed with a receipt (SHA3-256 + ML-DSA-44) binding verdict + job ID + calibration snapshot.

Recent results on IBM Heron processors (Open Plan, all job IDs citable):

- **Repetition-code QEC**: single deterministic bit-flip injected (measured physical error 99.3% - the error class the code is designed to correct); majority vote leaves 1.5% logical error (superconducting QPU)
- **CHSH**: S = 2.71 vs theoretical 2.83 (classical bound 2.0) - the deficit is consistent with the declared mean readout error (2.02%) from the calibration snapshot taken minutes before the run
- **GHZ device-trust gate**: state fidelity 0.977; decisions below threshold are REFUSED rather than guessed
- **Exact trivalent battery**: 9/9 exact Deutsch-Jozsa decisions at n = 4/5/6 (1024 shots)

The core is deliberately honest about noise: REFUSED is a first-class outcome and margins are derived from a declared epsilon, not tuned post hoc. Cross-validated in six SDKs (the Python quantum SDK, OpenQASM 3, Cirq, PennyLane, Braket, Q#) with exact agreement.

Code (MIT): https://github.com/SerenaSolutions/zephirum-lang
Proof index with all job IDs: https://github.com/SerenaSolutions/zephirum-lang/discussions/35
DOI: 10.5281/zenodo.23302045

Questions welcome, especially: has anyone here combined Mitiq's ZNE with a decision-bounded readout layer? We're considering it for the noise-sensitive frontiers (CHSH, larger Grover instances)."""
}

QUTIP = {
  "repo": "MDEwOlJlcG9zaXRvcnk2MTM2MjYx",
  "cat": "MDE4OkRpc2N1c3Npb25DYXRlZ29yeTMyMDgyMjM3",  # Show and tell
  "title": "Show and tell: ZEPHIRUM - a trivalent quantum decision language (1/0/REFUSED from Deutsch-Jozsa interference), validated on three IBM Heron QPUs",
  "body": """Hello QuTiP community! Sharing a language design experiment we've been validating on real hardware - critique very welcome.

**ZEPHIRUM** is a Lisp-style (s-expression) quantum decision language. Its core, **ZYQL**, reads three-valued verdicts from Deutsch-Jozsa interference:

- constant-1 oracle -> **1**
- constant-0 oracle -> **0**
- balanced oracle -> **REFUSED** (the circuit proves the answer space is split; no answer is claimed)

Design choices we care about scientifically:

- Statistical margins are declared per verdict (adaptive Hoeffding bound from a chosen epsilon), never tuned post hoc
- A GHZ-state "device-trust gate" measures processor coherence before any verdict is accepted (decohered device -> REFUSED_DEVICE_DECOHERED)
- Every run produces a sealed receipt (SHA3-256 + ML-DSA-44) binding verdict, job ID, backend and calibration snapshot, in a tamper-evident provenance chain
- Circuits are audited against statevector theory BEFORE hardware submission (we caught a real design bug in our CHSH circuit this way - the QPU executed it perfectly; the theory check exposed our error)

Hardware validation (IBM Heron: superconducting QPU, superconducting QPU, superconducting QPU; job IDs citable): GHZ fidelity 0.977; exact trivalent battery 9/9 at n=4/5/6; Bernstein-Vazirani secret recovery; Grover n=3/n=4 dominant; CHSH S=2.71; repetition-code correction of a single deterministic bit-flip (physical 99.3%) down to 1.5% logical.

The poliglota core agrees exactly across six SDKs (the Python quantum SDK, OpenQASM 3, Cirq, PennyLane, Braket, Q#).

Code (MIT): https://github.com/SerenaSolutions/zephirum-lang
Methodology + all job IDs: https://github.com/SerenaSolutions/zephirum-lang/discussions/35
DOI: 10.5281/zenodo.23302045

Would love feedback from this community on the trivalent semantics and the receipt-chain design."""
}

PENNYLANE = {
  "repo": "MDEwOlJlcG9zaXRvcnkxMjk5MzYzNjA=",
  "cat": "MDE4OkRpc2N1c3Npb25DYXRlZ29yeTMyNjQ3NjQ0",  # Q&A
  "title": "Methodology feedback: cross-validating a trivalent (1/0/REFUSED) Deutsch-Jozsa decision core across six SDKs - is our adaptive-margin approach sound?",
  "body": """Hi PennyLane community! We'd genuinely appreciate methodological feedback on a decision-layer design we've been validating, and PennyLane plays a direct role in the story.

We built **ZYQL** (core of the ZEPHIRUM language): it reads three-valued verdicts from Deutsch-Jozsa interference - **1** (constant-1 oracle), **0** (constant-0), **REFUSED** (balanced oracle; the circuit proves the split, no answer is claimed).

As a sanity check before hardware, we implemented the same trivalent battery in **six SDKs** - the Python quantum SDK, OpenQASM 3, Cirq, **PennyLane 0.45**, Braket and Q# - and all agree exactly, which was a very reassuring cross-check.

The design decisions we'd like feedback on:

1. **Adaptive margins**: verdict bands derive from an adaptive Hoeffding bound given a declared epsilon (band = sqrt(ln(2/eps)/(2S))): is this a sound way to declare shot-based confidence per verdict, or would you approach it differently?
2. **Device-trust gate**: a GHZ circuit measures state fidelity before any verdict is accepted (0.977 measured on superconducting QPU; below threshold -> REFUSED_DEVICE_DECOHERED): reasonable as a per-run coherence check?
3. Hardware results (three IBM Heron QPUs, job IDs citable): exact trivalent battery 9/9 at n=4/5/6; Bernstein-Vazirani secret recovery p=0.91; Grover n=4 target at p=0.54 vs runner-up 0.06; CHSH S=2.71 vs 2.83 theoretical (deficit consistent with the declared 2.02% mean readout error).

Every run is sealed with a receipt (SHA3-256 + ML-DSA-44) binding verdict + job ID + calibration snapshot.

Code (MIT): https://github.com/SerenaSolutions/zephirum-lang
Methodology post: https://github.com/SerenaSolutions/zephirum-lang/discussions/35

Would love to hear from this community: does the adaptive-margin approach hold up, and are there PennyLane-native tools (e.g., for shot-based confidence or device benchmarks) you'd recommend to strengthen the cross-validation?"""
}

def post(repo_id, cat_id, title, body):
    payload = {
      "query": "mutation($r:ID!,$c:ID!,$t:String!,$b:String!){ createDiscussion(input:{repositoryId:$r,categoryId:$c,title:$t,body:$b}){ discussion{ number url } } }",
      "variables": {"r": repo_id, "c": cat_id, "t": title, "b": body}
    }
    req = urllib.request.Request("https://api.github.com/graphql",
        data=json.dumps(payload).encode(),
        headers={"Authorization": f"token {T}", "Content-Type": "application/json"})
    d = json.load(urllib.request.urlopen(req))
    if "errors" in d:
        return "ERRO: " + str(d["errors"])[:200]
    disc = d["data"]["createDiscussion"]["discussion"]
    return f"OK: #{disc['number']} {disc['url']}"

for p in (MITIQ, QUTIP, PENNYLANE):
    print(p["title"][:40], "->", post(p["repo"], p["cat"], p["title"], p["body"]))

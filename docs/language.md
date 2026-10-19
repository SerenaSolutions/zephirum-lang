# Zephyron reference (v1.4.3)

Programs are `circuit NAME { ... }` blocks. Declarations:
`qubit[N] q;` registers; `zyqbit name = q[i];` first-class quantum values
(copying is a type error: no-cloning); `qif name { X target; }` branches
without collapse (controlled-X prototype).

Gates: H, X, Y, Z, S, T, RX(q, angle), RY, RZ, CNOT q[i] -> q[j], CZ,
SWAP, TOFFOLI. Angles accept `pi` and `pi/k`.

Neural: `zyql_rag "question";` runs docs -> BM25 -> translator -> gate -> receipt.
Transpilation: `src/oq3.py` emits and ingests OpenQASM 3 (round-trip verified).
Unknown lines raise; nothing executes silently.

## C API

`src/zephirum.h` declares the public C surface of the trivalent core:
one oracle call per decision, declared noise band, canonical rational
receipt (num/den) sealed with SHA3-256 (ML-DSA-44 signature: declared roadmap). Bindings and the language
frontends sit above this contract; nothing decides above the core.

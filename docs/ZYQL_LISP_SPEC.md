# ZYQL v2 — Lisp-style syntax (ZeptonQL core + quantum layer)

**Owner decision, 2026-10-21:** the ZEPHIRUM surface syntax moves from
Python-style statements to **Lisp s-expressions**. Rationale, declared honestly:

- **The core of ZF is NOT quantum.** The core is the *ZeptonQL* trivalent
  decision algorithm (1 / 0 / REFUSED) — a decision logic, best expressed as
  nested forms, not as scripts.
- Quantum execution (Grover, DJ, braiding) is an **optional layer**, expressed
  as explicit `(quantum ...)` forms. Highlighting should not pretend
  otherwise.
- s-expressions make rules, models and receipts homoiconic — decisions and
  their audit trail share one readable shape.

## Core forms (ZeptonQL — classical trivalent decision)

```lisp
;; trivalent decision: exactly one of 1, 0, REFUSED
(decide (model governance) (purpose "Is use x permitted?")
  (rule (oracle all-ones)    -> 1)
  (rule (oracle all-zeros)   -> 0)
  (rule (oracle balanced)    -> REFUSED))
```

## Quantum layer (optional, declared)

```lisp
(quantum dj6 (oracle f)
  (qubits 6)
  (circuit (h 0..5) (oracle f) (h 0..5))
  (measure (0 0 0 0 0 0) -> trivalent))

(quantum braid (anyons s3-qutrit)
  (word R S R S)          ; braid word — order matters (non-Abelian)
  (fusion-channels ch0 ch1 ch2)   ; |11> vetoed
  (verify commutator-L1 != 0))
```

## Receipts stay JSON (Z-QEA)

Source is Lisp; receipts remain sealed JSON (`selo_sha3_256`, SHA3-256).
Nothing about the seal protocol changes.

## Highlighting on GitHub

`*.zph` is mapped via `.gitattributes`:

```
*.zph linguist-language=Lisp
```

Lisp is the closest registered Linguist language to ZYQL v2. This is an
explicit, documented mapping (owner decision) — when Linguist registers
ZEPHIRUM, the mapping is dropped in favor of native highlighting.

## Photonic layer (dual-rail qubits, verified round 5)

```lisp
(photon-lab round5-fotonica
  (encoding dual-rail)                     ; |0_L>=|1,0>  |1_L>=|0,1>
  (test hom-bunching (expect p11 = 0))     ; two photons, 50:50 BS
  (test mzi-interference (expect deterministic-exit))
  (test trivalent const-0 (expect decision 0))
  (test trivalent const-1 (expect decision 1))
  (test trivalent balanced (expect decision REFUSED))
  (test braid-order (expect commutator != 0))
  (seal "experiments/round5_photonic_receipt.json"))
```

The interpreter is `src/zyql_lisp.py` — programs are .zph s-expressions and the
sealed Z-QEA receipt is emitted BY the language itself. Photonic Hadamard
(verified exact): BS50 . phase(pi/2 on rail 1) . BS50 = e^{-i pi/4} H — a
Mach-Zehnder with internal phase pi/2 IS the Hadamard.

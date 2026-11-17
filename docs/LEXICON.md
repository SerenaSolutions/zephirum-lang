# ZEPHIRUM LEXICON

Canonical names for the language. Five terms, each bound to a real artifact.
Everything else that was proposed as flavour is deliberately excluded: a
public technical document that borrows names from trademarked fiction ages
badly and has to be rewritten.

## 1. Teletransportador, the protocol

Quantum teleportation is not a metaphor here, it is the operation the receipt
attests. Measure in the Bell basis, send two classical bits, reconstruct the
state at the destination. The state is transported, not copied, because
no-cloning forbids a copy. Anything in ZEPHIRUM that claims to move a state
without consuming the original is not teleportation and must not use the name.

## 2. Katra, the no-cloning bound

The essence moves and is never duplicated: one state, one place. Two
consequences the language enforces rather than documents:

1. a receipt describes one execution, and the same execution cannot have two
   distinct receipts that both verify;
2. entanglement is monogamous, so a third party cannot hold the same correlation.

## 3. IDIC, the state space

n qubits, 2^n amplitudes, all combinations held at once. The name is used for
the space itself, never for a measurement outcome. If a sentence says "IDIC
returned 1", the sentence is wrong: what returns 1 is the Spark, over the IDIC.

## 4. Defletor, the error bound

The shield that absorbs error and lets the logical qubit survive. It drops when
error crosses the threshold, and that is the honest reading: the Defletor is a
declared error band, not a guarantee. A run without a declared band has no
Defletor and therefore no verdict.

## 5. Tradutor universal, the transpiler

Compiles the same intent to each machine's dialect, and like any translator it
can translate wrong. This is the only one of the five with a live defect
attached, see below.

# The Translator defect: canonical form is not pinned

Measured 2026-11-17. The same logical payload serializes to different bytes
depending on who escapes it, and the hashes diverge:

| serialization | bytes | SHA3-256 (first 16) |
|---|---|---|
| `\b` | `{"v":"a\bb"}` | `d596f6381c2dbaa2` |
| `\u0008` | `{"v":"a\u0008b"}` | `6bc64e1a412adce4` |

Both are valid JSON encodings of the same string. One receipt verifies, the
other does not. Python `json.dumps` and Node `JSON.stringify` agree with each
other (`\b`), so the drift comes from hand-rolled escaping in a port, not from
the languages.

The fix is not a convention, it is a standard plus vectors:

1. canonicalize per RFC 8785 (JSON Canonicalization Scheme);
2. keep `tests/vectors/canonical/*.json` with input, expected bytes and expected
   SHA3-256;
3. make every implementation (Python, Rust, JS) run the same vectors in CI.
   A port that disagrees with a vector fails the build, not the user.

# Excluded on purpose

Borrowed terms from Transformers and Star Trek lore beyond the five above:
AllSpark, Ravage, Teletraan, Vector Sigma, Primax, Energon, Stasis lock,
Sector 7, and the rest. Reasons, in order: trademark exposure on a public
project, and a lexicon that mixes two fictional universes reads as decoration
rather than specification.

# The principle that stays

A receipt that only its issuer can check is not a receipt, it is a chain.

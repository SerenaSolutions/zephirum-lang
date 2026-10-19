# ZYQL REFUSED — formal specification

Status: ESPECIFICAÇÃO FORMAL (behavior implemented across kernel, ZCA suite and portgate)
Date: 2026-10-19 (ISO 8601)

## 1. Semantics

`REFUSED` is a first-class verdict: ZYQL declines to decide. It is not an error
and not a failure; it is an explicit statement that confidence or contract
conditions were not met. A REFUSED decision NEVER consumes QPU resources and
never triggers execution of the refused program.

## 2. Triggers (exhaustive)

| # | Condition | Layer |
|---|---|---|
| R1 | measured p̂ inside the indifference band (δ < p̂ < 1−δ) | statistical (see ZYQL_STATISTICAL_PROTOCOL.md) |
| R2 | shots below the minimum n_min(α) for the declared band | statistical |
| R3 | unsupported syntax / unknown model type | parser/kernel (explicit error, labeled) |
| R4 | prohibited purpose class (portgate: weapons, lethality, surveillance, persecution, fraud, forgery, sabotage — PT/ES list v2) | portgate, BEFORE any compute |
| R5 | structural parse failure (missing blocks/fields) | parser |
| R6 | circuit/problem exceeds the declared classical budget (qubits, gates, expression size) | budget contract |

## 3. Cost model and DoS resistance

- R1–R2 are decided from a FIXED shot count; inputs cannot inflate QPU cost.
- R3–R5 are classical, polynomial-bounded (parse + safe constant folding, no
  loops, no recursion in the folder). Worst case is O(size of input).
- R6 caps classical work explicitly; the cap is part of the contract and the receipt.
- Therefore: no input can induce unbounded cost, QPU or classical. A REFUSED
  flood is bounded by the classical budget per request; rate limiting at the
  gate (not the kernel) remains the operator's responsibility and is declared here.

## 4. Receipt

Every REFUSED verdict carries a receipt with: trigger id (R1–R6), reason string,
band δ, n (if statistical), purpose hash (if portgate), and the SHA3-256
integrity seal. REFUSED receipts are chainable like any other receipt.

## 5. What REFUSED is NOT

- Not an error: errors (R3/R5) are labeled as errors inside the REFUSED family
  when they arise from input, and as kernel bugs when the kernel violates its
  own contract (the latter must NEVER be caught and presented as REFUSED).
- Not a fallback to execution: the kernel has no path from REFUSED to QPU.

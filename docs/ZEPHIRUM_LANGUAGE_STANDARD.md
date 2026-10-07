# ZEPHIRUM Language Standard
## Normative core, version 0.3 draft

> ASK FIRST. PROVE NEXT. COMPUTE LAST.

This document defines the language standard for ZEPHIRUM. It is normative for
source syntax, block structure, exact literal semantics, diagnostics and
conformance. It is not a book chapter and it does not promise self-hosting.

## 1. Language identity

ZEPHIRUM is a declarative language for questions about computation. A program
declares:

1. `ASK`: the question to decide.
2. `CONTRACT`: exactness and admissible error.
3. `MODEL`: the computational family and its data.
4. `BUDGET`: optional execution limits.
5. `REQUIRE`: optional preconditions.

A conforming implementation may answer without executing the original
computation, reduce it, execute a certified residual, refuse, or return
`UNKNOWN`. It must never turn an unproved hypothesis into a certified result.

## 2. Source encoding and lexical rules

A conforming implementation MUST:

1. Accept UTF-8 source.
2. Treat line feed as the canonical newline. CRLF MAY be accepted.
3. Ignore spaces and horizontal tabs outside literals.
4. Recognise block keywords only in uppercase: `ASK`, `CONTRACT`, `MODEL`,
   `BUDGET`, `REQUIRE`.
5. Recognise identifiers as `[A-Za-z_][A-Za-z0-9_]*`.
6. Recognise integers and decimal literals without converting decimals to
   binary floating point.
7. Reject illegal characters and unbalanced delimiters with a source location.

Reserved keywords MUST NOT be accepted as identifiers.

## 3. Canonical grammar

```ebnf
program     = { block } ;
block       = block_head, ":", newline, { statement } ;
block_head  = "ASK" | "CONTRACT" | "MODEL" | "BUDGET" | "REQUIRE" ;
statement   = identifier, ":", value, newline ;
identifier  = letter, { letter | digit | "_" } ;
value       = question | number | range | list | identifier | expression ;
question    = target, comparison, number ;
target      = "sum" | "mean" | "median" ;
comparison  = ">" | "<" | ">=" | "<=" | "==" ;
range       = number, "..", number ;
list        = number, { ",", number } ;
expression  = arithmetic expression over numeric literals ;
number      = integer | decimal ;
```

`ASK` is mandatory and may occur once. Other blocks are optional, but duplicate
blocks are rejected in the normative core. Unknown keys are rejected by a
strict conforming profile.

## 4. Exact numeric semantics

Decimal spelling is semantic data. The literal `0.1` means exactly one tenth.
Implementations MUST use an exact representation, such as rational numbers, for
parsing, comparison, certificate generation and verification.

The following must hold:

```text
0.1 + 0.2 == 3/10
0.1 * 10 == 1
```

An implementation MAY use floating point for display or an explicitly marked
non-certifying backend, but a floating result MUST NOT overwrite an exact
certified result. A backend disagreement is a refusal or `MISMATCH`.

Division by zero is a language or VM fault. Infinity and NaN are not valid
certified numeric results in the normative core.

## 5. Program meaning

The source program is parsed into a block IR. The IR is compiled into a
necessity decision. The language does not define a general-purpose imperative
runtime in this version. It defines the declarative question and contract that
feed the ZCA.

The implementation must preserve:

1. The question and comparison operator.
2. The declared model and its parameters.
3. The exact numeric meaning of literals.
4. The declared assumptions and bounds.
5. The distinction between result, refusal and `UNKNOWN`.

## 6. Standard result states

A conforming compiler or runtime reports one of these states:

```text
DECIDED_WITHOUT_EXECUTION
DECIDED_BY_REDUCTION
RESIDUAL_COMPUTATION_REQUIRED
FULL_EXECUTION_REQUIRED
UNKNOWN
REFUSED
```

`UNKNOWN` is a valid result, not an exception. `REFUSED` means that the
contract, model, backend, certificate or accounting requirements were not met.
Every refusal must include a machine-readable reason.

## 7. Certificates and verification

A certified result MUST include, at minimum:

```text
INPUT_HASH
QUESTION
CONTRACT
MODEL
KERNEL
RUNG
METHOD
EVIDENCE
ELIMINATION_TRACE
STATUS
ANSWER
CERT_HASH
```

The verifier MUST be independently callable from the generator. It MUST
rederive relevant evidence from the original input and MUST reject altered
values, invalid assumptions, mismatched hashes and unsupported model claims.
SHA-256 seals canonical integrity. It does not authenticate the issuer. An
issuer signature and trust registry are separate mechanisms.

## 8. Versioning and compatibility

The language standard uses `MAJOR.MINOR` versions.

1. A patch release fixes implementation defects without changing accepted
   meaning.
2. A minor release may add syntax or model families without changing the
   meaning of valid existing programs.
3. A major release may change grammar or semantics and requires a migration
   specification.

The compiler MUST expose its language version and MUST reject a future major
version rather than silently guessing.

## 9. Conformance suite

A conforming implementation MUST pass tests for:

1. Valid block parsing.
2. Duplicate and missing block rejection.
3. Exact decimal arithmetic.
4. All comparison operators.
5. Range and list syntax.
6. Invalid-character and delimiter diagnostics.
7. Certificate tampering rejection.
8. Budget enforcement.
9. Deterministic result and certificate hashes.
10. Honest `UNKNOWN` and `REFUSED` delivery.

The current Python implementation is the reference implementation. It is not
therefore the only valid implementation. A future Rust or C verifier must read
the same canonical certificate and independently reproduce its acceptance or
rejection decision.

## 10. Non-goals of version 0.3

This standard does not claim:

1. Full self-hosting.
2. A VM implemented in ZEPHIRUM.
3. A standard library.
4. A package manager.
5. Physical QPU execution.
6. A proof of novelty over all prior systems.

Those are separate engineering or research phases. The standard records what
exists and defines the boundary of what does not.

## 11. Trilha de evolução inspirada no início do Python

Python não começou como um sistema plenamente auto-hospedado. A linguagem foi
primeiro especificada e implementada por um hospedeiro, com um interpretador de
referência em C. A estabilidade veio por etapas: sintaxe, semântica, testes,
bytecode, biblioteca, documentação e implementações alternativas.

ZEPHIRUM segue a mesma ordem, adaptada ao seu objectivo:

| Degrau | Python histórico | ZEPHIRUM |
|---|---|---|
| 1 | ideia e sintaxe | pergunta antes da execução |
| 2 | lexer/parser | lexer próprio e parser de blocos |
| 3 | interpretador hospedeiro | referência em Python |
| 4 | semântica executável | IR, ZCA, certificados e estados 0/1/Z |
| 5 | regressão e biblioteca | baterias de soundness, exactidão e VM |
| 6 | bytecode | ISA e VM orçamentada |
| 7 | documentação estável | este padrão normativo e suíte de conformidade |
| 8 | implementações alternativas | verificador independente em Rust ou C |
| 9 | maturidade do ecossistema | ferramentas, pacotes e biblioteca padrão |

A conclusão é importante: o hospedeiro em Python não é uma falha de origem. É o
primeiro degrau normal de uma linguagem. O marco de independência relevante vem
quando outra implementação consegue ler a especificação e verificar os mesmos
certificados sem reutilizar o motor Python.

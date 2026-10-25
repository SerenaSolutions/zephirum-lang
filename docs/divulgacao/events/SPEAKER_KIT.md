# Kit de palestra/paper ZYQL (pronto para CFPs)

## Titulos
- "Trivalent Quantum Decisions: 1, 0, REFUSED - and receipts that prove them"
- "ZYQL: reading exact decisions from Deutsch-Jozsa interference on noisy hardware"
- (PT) "Decisoes quanticas trivalentes: o hardware decide, o recibo prova"

## Abstract (200 palavras, EN)
Most quantum algorithms answer probabilistically; ZYQL turns Deutsch-Jozsa
interference into an exact three-valued decision: 1 (constant-1 oracle), 0
(constant-0), or REFUSED (balanced - the circuit proves the answer space is
split; no answer is claimed). Statistical margins derive from an adaptive
Hoeffding bound on a declared epsilon, never tuned post hoc. Before any
verdict is accepted, a GHZ-state device-trust gate interrogates the processor's
coherence; decohered devices are refused (REFUSED_DEVICE_DECOHERED). Every run
seals a receipt (SHA3-256 + ML-DSA-44/FIPS 204) binding verdict, hardware job
ID and calibration snapshot in a tamper-evident chain. The core is validated
on three IBM Heron QPUs (superconducting QPU, superconducting QPU, superconducting QPU) with citable
job IDs: exact trivalent battery 9/9 at n=4/5/6, GHZ fidelity 0.977, CHSH
S=2.71, Bernstein-Vazirani secret recovery, Grover n=4 target detection, and
repetition-code correction of a single deterministic bit-flip (measured
physical error 99.3%, the one-qubit error class this code is designed to
correct) down to 1.5% logical error. The same battery agrees exactly across six SDKs (the Python quantum SDK,
OpenQASM 3, Cirq, PennyLane, Braket, Q#). REFUSED is not failure: it is the
honest verdict of a circuit that can prove what it knows.

## Bio curta (EN)
Ravimah Anjo (SerenaSolutions) - creator of ZEPHIRUM/ZYQL, a trivalent quantum
decision language with cryptographic provenance, validated on real QPU provider
hardware. MIT-licensed, DOI 10.5281/zenodo.23302045.

## Pitch 60 segundos (PT)
Toda computacao quantica hoje responde com probabilidades. Nos transformamos a
interferencia Deutsch-Jozsa em decisao exata trivalente: 1, 0 ou RECUSADO. A
margem estatistica e declarada antes do teste, a porta GHZ desconfia do
proprio processador antes de aceitar veredito, e cada decisao vem selada com
recibo criptografico pos-quantico. Tudo validado em tres processadores IBM
Heron com job IDs citaveis - inclusive codigo de repeticao corrigindo um bit-flip deterministico (erro fisico medido 99,3%) para 1,5% logico.

## Links de apoio
- Repo: https://github.com/SerenaSolutions/zephirum-lang
- Provas e job IDs: https://github.com/SerenaSolutions/zephirum-lang/discussions/35
- DOI: 10.5281/zenodo.23302045
- RFC metodologia (cutucada aberta): https://github.com/SerenaSolutions/zephirum-lang/issues/36
- Draft paper: docs/preprint/ZYQL_TRIVALENT_DECISION.md

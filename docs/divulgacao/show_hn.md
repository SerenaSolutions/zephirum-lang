# Show HN — Rascunho (publicar em https://news.ycombinator.com/submit)

**Título (Show HN):**
Show HN: Zephirum – a Lisp-style quantum language with a trivalent decision core

**URL:**
https://github.com/SerenaSolutions/zephirum-lang

**Primeiro comentário (colar como comentário do autor):**

Hi HN, we built Zephirum because we kept hitting a wall most quantum languages pretend isn't there: binary languages can't refuse.

Every mainstream stack returns 0 or 1 from a computation. But real hardware is noisy, and the honest answer to "is this result reliable?" is often neither yes nor no — it's "I refuse to decide". So the ZYQL decision core is trivalent: every decision returns 1 (permitted), 0 (forbidden), or REFUSED (insufficient statistical confidence). Refusal is a first-class value, not an exception.

What's in the repo:

1. A Lisp-style language (.zph) with a trivalent core — the quantum layer (OpenQASM 3) is optional; the decision logic runs classically too
2. Cross-language validation: the same Deutsch–Jozsa battery agrees exactly across the Python quantum SDK, OpenQASM 3, Cirq, PennyLane and Braket
3. Real-hardware receipts: every experiment round is sealed in a two-layer receipt — SHA3-256 plus an ML-DSA-44 (FIPS 204) post-quantum signature — with entropy sourced from IBM quantum measurements
4. The statistical protocol is documented with raw data: we validated the trivalent verdict on IBM Heron processors across 64–16384 shots, 100% accuracy at every level, zero spurious refusals (theory predicted the threshold near 29–82 shots; we measured exact verdicts down to 64)

Honest notes: we run on IBM's open plan as an independent test lab — no institutional endorsement implied. The receipts are self-verifiable (public key embedded); a strict-pq mode rejects any receipt without the post-quantum layer.

We'd love feedback on the trivalent idea, the receipt format, and where you'd want this to go next. The statistical protocol with all job IDs and raw counts is in docs/ZYQL_STATISTICAL_PROTOCOL.md.

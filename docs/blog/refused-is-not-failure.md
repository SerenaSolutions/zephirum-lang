# Why REFUSED is not failure

Boolean systems hide their uncertainty: a classifier under low confidence still returns 0 or 1,
and the error surfaces downstream, where nobody can trace it. In ZEPHIRUM/ZYQL, the third verdict
exists so the uncertainty is *returned* instead of hidden.

A REFUSED verdict means: the interference pattern did not reach statistical dominance, and the
decision core refuses to lie about it. In our Deutsch-Jozsa battery, the balanced oracle produces
exactly this: no dominant amplitude, so the core says REFUSED.

Hardware made this concrete. On IBM Heron processors we ran the trivalent battery from 64 to
16384 shots ([protocol](../ZYQL_STATISTICAL_PROTOCOL.md)): exact verdicts at every level, and the
theory-predicted threshold (~29-82 shots for n=3) held with zero spurious refusals. Refusal has
a *measured* boundary, which is what makes it engineering rather than a safety blanket.

Fail-closed systems already understand this: unknown means deny. ZYQL gives that principle a
first-class value that flows through programs, receipts and audits.

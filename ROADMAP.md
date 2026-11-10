# Roadmap

This roadmap describes the direction of ZEPHIRUM and ZYQL. It is an ordered
set of priorities, not a promise of dates. Evidence, reproducibility, and the
ability to refuse an unsupported conclusion remain release gates.

## Current priorities

- Keep the trivalent contract stable: `1` (permitted), `0` (forbidden), and
  `REFUSED` (insufficient or ambiguous evidence).
- Expand conformance tests and receipt verification across the language, runtime,
  CI action, and supported integrations.
- Improve reproducibility documentation so every published result states whether
  it came from simulation or hardware and includes the evidence needed to audit
  it.
- Maintain dependable packaging, examples, CI coverage, and security hygiene.

## Next

- Publish a clearer language and receipt specification with executable examples.
- Add regression suites for parser, runtime, statistical decision gates, and
  receipt integrity.
- Improve developer ergonomics for local development, CI use, and independent
  verification of published experiments.
- Document integration boundaries for quantum backends without presenting an
  integration as evidence of a hardware result.

## Later

- Formalize more of the public semantics and conformance model.
- Strengthen independent verification workflows for experiments and releases.
- Grow contributor and reviewer documentation around reproducible research,
  security, and technical governance.
- Evaluate ecosystem and community programs, including a CNCF Sandbox
  application, only when the project documentation and governance are ready.

## Release gates

A milestone is complete only when its behavior is covered by reproducible tests,
its documentation matches the implementation, and new claims carry auditable
evidence. Unsupported certainty is never a roadmap shortcut: `REFUSED` remains
a valid and expected result.

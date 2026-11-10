# Maintainers

## Primary maintainer

**SerenaSolutions** is the primary maintainer of ZEPHIRUM and ZYQL. The
maintainer is responsible for release decisions, repository administration,
security coordination, and protecting the project's evidence-first contract.

## Decision principles

- Evidence comes before velocity. Changes should include a reproducible test,
  receipt, or other falsifiable evidence when applicable.
- `1`, `0`, and `REFUSED` are part of the public semantic contract. A change
  that alters verdict semantics requires explicit maintainer approval and a
  documented migration path.
- Hardware results must identify the execution context and job evidence.
  Simulation must be labeled as simulation.
- Security and integrity concerns take priority over feature delivery.

## Contributions and review

Contributors should open an issue or discussion for substantial changes and
submit a pull request with focused scope, tests, and updated documentation.
Review evaluates the evidence and the reproducibility of the change, not only
its implementation style. See [CONTRIBUTING.md](CONTRIBUTING.md) for the
workflow and [GOVERNANCE.md](GOVERNANCE.md) for project rules.

## Maintainer changes

Changes to this file, the governance model, release policy, or the public
verdict contract require review by the primary maintainer. New maintainers may
be added after sustained, evidence-based contributions and explicit approval.

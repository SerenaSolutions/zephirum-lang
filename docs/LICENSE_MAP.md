# LICENSE_MAP — authoritative source per artifact

Founder rule (2026-11-27): what prevails is what the core, the DOI and PyPI state.
Audited against live records, not against documentation.

| Artifact | Authoritative source | License | Verified |
|---|---|---|---|
| ZEPHIRUM/ZYQL language + runtime (this repo) | Zenodo DOI 10.5281/zenodo.24250453 (software record v2.5.10, 2026-11-15) | Apache-2.0 | yes |
| PyPI package `zephirum` 2.5.9 | PyPI JSON `license_expression` | Apache-2.0 | yes |
| Repository `LICENSE` + `pyproject.toml` | this repo | Apache-2.0 | yes |
| Isthmus package | PyPI `isthmus` 1.0.3 | Apache-2.0 | yes |
| Isthmus preprint | Zenodo DOI 10.5281/zenodo.24339929 | CC-BY-4.0 | yes |
| Historical deposit v1.1.0 | Zenodo DOI 10.5281/zenodo.23302046 (2026-10-11) | MIT | immutable, superseded |

## Resolution

Apache-2.0 prevails for the ZEPHIRUM language and runtime. All current sources agree:
the software DOI, PyPI metadata, the repository LICENSE and `pyproject.toml`.

The MIT record 10.5281/zenodo.23302046 covers the v1.1.0 deposit from 2026-10-11 and is
immutable; it is historical, not current. No action is possible or needed on it.

The house hybrid rule (BSL 1.1 on the commercial core, MIT elsewhere) applies to the
commercial core paths `c-api/` and `plugin/`, which are not present in this repository.
There is therefore no in-repository conflict. If the commercial core returns to this
repository, it must arrive with its own BSL 1.1 LICENSE and a documented boundary.

## Open gap

`pyproject.toml` declares `license = "Apache-2.0"` but the package ships no
`License :: OSI Approved :: Apache Software License` classifier. Adding it requires a
release; tracked as a follow-up, not a blocker.

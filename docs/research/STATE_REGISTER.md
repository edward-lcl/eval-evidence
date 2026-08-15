# Repository state register

Snapshot date: 2026-08-15

Code authority inspected: `main` at `e27d55cfe948920220eebc356ef3059d3a4ff0d8`

Working branch: `codex/adversarial-research`

This register separates evidence classes. It is not a release declaration and does not
upgrade private or historical observations into reproducible proof.

| State | Statement | Evidence | Consequence |
|---|---|---|---|
| Verified fact | Local `main` and `origin/main` resolved to `e27d55cfe948920220eebc356ef3059d3a4ff0d8` before this research branch was created. | `git rev-parse main origin/main`; branch creation receipt | The snapshot above is the baseline for this review. |
| CI-backed evidence | GitHub Actions run `31907453803` passed for that baseline on Python 3.11-3.14 and the Ubuntu/macOS/Windows distribution jobs. | GitHub Actions run and job conclusions | The checked-in tests and packaging workflow passed on the advertised matrix; this does not validate untested semantics. |
| Verified fact | The local baseline suite passes 42 tests and skips the real-Harbor gate test. | `python -m unittest discover -s tests -v` | The existing suite is green, but G2 is not exercised. |
| Verified fact | The generic quickstart can create, check, bundle, and verify its synthetic run. | Locally reproduced CLI sequence | The synthetic path works; it is a demo, not real-data validation. |
| Verified fact | The latest public GitHub release and tag is `v0.1.0`, while package metadata and `eval_evidence.__version__` identify mutable development code as `0.2.0`. | `gh release list`, `git tag`, `pyproject.toml`, `eval_evidence/__init__.py` | Release identity is ambiguous until development builds and a frozen release are distinguished. |
| Verified fact | Published schema `$id` values resolve through mutable `main`. | `eval_evidence/schemas/*.json` | A wire document identity can change without its `$id` changing. |
| Local test-backed evidence | G1-G4 are met by non-skipping named tests on this working branch; the separate private-archive test remains optional and skips without external input. | `docs/READINESS.md`; local readiness-suite receipt | Current technical gates pass locally. This branch becomes CI-backed only after the canonical commit's Actions run passes; neither state is release or upstream-adoption authorization. |
| CI-backed evidence | Generic archive tamper detection, deterministic bundles, schema checks, package audits, and the composite-action smoke path are exercised in regular CI. | `.github/workflows/ci.yml`; tests | These behaviors have repeatable public automation. |
| Local-only evidence | Seven private Harbor trials reportedly passed adapter dogfooding during the v0.2 readiness review. | PR #2 description and readiness artifacts; source archive is not public CI input | Useful historical evidence, but not independently reproducible from this repository. |
| Local test-backed evidence | A checked-in two-trial fixture preserves the genuine Harbor directory/key structure with all scalar values replaced; it adds an explicitly synthetic conflict/error case. | `tests.test_readiness.ReadinessTests.test_sanitized_harbor_structural_fixture`; local readiness-suite receipt | G2 is met locally for public structural coverage, not representative real values or all Harbor layouts. The canonical commit still needs its Actions receipt. |
| Known gap | Discovery requires `result.json`, `config.json`, and an ATIF trajectory, so incomplete and non-ATIF attempts can be omitted before reporting. | `HarborAdapter.required` and `discover` | Trial counts from adapter discovery are not campaign denominators. |
| Known gap | The bundle is trial-scoped and does not encode expected attempts, exclusions, retries, supersession, regrades, or aggregation. | Bundle schema and blind-spot register | A complete set of selected trial bundles can still support a misleading campaign claim. |
| Known gap | `available_fraction` weights every instrument field equally. | `_instrument_manifest`; bundle schema | It is a coarse diagnostic, not a trust or claim-readiness score. |
| Hypothesis | A portable evidence envelope makes evaluation claims more independently interpretable and falsifiable after execution. | Research thesis; not established by the demo | Must be tested against real archives, conflicts, another evaluator, and prospective capture cost. |
| Counter-hypothesis | Campaign denominators and native harness capture dominate trial-level sealing, making most of this package redundant. | Current blind spots and likely upstream overlap | A successful outcome may be a smaller contract or upstream primitives rather than a standalone package. |
| Counter-hypothesis | Retrospective evidence reconstruction is too incomplete or ambiguous to justify a generic envelope. | Private review gaps and unresolved source semantics | Recoverability and conflict studies must precede broad portability claims. |

## Immediate semantic findings to reproduce

The adversarial suite reproduced and resolved four semantic defects plus release
identity drift:

1. Partial or contradictory generic provenance now fails closed.
2. Harbor model/provider, agent, task, revision, and metric disagreements now remain
   visible as structured source conflicts instead of precedence winners.
3. Absent Harbor list keys now remain unavailable unless the lists were serialized.
   Current upstream intentionally omits defaults, but historical producer identity is
   not retained strongly enough for the adapter to apply that default safely.
4. `verify` now recomputes all coverage metadata from the actual fields.
5. Development code identifies as `0.2.0rc1`; final `0.2.0` remains reserved, and
   schema `$id` values are immutable versioned URNs rather than mutable `main` URLs.

Named regression evidence is in `tests/test_adversarial_semantics.py`. The upstream
source snapshots used for current behavior review are recorded in `RESEARCH_MAP.md`
and `UPSTREAM_MAP.md`.

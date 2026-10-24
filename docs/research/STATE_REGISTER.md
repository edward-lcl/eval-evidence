# Repository state register

Snapshot date: 2026-08-15 (claim reconstruction rows added 2026-08-16)

Label note: rows labelled **Study evidence (public artifacts)** were reproduced from
public third-party artifacts by two independent reviewers during the 2026-08-16 claim
reconstruction study. They are not reproducible from this repository — no committed
script or test rebuilds them — so they rank below `Verified fact` and `CI-backed
evidence` in this register. `EE-08` would make the TB2.0 case reproducible from a
committed script.

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

## Additions from the claim reconstruction study (2026-08-16)

Code authority inspected for these rows: `main` at
`6d4a25b5f288f9646f30e0d1c9f5923cc6c1ec8c`; Harbor at
`a27e9c2ae10a31c40b2dcef33ef5486bce36e185`. Receipts: [`CLAIM_RECONSTRUCTION.md`](CLAIM_RECONSTRUCTION.md)
and [`claim-reconstruction/`](claim-reconstruction/README.md).

| State | Statement | Evidence | Consequence |
|---|---|---|---|
| Verified fact | Harbor deletes a failed attempt's trial directory before retrying it and deletes result-less trial directories on resume; only `stats.n_retries` survives. Default `max_retries` is 0. | `src/harbor/trial/queue.py:222`, `src/harbor/job.py:252-260` at `a27e9c2` and `origin/main` `f03db62`; commit `080a1cb30` (2026-05-17) | Attempt-level retry lineage is retrospectively unrecoverable by construction; a tombstone is prospective-only. No public incident of harm found (hypothetical). |
| Verified fact | Harbor's job-level `mean` counts errored/cancelled trials as reward 0 in the denominator; the policy is in code, not in any artifact field. | `src/harbor/metrics/base.py`, `src/harbor/job.py:940-944`; a genuine errored oracle job reports `mean 0.0` with `evals.n_trials 0` | Aggregate rules must be declared next to the number; reading Harbor's code at a pinned commit is the only retrospective route. |
| Local-only evidence | On 17 genuine Harbor 0.16.1 oracle jobs the Harbor adapter discovers 0/17 trials (no ATIF trajectory) while `harbor.version` is present in 17/17 job locks that the adapter never reads. | `HarborAdapter.required` (`adapters.py:378`); `grep lock.json eval_evidence/adapters.py` → 0 hits (both independently checkable in this repository); key/count inspection of private job dirs (not public CI input) | Adapter discovery is not a denominator on real data; `harness_version` is natively available and reported unavailable. Fix candidates recorded in study §F; not applied here. |
| Study evidence (public artifacts) | The TB2.0 rank-1 row (84.7% ± 2.1) reproduces to ~1e-15 as a mean of per-task success rates over 443 counted trials with two never-verified trials dropped, ± = 1.96 × a within-task SE; Harbor's own job `mean` gives 84.49%. The rule was recovered by matching, not read; the importer code is not public. 63/142 rows count < 445 trials; 21 merged submission folders are not displayed. | Study §A1, §E; lane L2 with saved public payloads; critic C1/C2 re-derivation | Per-trial evidence is public and sufficient; the row-level rule and exclusion predicate are the missing record. |
| Study evidence (public artifacts) | The SWE-bench Verified rank-1 row (79.20%) re-derives to 396/500 from per-instance logs, but drifts to 79.4% under the current unpinned dataset revision; harness version and image digest are unavailable; 47/180 rows take their number from a hand-typed field; a merged 77.6% row is silently absent from the page. | Lane L3; critic C1 spot-checks | Pins and an expected-set (merged == displayed) check are the missing artifacts; sealing is not. |
| Study evidence (public artifacts) | The HF Open LLM Leaderboard row reproduces to the last float digit from the fourth of four results files, while the displayed model sha is the first file's and stderr/group fields are stale after two in-place rescorings. | Lane L4; critic C1 re-fetch | Mixed provenance inside one record is the class where per-field source pointers matter and a coverage fraction misleads. |
| Known gap | No surveyed provenance, tracking, attestation, or eval-log standard represents a per-field `unavailable` state or an unresolved two-source conflict; Inspect AI carries per-sample invalidation with author/reason/timestamp; PROV-DM carries every needed relation. | Lane L6 (PROV-DM REC 2013; Inspect `7b17bdfe`; EEE, in-toto, MLPerf, RO-Crate) | The evidence-state vocabulary is the one novel portable piece; the lineage vocabulary and exclusion-record shape should be borrowed. |
| Hypothesis (downgraded) | "Claim lineage" is a distinct fourth layer above campaign lineage. | Study §B, §H; lane L8 | Not supported: every proposed field maps to a PROV node/edge/attribute; layers 2 and 3 merge into campaign provenance; layer 4 is argumentation. |
| Hypothesis (open) | A per-row publication record with an expected-set check is sufficient retrospectively for the TB2.0 rows. | Study §G item 2 (public retro-fit not yet run) | Decides whether the missing artifact is cheap or must be captured prospectively. |

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

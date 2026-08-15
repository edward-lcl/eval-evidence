# External-sharing readiness

These are release gates, not aspirations. A gate is a falsifiable claim tied to an
executable test. `met` means the repository currently carries passing evidence;
`unmet` remains deliberately visible until its external prerequisite is supplied.
The same states are exposed to agents and tooling in
[`PROJECT_HANDOFF.json`](../PROJECT_HANDOFF.json). If the two disagree, treat the
optimistic state as invalid and correct both artifacts with the named executable
evidence.

| gate | claim | test | status(met/unmet) |
|---|---|---|---|
| G1 — CLI path | The `demo` → `check` → `bundle` → `verify --run-root` sequence succeeds from the current source tree for both synthetic input formats. | `tests.test_product.ProductTests.test_cli_quickstart_both_formats` | met |
| G2 — Harbor structural evidence | A sanitized, genuine-layout multi-trial Harbor fixture with absent optional files, an errored trial, two ATIF versions, omitted defaults, and conflicting retained sources loads and verifies in regular CI. | `tests.test_readiness.ReadinessTests.test_sanitized_harbor_structural_fixture` | met |
| G3 — release drift | An unknown Harbor trajectory schema version produces a visible compatibility warning without invalidating an otherwise valid run. | `tests.test_product.ProductTests.test_unknown_harbor_trajectory_version_warns_without_failing` | met |
| G4 — tamper boundary | Changing covered bundle claims without recomputing the digest is detected as a bundle digest mismatch. | `tests.test_product.ProductTests.test_bundle_tamper_matrix` | met |

A 2026-07-28 genuine-data run passed locally and its field-level review was completed.
G2 now has a checked-in sanitized structural fixture derived from that genuine layout.
All scalar values and trajectory content were replaced, and a separately identified
adversarial conflict case was added. The former blocker and private evidence remain at
`artifacts/g2-blocker.md` and `artifacts/harbor-readiness-redacted.txt` as historical
records, not current gate state.
A clean-wheel build, audit, installed-CLI dogfood, and tamper session is likewise retained
at `artifacts/clean-wheel-session.txt`. Linux, macOS, and Windows distribution jobs
passed for pull request #2 after CI exposed and the branch fixed platform-dependent
demo newlines. These workspace evidence records are intentionally excluded from
distributions.

## Mapping-review milestone: ready to show the Terminal-Bench team

A maintainer review is still needed to challenge G2's fixture fidelity and mapping. The
candidate is ready for a narrow mapping and fixture review while all four gates remain
met, cross-platform clean-wheel jobs pass, genuine local results are
reported separately from reproducible CI evidence; and known unsupported Harbor
layouts are visible. Those conditions are now satisfied. The focused entry point is
[`TBENCH_REVIEW.md`](TBENCH_REVIEW.md).

## Adoption/release-endorsement milestone

Before asking Terminal-Bench/Harbor maintainers to endorse or depend on the adapter, G2
must remain `met`. Run the protocol in [`DOGFOOD.md`](DOGFOOD.md), inspect coverage and
unavailable values against source JSON, and retain only an approved redacted
transcript—not benchmark data. Regular CI must keep the sanitized structural fixture
free of restricted content and run the named gate test without a skip. The pass
criterion is: a new user following the README can produce and verify a bundle from a
real Harbor job in under five minutes without undocumented corrections.

Current multi-step `step_results`, regrade lineage, and job-level denominators/retries
are outside the validated Harbor surface. They must be mapped and tested, or explicitly
excluded from the first supported compatibility
statement, before broader Harbor adoption.

## Wider-use milestone

After the Terminal-Bench review, wider use additionally requires:

- a published compatibility/deprecation policy and changelog (now present);
- confirmed PyPI trusted publishing before changing the install command;
- one external harness author successfully emitting `eval-run.json` from the docs alone;
- one paired, real-run comparison classified with the decision record in
  `OWNER_WALKTHROUGH.md`, including explicit evidence gaps rather than an inferred
  model-quality verdict (completed locally; redacted source-checkout record at
  `artifacts/real-comparison-redacted.md`);
- archive scale measurements within the bounds in `COMPATIBILITY.md` (completed
  locally on 8,633 genuine Harbor runs; redacted source-checkout record at
  `artifacts/scale-measurement.txt`);
- a documented support and release path through `CONTRIBUTING.md`.

The local comparison classified a genuine three-group baseline as not comparable after
finding task-checksum, denominator, and turn-budget drift; it did not rank the models.
The PyPI and external-emitter items remain unmet. Do not describe this repository as
generally available until they have evidence.

## Explicit non-goals

Neither gate requires signing or attestation, additional built-in adapters, plugin
loading, or a hosted service. Those omissions keep this review about post-run content
integrity, provenance, and adapter correctness.

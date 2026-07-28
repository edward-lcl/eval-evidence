# External-sharing readiness

These are release gates, not aspirations. A gate is a falsifiable claim tied to an
executable test. `met` means the repository currently carries passing evidence;
`unmet` remains deliberately visible until its external prerequisite is supplied.

| gate | claim | test | status(met/unmet) |
|---|---|---|---|
| G1 — CLI path | The `demo` → `check` → `bundle` → `verify --run-root` sequence succeeds from the current source tree for both synthetic input formats. | `tests.test_product.ProductTests.test_cli_quickstart_both_formats` | met |
| G2 — real Harbor evidence | A genuine multi-trial Harbor job, including a trial with absent optional files, loads and verifies without synthetic assumptions. | `tests.test_readiness.ReadinessTests.test_real_harbor_archive_when_supplied` | unmet |
| G3 — release drift | An unknown Harbor trajectory schema version produces a visible compatibility warning without invalidating an otherwise valid run. | `tests.test_product.ProductTests.test_unknown_harbor_trajectory_version_warns_without_failing` | met |
| G4 — tamper boundary | Changing covered bundle claims without recomputing the digest is detected as a bundle digest mismatch. | `tests.test_product.ProductTests.test_bundle_tamper_matrix` | met |

A 2026-07-28 genuine-data run passed locally and its field-level review was completed.
G2 remains unmet because regular CI still lacks an approved sanitized fixture or secure
fixture access. A source-checkout-only record is retained at `artifacts/g2-blocker.md`.
A clean-wheel build, audit, installed-CLI dogfood, and tamper session is likewise retained
at `artifacts/clean-wheel-session.txt`; it does not replace the required cross-platform
CI run. These workspace evidence records are intentionally excluded from distributions.

## Sharing milestone: ready to show the Terminal-Bench team

G1 and G4 must remain met, G2 must move to met, and the cross-platform `distribution`
job must pass its clean-wheel `scripts/dogfood.sh` run. Run the G2 protocol in
[`DOGFOOD.md`](DOGFOOD.md), inspect coverage and unavailable values against the source
JSON, and retain only an approved redacted transcript—not benchmark data. Before G2 is
changed to `met`, regular CI must receive an approved sanitized structural fixture or
secure fixture access so the named test runs without a skip. The owner should also
complete the real-run and tamper sessions in
[`OWNER_WALKTHROUGH.md`](OWNER_WALKTHROUGH.md). The pass criterion is: a new user
following the README can produce and verify a bundle from a real Harbor job in under
five minutes without undocumented corrections. Source-tree G1 alone does not establish
that install/distribution criterion.

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

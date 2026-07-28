# Terminal-Bench / Harbor review brief

## What this adds

Eval Evidence is an offline post-run layer. It reads an existing Harbor trial, records
instrument fields with explicit provenance and unavailable state, hashes the source
artifacts, and emits a deterministic schema-validated bundle. It does not require a
runner change and gives CI/reviewers one `check` command for content integrity,
coverage, and Harbor-version drift.

## What it does not claim

A digest is not a trusted-runner signature; a reward is not ground truth; configured
network policy is not proof of enforcement. The tool neither executes a model nor
copies trajectories into a bundle. Signing, hosted services, plugin loading, and new
adapters are explicitly outside this review. See `TRUST_MODEL.md` for the complete
boundary.

## Evidence to review

The steps below require Eval Evidence 0.2.0 or a current `main` checkout; the older
`v0.1.0` tag does not include the review commands or compatibility warnings.

1. Follow the README path on a genuine multi-trial Harbor job.
2. Red-line `HARBOR_MAPPING.md`, especially agent timeout, cache-token,
   exception/termination, and ATIF `steps` mappings.
3. Check that unavailable values correspond to genuinely absent source evidence.
4. Change a referenced file and confirm `verify --run-root` names it.
5. Try an unknown trajectory schema version and confirm `check` warns without failing.
6. Use the paired-result decision record in `OWNER_WALKTHROUGH.md` on one surprising
   comparison; classify integrity, comparability, and missing-evidence findings without
   converting them into an unsupported model-quality verdict.

The current readiness table intentionally marks real-Harbor validation unmet because
only synthetic fixtures are available in this repository.

## Specific ask

Please review/correct the Harbor field mapping and provide a redacted structural
fixture for regression tests. If the mapping is acceptable, consider having Harbor
emit the framework-neutral `eval-run.json` contract natively. Native emission would
make the heuristic Harbor adapter optional while preserving the same bundle and
verification path.

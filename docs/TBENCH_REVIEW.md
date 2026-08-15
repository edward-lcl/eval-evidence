# Terminal-Bench / Harbor review brief

## The five-minute version

Eval Evidence is a post-run evidence envelope and integrity checker. It reads existing
Harbor trial artifacts, records where normalized fields came from (or that they are
unavailable), hashes the referenced bytes, and emits a deterministic JSON bundle.
Later verification can detect whether those covered bytes differ from the baseline.

It does **not** determine whether a Terminal-Bench task is broken, whether a verifier is
correct, or whether one agent/model is better. It carries supplied item-validity and
verifier claims without upgrading them into facts.

This complements rather than replaces Harbor:

| Harbor capability | Eval Evidence boundary |
|---|---|
| Run tasks and agents | Never executes models, tasks, or verifiers |
| `harbor view` job/trial exploration and comparison | Portable per-trial JSON for offline integrity and provenance checks |
| `result.json`, `config.json`, ATIF, verifier outputs | Normalized cross-framework envelope plus hashes of selected source files |
| Job statistics and retries | No job/campaign denominator manifest in v0.2 |

## Try the review checkout

Review pull request [#2](https://github.com/edward-lcl/eval-evidence/pull/2). Its
description records the tested head SHA; confirm it matches `git rev-parse HEAD` before
reproducing the evidence. From that checkout:

```bash
git rev-parse HEAD
python -m pip install .
eval-evidence check /path/to/jobs/job-name
eval-evidence inspect /path/to/jobs/job-name --adapter harbor --explain
eval-evidence bundle /path/to/jobs/job-name -o /separate/evidence/
eval-evidence verify /separate/evidence/TRIAL_NAME.eval-evidence.json \
  --run-root /path/to/jobs/job-name/TRIAL_DIRECTORY
```

`check` recursively discovers qualifying trial directories that contain the required
result, config, and ATIF files. It does not compare that count with Harbor's job result,
so a missing/non-ATIF trial can be absent from the report. `bundle` emits one bundle
per trial; it does not seal the job-level `result.json` or establish which trials entered a
reported aggregate. The bundle destination should be outside the run root so a later
source mutation cannot silently replace both source and baseline together.

## What we have already learned

A private seven-trial genuine Harbor job loaded and verified locally, including absent
optional files. The review exposed and fixed null metric fallbacks and an effective
agent-timeout fallback. A separate genuine three-group comparison found differing task
checksums, denominators, and turn budgets and was classified **not comparable** rather
than converted into a model ranking. Only redacted summaries are retained here.

The reproducible structural CI gate is now `met` with a two-trial fixture derived from
the genuine retained layout. All scalar values and trajectory content were replaced;
one trial was then modified to contain explicit source conflicts. This is repeatable
adapter-structure evidence, not proof that the synthetic values are representative or
that every Harbor layout is supported.

## Current compatibility boundary

| Input | v0.2 status |
|---|---|
| Single-step Harbor trial with `agent/trajectory.json` | Exercised on genuine retained data |
| Trial without an ATIF trajectory | Not discovered by v0.2; Harbor documents agent-directory contents as implementation-dependent |
| Job directory containing multiple trials | Deterministic discovery of qualifying children; no completeness check or job-level output |
| ATIF v1.5, v1.6, v1.7 | Recognized for the fields this adapter reads |
| Unknown ATIF version | Visible non-fatal compatibility warning |
| Current Harbor multi-step `step_results` aggregation | Not yet validated or mapped |
| Regraded trials and job-level retry/denominator semantics | Not yet validated or represented |
| Provider-returned response-model identity | Unavailable unless Harbor records it in a mapped run artifact |
| Claim-specific critical-field policy | Not implemented; `--min-coverage` is only a coarse fraction |

See [`HARBOR_MAPPING.md`](HARBOR_MAPPING.md) for every source path and known gap.

## Terms used in this review

- **Job:** Harbor's campaign container and aggregate state. Eval Evidence does not seal
  this layer in v0.2.
- **Trial/run:** one task attempt and the unit of an evidence bundle.
- **Configured model:** the name requested in Harbor configuration. It is not necessarily
  the provider-returned response model.
- **Reward:** verifier-reported outcome. It is not automatically independent evidence
  that the task or solution is valid.
- **Baseline:** the bundle and source hashes created after a stable trial. An unsigned
  baseline detects later differences only while the baseline itself remains trusted.

## Requested decisions

The review is intentionally narrow. In priority order, please:

1. **Correct or approve the field mapping.** The adapter now computes the effective
   agent timeout as `min(override base, optional cap) * resolved multiplier`, preserves
   those components in `extensions.harbor.timeout`, and leaves the field unavailable
   when only the task definition contains the base. Please confirm that formula, the
   top-level multiplier precedence, and the task-config base source. Also review
   token/cache semantics, exception/termination, task identity, network configuration,
   verifier evidence, and the ATIF fields used.
2. **Review the reproducible G2 fixture.** Confirm that its retained structure is useful
   for compatibility testing, its sanitization boundary is sufficient, and its
   deliberately adversarial conflict trial matches the semantics maintainers expect.
3. **Advise on the job-level boundary.** Before external adoption, we expect a
   deterministic job/campaign index that links exact trial bundle digests and records
   attempted, retried, failed, timed-out, cancelled, and excluded denominators. Please
   confirm whether Harbor's job `result.json` should be the source of that contract.
4. **Confirm the capture-time field contract.** The Unknown entries in
   [`artifacts/real-comparison-redacted.md`](../artifacts/real-comparison-redacted.md)
   show that retained runs need standardized, machine-readable `response_model`,
   `verifier_digest`, `environment_image_digest`, and `system_prompt_sha256` values.
   Please confirm where Harbor can record each value at run close, and whether the task
   digest already covers the verifier directory. We are not requesting a new
   `harness_version`/commit capture field: current Harbor `lock.json` already records
   its version and, when installation metadata establishes it, its Git commit; the
   adapter instead needs a reviewed job-to-trial association for that existing record.

Native Harbor emission is a later option, not a condition of this review. If desired,
the clean integration point is after each trial result and trajectory are finalized:
Harbor would either invoke the same normalization/sealing library or emit the
framework-neutral `eval-run.json`; evidence failure should report separately and must
not rewrite the completed trial result. A job-level index would be finalized only after
job status and retry counts stabilize.

## What acceptance would mean

Acceptance means the adapter accurately describes the evidence present in the reviewed
Harbor layouts and fails honestly when evidence is missing. It would not endorse Eval
Evidence as a leaderboard, certify Terminal-Bench tasks, validate model-quality claims,
or make unsigned digests trustworthy against an actor who can replace both source and
bundle.

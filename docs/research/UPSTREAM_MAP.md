# Upstream map: Harbor, Terminal-Bench, and Fortify

Snapshot date: 2026-08-15. Source revisions inspected:

- Harbor `a27e9c2ae10a31c40b2dcef33ef5486bce36e185`
- Terminal-Bench `d435a67e30ecb41f916716607c30c4646f208ee6`
- harden-v0 `342b8474e0c0cf96e4a8313fd2e26c7a11d51193`

This is a placement analysis, not an upstream proposal or endorsement.

## What already exists

| Need | Existing upstream primitive | Implication |
|---|---|---|
| Expected trial count and progress | Harbor `JobResult.n_total_trials` plus `JobStats` completed, errored, running, pending, cancelled, and retry counts | Start campaign reconstruction from Harbor job state; do not invent a second scheduler or retry ontology. |
| Requested attempts and retry policy | Harbor `JobConfig.n_attempts`, `RetryConfig`, generated trial configs, and job execution state | Expected denominator and retry semantics belong at the Harbor job layer. |
| Frozen replay-affecting inputs | Harbor `JobLock`/`TrialLock`: schema versions, Harbor version/commit when known, task digest/source, resolved agent/environment/verifier config, skill digests, retry, and source-trial lineage | Eval Evidence currently duplicates a weaker subset because it ignores `lock.json`. The natural fix is a reviewed lock-to-trial join or native export. |
| Task content identity | Harbor `TaskLock.digest` and per-trial `task_checksum`; Terminal-Bench task versioning direction | A checksum-to-version registry belongs with task publishing, not in this repository. |
| Regrade lineage | Harbor `source_jobs`, `SourceTrialConfig`, `SourceTrialLock`, and `RegradeTrial` | Regrade/supersession should be exported from Harbor's native lineage rather than re-modeled independently. |
| Trial outcome and execution | Harbor `TrialResult`, `AgentContext`, verifier results, timings, exceptions, `step_results`, and ATIF trajectory | Per-trial normalization may remain useful, but native records are authoritative. |
| Verifier score detail | Terminal-Bench issue #1390 documents ad-hoc sidecars and discarded rich metrics, proposing standardized score provenance in `reward.json` | Score-component provenance belongs in the verifier output contract; an envelope should carry it, not define each task's scoring schema. |
| Adversarial task acceptance evidence | `/fortify` wraps harden-v0, which retains per-task result/config, Harbor jobs, iteration outcomes, patches, journals, and terminal status | Fortify already produces acceptance-process evidence. Eval Evidence could later link its outputs; it should not reproduce the hacker/fixer loop. |
| Archive/upload closure | Current Harbor upload requires `lock.json` and packages a defined job/trial allowlist | Measure whether this already provides sufficient custody before adding another archive layer. |

## What Eval Evidence currently duplicates

- Selected trial configuration that Harbor already freezes more completely in
  `TrialLock`.
- Harness identity that Harbor `JobLock.harbor` can already retain.
- Task identity that Harbor represents with typed task IDs and content digests.
- Metric and agent/model values already present in `TrialResult` and ATIF.
- A partial view of network/tool configuration that native resolved configuration can
  describe more accurately.

The duplication is defensible only as a portable review/interchange layer. If a second
evaluator does not validate that role, shrink it.

## What is genuinely missing or not yet joined

| Missing primitive | Smallest useful form | Natural home |
|---|---|---|
| Published-claim membership | Expected attempt ID, occurred state, included boolean, exclusion reason, supersedes/regrades link, and exact trial evidence digest | Harbor job export or leaderboard submission manifest |
| Aggregation lineage | Named/versioned transform, input attempt IDs, grouping keys, output statistic, uncertainty method | Leaderboard/publication layer, sourced from Harbor job outputs |
| Comparison qualification | Required fields by claim plus unresolved material differences | Comparison/publishing policy, potentially shared interchange logic |
| Prospective response identity | Provider-returned model/deployment identity captured at call/run close | Harbor agent/provider result |
| Prospective verifier/environment/prompt identity | Stable digests recorded before evidence evaporates | Harbor trial lock/result; task publisher for verifier/task components |
| Machine-joinable provenance | Input reference + JSON pointer + input digest + transform name/version + candidates/conflicts | Native exporter or small portable envelope after prototype evidence |
| Standard score-component provenance | Typed extra fields alongside reward | Terminal-Bench verifier contract, aligned with issue #1390 |
| Fortify before/after acceptance regression | Task/verifier versions, attack result, accepted fix, legitimate-solution acceptance evidence | Fortify/Terminal-Bench review workflow |

## 2026-08-16 addendum

The [claim reconstruction study](CLAIM_RECONSTRUCTION.md) found that the record
sketched below already exists, field for field, in the Terminal-Bench 2.1 leaderboard
tooling (`harbor-framework/terminal-bench-2-1@7131e437…`: `leaderboard/submissions/*.json`
with `source_jobs`, `source_filter`, `disqualified_trials[{trial_id, reason,
judge_trial}]`, `trials[]`, `metrics`, plus public `core/metrics.py` with an explicit
errored-trials rule and SE formula) — in the leaderboard layer, as this map predicted.
Two additions the study makes to the placement: (i) every layer needs an *expected set*
held by a different actor than the record (Harbor has `lock.trials` for trials; no
leaderboard studied has "merged submissions == displayed rows"), or the record cannot
detect an omitted transition; (ii) three Harbor-side gaps are concrete fields, not
ontology — retry tombstones, member-trial digests at job close, and a metric
null-policy/denominator/version field.

## Minimal campaign record to test, not yet build

The first experiment needs only:

```text
campaign identity and locked configuration
  expected attempts[]
    attempt identity
    task identity/digest
    requested instrument
    lifecycle state
    trial evidence digest or unavailable reason
    included in claim? + reason
    retry/regrade/supersession links
  aggregation
    transform name/version
    ordered input attempt identities
    grouping and missing-data policy
    reported value and uncertainty
  comparison
    matched conditions
    unresolved material differences
```

Harbor should remain the source of expected attempts, retry/cancellation state, locks,
and regrade lineage. A publication or leaderboard layer should own inclusion and
aggregation. Eval Evidence should at most supply portable trial references and a
comparison decision record.

## Recommended architecture direction

1. Keep the current package as a research instrument and interchange prototype through
   the conflict/recoverability and second-evaluator studies.
2. Add no scheduler, hosted service, plugin system, or generalized campaign platform.
3. Prototype a read-only Harbor job index that consumes `JobResult`, `JobConfig`, and
   `JobLock`; do not define new retry semantics.
4. Prefer a small native Harbor post-run evidence export if prospective capture proves
   cheaper and more complete.
5. Place task acceptance requirements and score provenance in Terminal-Bench/Fortify;
   place run identity and denominators in Harbor; place final selection/aggregation in
   the leaderboard or publication artifact.
6. Retain standalone Eval Evidence only for the framework-neutral pieces that survive
   the Inspect experiment: evidence-state vocabulary, structured source references,
   portable content identities, and claim comparison qualification.

No upstream PR should be opened until the experiments show which of these primitives is
missing in practice and maintainers have reviewed the mapping.

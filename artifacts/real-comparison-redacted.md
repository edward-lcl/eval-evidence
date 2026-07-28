# Redacted real-run comparison record

Recorded 2026-07-28 from a private local copy of the frozen TB3 working snapshot
`3c5be84efd707da8`. This is a product dogfood result, not a model ranking. Model names,
task/run identifiers, UUIDs, rewards, trajectories, source values, and absolute paths
are intentionally omitted.

## Scope

One nominal task was selected because genuine baseline trials existed for three model
groups. Only `baseline_trajectories` were included; adversarial/hack trajectories were
excluded from this comparison. The retained denominators were unequal:

| Redacted group | Baseline trials found |
|---|---:|
| A | 1 |
| B | 3 |
| C | 2 |

The current source checkout ran `check`, `bundle`, and `verify --run-root` for every
selected trial:

```text
A: check_exit=0 discovered=1 valid=true bundle_exit=0 verify_count=1 verify_all_valid=true
B: check_exit=0 discovered=3 valid=true bundle_exit=0 verify_count=3 verify_all_valid=true
C: check_exit=0 discovered=2 valid=true bundle_exit=0 verify_count=2 verify_all_valid=true
```

All six source-level bundles were internally valid and matched their preserved
referenced files. This establishes content integrity only; it does not establish that
the runs are comparable or that their rewards are correct.

## Matched, different, and unknown

| Dimension | Finding | Evidence interpretation |
|---|---|---|
| Nominal task ID | Matched | All six bundles recorded the same value. |
| Task revision | Matched | All six bundles recorded the same revision. |
| Task checksum | **Different** | Group A had one checksum; groups B and C each contained two distinct checksums. The nominal task/revision therefore did not identify stable task bytes across the selected trials. |
| Trial denominator | **Different** | Groups A/B/C contained 1/3/2 baseline trials, and no campaign claim package established attempted, retried, failed, or excluded denominators. |
| Requested/recorded model | Different by design | Each group consistently recorded a distinct model ID. |
| Provider-returned model | **Unknown** | `response_model` was unavailable in all six bundles, so a requested label was not independently tied to the backend response identity. |
| Agent name/version | Matched | Observed values matched across the selected runs. |
| Agent binary digest | **Unknown** | Unavailable in all selected runs. |
| Harness name | Matched | Derived as Harbor from the recognized directory layout. |
| Harness version/commit | **Unknown** | Both fields were unavailable in every selected run. |
| Maximum turns | **Different** | Values differed across groups, and group B also used two values internally. |
| Agent wall-time | Mixed/unknown | Some runs recorded an effective result timeout; others had no mapped timeout. Values were not uniformly available or matched. |
| Effort/thinking | Mixed/unknown | Unavailable for A and B and for one C trial; only one C trial recorded a value. |
| Sampling parameters | Matched | Captured parameters matched across the selected runs. |
| Tools/network configuration | Matched as derived configuration | The derived values matched, but configuration is not proof of effective tools or network enforcement. |
| System-prompt/policy identity | **Unknown** | Prompt hash and policy profile were unavailable throughout. |
| Environment image digest | **Unknown** | Unavailable throughout. |
| Verifier digest | **Unknown** | Unavailable throughout; reported reward is not reward-independent verifier evidence. |
| Harbor trajectory compatibility | Matched after compatibility review | The selected runs declared ATIF-v1.5 or ATIF-v1.6. Both are now recognized for the stable root agent, steps, and final-metrics fields used by the adapter; this does not claim full ATIF validation. |
| Bundle/source integrity | Matched/passed | Schema, bundle digest, and referenced-file checks passed for all six trials. |

## Cohort refinement

The two task-checksum states correlated with run date rather than model group: an
earlier state appeared in B and C, while a later state appeared once in A, B, and C.
This means either the task bytes or the checksum-producing pipeline changed while the
recorded nominal revision stayed constant; the bundles alone do not distinguish those
causes.

Restricting the comparison to the one later-checksum trial available in each group
produced a materially better matched cohort: task checksum, maximum turns, wall-time,
sampling parameters, agent name/version, and derived tool/network configuration all
matched. Effort/thinking was still inconsistent or unavailable, and response-model,
harness-build, prompt, environment, verifier, and agent-binary identities remained
unknown. Eval Evidence therefore identified a candidate controlled cohort, but the
retained evidence is still insufficient for a model-quality verdict.

## Classification

- [ ] Integrity failure
- [x] **Not comparable**
- [ ] Inconclusive evidence gap only
- [ ] Not falsified

The primary classification is **not comparable** because material recorded conditions
already differ: task checksums are unstable, trial denominators are unequal, and turn
budgets differ. The many unknown fields independently limit interpretation, but they are
not needed to establish the primary classification.

This does not say which model is better, whether any reward is wrong, or why the task
checksum changed. It says an aggregate comparison over all selected artifacts cannot be
treated as apples-to-apples without first explaining the checksum drift, fixing the
campaign denominator, and matching the declared instrument. The refined one-per-group
cohort is closer but remains evidence-limited. The next investigation should trace
each checksum to the exact task package and add a campaign-level claim recording all
attempts, retries, exclusions, aggregation rules, and uncertainty.

## Product conclusion

The first real paired dogfood produced a material finding that the integrity-only demo
could not: **the same nominal task and revision traveled with different task checksums
and different run budgets.** That is the intended value of Eval Evidence. It replaces a
model-quality argument with a concrete, falsifiable comparability question while
remaining explicit about what the retained artifacts cannot prove.

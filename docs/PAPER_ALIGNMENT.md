# Research-paper alignment and authority boundary

Eval Evidence operationalizes the paper's acceptance-contract questions, but it does
not own the paper's data, numerical claims, manuscript authority, or submission state.
The paper repository must name one canonical repository, path, and revision before this
crosswalk can be treated as frozen reviewer evidence.

**Current status:** conceptually aligned; manuscript authority pending owner freeze.

## Authority rule

Before citing this project from the paper—or citing “the paper” from this project—record:

1. the canonical paper repository;
2. the manuscript path;
3. an immutable Git revision or released artifact digest;
4. the section or label containing the acceptance contract; and
5. the paper owner's approval of that revision.

Until all five are recorded, references to “the paper's Section 8” are directional
context, not a reproducible citation. Paper numbers and scientific conclusions must be
verified in the paper repository from frozen tables and claim audits; Eval Evidence does
not reproduce or supersede them.

## Acceptance-contract crosswalk

| Paper question | v0.2 evidence support | Status | Next machine-checkable contract |
|---|---|---|---|
| Does the reference pass repeatedly? | A generic manifest can carry supplied control-run evidence; no named repeated-reference policy exists. | deferred | reference-control profile with repetitions, task identity, and retained outcomes |
| Does an empty solution fail? | A bundle can retain a supplied null-control outcome; `check` does not require it. | deferred | null-control profile tied to the exact task/verifier version |
| Are required tools reachable? | Configured tools can be retained; effective reachability is not tested. | deferred | preflight evidence for required tools and environment dependencies |
| Is scoring state isolated and pinned? | Selected configuration and digests can be carried when captured; isolation is not enforced. | partial | environment/verifier identity plus enforceable isolation evidence |
| Does strict independent evidence show a bypass? | Reward-independent claims can be carried without being upgraded to truth. | partial | typed bypass evidence with protocol, source, and outcome |
| Do failures occur at the claimed crux? | Termination and supplied item-validity evidence can be retained; failure localization is not inferred. | deferred | crux-localization evidence linked to task validity and trajectory references |
| Does the result replicate under a declared instrument? | Per-trial instrument evidence and byte identity are implemented; repeated-run comparison is manual. | partial | campaign claim linking repeated runs, matched fields, and uncertainty |
| Are denominators, uncertainty, and unresolved cases visible? | Unavailable state is explicit per trial; job denominators and statistical uncertainty are not represented. | deferred | job/campaign index with attempts, retries, exclusions, seeds, and uncertainty |

`docs/VISION.md` keeps these questions as the policy backlog. This table prevents the
product vision from being mistaken for shipped v0.2 behavior.

## Reviewer reading order

1. Read the paper's frozen acceptance-contract section.
2. Read [`VISION.md`](VISION.md) for the product translation.
3. Read [`BUNDLE_SPEC.md`](BUNDLE_SPEC.md) and [`TRUST_MODEL.md`](TRUST_MODEL.md) for the
   current wire and proof boundaries.
4. Read [`READINESS.md`](READINESS.md) for executable evidence and unmet gates.
5. Use [`TBENCH_REVIEW.md`](TBENCH_REVIEW.md) for the first upstream integration review.

An aligned roadmap is not validation of the paper's empirical claims. A passing bundle
check is not evidence that an item is valid, a verifier is correct, or a model ranking is
true.

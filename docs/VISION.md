# Product vision

> **A score should never travel alone. Eval Evidence is the acceptance contract for evaluation results.**

Eval Evidence turns a reported score into a portable, machine-checkable claim with receipts for the model, harness, budgets, verifier, artifacts, and field-level provenance. It is an offline evidence and comparability layer, not an evaluation runner or a claim that the recorded result is physically true.

The product lifecycle is **declare → capture → seal → compare/publish**. Existing
runners own execution and capture; Eval Evidence should eventually validate the
evidence plan before compute, seal results afterward, and render claim comparisons. It
also reprocesses retained runs without model compute, while marking anything the old
archive cannot establish as unavailable. [LIFECYCLE.md](LIFECYCLE.md) separates those
prospective, post-run, and retrospective modes from features v0.2 does not yet ship.

## 1. Harbor first; Inspect AI exporter second

The Inspect AI exporter is the second integration, sequenced **after G2 passes** against genuine Harbor data. Harbor comes first because it can invalidate inferred mappings and is the anchor readiness dependency in [READINESS.md](READINESS.md). An Inspect post-run exporter should then test whether the framework-neutral input is genuinely portable; a plugin system remains deferred until a third evaluator justifies it, as specified in [ADAPTERS.md](ADAPTERS.md).

## 2. Live monitoring is rejected

A live monitoring, dashboard, or observability product is **rejected**. Eval Evidence stays post-run, offline, deterministic, runs no models, and uploads nothing. Existing harness viewers can own live operations; this product's differentiator is that a reviewer can verify retained evidence without trusting or re-executing the harness.

## 3. Physical verification and attestation are deferred

Physical verifiers, sensors, facilities, and authenticated attestation are **deferred** to a later trust layer. The v0.1 schema deliberately leaves the `attestation.signature: null` signature slot empty. [TRUST_MODEL.md](TRUST_MODEL.md) defines the signer-governance gate and makes clear that a signature authenticates a scoped statement rather than proving physical truth. The evidence categories may generalize later, but this release neither operates physical experiments nor certifies them.

## 4. Neutral contract; Terminal-Bench maintainers first

The format remains framework-neutral and evaluator-agnostic; adoption is intentionally opinionated. The first go-to-market user is the Terminal-Bench/Frontier-Bench maintainer team, with Harbor as the anchor integration. [HARBOR_MAPPING.md](HARBOR_MAPPING.md) is the concrete mapping review surface, while [TBENCH_REVIEW.md](TBENCH_REVIEW.md) asks maintainers to validate it and consider native `eval-run.json` emission.

## 5. The flagship pitch is the five-minute tamper demo

The flagship pitch is the **five-minute tamper demo**: run `demo` → `check` → `bundle` → `verify`, flip one byte in a referenced source file, and watch `verify` name the digest mismatch. A source-checkout-only transcript at `artifacts/demo-session.txt` shows both the passing path and the failure and is intentionally excluded from distributions. This makes the acceptance contract visible without presenting a schema tour or building a dashboard.

## 6. Lightweight maintainership is sufficient

Current lightweight, single-maintainer governance is **sufficient for now**. Fast issue response, reviewed contributions, a changelog, and the stability promises in [COMPATIBILITY.md](COMPATIBILITY.md) are enough at this stage; [CONTRIBUTING.md](../CONTRIBUTING.md) defines the contribution and data-handling path. No steering group is needed before multiple independent adopters create a real coordination problem.

## What real dogfooding has already falsified

The first genuine Harbor run did more than confirm the happy path. Seven trials loaded
and verified, but the source review found six result-level timeout values that the
adapter had left unavailable; the fallback was fixed and regression-tested. A separate
redacted three-group baseline comparison then found the same nominal task/revision
traveling with two task checksums, unequal 1/3/2 trial denominators, and inconsistent
turn budgets. A checksum-matched one-per-group cohort was closer, but still lacked
provider-returned model, harness-build, prompt, environment, verifier, and agent-binary
identity.

Those results are retained only as redacted workspace evidence in
`artifacts/harbor-readiness-redacted.txt` and
`artifacts/real-comparison-redacted.md`; neither is shipped. They do not rank models.
They demonstrate the product's near-term job: expose the exact integrity,
comparability, and unavailable-evidence questions hidden by a score. G2 nevertheless
remains `unmet` until regular CI can run the genuine/sanitized fixture without a skip,
as required by [READINESS.md](READINESS.md).

## Acceptance-contract backlog

The research paper's eight acceptance-contract questions are the machine-checkable
backlog for future `check` policies. The canonical manuscript revision is not frozen in
this repository, so [`PAPER_ALIGNMENT.md`](PAPER_ALIGNMENT.md) is the authority boundary
for this directional crosswalk. The policies should produce explicit evidence, failure,
or unavailable states rather than a universal fairness score. In order:

1. **Does the reference pass repeatedly?** Add repeatable reference-control evidence.
2. **Does an empty solution fail?** Add a null-control policy and retained outcome.
3. **Are required tools reachable?** Add environment and dependency preflight evidence.
4. **Is scoring state isolated and pinned?** Extend instrument pinning into an enforceable isolation policy.
5. **Does strict independent evidence show a bypass?** Record reward-independent exploit and bypass checks.
6. **Do failures occur at the claimed crux?** Require failure localization evidence rather than inferring it from a zero reward.
7. **Does the result replicate under a declared instrument?** Check repeated runs against the declared model, harness, budgets, environment, and verifier.
8. **Are denominators, uncertainty, and unresolved cases visible?** Add campaign-level aggregation and explicit unresolved-case policies.

This is what `check --min-coverage` should grow into: machine-checkable acceptance policies grounded in declared evidence. It does not change today's gate status or trust boundary. [READINESS.md](READINESS.md) remains authoritative for current release evidence, [ADAPTERS.md](ADAPTERS.md) for integration sequencing, and [TRUST_MODEL.md](TRUST_MODEL.md) for claims the bundle does not prove.

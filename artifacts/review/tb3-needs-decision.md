# Frozen decision: what TB3 / Frontier-Bench needs from the evidence layer

## Decision

The list below is frozen at **five items**. It states the target acceptance contract,
not five changes to implement in this documentation episode. Sequencing remains the
`docs/LIFECYCLE.md` **“Product sequence”**: first correct deterministic run sealing and
G2, then a second integration, then campaign claims and policies.

## TB3 / Frontier needs

1. **Capture exact run-time identity before it evaporates.** Standardize
   provider-returned model, prompt digest, verifier digest, environment image digest,
   and resolved harness/job lock association; distinguish requested, configured,
   effective, and observed facts. Justification: the Unknown column and budget mismatch
   in `artifacts/real-comparison-redacted.md:42-54`; evolution analysis §§TB2–TB2.1;
   blind-spot register ranks 2, 4, and 6.
2. **Make the campaign claim the sealed publication unit.** A claim must bind every
   trial-bundle digest to attempted/retried/failed/timed-out/cancelled/excluded counts,
   arm and retry policy, aggregation rule, seeds, uncertainty, and stable job inputs.
   Justification: six valid trial bundles still produced an invalid 1/3/2 comparison
   (`artifacts/real-comparison-redacted.md:14-29,39-40,81-92`); blind-spot rank 1 and
   evolution analysis §TB3/Frontier.
3. **Use content-addressed task identity end to end.** Require the exact task/package
   digest in claims, retain a digest-to-release mapping, and census nominal identities
   for multiple content states. Names and Git refs remain labels, not primary identity.
   Justification: two checksums traveled under one nominal task/revision
   (`artifacts/real-comparison-redacted.md:39,60-69`); blind-spot rank 7 and evolution
   analysis §§TB2–TB2.1.
4. **Account for every expected attempt and every later interpretation.** Discovery must
   report sealed, incomplete, malformed, missing, cancelled, or explicitly excluded
   attempts; multi-step outcomes, regrades/supersession, and taxonomy-bound item
   adjudication must retain lineage. Justification: `eval_evidence/adapters.py:209-228`
   [superseded; see Erratum] silently filters non-ATIF roots; current multi-step exclusion is
   `docs/HARBOR_MAPPING.md:101-109` [superseded; see Erratum]; blind-spot ranks 3, 8, and 11.
5. **Turn sufficiency into named policies, not a percentage.** Publication and
   task-acceptance profiles should state required fields/statuses, controls, artifact
   closure, replication, unresolved-case behavior, and supported OTel transport fields.
   Keep unavailable explicit. Justification: equal-weight coverage at
   `eval_evidence/core.py:126-141`; Section 8 backlog at `docs/VISION.md:57-68`;
   blind-spot ranks 9, 12, 14, and 16.

These needs are mutually reinforcing but bounded: a campaign package is deterministic
JSON over evidence the runner already owns; it is not a new execution service.

## Non-goals

The following rejections remain binding and mirror `docs/VISION.md` **“Live monitoring
is rejected”** and **“Physical verification and attestation are deferred”**:

- **No dashboard or live monitoring product.** Produce static, offline reports from the
  machine-readable claim.
- **No runner.** Eval Evidence never executes models, tasks, or verifiers and does not
  compete with Harbor.
- **No universal fairness score or universal trust score.** Named policies expose
  evidence, differences, and unavailable state rather than collapsing validity.
- **No plugin system before a third evaluator.** Harbor stays first; Inspect is the
  second portability test.
- **No signing or attestation before signer governance.** Follow
  `docs/TRUST_MODEL.md` **“Gate before signing”**; a digest or signature does not prove
  physical truth. A witnessing idea remains deferred rather than becoming a hosted
  transparency service now.

## Cross-document consistency

- `docs/VISION.md` contains **“Live monitoring is rejected”** and **“Physical
  verification and attestation are deferred”**, plus the Section 8 policy backlog.
- `docs/LIFECYCLE.md` contains **“Before a new evaluation run”** and **“Product
  sequence”**; the five needs fit declare → capture → seal → compare/publish.
- `docs/TRUST_MODEL.md` contains **“v0.1 trust boundary”** and **“Gate before signing”**;
  nothing here upgrades unsigned integrity into authenticity or physical truth.

This decision therefore carries forward the existing VISION, LIFECYCLE, and TRUST_MODEL
boundaries rather than creating a dashboard, runner, generic telemetry platform, or
certification authority.

## Erratum (2026-07-29)

Item 4's historical numeric citations `eval_evidence/adapters.py:209-228` and
`docs/HARBOR_MAPPING.md:101-109` became stale when line counts shifted during earlier
updates. The active discovery evidence is identified by `HarborAdapter.required`,
`HarborAdapter.detect()`, and `HarborAdapter.discover()`, as recorded in
`artifacts/review/claim-verification-matrix.md` (a). The active mapping exclusions are
documented in `docs/HARBOR_MAPPING.md` (**Layout support and known gaps**: **Trial
without `agent/trajectory.json`**, **Multi-step `step_results`**, **Regraded trials**,
and **Job stats/retries/cancellations**).

This erratum repairs only the historical source locators. It does not alter the item-4
requirement, its justification, priority, scope, or the frozen five-item decision.

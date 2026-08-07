# Product lifecycle: before, after, and retrospective evaluation evidence

Eval Evidence is designed to sit beside evaluation runners such as Harbor and Inspect
AI. It does not replace their execution, scoring, trajectory viewers, or live
operations. Its job is to make the resulting claim portable and auditable.

The intended lifecycle has four stages:

1. **Declare** what must be captured before expensive evaluation begins.
2. **Capture** those facts and source artifacts in the existing runner.
3. **Seal** each completed run into deterministic evidence.
4. **Compare and publish** a campaign claim with matched, different, and unknown
   conditions visible.

Version 0.2 implements the sealing layer and retrospective import foundation. The other
stages below distinguish what works now from product direction.

## Before a new evaluation run

Today, “set it up before the run” means configuring the harness to retain the evidence
that Eval Evidence will seal afterward. It does **not** mean running an Eval Evidence
live monitor.

Before spending compute, decide which run-time records will establish:

- requested model and provider-returned model identity;
- agent, harness version/commit, tools, prompt hash, and policy profile;
- turn, time, token, reasoning, and sampling budgets;
- task revision/checksum, environment image digest, and network configuration;
- verifier code/configuration digest and reward-independent evidence;
- attempted, retried, failed, timed-out, and excluded trial denominators.

For a generic evaluator, have the runner emit `eval-run.json` when the run closes. For
Harbor, preserve `result.json`, `config.json`, `agent/trajectory.json`, and verifier
outputs. Capture provider-returned metadata at request time; a later system card cannot
recover it.

A future preflight policy should validate the intended evidence plan before compute—for
example, refusing a campaign that cannot record task or verifier identity. Its output
should have a stable plan digest that completed run bundles can reference, making
planned-versus-actual drift visible without operating a dashboard. There is no `plan`
or `preflight` command in v0.2, so documentation must not imply that this policy is
currently enforced.

## Immediately after a run

Wait until the run directory is stable, then execute:

```bash
eval-evidence check /path/to/run
eval-evidence inspect /path/to/run --explain
eval-evidence bundle /path/to/run -o /separate/evidence/run.json
eval-evidence verify /separate/evidence/run.json --run-root /path/to/run
```

Store the bundle separately from the run root. The bundle records current source-file
hashes and field-level provenance. Later `verify --run-root` calls can detect changed,
deleted, or replaced referenced files relative to that baseline.

This is post-run sealing, not authentication. An actor who can replace the source and
recompute an unsigned bundle can create a new internally consistent baseline.

## Reprocessing prior evaluations without rerunning models

Yes: this is a primary use case and requires no model compute.

### Existing Harbor data

Point `check`, `inspect`, and `bundle` at the retained trial or archive root. The Harbor
adapter recursively discovers qualifying trials. This repository's own dogfood
reprocessed genuine historical Harbor trials and exposed task-checksum, denominator,
and budget drift that was invisible in the nominal labels.

### Other retained evaluation data

Work from a preserved copy of the old run and add a generic `eval-run.json` describing
only what the retained files support. Reference the original score, log, response
metadata, build metadata, and verifier files beneath that copied root. Use provenance
statuses honestly:

- `observed` for a value present in a named retained run artifact;
- `derived` for a reproducible calculation such as a file digest;
- `operator_asserted` for a value reconstructed from operator records;
- `provider_asserted` for a provider document or system-card claim;
- `unavailable` when the archive cannot establish it.

For generic `eval-run.json` input, an instrument value without a matching `provenance`
entry defaults to `operator_asserted`. Plain `item_validity` and `verifier_evidence`
claims do the same; use a complete `{value, status, source}` claim object to declare a
stronger provenance. Do not silently upgrade a release note, filename, directory label,
or system card into run-time observation.

### Retrospective limitation

A retrospective bundle proves what the archive contained **when it was bundled**. It
cannot prove that the archive was unchanged since the original run unless an older
trusted digest or signed baseline exists. It also cannot recover data that was never
captured. That limitation is useful evidence debt, not a reason to rerun automatically:
first bundle what exists, identify which missing fields are decision-relevant, and rerun
only when the intended claim actually requires them.

Version 0.2 does not require a capture-mode field. Integrations that need one may use a
namespaced `extensions` record to distinguish `native-post-run` from `retrospective`
capture and record the externally supplied baseline time. A future claim contract
should standardize that distinction without injecting a nondeterministic clock value
into bundle construction.

## Graphics and reports

A visual output is useful when it makes a comparison legible; it is not useful as a
second observability dashboard.

The intended report is a static, offline rendering of machine-readable claim data:

- **Matched** conditions;
- **Different** conditions;
- **Unknown** or unavailable evidence;
- integrity failures and exact affected paths;
- campaign denominators, exclusions, uncertainty, and supported claim;
- links to downloadable bundles and the verification command.

The graphic must be derived from the JSON evidence and never become the source of
truth. It must not collapse differences into a universal fairness or trust score.
Version 0.2 provides the manual decision record in
[`OWNER_DOGFOOD_REPORT_TEMPLATE.md`](OWNER_DOGFOOD_REPORT_TEMPLATE.md); it does not yet
ship `compare`, a campaign-claim contract, or an HTML report generator.

## Product sequence

1. Validate and ship deterministic run sealing for real Harbor data.
2. Give regular CI an approved genuine/sanitized fixture so G2 is reproducible.
3. Add the Inspect AI post-run exporter as the second integration.
4. Specify a campaign/evaluation-claim package for denominators, retries, exclusions,
   aggregation, seeds, and uncertainty.
5. Generate a structured comparison and static report from that claim package.
6. Add preflight evidence policies before considering event streaming.
7. Add signing or physical-facility profiles only after signer roles, calibration,
   chain of custody, and revocation semantics are defined.

This sequence supports prospective and retrospective evaluation work without competing
with runners or spending compute merely to reconstruct bookkeeping.

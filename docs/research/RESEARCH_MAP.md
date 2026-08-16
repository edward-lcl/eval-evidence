# Research map: evaluation evidence after execution

Status: working plan, 2026-08-15; hypothesis states updated 2026-08-16 from the
[claim reconstruction study](CLAIM_RECONSTRUCTION.md). This is a falsification plan,
not a paper claim.

## 2026-08-16 update: what the claim reconstruction study changed

The study asked whether a "claim lineage" layer above trial evidence is a real missing
abstraction. Answer: no — it is a missing *record*, PROV-shaped and small, owned mostly
by Harbor (job close) and publishers (row); "claim support" is out of infrastructure
scope. Five real reported numbers reproduced exactly from per-instance artifacts; none
from a written rule; all had at least one unavailable instrument pin. Consequences for
the hypotheses below (details and receipts in the study):

- H1: supported in a specific form — mixed-provenance values (a displayed model sha from
  one run, scores from a later rewrite of another) and unavailable pins, not a coverage
  fraction. Per-field source pointers, not `available_fraction`.
- H3: weakly supported, only where an archive is not already content-addressed. No
  documented failure was prevented by trial sealing.
- H4: the falsifier is present — denominator, selection, rescoring, and aggregation
  ambiguity dominated every walk-back even with near-complete trial records.
- H5: further weakened — completeness is claim-relative; a Harbor bundle's ceiling is
  14/20 even with perfect mapping.
- H6: per-field, not global — arithmetic and membership are retrospectively recoverable;
  retry history (Harbor `rmtree`s the failed attempt), harness commit, image digest,
  dataset revision, and provider-returned model are prospective-only.
- E1 becomes E1′ (version-stratified, with an expected == discovered == included check);
  a public row-manifest retro-fit over the 142 TB2.0 rows is added ahead of E3–E6 (see
  study §G and `PROJECT_HANDOFF.json` EE-08).

## Central question

What is the smallest evidence contract that makes a reported AI-evaluation claim
independently interpretable and falsifiable after execution, without implying that
metadata proves correctness?

The current hypothesis is that a portable envelope with explicit evidence states and
byte identities is useful. The strongest alternative is that native harness job state,
denominator accounting, and prospective capture solve most of the problem, leaving only
a small interchange record—or no standalone Eval Evidence package.

## Competing hypotheses

| Hypothesis | Observation that would support it | Observation that would falsify or shrink it |
|---|---|---|
| H1: explicit provenance states prevent materially misleading interpretation | Real archives contain important asserted, unavailable, or conflicting values that ordinary result summaries hide | Nearly every claim-critical field is already unambiguous and native tools expose it reliably |
| H2: a framework-neutral envelope survives translation | Harbor and a second evaluator map a useful common core without semantic coercion | The generic fields encode Harbor-specific assumptions or require prose exceptions for most second-framework concepts |
| H3: post-run byte sealing adds review value | Mutation studies find consequential retained bytes can change without another stable integrity signal | Source archives are already content-addressed, immutable, and closed over every claim-relevant artifact |
| H4: trial evidence is a useful unit | Trial envelopes materially improve diagnosis after campaign membership is known | Denominator, selection, retry, and aggregation ambiguity dominates conclusions even with perfect trial records |
| H5: uniform coverage is a useful diagnostic | Low coverage predicts review friction while remaining clearly non-normative | Users treat it as trust/readiness, or extra low-value fields change it more than claim-critical gaps |
| H6: retrospective reconstruction is economical | Most critical evidence can be recovered safely across historical Harbor versions | Critical identities disappear after run close or require operator guesses; prospective native capture is cheaper |

## Available evidence sources

- The private frozen Terminal-Bench working archive: 8,633 structurally measured Harbor
  runs and a previously reviewed seven-trial slice. Raw content remains outside this
  repository; experiments retain aggregates and redacted receipts only.
- The checked-in two-trial sanitized structural fixture, derived from the genuine
  layout and extended with an explicitly synthetic conflict/error case.
- Current public Harbor at `a27e9c2ae10a31c40b2dcef33ef5486bce36e185`.
- Current public Terminal-Bench at `d435a67e30ecb41f916716607c30c4646f208ee6`.
- Current public harden-v0 at `342b8474e0c0cf96e4a8313fd2e26c7a11d51193`.
- A future, narrowly scoped Inspect AI sample. It is an experiment, not permission to
  build a plugin system.

## Experiments in information-value order

### E1 — campaign-denominator reconstruction

**Question:** Can current Harbor job files answer what was expected, attempted,
retried, completed, cancelled, included, and aggregated?

**Method:** sample genuine job directories across available Harbor versions; reconcile
`config.json`, `result.json`, `lock.json`, and discovered trial directories. Produce a
row per expected attempt with state and inclusion reason. Do not build a public campaign
format first.

**Metrics:** expected/discovered/reported counts; unexplained count delta; retry and
cancellation recoverability; fraction of reported aggregates with reconstructable
membership and aggregation; version-stratified failure reasons.

**Failure condition:** if membership or selection cannot be reconstructed without
guessing, the result is "retrospective campaign evidence unavailable," and prospective
Harbor capture becomes the recommendation.

### E2 — retrospective recoverability and conflict census

**Question:** Which claim-critical fields can be recovered, and how often do retained
sources disagree?

**Method:** for a version-stratified archive sample, classify model, agent, task,
verifier, budgets, metrics, environment, network, prompt, and response identity as
observed, safely derived, asserted, unavailable, or conflicting. Compare every field
that has multiple retained sources; do not apply precedence before counting conflicts.

**Metrics:** state distribution per field and Harbor version; conflict frequency and
magnitude; fields recoverable only prospectively; operator minutes per run; percentage
of headline-comparable cohorts invalidated by hidden differences.

**Failure condition:** if conflict is negligible and native Harbor already exposes the
same review signal, remove generic conflict machinery rather than defending it.

### E3 — claim-readiness versus uniform coverage

**Question:** Does `available_fraction` help diagnosis, or does it mislead?

**Method:** define three concrete claims—single-run reproduction, model A versus B, and
campaign score publication. For each, preregister required evidence and unresolved-
difference rules. Compare the claim-specific decision with uniform coverage.

**Metrics:** false-ready and false-not-ready rates; rank correlation; sensitivity to
adding irrelevant extension fields; reviewer agreement and decision time.

**Failure condition:** if uniform coverage frequently disagrees with claim readiness or
is easily inflated, remove the CLI gate in the next wire-breaking release and retain at
most per-status counts as diagnostics.

### E4 — mutation and closure study

**Question:** Which retained bytes can change after scoring, and which existing native
signals already reveal the change?

**Method:** on copied, non-authoritative archives, mutate one class at a time: result,
config, trajectory, verifier output, artifact manifest, referenced artifact, and job
membership. Compare Eval Evidence detection with Harbor locks, immutable storage, and
repository history.

**Metrics:** detection coverage, false assurance from manifest-only hashing, storage and
verification cost, and classes already protected upstream.

**Failure condition:** if native content addressing already closes the useful surface,
delete redundant sealing and keep only normalization/comparison logic.

### E5 — prospective capture cost

**Question:** Is a small native post-run manifest cheaper and more complete than
retrospective adaptation?

**Method:** instrument one non-sensitive Harbor run to emit response model, harness
identity, task/verifier/environment digests, prompt identity, resolved budgets, and
network policy at run close.

**Metrics:** implementation lines, runtime/storage overhead, new evidence recovered,
fields still unknowable, failure modes, and maintainer burden.

**Failure condition:** if capture cost is high relative to review value, narrow the
required set by claim type instead of standardizing every desirable field.

### E6 — second-evaluator portability test

**Question:** Does the current generic contract survive one Inspect AI translation?

**Method:** implement one bounded exporter against public, synthetic output. Record
lossy mappings and framework-specific concepts before changing the schema.

**Metrics:** clean common fields; forced/coerced mappings; prospective-only fields;
provenance joinability; campaign semantic differences; adapter-specific extension size.

**Failure condition:** if core concepts require Harbor semantics, rename or redesign the
contract rather than adding an abstraction layer.

## Claim-specific decision prototype

The research direction is:

`claim -> required evidence -> evidence state -> unresolved differences -> decision`

For a claim that model A outperforms model B, the first policy prototype should require:
task content identity, evaluation instrument identity, denominator and membership,
model/provider identity, relevant budgets, verifier identity, aggregation rule, and an
explicit list of unmatched conditions. `available_fraction` is not an input to the
decision except as a display diagnostic.

## Structured-provenance prototype

Do not change the v0.1 wire yet. Test this companion record first:

```json
{
  "status": "observed",
  "source_ref": {
    "input_path": "result.json",
    "json_pointer": "/agent_info/model_info/name",
    "input_sha256": "..."
  },
  "transform": {"name": "harbor.model_identity", "version": "0.1"},
  "candidates": [],
  "note": null
}
```

Success means reviewers can mechanically join the normalized value to an exact sealed
input and reproduce the transform. Failure means the extra complexity does not improve
review or portability enough to replace the current prose source.

## Paper decision

A paper is worth writing only if at least two experiments produce a generalizable
empirical result beyond "we built a bundle." Strong contributions would be a measured
recoverability/conflict taxonomy, an apparent-comparability collapse curve, a minimal
campaign claim contract, or evidence that prospective capture dominates retrospective
reconstruction.

Do not write a systems paper around the current CLI alone. Do not proceed if the study
sample cannot be audited, framework/version denominators cannot be stated, or the only
result is a synthetic tamper demo. A negative result that shrinks Eval Evidence into a
small Harbor primitive remains a valid paper outcome.

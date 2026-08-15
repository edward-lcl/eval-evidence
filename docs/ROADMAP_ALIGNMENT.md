# Frontier-Bench roadmap alignment

**Status:** proposal crosswalk, 2026-08-06. Anchor sources: the maintainers' living
roadmap, [terminal-bench#1422](https://github.com/harbor-framework/terminal-bench/issues/1422)
("[Roadmap] v0.2 and v1.0", opened 2026-07-23 by @RyanMarten, WIP), the
[Terminal-Bench 3.0 announcement](https://www.frontierbench.ai/announcement), and the
`/fortify` workstream ([#1191](https://github.com/harbor-framework/terminal-bench/pull/1191),
[#1259](https://github.com/harbor-framework/terminal-bench/pull/1259),
[#1266](https://github.com/harbor-framework/terminal-bench/pull/1266)).

A naming note: Terminal-Bench 3.0 launched as Frontier-Bench v0.1; the canonical
GitHub repository is `harbor-framework/terminal-bench`, and every issue/PR link below
uses that slug because `frontier-bench` issue deep-links do not redirect.

Eval Evidence is a post-run evidence envelope and integrity checker: it reads
existing trial artifacts, records where each normalized field came from (or that it
is unavailable), hashes the referenced bytes, and emits a deterministic JSON bundle.
It runs no models, tasks, or verifiers and adjudicates nothing. This document maps
each relevant roadmap item to (a) what the bundle already records, (b) a known gap
and what unblocks it, and (c) a suggestion the maintainers can accept, reprioritize,
or reject. It exists so suggestions arrive attached to items the maintainers have
already chosen to work on, rather than as free-floating feature requests. It changes
no scope: the non-goals in [VISION.md](VISION.md) remain binding, and
[TBENCH_REVIEW.md](TBENCH_REVIEW.md) remains the review entry point.

Row statuses — named to avoid colliding with the roadmap's own version numbers:

- **covered-by-bundle** — exists in Eval Evidence's merged v0.2.0 readiness candidate
  (PR [#2](https://github.com/edward-lcl/eval-evidence/pull/2); reviewed branch head
  `2743a29`, squash-merged to `main`).
- **known-gap** — a recorded gap, with its sequencing or unblocking condition stated.
- **suggestion** — a maintainer decision, not an Eval Evidence commitment.
- **out-of-scope** — outside the evidence layer's boundary.

## 1. v0.2 — the "verifier-only" release

The roadmap defines the next minor release as *"task bugs that can be fixed by only
updating the verifier"* ([#1422](https://github.com/harbor-framework/terminal-bench/issues/1422)).
The announcement separately states the machinery that makes verifier fixes
retroactive: *"Tasks are versioned so corresponding trials can be re-used, re-graded,
or re-run to minimize the cost and complexity of updating leaderboard results"*
([announcement](https://www.frontierbench.ai/announcement)).

| Roadmap anchor | Eval Evidence today | Status / suggestion |
|---|---|---|
| Move score provenance to extra fields ([#1390](https://github.com/harbor-framework/terminal-bench/issues/1390), [#1382](https://github.com/harbor-framework/terminal-bench/issues/1382), [#1375](https://github.com/harbor-framework/terminal-bench/issues/1375)) | The bundle's `instrument_manifest` carries field-level provenance with a five-state vocabulary (`observed` / `derived` / `operator_asserted` / `provider_asserted` / `unavailable`) and a coverage gate ([BUNDLE_SPEC.md](BUNDLE_SPEC.md)). | **covered-by-bundle**, plus **suggestion S1**: when relocating score provenance, keep any vocabulary that preserves the asserted-vs-observed distinction — not necessarily ours — so "this score component was asserted, not observed" survives the move. Native `eval-run.json` emission is recorded in [TBENCH_REVIEW.md](TBENCH_REVIEW.md) as a later option, not a review condition. |
| Enforce binary rewards strictly ([#1382](https://github.com/harbor-framework/terminal-bench/issues/1382), [#1388](https://github.com/harbor-framework/terminal-bench/issues/1388), [#1389](https://github.com/harbor-framework/terminal-bench/issues/1389)) | `outcome.reward` is captured as reported run output and explicitly labeled "not independent correctness evidence"; hashed verifier files (`reward.txt`, `ctrf.json`) travel with it. | **covered-by-bundle** (capture side). **Suggestion S2**: publish the binary-reward rule as a machine-checkable contract (schema or lint) so third-party tooling can validate stored trials against it during re-grades, not only new runs. |
| Verifier timeouts / slow verifiers / flakes under host load ([#1230](https://github.com/harbor-framework/terminal-bench/issues/1230), [#1233](https://github.com/harbor-framework/terminal-bench/issues/1233), [#1378](https://github.com/harbor-framework/terminal-bench/issues/1378), [#1379](https://github.com/harbor-framework/terminal-bench/issues/1379), [#1380](https://github.com/harbor-framework/terminal-bench/issues/1380), [#1383](https://github.com/harbor-framework/terminal-bench/issues/1383)) | Effective `max_wall_time_s` is resolved as `min(base, cap) × multiplier` with all components preserved (`extensions.harbor.timeout`), after review found a configured cap could masquerade as an observed effective value. | **covered-by-bundle** (resolution semantics). **Suggestion S3**: a timeout verdict should record the same decomposition (base, cap, multiplier, resolution path). The statistical flakiness protocol proposed in the [#1422 comments](https://github.com/harbor-framework/terminal-bench/issues/1422) (N *concurrent* oracle runs on a pinned instance to simulate host load; flag a timeout that falls inside the oracle-runtime CI) pairs naturally with retained bundles, which record the conditions of those re-runs so cross-host comparisons can be audited. |
| Re-grading stored trials when verifiers are updated ([announcement](https://www.frontierbench.ai/announcement); the v0.2 verifier-only framing makes this the natural mechanism) | Regrade lineage is a recorded gap: bundles have no supersession field, documented in [HARBOR_MAPPING.md](HARBOR_MAPPING.md) ("Layout support and known gaps" → "Regraded trials"). The gap stays deferred until a current Harbor regrade wire contract (and a sanitized fixture) identifies the actual source/supersession fields — the v0.2 re-grade work is likely to produce exactly that contract. | **known-gap**, and **suggestion S4**: when re-grading, emit `(original outcome, superseding outcome, verifier version pair)` rather than overwriting — otherwise a re-graded corpus silently loses the before/after evidence that makes verifier fixes auditable. |

## 2. v0.2 patch-level and environment items

| Roadmap anchor | Eval Evidence today | Status / suggestion |
|---|---|---|
| Pin docker images / reproducible builds ([#1360](https://github.com/harbor-framework/terminal-bench/pull/1360), [#1411](https://github.com/harbor-framework/terminal-bench/issues/1411)) | `environment_image_digest` is currently an explicit `unavailable` record in real Harbor bundles — absence is first-class evidence. | **suggestion S5**: of everything on the roadmap, this is the item the evidence layer benefits from most. The delta being asked is small and rides work already planned: when pinning lands, emit the image digest into per-trial run output (one field). The bundle field then flips from `unavailable` to `observed` with no schema change on either side. |
| Enforce "do not modify" constraints ([#1192](https://github.com/harbor-framework/terminal-bench/issues/1192)) | Hashing of referenced source bytes is the core `bundle`/`verify` mechanism — a modified covered file is a digest mismatch. | **covered-by-bundle** (post-hoc detection over covered bytes). Enforcement at run time is the maintainers' side; the two are complementary, not redundant. |
| Task identity across versions (task versioning, per the [announcement](https://www.frontierbench.ai/announcement)) | A checksum detects drift but cannot name which release a checksum is. In a real three-group comparison, two distinct content states were observed traveling under one nominal task name/revision ([artifacts/real-comparison-redacted.md](../artifacts/real-comparison-redacted.md)); the comparison was classified not comparable rather than ranked. | **known-gap**, unblocked if task versioning publishes a checksum→version map as one of its outputs — likely small if it can ride that work, though that is the maintainers' call. **Suggestion S6**: publish the map; the observed collision shows a name/ref can carry two content states. |

## 3. CI / CD / Leaderboard

| Roadmap anchor | Eval Evidence today | Status / suggestion |
|---|---|---|
| Upload agent/cheat/oracle/nop CI runs to Harbor Hub ([#1381](https://github.com/harbor-framework/terminal-bench/issues/1381)) | Control-run evidence (the reference passes repeatedly; an empty solution fails) heads the acceptance-policy backlog in [VISION.md](VISION.md) ("Section 8 acceptance-contract backlog"); bundles can seal each control trial today. | **suggestion S7**: publish the four control outcomes *per task version* alongside the leaderboard rows they gate. A leaderboard row whose task lacks a passing-oracle/failing-null pair at that exact version is a different kind of claim, and the distinction is machine-checkable. |
| Leaderboard package + PR-submit CI ([#1405](https://github.com/harbor-framework/terminal-bench/pull/1405)) | Campaign/job-level claims — denominators, retries, exclusions, aggregation — are the level the bundle deliberately does not cover in v0.2; that work is sequenced after run sealing and a second integration ([LIFECYCLE.md](LIFECYCLE.md), "Product sequence"). | **known-gap** (sequenced, not trigger-gated). **Suggestion S8**: define the leaderboard row's denominator contract now (attempted / retried / excluded counts per row), even before any external tooling exists — retrofitting denominators after publication is the expensive path. |
| Rubric review as Harbor run ([#1287](https://github.com/harbor-framework/terminal-bench/issues/1287)) | Outside the bundle's boundary: adapters must not upgrade assertions to observations ([BUNDLE_SPEC.md](BUNDLE_SPEC.md)); carried opinions would be `operator_asserted`. | **out-of-scope** (the evidence layer carries judgments as assertions; it does not make them). |

## 4. The `/fortify` workstream (adversarial hardening)

The `/fortify` command ([#1191](https://github.com/harbor-framework/terminal-bench/pull/1191),
experimental) operationalizes the adversarial hacker-fixer loop
([arXiv:2606.08960](https://arxiv.org/abs/2606.08960), harden-v0) inside the PR
workflow, and merged task PRs already carry fixes for loopholes it found. This is the
false-positive side of verifier quality: it makes verifiers harder to pass without
solving the task.

The same paper reports the cost on the other side: in its Terminal Bench case study,
hardened verifiers rejected measurably more *legitimate* solutions than the originals
(legitimate-solution acceptance dropped from 76.1% to 65.2%). The false-negative side
is not hypothetical elsewhere either: Datacurve's DeepSWE audit of SWE-Bench Pro
reported a 24.0% false-negative rate via LLM-judge re-review of 789 rollouts
([audit](https://deepswe.datacurve.ai/blog/deepswe), paper
[arXiv:2607.07946](https://arxiv.org/abs/2607.07946)). No fortify-equivalent exists
for false negatives.

**Suggestion S9 (the complementary instrument):** track verifier **false-negative
pressure** alongside fortify's false-positive hardening — per task version, record
legitimate-solution acceptance before/after each fortify patch, and treat a hardening
patch that costs acceptance as a scored trade-off rather than a free win. The honest
open question is where the acceptance set comes from: the loop's current solver check
is a single solution, and passing trajectories from the *old* verifier are not
automatically legitimate (that is the very problem fortify exists to fix). A
candidate seed is the oracle solution plus human-reviewed passing trajectories, with
the set's own provenance recorded — but the sourcing question is genuinely part of
the design opinion being asked for here. This slots directly into the v0.2
verifier-only release: verifier updates, task versioning, and stored-trial re-grading
are exactly the machinery an acceptance regression check needs, and
[#1429](https://github.com/harbor-framework/terminal-bench/issues/1429) (the agent
container is torn down before verification) bounds which end-state evidence any such
check can see. Eval Evidence's role stays post-run: sealing the before/after
acceptance evidence so the trade-off is auditable — not running the checks.

## 5. v1.0 task design decisions

| Roadmap anchor | Alignment |
|---|---|
| Agent as non-root | Changes the meaning of recorded network/permission fields; worth a manifest field once standardized (today it would be `operator_asserted`). |
| Standardize (long) timeouts (8 hrs?) | Makes S3's decomposition (base/cap/multiplier) more load-bearing, not less — a single long cap hides more. |
| Task additions (candidates) | No alignment claim; additions are quality-bar decisions for the maintainers. The only evidence-layer note: new tasks born with pinned images (S5) and control-run records (S7) avoid the retrofit cost the v0.1 tasks now face. |

## What this asks of the maintainers

Four grouped asks — the first three are format and publishing decisions on work
already planned, the last is a design opinion:

1. **S5 / S6:** when image pinning and task versioning land, surface their outputs —
   the image digest as a per-trial run-output field, and the checksum→version map as
   a published artifact. Both convert existing `unavailable`/ambiguous evidence into
   observed identity.
2. **S4:** make re-grading append-only (supersession, not overwrite) in whatever
   format v0.2 re-grades land.
3. **S7 / S8:** publish control-run outcomes and row denominators with the
   leaderboard package while its format is still being designed.
4. **S9:** whether false-negative pressure tracking belongs inside `/fortify`
   (an acceptance-set check in the loop), beside it (a re-grade comparison job), or
   nowhere — including how a legitimate-acceptance set should be sourced. This one is
   a genuine design opinion, and the maintainers are best placed to judge it.

Everything else in this document is descriptive: it states where the bundle spec
already meets the roadmap and where it deliberately stops.

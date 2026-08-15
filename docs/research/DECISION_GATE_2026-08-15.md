# Adversarial review decision gate

Date: 2026-08-15

Baseline reviewed: `main` at `e27d55cfe948920220eebc356ef3059d3a4ff0d8`

Working branch: `codex/adversarial-research`

## 1. Confirmed implementation defects

1. A partial generic provenance object defaulted missing status to `observed` and
   missing source to an adapter-generated source.
2. Explicit evidence could pair `unavailable` with a non-null value or a stronger
   status with null.
3. Harbor model/provider, agent, task, revision, and metric disagreements were silently
   reduced by precedence.
4. Missing Harbor list keys were converted to empty tool/network configuration even
   though the producer/version required to justify that default was not retained.
5. Coverage metadata was trusted after digest verification instead of being recomputed.
6. Mutable development code identified as final-looking `0.2.0`, and schema `$id`
   values used mutable `main` URLs.

## 2. Fixes made

- Partial provenance now fails schema validation; complete declarations pass through a
  shared contradiction check.
- Source candidates are reconciled only when their normalized values agree. Conflicts
  retain safe candidates under `extensions.harbor.source_conflicts`; standard evidence
  fields become unavailable, metrics become null, and task identity keeps only its
  addressing name with an explicit unresolved-comparison record.
- Task identity candidates use redacted digests, not copied private local paths.
- Missing Harbor list configuration remains unavailable; explicitly serialized empty
  lists remain a derived empty configuration.
- Verification recomputes field count, every status count, and available fraction.
- Development version is `0.2.0rc1`; `0.2.0` remains reserved for a frozen release.
- Schema document identities are immutable, versioned URNs.

## 3. Tests added

`tests/test_adversarial_semantics.py` covers absent, complete, partial, malformed, and
contradictory provenance; Harbor source conflicts; absent versus explicit-empty list
configuration; and re-digested false coverage. The readiness suite now exercises a
checked-in sanitized two-trial Harbor structural fixture with missing optionals, ATIF
v1.5/v1.6, an errored/unfinished trial, omitted defaults, and deliberate conflicts.

## 4. Readiness state

All four public technical gates are met by named, non-skipping tests. The separate
private-archive test remains optional and skips without external input. This is not a
release declaration: upstream mapping review, campaign completeness, independent
emission, paper authority, and PyPI/release authorization remain open.

## 5. Strongest evidence for the thesis

- A previous genuine comparison passed trial bundle verification but became not
  comparable after task checksum, denominator, and turn-budget drift were surfaced.
- The adversarial review found multiple places where convenient defaults upgraded or
  hid evidence state. Machine-checkable boundaries changed the outcome.
- Current Harbor retains multiple sources for identity and metrics, making disagreement
  representable and testable rather than merely philosophical.
- A sanitized genuine-layout fixture can exercise meaningful failure modes in public CI
  without redistributing benchmark content.

## 6. Strongest evidence against the thesis

- Current Harbor already has richer `JobLock`, `TrialLock`, `JobResult`, retry, task
  digest, and regrade-lineage primitives than Eval Evidence currently consumes.
- Campaign membership and aggregation can dominate trial-level correctness; sealing a
  selected subset does not make a publication claim honest.
- No real-archive conflict frequency has yet been measured. The public conflict fixture
  is adversarial, not prevalence evidence.
- Uniform `available_fraction` is coarse and gameable; it is not claim readiness.
- The current evidence for cross-framework portability is zero until a second evaluator
  experiment is run.

## 7. What should remain standalone for now

- The generic evidence-state vocabulary and conservative unavailable boundary.
- Deterministic offline bundle verification and safe content references.
- The small generic manifest as an experimental interchange surface.
- Read-only conflict and comparison diagnostics needed for the research studies.

These remain provisional research instruments, not a commitment to a permanent package.

## 8. What should move upstream if supported by experiments

- Expected attempts, retry/cancellation state, locks, response identity, and regrade
  lineage: Harbor.
- Task/verifier identity, score-component provenance, and acceptance conditions:
  Terminal-Bench and Fortify.
- Inclusion/exclusion, aggregation, uncertainty, and row publication identity:
  leaderboard or publication tooling.
- Eval Evidence should contribute only a portable reference/qualification primitive
  that is genuinely shared with another evaluator.

## 9. Next three highest-information experiments

1. Reconstruct expected/discovered/included denominators from genuine Harbor jobs and
   report unexplained deltas by version.
2. Run the retrospective recoverability and conflict census before applying precedence.
3. Compare claim-specific readiness decisions with uniform coverage on real candidate
   publication claims.

Prospective native capture and the Inspect translation follow these results; the order
can change if archive access blocks E1/E2.

## 10. Paper recommendation

Do not draft the main paper yet. Freeze the manuscript authority, preregister the first
three experiments and denominators, and write only after at least two yield a
generalizable empirical finding. A negative paper showing that campaign accounting or
native prospective capture subsumes most of Eval Evidence is a successful outcome.

## 11. Architecture recommendation

Keep the repository small and read-only. Do not add a scheduler, hosted registry,
plugin framework, or comprehensive campaign platform. Prototype campaign reconstruction
against Harbor's native job/lock models; prototype structured provenance as a companion
record; test one second evaluator. Then shrink, upstream, or remove components according
to measured overlap and portability.

## Unknowns that remain decision-relevant

- Real frequency and severity of retained-source conflicts.
- Version-stratified recoverability of denominators, selection, and aggregation.
- Whether native Harbor archive/upload custody already makes trial sealing redundant.
- Prospective capture cost and which identities providers can actually expose.
- Whether a second evaluator validates or breaks the generic contract.

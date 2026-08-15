# Architecture and authority map

Eval Evidence is an offline, post-run evidence layer. It does not execute an evaluation.
It converts retained evaluator artifacts into a deterministic evidence bundle, then
checks the bundle and selected referenced bytes inside a deliberately narrow trust
boundary.

## Runtime path

```text
run directory
    │
    ├─ generic eval-run.json ─┐
    └─ Harbor trial files ────┤
                              ▼
                         adapter detection
                              ▼
                         NormalizedRun
                              ▼
                 canonical bundle + SHA-256
                              ▼
                 schema/digest/reference checks
                              ▼
             scoped JSON report with explicit gaps
```

| Layer | Authority | Responsibility | Must not do |
|---|---|---|---|
| CLI | `eval_evidence/__main__.py` | argument handling, discovery orchestration, exit codes, JSON reporting | reinterpret adapter evidence or hide failures |
| Adapters | `eval_evidence/adapters.py` | detect input shape and map source values with provenance | execute models/verifiers, guess missing values, or copy secrets |
| Evidence model | `eval_evidence/models.py` | typed normalized run and evidence values | make harness-specific fields canonical |
| Bundle core | `eval_evidence/core.py` | canonical JSON, digests, schema checks, safe reference verification | claim signer authenticity or physical truth |
| Wire contracts | `eval_evidence/schemas/` | generic input, instrument, bundle, and informative crosswalk contracts | change meaning without the version policy |
| Product boundaries | `docs/TRUST_MODEL.md`, `docs/COMPATIBILITY.md` | supported claims, threats, versioning, and deprecation | be silently overridden by an adapter convenience |
| Current state | `PROJECT_HANDOFF.json`, `docs/READINESS.md` | development authority, gates, blocked decisions, next work | present local-only evidence as reproducible CI evidence |

## Data and evidence flow

An adapter returns `NormalizedRun`; it does not write output. Bundle construction hashes
the normalized claims and selected run-relative references. Verification can check the
bundle schema and embedded digest alone, or re-hash source files when `--run-root` is
provided. A content digest identifies bytes. It does not authenticate the runner,
establish when the original run occurred, or make the reported reward true.

Evidence status is part of the contract:

- `observed`: present in a named retained run artifact;
- `derived`: reproducibly computed from retained data;
- `operator_asserted`: supplied or reconstructed by an operator;
- `provider_asserted`: supplied by a provider-side source;
- `unavailable`: the retained evidence cannot establish the field.

Do not collapse these categories in code, fixtures, documentation, or visual labels.

## Adapter boundaries

The generic `eval-run.json` format is the framework-neutral contract. The Harbor adapter
is the first compatibility layer, not the canonical format. Its current supported and
unsupported layouts are enumerated in [`HARBOR_MAPPING.md`](HARBOR_MAPPING.md).

Adapter changes require tests for:

- deterministic detection and output;
- source provenance and honest unavailable state;
- malformed and missing input;
- compatibility warnings;
- traversal, symlink, collision, and overwrite safety where applicable; and
- exclusion of prompts, credentials, tool URLs/paths, and other unintended contents.

## Change ownership

| Change | Required review surface |
|---|---|
| CLI behavior or exit code | product tests, README, compatibility/changelog review |
| Adapter mapping | adapter tests, `HARBOR_MAPPING.md` or equivalent, provenance review |
| Wire meaning or required shape | schema version decision under `COMPATIBILITY.md` |
| Trust or security claim | `TRUST_MODEL.md`, `SECURITY.md`, negative test |
| Figure semantics | semantic brief, render manifest, source map, figure verifier, README-width and mobile inspection |
| Gate status | executable named test plus `READINESS.md` and `PROJECT_HANDOFF.json` |
| Release claim | maintainer handoff, installed distribution dogfood, exact artifact hashes, protected CI |

## Definition of done

A change is not complete merely because its focused test passes. It is complete when the
code, contract, tests, documentation, visual/source map where relevant, and handoff
status agree—and when the final report states the proof boundary and remaining gaps.

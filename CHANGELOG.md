# Changelog

All notable package, wire-contract, and adapter-compatibility changes are recorded here.

## 0.2.0rc1 (unreleased candidate, 2026-08-15)

- Reject partial or contradictory generic provenance declarations instead of allowing
  them to acquire stronger evidence semantics through defaults.
- Preserve contradictory Harbor source values as structured conflicts and make the
  normalized value unavailable rather than silently selecting by precedence.
- Recompute coverage during verification and reject internally inconsistent metadata.
- Distinguish absent Harbor list configuration from explicitly serialized empty lists.
- Give schema documents immutable, versioned URN identities and reserve `0.2.0`
  for a future frozen release.

### Added

- Executable external-sharing readiness gates and distribution dogfood protocol.
- Harbor trajectory-version compatibility metadata and non-failing `check` warnings.
- Harbor mapping review table and `inspect --explain` field-source output.
- Optional `check --min-coverage` CI gate.
- Compatibility, contribution, and support policies.
- A product-lifecycle guide covering pre-run capture setup, post-run sealing,
  retrospective reprocessing without model compute, and static comparison reports.
- Source-mapped lifecycle and command-switchboard figures with deterministic SVG
  generation, locked local raster provenance, accessibility metadata, overflow checks,
  and explicit proof boundaries.
- Three source-mapped visual stories that show retained files becoming an evidence
  envelope, open `check` into six concrete gates, and demonstrate a later byte mismatch;
  the command switchboard is now a plain-language index rather than an implementation
  summary. The complete figure set now uses one high-contrast visual system.

### Changed

- Generic `eval-run.json` instrument values and plain claims without declared
  provenance now default to `operator_asserted` rather than `observed`. Emitters must
  declare provenance explicitly to make a stronger claim; this is a pre-adoption
  breaking evidence-status semantic correction that alters emitted bundle bytes,
  expectations, and pinned digests for provenance-free input while keeping wire versions
  unchanged (see `docs/COMPATIBILITY.md`). Coverage fractions remain unchanged.
- The synthetic Harbor fixture now exercises the resolved agent wall-time mapping and
  top-level multipliers; its pinned demonstration-bundle digest changed with those
  fixture bytes.
- `check` reports tool and bundle-schema versions.
- `check` now separates integrity results (`valid` and `errors`) from coverage-policy
  results (`policy_passed` and `policy_errors`).

### Fixed

- Harbor token and cost metrics now fall back to trajectory totals when the primary
  `result.json` value is absent or explicitly `null`.
- Harbor agent wall-time now computes `min(override base, optional cap) * resolved
  multiplier`, exposes the components under `extensions.harbor.timeout`, and never
  mistakes `max_timeout_sec` alone for an effective budget. Legacy
  `result.json:agent_result.timeout_sec` remains an observed fallback and is not
  multiplied again.
- Synthetic demo files are written as explicit UTF-8/LF bytes so their pinned bundle
  digests are identical on Windows, macOS, and Linux.
- The Harbor adapter now recognizes the observed `ATIF-v1.5` and `ATIF-v1.6` root
  surfaces alongside `ATIF-v1.7`; unrelated versions still warn without failing.
- The Terminal-Bench review brief now distinguishes Harbor's viewer/job semantics from
  per-trial sealing and exposes unsupported multi-step, regrade, and campaign surfaces
  before maintainer review.
- Harbor network configuration now retains environment-baseline and agent-phase host
  additions as separate configured layers; an unfinished result no longer defaults to
  a `completed` termination reason without a non-null `finished_at`.
- Harbor tool configuration is represented by counts and canonical hashes, and verifier
  configuration is reduced to selected non-secret fields instead of copying tool paths,
  URLs, environment values, kwargs, or import paths into the bundle.

### Security

- Added negative tests for stale bundle digests and documented that an attacker can
  edit and re-digest an unsigned bundle.
- Distribution audits now reject workspace-only `artifacts/` evidence records if they
  are ever added to a wheel or sdist.

## 0.1.0

- Initial generic and Harbor adapters.
- Deterministic v0.1 evidence bundles, schema validation, content digests, and local
  referenced-file verification.
- GitHub Action and OIDC-gated PyPI publishing workflow.

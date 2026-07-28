# Changelog

All notable package, wire-contract, and adapter-compatibility changes are recorded here.

## 0.2.0 (unreleased candidate, 2026-07-27)

### Added

- Executable external-sharing readiness gates and distribution dogfood protocol.
- Harbor trajectory-version compatibility metadata and non-failing `check` warnings.
- Harbor mapping review table and `inspect --explain` field-source output.
- Optional `check --min-coverage` CI gate.
- Compatibility, contribution, and support policies.
- A product-lifecycle guide covering pre-run capture setup, post-run sealing,
  retrospective reprocessing without model compute, and static comparison reports.

### Changed

- The synthetic Harbor fixture now exercises the agent wall-time mapping; its pinned
  demonstration-bundle digest changed with those fixture bytes.
- `check` reports tool and bundle-schema versions.
- `check` now separates integrity results (`valid` and `errors`) from coverage-policy
  results (`policy_passed` and `policy_errors`).

### Fixed

- Harbor token and cost metrics now fall back to trajectory totals when the primary
  `result.json` value is absent or explicitly `null`.
- Harbor agent wall-time now falls back to `result.json:agent_result.timeout_sec` when
  both configured agent timeout fields are absent or `null`, as found in genuine runs.

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

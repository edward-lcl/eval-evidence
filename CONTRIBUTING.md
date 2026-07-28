# Contributing

## Report an adapter mismatch

Open an issue at <https://github.com/edward-lcl/eval-evidence/issues> with the Eval
Evidence version, Harbor/ATIF version, the field that was wrong or unavailable, and the
expected JSON path. When safe, attach a minimal **redacted structural fixture** derived
from `result.json` and/or `config.json`; include `agent/trajectory.json` only if the
shape itself is necessary. The Harbor review table is in
[`docs/HARBOR_MAPPING.md`](docs/HARBOR_MAPPING.md).

## Adapter contract

Read [`docs/ADAPTERS.md`](docs/ADAPTERS.md) before changing detection or normalization.
Adapter changes need tests for provenance, missing fields, compatibility warnings, and
deterministic bundle output. If bundle semantics change, apply the version policy in
[`docs/COMPATIBILITY.md`](docs/COMPATIBILITY.md) rather than silently changing v0.1.

## No benchmark data in issues

Do not post benchmark tasks, prompts, trajectories, model outputs, credentials,
customer data, or private run archives. `NOTICE` excludes benchmark corpora and
trajectory archives from the release. Prefer fabricated fixtures; otherwise redact
identifiers and values locally before attaching the smallest shape needed to reproduce
the mapping. Report security-sensitive data exposure privately through `SECURITY.md`.

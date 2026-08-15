# Contributing

Start with [`docs/START_HERE.md`](docs/START_HERE.md), then read
[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) and the selected work item's acceptance
criteria in [`PROJECT_HANDOFF.json`](PROJECT_HANDOFF.json). Preserve unrelated local
changes, use a feature branch or isolated worktree, and keep one writer per checkout.

## Development loop

```bash
python -m pip install -e '.[test]'
python -m unittest discover -s tests -v
python scripts/verify_figure.py
uv build --offline --wheel --sdist --out-dir /tmp/eval-evidence-dist
python scripts/audit_distribution.py /tmp/eval-evidence-dist
```

A change is reviewable when focused and full tests pass; code, schemas, documentation,
figures, and handoff status agree; and the description states both what was proved and
what remains unproved. Update `PROJECT_HANDOFF.json` only when executable evidence or a
recorded owner decision changes its status.

Before requesting review, confirm:

- no benchmark prompts, trajectories, credentials, private identifiers, or raw run
  archives entered the diff;
- adapter mappings preserve provenance and honest `unavailable` state;
- wire changes follow `docs/COMPATIBILITY.md`;
- figures rebuild from their semantic briefs and remain readable in portrait and wide
  layouts; and
- release, G2, paper-authority, and upstream-endorsement claims remain behind their
  named approval boundaries.

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

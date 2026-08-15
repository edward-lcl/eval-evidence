# Maintainer handoff

This is the owner-only continuation of the shared [handoff router](START_HERE.md).
Machine-readable gate status, work ownership, and approval boundaries live in
[`PROJECT_HANDOFF.json`](../PROJECT_HANDOFF.json); keep this page and that file aligned.

## Product identity

- Project: **Eval Evidence**
- Repository: `https://github.com/edward-lcl/eval-evidence`
- Distribution / CLI: `eval-evidence`
- Python import: `eval_evidence`
- License: Apache-2.0
- Maintainer/security: Edward Lue Chee Lip (`eluecheelip@gmail.com`)

The initially considered PyPI name `eval-integrity` is owned by an unrelated project.
`eval-evidence` was the recorded fallback and is the only identity used here.

## What the 0.2.0 candidate contains

- generic `eval-run.json` adapter;
- Harbor trial adapter;
- `check` and `bundle` primary UX plus `inspect`, `verify`, and `audit` compatibility;
- canonical JSON/SHA-256 bundle and instrument schemas;
- deterministic generic and Harbor demos;
- traversal, symlink, mutation, malformed-run, collision, and source-overwrite guards;
- composite GitHub Action constrained to `GITHUB_WORKSPACE`;
- Apache-2.0 wheel/sdist boundary audit.

It contains no benchmark corpus, Parquet tables, raw trajectories, manuscripts, model
execution, hosted registry, signing implementation, or Harbor source.

## Verification commands

```bash
python -m pip install -e '.[test]'
python -m unittest discover -s tests -v
python -m py_compile eval_evidence/*.py
uv build --offline --wheel --sdist --out-dir dist
python scripts/audit_distribution.py dist
```

The distribution audit proves archive scope and metadata eligibility. It deliberately
reports `authorized_for_distribution: false`: no local script can substitute for the
owner's release decision, protected CI, tag, and published-hash verification.

Then install the wheel into a clean virtual environment and run:

```bash
eval-evidence demo -o /tmp/demo
eval-evidence check /tmp/demo
eval-evidence bundle /tmp/demo -o /tmp/evidence.json
eval-evidence verify /tmp/evidence.json --run-root /tmp/demo
```

## Release state

Protected `main` is the current development authority for the reviewed 0.2.0 candidate.
Historical pull requests document review history but are not installation or release
authorities. No `v0.2.0` tag or PyPI release exists yet.

The GitHub repository and CI are public. GitHub CI covers Python 3.11–3.14, distribution
scope, installed-wheel dogfood on Linux/macOS/Windows, and the composite action. The repository-side PyPI Trusted
Publishing path is configured without a stored token: `.github/workflows/publish-pypi.yml`
downloads the exact audited GitHub release assets, verifies `SHA256SUMS`, and publishes
from the protected `pypi` environment using a short-lived OIDC credential.

Publication is not the only remaining readiness step. The genuine-Harbor G2 gate still
needs an approved sanitized fixture or secure CI access, and the Terminal-Bench/Harbor
mapping review is pending. Separately, the remaining PyPI infrastructure step is to
register this pending publisher while logged into PyPI:

- PyPI project: `eval-evidence`
- GitHub owner: `edward-lcl`
- repository: `eval-evidence`
- workflow: `publish-pypi.yml`
- environment: `pypi`

A pending publisher does not reserve the name. After registering it, dispatch **Publish
to PyPI** with tag `v0.2.0`; successful publication creates the project and converts the
publisher to a normal trusted publisher. Do not claim PyPI availability until the
project page exists and the published hashes match the audited release.

## Next highest-value milestone

Complete the narrow Harbor maintainer review in [`TBENCH_REVIEW.md`](TBENCH_REVIEW.md):
correct the mapping, choose a reproducible G2 fixture route, and decide the source of a
future job-level denominator/index contract. Do not mistake per-trial bundle discovery
for campaign membership or aggregate-score evidence.

After that review, obtain one real consumer outside the original analysis repository.
Prefer a small integration that emits `eval-run.json`; use the built-in Harbor adapter
as proof that the normalized contract is not tied to one framework. Record friction
before adding a plugin system or more adapters.

Only after a real consumer:

1. decide whether Python entry-point plugins are necessary;
2. define a reviewed signing profile from `docs/TRUST_MODEL.md`;
3. consider an optional transport mapping or upstream Harbor emitter.

Do not build a hosted registry, global leaderboard, model runner, microVM runtime, or
physical-verification service before the evidence contract has external adoption.

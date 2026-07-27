# Maintainer handoff

## Product identity

- Project: **Eval Evidence**
- Repository: `https://github.com/edward-lcl/eval-evidence`
- Distribution / CLI: `eval-evidence`
- Python import: `eval_evidence`
- License: Apache-2.0
- Maintainer/security: Edward Lue Chee Lip (`eluecheelip@gmail.com`)

The initially considered PyPI name `eval-integrity` is owned by an unrelated project.
`eval-evidence` was the recorded fallback and is the only identity used here.

## What v0.1 contains

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

Then install the wheel into a clean virtual environment and run:

```bash
eval-evidence demo -o /tmp/demo
eval-evidence check /tmp/demo
eval-evidence bundle /tmp/demo -o /tmp/evidence.json
eval-evidence verify /tmp/evidence.json --run-root /tmp/demo
```

## Release state

The GitHub repository and CI are public. GitHub CI covers Python 3.11–3.13, distribution
scope, installed-wheel demo, and the composite action. PyPI publication is a separate
remaining gate because this environment has no PyPI token or configured Trusted
Publisher. Do not claim PyPI availability until the project page exists and the
published artifacts reproduce the audited release.

## Next highest-value milestone

Obtain one real consumer outside the original analysis repository. Prefer a small
integration that emits `eval-run.json`; use the built-in Harbor adapter as proof that
the normalized contract is not tied to one framework. Record friction before adding a
plugin system or more adapters.

Only after a real consumer:

1. decide whether Python entry-point plugins are necessary;
2. define a reviewed signing profile from `docs/TRUST_MODEL.md`;
3. consider an optional transport mapping or upstream Harbor emitter.

Do not build a hosted registry, global leaderboard, model runner, microVM runtime, or
physical-verification service before the evidence contract has external adoption.

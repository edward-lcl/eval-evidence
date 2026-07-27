# Eval Evidence

**Machine-checkable evidence for AI evaluation runs.**

> A score should travel with a machine-checkable record of what was observed,
> asserted, derived, and unavailable.

Eval Evidence produces a deterministic JSON bundle that joins three questions without
collapsing them into another score:

1. **Is the item valid?** Carry item-validity claims—or state that none were supplied.
2. **What instrument produced the result?** Record model, agent, harness, budgets, and
   other fields with explicit provenance and coverage.
3. **What does the verifier establish?** Keep reward and reward-independent evidence
   separate.

It works offline, runs no models, uploads nothing, and treats missing evidence as
`unavailable` rather than guessing.

## Five-minute quickstart

Python 3.11+:

```bash
python -m pip install "eval-evidence @ git+https://github.com/edward-lcl/eval-evidence@v0.1.0"
eval-evidence demo -o /tmp/eval-run
eval-evidence check /tmp/eval-run
eval-evidence bundle /tmp/eval-run -o /tmp/eval-evidence.json
eval-evidence verify /tmp/eval-evidence.json --run-root /tmp/eval-run
```

The demo is deterministic and synthetic. `check` is the one-command path: it detects
the input adapter, builds a bundle in memory, validates the schema and digest, re-hashes
local references, and reports evidence coverage.

## Works with any evaluation stack

### Generic manifest

Add one `eval-run.json` next to your run outputs:

```json
{
  "schema_version": "eval-evidence.run/v0.1",
  "run": {"id": "run-42", "task_id": "task-7", "task_revision": "abc123"},
  "instrument": {
    "model_id": "provider/model",
    "harness_name": "my-evaluator",
    "harness_version": "2.4.0",
    "max_turns": 20
  },
  "metrics": {"input_tokens": 1200, "output_tokens": 300},
  "outcome": {"reward": 1, "scores": {"tests": 1}, "termination_reason": "completed"},
  "references": [
    {"path": "results.json", "role": "score-output"},
    {"path": "logs/events.json", "role": "execution-log", "required": false}
  ]
}
```

Then run:

```bash
eval-evidence check /path/to/run
eval-evidence bundle /path/to/run -o evidence.json
```

### Harbor

Harbor trial directories are detected directly from `result.json`, `config.json`, and
`agent/trajectory.json`:

```bash
eval-evidence check /path/to/harbor-job
eval-evidence bundle /path/to/harbor-job -o evidence/
```

Harbor is the first adapter, not the canonical format. See
[`docs/ADAPTERS.md`](docs/ADAPTERS.md) to integrate another evaluator.

## One entry point per audience

| Audience | Start here | Benefit |
|---|---|---|
| Benchmark maintainers | `eval-evidence check ./runs` in CI | Detect malformed, mutated, and evidence-poor run records before release |
| Frontier labs and eval teams | Emit `eval-run.json` | Carry instrument settings and unavailable state across harness boundaries |
| Reviewers and auditors | `verify` offline | Check schema, digest, and referenced bytes without executing the evaluation |
| Runtime and physical-verification teams | Populate future attestation profiles | Reuse the evidence format while adding a separately scoped trust layer |

## GitHub Action

Pin the action to a release tag or commit:

```yaml
- uses: edward-lcl/eval-evidence@v0.1.0
  with:
    run-path: evaluation-runs
    adapter: auto
```

`run-path` must remain inside the checked-out repository. Absolute paths, `..`, and
resolved escapes are rejected.

## What a bundle does not prove

- A SHA-256 digest identifies bytes; it is not a trusted-runner signature.
- A reported reward is not ground truth.
- A signature can authenticate a signer and scoped claims; it cannot make claims true.
- Provider-side policy, prompt assembly, or effective network enforcement remain
  unavailable unless the run records them.
- Eval Evidence hashes referenced files but does not copy prompts, trajectories,
  credentials, or environment variables into the bundle.
- This tool is not a leaderboard, model runner, certification authority, hosted
  registry, or physical-verification system.

Version 0.1 intentionally emits `attestation.signature: null`. The trust model in
[`docs/TRUST_MODEL.md`](docs/TRUST_MODEL.md) describes the gate before signing or a
physical verifier is added.

## Contracts and identity

The distribution includes four contracts/crosswalks under `eval_evidence/schemas/`:

- generic run manifest: `eval-evidence.run/v0.1`;
- evidence bundle: `eval-evidence.bundle/v0.1`;
- instrument manifest: `eval-evidence.instrument/v0.1`;
- informative OpenTelemetry GenAI crosswalk.

A schema's HTTPS `$id` identifies its published document. The `schema_version` string
inside a run or bundle is the wire contract. The package/CLI name is `eval-evidence`,
and the Python import is `eval_evidence`; these are deliberately distinct layers.

## Development

```bash
python -m pip install -e '.[test]'
python -m unittest discover -s tests -v
python -m build --wheel --sdist --outdir dist
python scripts/audit_distribution.py dist
```

See the [bundle specification](docs/BUNDLE_SPEC.md), [adapter guide](docs/ADAPTERS.md),
[trust model](docs/TRUST_MODEL.md), and [security policy](SECURITY.md).

## License

Apache-2.0. `NOTICE` describes the exact release boundary. No benchmark corpus,
trajectory archive, manuscript, or third-party source tree is included.

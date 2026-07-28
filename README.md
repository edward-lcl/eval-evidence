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

Python 3.11–3.14:

```bash
python -m pip install "eval-evidence @ git+https://github.com/edward-lcl/eval-evidence@main"
eval-evidence demo -o /tmp/eval-run
eval-evidence check /tmp/eval-run
eval-evidence bundle /tmp/eval-run -o /tmp/eval-evidence.json
eval-evidence verify /tmp/eval-evidence.json --run-root /tmp/eval-run
```

The demo is deterministic and synthetic. `check` is the one-command path: it detects
the input adapter, builds a bundle in memory, validates the schema and digest, re-hashes
local references, and reports evidence coverage. Use `check --min-coverage 0.5` when CI
should reject a run with less than 50% of instrument fields available. Coverage
shortfalls appear under `policy_errors`; they return exit 1 without mislabeling schema,
digest, or reference integrity as invalid.

## Use it before, after, or on prior runs

| When | How Eval Evidence fits |
|---|---|
| Before a new run | Configure the existing harness to retain model-response identity, instrument settings, task/environment/verifier digests, and source artifacts. v0.2 does not yet provide a preflight or live monitor. |
| After a run | Run `check`, seal a bundle, store it separately, and verify it against the stable run root. |
| On historical runs | Reprocess retained Harbor trials directly, or add an honestly sourced generic manifest to a preserved copy. No model rerun is required. Missing historical evidence remains `unavailable`. |
| When publishing | Compare recorded conditions and disclose integrity failures, material differences, unknowns, denominators, and exclusions. Campaign packages and generated comparison reports are future work. |

A retrospective bundle establishes archive identity from the time it is created; it
cannot prove the archive was unchanged since the original evaluation without an older
trusted baseline. See the [product lifecycle](docs/LIFECYCLE.md) for prospective setup,
retrospective import, and the role of static graphics.

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

For manually assembled manifests, add `provenance` entries rather than allowing a
system-card claim or operator-entered value to look like a run-time observation. See
the [owner walkthrough](docs/OWNER_WALKTHROUGH.md) for a complete application example
and a paired-result investigation.

### Harbor

Harbor trial directories are detected directly from `result.json`, `config.json`, and
`agent/trajectory.json`:

```bash
eval-evidence check /path/to/harbor-job
eval-evidence bundle /path/to/harbor-job -o evidence/
```

Harbor is the first adapter, not the canonical format. See the reviewable
[`Harbor field mapping`](docs/HARBOR_MAPPING.md) and
[`adapter guide`](docs/ADAPTERS.md) to inspect it or integrate another evaluator.

## One entry point per audience

| Audience | Start here | Benefit |
|---|---|---|
| Benchmark maintainers | `eval-evidence check ./runs` in CI | Detect malformed, mutated, and evidence-poor run records before release |
| Frontier labs and eval teams | Emit `eval-run.json` | Carry instrument settings and unavailable state across harness boundaries |
| Reviewers and auditors | `verify` offline | Check schema, digest, and referenced bytes without executing the evaluation |
| Runtime and physical-verification teams | Populate future attestation profiles | Reuse the evidence format while adding a separately scoped trust layer |

## GitHub Action

During the 0.2.0 pre-release review, use `main`; for production, replace it with the
reviewed commit SHA or `v0.2.0` after that tag exists:

```yaml
- uses: edward-lcl/eval-evidence@main
  with:
    run-path: evaluation-runs
    adapter: auto
```

The `main` install above is intentional while 0.2.0 is under review; the older
`v0.1.0` tag does not provide `--min-coverage`, `inspect --explain`, or Harbor schema
compatibility warnings.

`run-path` must remain inside the checked-out repository. Absolute paths, `..`, and
resolved escapes are rejected. The action also accepts optional `max-runs` and
`min-coverage` inputs.

## Exit codes and verification boundary

| Exit | Meaning |
|---|---|
| `0` | Command completed and all requested checks passed. |
| `1` | Checks completed, but a run/bundle was invalid, a reference differed, or a requested coverage threshold was missed. |
| `2` | Usage, discovery, unsafe-path, malformed-input, or output precondition error prevented the requested check. |

`verify BUNDLE` without `--run-root` checks the JSON schema and whether the bundle's
claims match its embedded digest. It does **not** re-hash source files. Add
`--run-root PATH` to compare referenced files with local bytes. Neither mode proves who
created the bundle: anyone who edits an unsigned bundle can recompute its digest.

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

The v0.1 bundle contract intentionally emits `attestation.signature: null`. The trust model in
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

See the [readiness gates](docs/READINESS.md),
[product lifecycle](docs/LIFECYCLE.md),
[owner walkthrough](docs/OWNER_WALKTHROUGH.md),
[Terminal-Bench review brief](docs/TBENCH_REVIEW.md),
[bundle specification](docs/BUNDLE_SPEC.md), [adapter guide](docs/ADAPTERS.md),
[compatibility policy](docs/COMPATIBILITY.md), [trust model](docs/TRUST_MODEL.md),
and [security policy](SECURITY.md).

## License

Apache-2.0. `NOTICE` describes the exact release boundary. No benchmark corpus,
trajectory archive, manuscript, or third-party source tree is included.

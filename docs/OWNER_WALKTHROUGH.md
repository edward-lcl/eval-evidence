# Owner walkthrough: from application run to a reviewable comparison

Use this walkthrough before sharing Eval Evidence with Terminal-Bench and when a
published result looks surprising. The running example is a claim such as “model A
scored above model B when prior expectations suggested the reverse.” It applies to an
Opus/Fable comparison, but it does not assume either ordering is correct.

## What this can and cannot answer

Eval Evidence can falsify narrower claims that often hide behind a headline score:

- the cited files still match the bytes that were bundled;
- both results used the same task identity/revision and verifier evidence;
- the requested/recorded model, agent, harness, budgets, tools, and environment were
  captured and comparable;
- absent evidence is visible rather than silently treated as equivalent;
- Harbor fields were mapped from the source paths the reviewer expected.

It **cannot** establish that a model “should” rank above another, that a reward measures
the intended capability, that a system card describes the model actually served for a
specific request, or that consistently fabricated artifacts are true. A public aggregate
score or system card alone is not enough: this workflow needs run-level artifacts.

The useful outcomes are therefore:

1. **integrity failure** — the published run bytes differ from the baseline bundle;
2. **comparability failure** — the runs differ in task, instrument, harness, verifier,
   or another material condition;
3. **evidence gap** — the comparison might be valid, but the records cannot establish
   it;
4. **not falsified** — integrity and recorded conditions align, so the surprising score
   remains plausible and needs task-level/statistical or verifier investigation outside
   this tool.

“Not falsified” is not “proven correct.”

## Session 1 — rehearse the user path

Do this from a clean virtual environment, not an editable checkout. During the 0.2.0
review, install the reviewed wheel you built; after publication, use the exact released
wheel and record its SHA-256.

```bash
python3 -m venv /tmp/ee-owner-venv
/tmp/ee-owner-venv/bin/python -m pip install /path/to/eval_evidence-0.2.0-py3-none-any.whl
/tmp/ee-owner-venv/bin/eval-evidence --version

python3 -c 'import hashlib, pathlib, sys; p=pathlib.Path(sys.argv[1]); print(hashlib.sha256(p.read_bytes()).hexdigest(), p)' \
  /path/to/eval_evidence-0.2.0-py3-none-any.whl

rm -rf /tmp/ee-owner-demo
/tmp/ee-owner-venv/bin/eval-evidence demo --format harbor -o /tmp/ee-owner-demo
/tmp/ee-owner-venv/bin/eval-evidence check /tmp/ee-owner-demo
/tmp/ee-owner-venv/bin/eval-evidence inspect /tmp/ee-owner-demo --explain
/tmp/ee-owner-venv/bin/eval-evidence bundle /tmp/ee-owner-demo -o /tmp/ee-owner-demo.bundle.json
/tmp/ee-owner-venv/bin/eval-evidence verify /tmp/ee-owner-demo.bundle.json \
  --run-root /tmp/ee-owner-demo
```

Windows users should substitute `Scripts/python.exe` and
`Scripts/eval-evidence.exe`. Record:

- wheel filename and SHA-256;
- Python, OS, and `eval-evidence --version` output;
- every command and exit code;
- any instruction you had to change. A required undocumented correction is a product or
  documentation failure, even if the command eventually succeeds.

Then run the complete clean-wheel and tamper protocol in [`DOGFOOD.md`](DOGFOOD.md).
Do not proceed to a real comparison until the rehearsal exits as documented.

## Session 2A — integrate a normal application or evaluator

Use this route when the application does not produce a Harbor trial. At the end of each
run, place `eval-run.json` beside the outputs it describes. Reference only files below
that run root. Capture values from run-time records rather than reconstructing them later
from release notes.

Prioritize these instrument fields for model comparisons:

| Field | Why it matters |
|---|---|
| `model_id`, `model_provider`, `response_model` | Distinguish the requested label from the model identity returned at run time. |
| `agent_name`, `agent_version`, `agent_binary_sha256` | Agent scaffolding can materially change benchmark performance. |
| `harness_name`, `harness_version`, `harness_commit` | Detect evaluator drift between result sets. |
| `tools`, `max_turns`, `max_wall_time_s` | Compare capability and budget. |
| `effort_or_thinking`, `sampling_parameters` | Compare inference settings and stochastic conditions. |
| `system_prompt_sha256`, `policy_profile_id` | Compare prompt/policy bytes without copying sensitive text. |
| `task_checksum`, `environment_image_digest`, `verifier_digest` | Establish task, environment, and scorer comparability. |
| `network_policy` | Record configured access; it is not proof of enforcement. |

Use `provenance` honestly. A value copied from a system card is
`provider_asserted`; a value typed by the operator is `operator_asserted`. Reserve
`observed` for a value captured in a named run artifact, and name that artifact in
`source`. An instrument value omitted from `provenance` defaults to
`operator_asserted`, never `observed`. For example:

```json
{
  "schema_version": "eval-evidence.run/v0.1",
  "run": {"id": "run-a-task-17", "task_id": "task-17", "task_revision": "rev-3"},
  "instrument": {
    "model_id": "requested-model-alias",
    "response_model": "model-id-returned-by-api",
    "harness_commit": "0123456789abcdef",
    "task_checksum": "sha256:replace-with-real-value",
    "verifier_digest": "sha256:replace-with-real-value"
  },
  "provenance": {
    "model_id": {
      "status": "operator_asserted",
      "source": "runner request configuration"
    },
    "response_model": {
      "status": "observed",
      "source": "responses/response-metadata.json:model"
    },
    "harness_commit": {
      "status": "observed",
      "source": "runner/build-info.json:git_commit"
    },
    "task_checksum": {
      "status": "derived",
      "source": "sha256(task-package)"
    },
    "verifier_digest": {
      "status": "derived",
      "source": "sha256(verifier-package)"
    }
  },
  "metrics": {"input_tokens": 1200, "output_tokens": 300},
  "outcome": {"reward": 1, "scores": {"tests": 1}, "termination_reason": "completed"},
  "references": [
    {"path": "responses/response-metadata.json", "role": "provider-response-metadata"},
    {"path": "outputs/scores.json", "role": "score-output"},
    {"path": "runner/build-info.json", "role": "harness-build-metadata"}
  ]
}
```

The strings above are placeholders, not recommended values. Validate and bundle each
finished run:

```bash
eval-evidence check /path/to/run --adapter generic
eval-evidence inspect /path/to/run --adapter generic --explain
eval-evidence bundle /path/to/run --adapter generic -o /separate/evidence/run.json
eval-evidence verify /separate/evidence/run.json --run-root /path/to/run
```

Create the baseline bundle while the run directory is stable. Bundling after an
unnoticed mutation merely records the mutated bytes; tamper detection is always
relative to an earlier trusted digest baseline.

## Session 2B — process a real Harbor job

A Harbor trial is auto-detected from `result.json`, `config.json`, and
`agent/trajectory.json`. Start at the job root:

```bash
mkdir -p /secure/ee-review/model-a /secure/ee-review/model-b

eval-evidence check /secure/harbor/model-a --adapter harbor \
  > /secure/ee-review/model-a/check.json
eval-evidence inspect /secure/harbor/model-a --adapter harbor --explain \
  > /secure/ee-review/model-a/inspect.json
eval-evidence bundle /secure/harbor/model-a --adapter harbor \
  -o /secure/ee-review/model-a/bundles

# Repeat the same three commands for model B.
```

Immediately inspect the command exit code and JSON after each command. `check.json`
lists each discovered trial's `root`, `run_id`, `task_id`, coverage, warnings, and
errors. When more than one trial is discovered, `bundle` writes one JSON file per run.
To re-hash source files, verify each bundle against the **trial root shown by `check`**,
not merely the parent job directory:

```bash
eval-evidence verify /secure/ee-review/model-a/bundles/RUN_ID.eval-evidence.json \
  --run-root /secure/harbor/model-a/PATH/TO/THAT/TRIAL
```

The exact bundle filename is reported by `bundle`; do not guess it from the example.
Follow the source/value spot-check in [`DOGFOOD.md`](DOGFOOD.md) and red-line
[`HARBOR_MAPPING.md`](HARBOR_MAPPING.md). `inspect --explain` shows mapping sources;
the generated bundle holds the corresponding values and provenance statuses.

For model-identity questions, note the current Harbor boundary: `model_id` is mapped
best-effort from result/config/trajectory data, while `response_model` is currently
unavailable. Unless Harbor captured the provider-returned identity elsewhere and the
mapping is reviewed, a requested model label does not establish which backend model
served the run. That is an evidence gap to report, not a value to infer from a system
card.

## Session 3 — test the tamper claim safely

Never modify the only copy of a real run. Copy one trial to disposable storage, bundle
it, alter one referenced file, and verify the pre-mutation bundle:

```bash
rm -rf /tmp/ee-tamper-trial /tmp/ee-before-tamper.json
cp -R /secure/harbor/model-a/PATH/TO/TRIAL /tmp/ee-tamper-trial
eval-evidence bundle /tmp/ee-tamper-trial -o /tmp/ee-before-tamper.json
printf '\n' >> /tmp/ee-tamper-trial/result.json
eval-evidence verify /tmp/ee-before-tamper.json --run-root /tmp/ee-tamper-trial
echo $?
```

Expected: exit `1`, `valid: false`, and an error naming `result.json`. Then edit a copy
of the bundle without recomputing `bundle_digest`; `verify` should report `Bundle
digest mismatch`. The automated variants are in `scripts/dogfood.sh`.

Also demonstrate the boundary once: an attacker can edit an unsigned bundle and
recompute its digest. That bundle is internally consistent and will pass verification
without an independent trusted baseline or signature.

## Session 4 — adjudicate a surprising model comparison

Select matched trials before looking at the headline aggregate. For every model A/model
B pair, answer the following from the bundles and their referenced source records:

- Are `task_id`, `task_revision`, and `task_checksum` equal?
- Are the number of attempted, failed, timed-out, and excluded trials accounted for?
- Do model identity and provider have run-specific evidence? Is a returned
  `response_model` captured, or only a requested alias?
- Are agent version/binary, harness commit, tools, turn/time budget, thinking effort,
  sampling parameters, prompt hash, and network configuration equal or intentionally
  controlled?
- Are environment and verifier digests equal?
- Are item-validity and reward-independent verifier claims present, or is the only fact
  a reported reward?
- Do both bundles verify against preserved run roots?
- Are compatibility warnings, missing optional files, and unavailable-heavy runs
  included in the interpretation?

Do not treat equal aggregate rewards as matched evidence, and do not treat unequal
aggregate rewards as an integrity failure. Use per-task results and repeated trials to
estimate variance outside Eval Evidence; this package currently does not run models,
aggregate leaderboards, or perform significance tests.

### Decision record

For each discrepancy, write one conclusion and link the exact bundle/report fields:

| Conclusion | Required evidence | Next action |
|---|---|---|
| Integrity failure | Digest, schema, or referenced-file error | Quarantine the result; recover/rebuild from a preserved baseline. |
| Not comparable | Material task/instrument/harness/verifier difference | Re-run under matched conditions or qualify the published claim. |
| Inconclusive | A material field is unavailable or only weakly asserted | Ask the runner/provider to capture the missing run-time evidence. |
| Not falsified | Integrity passes and recorded material conditions align | Review task validity, verifier construct, exclusions, contamination, and trial-level statistics. |

A result such as “Opus scored above Fable” is therefore not something Eval Evidence
mechanically fixes or reverses. The tool makes the comparison auditable enough to say
whether the ranking rests on intact, matched, sufficiently identified runs—and makes it
explicit when the available artifacts cannot support that statement.

## Owner sign-off before sharing

Copy [`OWNER_DOGFOOD_REPORT_TEMPLATE.md`](OWNER_DOGFOOD_REPORT_TEMPLATE.md) into a
dated private report, then fill this sign-off checklist:

- [ ] Exact wheel/sdist or commit tested, with SHA-256.
- [ ] Clean-environment demo and `scripts/dogfood.sh` passed with captured exit codes.
- [ ] Genuine multi-trial Harbor job passed the G2 protocol, including a missing
      optional file.
- [ ] An approved sanitized or secure fixture lets the G2 test run without a skip in
      regular CI before the gate is marked `met`.
- [ ] Every `real-trial` row in `HARBOR_MAPPING.md` was checked against source JSON.
- [ ] A disposable real trial detected referenced-file tampering and named the path.
- [ ] At least one paired comparison was classified using the decision table above.
- [ ] Missing model identity, verifier, task, or environment evidence was reported as
      unavailable—not inferred from a system card or score.
- [ ] No benchmark data, prompts, trajectories, credentials, or private identifiers were
      copied into the public report.
- [ ] A second person followed the public README without undocumented corrections.

Keep raw artifacts private. Publish only the redacted environment, commands, exit codes,
digests, coverage summaries, mapping decisions, and limitations permitted by the data
owner.

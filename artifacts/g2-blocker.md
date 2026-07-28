# G2 remaining blocker record

Recorded 2026-07-28. Genuine multi-trial Harbor data **is** locally reachable and was exercised successfully. G2 nevertheless remains **unmet** because regular CI has neither an approved sanitized structural fixture nor secure fixture access, so the named readiness test still skips in an ordinary checkout.

## Corrected local findings

- `<local-tb3-working-archive>/sources/repos/terminal-wrench/tasks/<task>/<model>/` — seven qualifying genuine trial directories found; each matched the required `result.json`, `config.json`, and `agent/trajectory.json` shape.
- `<selected-job-root>/**/trial/` — missing optional `verifier/ctrf.json` and `artifacts/manifest.json` outputs found, satisfying the optional-absence case.
- `<regular-ci-fixture>/` — no approved sanitized fixture found; secure CI access is also absent.

The selected job root belongs to the frozen 28,801-trial snapshot `3c5be84efd707da8`. Absolute roots, task/run identifiers, UUIDs, prompts, trajectories, and values are intentionally redacted; no archive data was copied into this repository.

## Real-data outcome

With `EVAL_EVIDENCE_REAL_HARBOR_ROOT` set privately, `tests.test_readiness.ReadinessTests.test_real_harbor_archive_when_supplied` ran without skipping and passed: seven trials loaded, bundled, schema-validated, and passed referenced-file verification. `check` and `inspect --explain` also exited 0. The source review checked 133 mapped path/derivation outcomes, confirmed 59 unavailable field states as absent or candidate-null, and observed missing optional outputs in every selected trial. It also exposed a real adapter gap: six trials recorded `result.json:agent_result.timeout_sec` while `max_wall_time_s` remained unavailable. A fallback and regression test were added, and the entire protocol passed again. ATIF-v1.5 and ATIF-v1.6 remained visible non-fatal compatibility warnings rather than being silently accepted as ATIF-v1.7. The redacted command record is retained in `artifacts/harbor-readiness-redacted.txt` in the source checkout only.

## Exact remaining input required

Provide regular CI with an approved sanitized structural fixture, or secure fixture access, representing at least two genuine trials from snapshot `3c5be84efd707da8`, including one trial with an absent optional output. Mount it outside the repository and export its job root as `EVAL_EVIDENCE_REAL_HARBOR_ROOT`.

The completion command is:

```bash
python -m unittest tests.test_readiness.ReadinessTests.test_real_harbor_archive_when_supplied -v
```

Only when that command runs without a skip in regular CI may the G2 row change to `met`. The local pass does not weaken that release gate.

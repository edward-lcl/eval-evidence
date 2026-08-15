# Final review gate report

> **Historical report, superseded for current gate status on 2026-08-15.** The
> sanitized structural fixture now makes G2 reproducible without the private
> environment variable. See `docs/READINESS.md` and `PROJECT_HANDOFF.json`.

Recorded from repository root on 2026-07-29. This report validates the bounded review
deliverables; it does not change G2, authenticate archive data, or substitute for the
external immutable acceptance script.

## Test results

Command:

```bash
python3 -m unittest discover -s tests -v
```

Result after the follow-up implementation: **PASS** — `Ran 34 tests`,
`OK (skipped=1)`. The one skip is
`test_real_harbor_archive_when_supplied`, as expected without
`EVAL_EVIDENCE_REAL_HARBOR_ROOT`; G2 remains `unmet`.

### Handoff refresh (2026-08-15)

After pull request #2 merged and the deterministic figure pipeline was added, the same
command reports **PASS** — `Ran 37 tests`, `OK (skipped=1)`. The three added tests cover
brief-to-SVG reproducibility, local locked-render verification when the declared
renderer/font is present, and a negative text-overflow fixture. The sole skip remains
the external G2 test above; this refresh does not change its status.

## Cross-reference heading resolution

Command class: exact `grep -nF` checks.

| Citation | Resolution |
|---|---|
| `docs/VISION.md` — “Live monitoring is rejected” | PASS, heading at line 18 |
| `docs/VISION.md` — “Physical verification and attestation are deferred” | PASS, heading at line 22 |
| `docs/LIFECYCLE.md` — “Before a new evaluation run” | PASS, heading at line 18 |
| `docs/LIFECYCLE.md` — “Product sequence” | PASS, heading at line 125 |
| `docs/TRUST_MODEL.md` — “v0.1 trust boundary” | PASS, heading at line 3 |
| `docs/TRUST_MODEL.md` — “Gate before signing” | PASS, heading at line 29 |

## Path-existence verification

A `test -f` loop verified that every path cited by the four analytical artifacts exists in the repository or local archive. This path-existence check proves that target files are present, not that individual line ranges or semantic anchors within them remain current.

| Path group | Resolution |
|---|---|
| `docs/{VISION,READINESS,HARBOR_MAPPING,TRUST_MODEL,TBENCH_REVIEW,LIFECYCLE}.md` | PASS — all exist |
| `artifacts/real-comparison-redacted.md`, `artifacts/g2-blocker.md` | PASS — both exist |
| `eval_evidence/adapters.py`, `core.py`, `models.py` | PASS — all exist |
| `eval_evidence/schemas/eval-evidence-run-v0.1.schema.json` | PASS — exists |
| `eval_evidence/schemas/otel-genai-crosswalk-v0.1.json` | PASS — exists |
| Harbor `models/job/lock.py`, `upload/uploader.py`, `trial/trial.py` | PASS under `../tbench3-archive/sources/repos/harbor/src/harbor/` |
| Harbor task config, trial result, artifact manifest models | PASS under the same local Harbor source |
| Terminal Wrench `README.md` | PASS under `../tbench3-archive/sources/repos/terminal-wrench/` |
| TB3 `README.md` and `TASK_REVIEW_AUTOMATION.md` | PASS under `../tbench3-archive/sources/repos/terminal-bench-3/` |
| Frozen framing note | PASS at `../tbench3-archive/docs/session-notes/2026-07-26-ivan-framing-response.md` |

## Line-anchor and named-pattern verification

In addition to file existence, active source anchors were verified using stable named symbols and patterns rather than static numeric line ranges:

- **Harbor discovery:** `class HarborAdapter`, `required = ...`, `def detect`, `def discover`, and `rglob("result.json")` in `eval_evidence/adapters.py`.
- **Network policy mapping:** `"network_policy"`, `extra_allowed_hosts`, `agent_extra_allowed_hosts`, and `"Configured layers are not proof of effective enforcement"` in `eval_evidence/adapters.py`.
- **Optional artifact closure:** `FileReference("artifacts/manifest.json", "artifact-manifest", False)` in `eval_evidence/adapters.py`.
- **Absence of `lock.json` / `JobLock` mapping:** negative package search `grep -RInE 'lock\.json|JobLock' eval_evidence || true`.

The historical numeric citation in frozen `tb3-needs-decision.md` item 4 is superseded by an explicit erratum noting the shift. See `artifacts/review/claim-verification-matrix.md` for executable verification commands and outputs.

The only deliberately unverified technical subclaim is the exact current Harbor regrade field name `source_trial`; the matrix and PR review both mark that qualification. Current remote/web claims are also explicitly unverified because this session had no web access.

## Content checks

```bash
grep -c '^| G' docs/READINESS.md
grep -o 'fix-in-this-PR\|fixed-in-follow-up\|document-as-known-gap\|defer-with-named-trigger\|reject-with-reason' artifacts/review/blind-spot-register.md
grep -oi 'confirmed\|refuted\|unverifiable' artifacts/review/claim-verification-matrix.md
# A redaction scan for local absolute-root, worktree-name, and submission tokens was also run.
```

Results:

- PASS — READINESS retains exactly four gate rows.
- PASS — every register row has one allowed disposition; capture-time decision 4 is
  scoped as `fix-in-this-PR`, while the timeout and provenance defects are
  `fixed-in-follow-up`.
- PASS — claims (a)–(g) have explicit statuses: (c) and (e) are resolved after being
  confirmed, and claim (d) is refuted. Re-verification found that `network_policy` is
  partial but explicitly
  marked `derived` and “not proof of effective enforcement” in both adapter and mapping,
  so incompleteness is a disclosed gap rather than an overclaim. Claim (g) retains its
  wire-name qualification as unverifiable.
- PASS — no sensitive absolute path/worktree token matched in new review artifacts or
  the modified review brief.

## Cross-document consistency

| Check | Result |
|---|---|
| Single PR verdict versus findings | PASS — the two semantic correctness defects are fixed and tested; other gaps remain scoped adoption blockers. |
| Blind-spot dispositions versus five needs | PASS — no required item is rejected; campaign claims are a target contract, not code added in this episode. |
| Capture-time `fix-in-this-PR` versus delivery | PASS — decision 4 exists in `docs/TBENCH_REVIEW.md`. |
| Harness wishlist versus `lock.json` finding | PASS — new capture request is pruned; existing Harbor version/conditional commit requires adapter association. |
| VISION/LIFECYCLE/TRUST_MODEL boundaries | PASS — no dashboard, runner, universal score, premature plugins, or signing is authorized. |
| G2 status | PASS — remains `unmet`; no fixture or readiness claim changed. |

## Git status and diff evidence

The follow-up workspace contains the adapter/model/demo implementation, regression
coverage, golden digest and demo-session refreshes, lockstep lifecycle/mapping/review
documentation, and the pre-existing requested decision 4 addition.

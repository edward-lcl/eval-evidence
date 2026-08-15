# Review source inventory

## Access boundary

This review was performed in an offline harness with **no-web access and no live GitHub
access** (`PI_OFFLINE=1`). It does not claim to have traversed current websites or remote
repositories. Sources are limited to this checkout and the readable local
`tbench3-archive`; statements that would require a current remote are labeled
`model-knowledge` and unverifiable in-session.

## Repository documents

| Surface | Resolved path | Use |
|---|---|---|
| VISION | `docs/VISION.md` | Product boundary, acceptance backlog, non-goals |
| READINESS | `docs/READINESS.md` | G1–G4 evidence and adoption gates |
| HARBOR_MAPPING | `docs/HARBOR_MAPPING.md` | Claimed Harbor mapping and explicit exclusions |
| TRUST_MODEL | `docs/TRUST_MODEL.md` | Unsigned trust boundary and signing gate |
| TBENCH_REVIEW | `docs/TBENCH_REVIEW.md` | Maintainer review brief and requested decisions |
| LIFECYCLE | `docs/LIFECYCLE.md` | Declare/capture/seal/publish sequence |
| Adapter implementation | `eval_evidence/adapters.py` | Generic and Harbor normalization/discovery |
| Bundle implementation | `eval_evidence/core.py` | Canonical bytes, file receipts, coverage |
| Evidence model/schema | `eval_evidence/models.py`; `eval_evidence/schemas/eval-evidence-run-v0.1.schema.json` | Provenance and claim contract |
| OTel crosswalk | `eval_evidence/schemas/otel-genai-crosswalk-v0.1.json` | Existing optional transport subset |

## Repository artifacts

| Artifact | Resolved path | Use |
|---|---|---|
| Real comparison | `artifacts/real-comparison-redacted.md` | Two checksums, 1/3/2 denominators, differing budgets, Unknown fields |
| G2 blocker | `artifacts/g2-blocker.md` | Genuine local pass versus reproducible-CI distinction |
| Genuine-data summary | `artifacts/harbor-readiness-redacted.txt` | Redacted adapter dogfood |
| Scale dogfood | `artifacts/scale-measurement.txt` | Retrospective archive scale evidence |
| Readiness docs | `docs/READINESS.md`; `docs/HARBOR_MAPPING.md` | Gate and mapping evidence |

No private trial bytes were copied into this review.

## Local archive sources

The sibling archive is readable at `../tbench3-archive`.

| Source | Resolved path | Access/result |
|---|---|---|
| Harbor job lock model | `../tbench3-archive/sources/repos/harbor/src/harbor/models/job/lock.py` | Readable; defines `LOCK_FILENAME = "lock.json"`, `HarborLockInfo`, `TrialLock`, and `JobLock` |
| Harbor archive uploader | `../tbench3-archive/sources/repos/harbor/src/harbor/upload/uploader.py` | Readable; job archive allowlist includes `lock.json` |
| Harbor timeout implementation | `../tbench3-archive/sources/repos/harbor/src/harbor/trial/trial.py` | Readable; resolves cap and multiplier |
| Harbor task network model | `../tbench3-archive/sources/repos/harbor/src/harbor/models/task/config.py` | Readable; baseline and phase policy fields |
| Harbor result model | `../tbench3-archive/sources/repos/harbor/src/harbor/models/trial/result.py` | Readable; current `step_results` model |
| TB1/TB2 corpus evidence | `../tbench3-archive/sources/repos/terminal-wrench/README.md` | Readable; local counts and reward-hackable subset |
| TB3 process | `../tbench3-archive/sources/repos/terminal-bench-3/TASK_REVIEW_AUTOMATION.md` | Readable; checks, controls, trial and review process |
| TB3 status | `../tbench3-archive/sources/repos/terminal-bench-3/README.md` | Readable; explicitly work in progress |
| Frozen counts/taxonomy | `../tbench3-archive/docs/session-notes/2026-07-26-ivan-framing-response.md` | Readable; locally recorded counts and decomposition |

The exact Harbor model path expected by the acceptance contract resolves to
`../tbench3-archive/sources/repos/harbor/src/harbor/models/job/lock.py`. The exact
real-comparison artifact resolves to `artifacts/real-comparison-redacted.md`.

## Evidence-class rule

- `repo-artifact`: this checkout's docs, code, tests, or redacted artifacts.
- `local-archive`: files under `../tbench3-archive`.
- `model-knowledge`: contextual memory not independently verifiable in this no-web
  session; never used here as the sole support for a blocking finding.

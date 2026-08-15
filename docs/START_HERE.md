# Start here

This is the handoff router for Eval Evidence. The repository is intentionally in
development. A new teammate should be able to identify the current authority, choose a
bounded task, and prove completion without oral context from the original author.

The machine-readable companion is [`PROJECT_HANDOFF.json`](../PROJECT_HANDOFF.json).
When this page and that file disagree about status, stop and open a correction issue;
do not choose the more optimistic interpretation.

## Current state in one minute

- **Authority:** the latest protected commit on `main` is the development authority.
- **Current decision:** ready for a narrow Terminal-Bench/Harbor mapping review.
- **Not release-ready:** the genuine-Harbor G2 fixture still skips in regular CI.
- **Distribution:** `v0.1.0` is the latest tag; `0.2.0` is an unreleased candidate and
  is not available from PyPI.
- **Supported claim:** deterministic per-trial evidence bundles and scoped local
  integrity/provenance checks.
- **Unsupported claims:** campaign completeness, trusted-runner authenticity,
  leaderboard correctness, model ranking, or physical truth.

Verify the checkout before doing work:

```bash
git status --short --branch
git rev-parse HEAD
git rev-list --left-right --count main...origin/main
```

Preserve unrelated working-tree changes. Use a feature branch or isolated worktree for
implementation, and keep one writer per checkout.

## Choose your role

| I am… | Read first | First useful action | Completion evidence |
|---|---|---|---|
| New teammate | this page, then the [README](../README.md) | run the synthetic quickstart and select one `ready` item in `PROJECT_HANDOFF.json` | command transcript plus any undocumented correction |
| Developer | [architecture](ARCHITECTURE.md), then [contributing](../CONTRIBUTING.md) | run tests and inspect the adapter/core boundary before editing | focused tests, full suite, and diff review |
| Repository owner | [maintainer handoff](MAINTAINER_HANDOFF.md) and [readiness gates](READINESS.md) | resolve an owner-only approval or release decision | dated sign-off with exact commit/artifact hashes |
| Terminal-Bench or Harbor maintainer | [five-minute review brief](TBENCH_REVIEW.md) | red-line the field mapping and answer the four requested decisions | recorded decisions and a reproducible G2 route |
| Paper author or reviewer | [paper alignment](PAPER_ALIGNMENT.md) and [trust model](TRUST_MODEL.md) | freeze the manuscript authority or review one acceptance-contract row | canonical revision plus row-level disposition |
| Agent | [`AGENTS.md`](../AGENTS.md), this page, then `PROJECT_HANDOFF.json` | choose one bounded item whose dependencies are met | tests, receipts, changed-path summary, and remaining gaps |
| Security reviewer | [security policy](../SECURITY.md) and [trust model](TRUST_MODEL.md) | test a documented threat boundary with synthetic input | minimal reproduction and scoped impact |

## How to choose work without asking the original author

1. Read `PROJECT_HANDOFF.json.next_work` in priority order.
2. Skip `blocked-owner-input` and `blocked-by-sequence` items unless the named approval
   or dependency is already recorded in the repository or issue.
3. Select one `ready` or `ready-for-review` item.
4. Read its `start_at` document and acceptance criteria.
5. State the supported claim and the claims your work will not establish.
6. Implement and validate only that bounded outcome.
7. Update code, tests, status, and reader-facing documentation together.

No silence means approval. If work would share genuine run data, mark G2 met, publish a
release, change the paper authority, or claim upstream endorsement, stop at the owner or
external-approval boundary.

## Minimum local verification

```bash
python3 -m unittest discover -s tests -v
python3 scripts/verify_figure.py
uv build --offline --wheel --sdist --out-dir /tmp/eval-evidence-dist
python3 scripts/audit_distribution.py /tmp/eval-evidence-dist
```

For a release decision, also run the installed-wheel and tamper protocol in
[`DOGFOOD.md`](DOGFOOD.md), verify the exact GitHub Actions run, and complete the owner
sign-off in [`OWNER_WALKTHROUGH.md`](OWNER_WALKTHROUGH.md).

## What “handoff complete” means

Handoff does not mean every gate is met. It means an unfamiliar teammate can determine:

- which source is authoritative;
- what works and what is still unknown;
- which task is safe to start;
- who owns blocked decisions;
- what evidence closes the task; and
- which claims remain forbidden afterward.

If any of those answers require private verbal history, the handoff is not complete yet.

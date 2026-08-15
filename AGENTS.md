# Project agent orchestration

## Project state and semantic authority

Before selecting work, load `PROJECT_HANDOFF.json`, `docs/START_HERE.md`, and
`docs/ARCHITECTURE.md`. Treat `PROJECT_HANDOFF.json.next_work` as the machine-readable
queue: choose only work whose status and dependencies permit it. A blocked item is not
permission to improvise around its owner, data, release, paper, or upstream-approval
boundary.

The latest protected `main` commit is the development authority; a release tag becomes
distribution authority only after its release checklist passes. Preserve the distinctions
between configured, synthetic/lab-verified, regular-CI verified, owner-approved,
published, and independently reviewed. Never upgrade one state to another by wording.

Definition of done: satisfy the scoped acceptance criteria; run focused and full
checks; update code, contracts, docs, figures, and handoff state together where
applicable; list changed paths and exact receipts; and keep remaining gaps explicit.

## Control-plane stack

- **Herdr is the visible execution substrate:** project workspaces, panes, worktrees, terminals, and lifecycle state.
- **Fusion is the default substantial-work orchestrator:** role routing, parallel model work, single-writer leases, gates, budgets, retries, and durable project state.
- **SSSF/ADWs are reusable workflow assets:** deterministic phase code, typed envelopes, code checks, gates, and trace evidence. They do not become a second concurrent scheduler beneath Fusion.
- **Pi is the underlying agent runtime:** use raw Pi only for narrow interactive work where coordinated Fusion execution would be unnecessary.
- Choose exactly one execution authority for a run. Do not nest independent Fusion and SSSF agent schedulers or allow them to compete for retries, completion, or workspace writes.

## Herdr workspace conventions

- Keep the current Herdr workspace as the orchestration/control workspace.
- Start a project Fusion host in the workspace's returned root pane and name it `fusion-<project>` after Herdr detects the underlying Pi process. Do not create a blank root shell and then add the host in an unnecessary split.
- Keep the working host or primary agent in the left/root pane. Add static shells, tests, logs, or monitors on the right; place secondary supporting terminals below. Create panes only when a role needs them.
- Reuse one workstream workspace for sequential phases on the same checkout. Preserve native sessions and receipts before cycling a role or closing a pane.
- Open separate workspaces only for distinct projects, worktrees, isolation boundaries, or genuinely simultaneous workstreams.
- Close completed agent panes and disposable workspaces after their final response, native session reference, and outcome receipt are recorded.

## Execution and completion

- Do not launch delegated agents only as hidden background subprocesses. Fusion-owned clean-room children are the exception because Fusion renders and governs their lifecycle inside its visible host pane.
- Every non-Fusion delegated launch must install an asynchronous completion path: observe Herdr state without blocking the control workspace, capture the final response, record the outcome, and notify or resume the orchestrator.
- After a relay reconnect, reconcile all nonterminal work with `herdr agent list` and the relevant Fusion/SSSF state before launching anything else.
- Keep orchestrating while delegates run. Parallelize independent read-only discovery, review, and validation; model dependencies explicitly instead of serially waiting on broad tasks.
- Preserve one writer per checkout. Use Git worktrees when writers must run concurrently.

## Task routing

- Tiny, obvious change: Fusion host plain chat.
- Uncertain decision or independent perspectives: Fusion `/opinion` or `/wayfinder`.
- Bounded implementation with acceptance criteria: Fusion `/auto-validate`.
- Broad or multi-workstream objective: Fusion `/go`, then an explicitly approved sprint when routed.
- Repeatable factory process: a registered SSSF-backed workflow invoked under the chosen control plane; until that adapter exists, do not run SSSF's hidden agent subprocess launcher.

## Multiple projects

- Give each active project its own Herdr workspace, Fusion host, project-keyed state, checkout/worktree, writer lease, and acceptance receipts.
- A portfolio controller may coordinate priorities, cross-project dependencies, global provider concurrency, and spend, but it must not write project checkouts or become a second project scheduler.
- Cross-project orchestration exchanges typed requests and bounded receipts, not ambient transcripts, credentials, or generic shell commands.

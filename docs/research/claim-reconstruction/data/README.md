# Committed result tables

Derived from public artifacts by `scripts/research/tb20_reconstruction.py` on 2026-08-16.
See [`../../E1_EE08_RESULTS.md`](../../E1_EE08_RESULTS.md) for what they establish.

- `tb20_rows_reconstruction.csv` — one row per displayed Terminal-Bench 2.0 leaderboard
  row (142): displayed accuracy and stderr, the per-task-mean and within-task-SE values
  recomputed from the published breakdown, the pooled alternative, and whether each
  matches. `accuracy_matches_1e12` is true for all 142; `stderr_matches_1e9` is true for
  all 134 rows that display one.
- `tb20_jobs_denominators.csv` — one row per genuine Harbor job in the public submission
  dataset (245): stated `n_total_trials`, actual trial-directory count, trials named in
  job stats, pending/running, `n_retries`, `n_errored`. Three rows disagree between
  stated and actual; `n_retries` is zero throughout.

Both tables contain only public third-party values (aggregate counts and scores already
displayed on the leaderboard). No trajectories, prompts, or task content.

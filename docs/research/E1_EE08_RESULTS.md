# E1′ and EE-08 results: denominator reconstruction and the row-manifest retro-fit

Status: measured result, 2026-08-16. Both experiments preregistered in
[`CLAIM_RECONSTRUCTION.md`](CLAIM_RECONSTRUCTION.md) §G were run against public artifacts.
This reports what was measured, including the parts that came out against the study's
expectations, and the caveats that limit what the numbers license.

Reproduce with:

```bash
python3 scripts/research/tb20_reconstruction.py --out /tmp/tb20
```

The script fetches only public artifacts, runs no models, and writes nothing outside its
output directory. Committed result tables:
[`claim-reconstruction/data/`](claim-reconstruction/data/). Corpus: 142 leaderboard rows,
75 public submission folders, 245 genuine Harbor jobs, 32,803 trial directories, jobs
dated 2025-11 through 2026-05.

## Headline

| Preregistered metric | Threshold | Measured | Verdict |
|---|---|---|---|
| E1′ unexplained expected-vs-discovered delta | under 5% of jobs | **3/243 = 1.2%** | below threshold |
| E1′ jobs using retries | "rare" | **0/245 = 0.0%** | below threshold, but see caveat |
| EE-08 rows reproducing from the published breakdown | most | **142/142 to 1e-12** | reproduces |
| EE-08 exclusion predicate uniquely recoverable | yes/no | **no** | not recoverable |

Per the preregistration, the first two send the recommendation to "a small Harbor change
plus a publisher checklist" rather than "tombstones and a job-close manifest are
mandatory". The fourth is the preregistered case for prospective recording. The study's
§G row-1 flip condition therefore **did not fire**; its row-2 alternative **did**.

## EE-08 — reconstructing 142 published rows

**The aggregation and uncertainty rules are uniquely recoverable and now confirmed on the
complete population.** Previously three rows had been checked exactly and the rest only
for consistency.

- **142/142 rows** reproduce their displayed accuracy to within 1e-12 under
  `accuracy = mean over 89 tasks of (successes / counted trials)`.
- Pooled `successes/counted` matches only **73/142** — it coincides only where every task
  carries the same number of counted trials. This settles the CONFLICTING reading recorded
  in the study §A: the 2.0 page is a mean of per-task rates, not the pooled rule that the
  2.1 code comment describes as "matching the Harbor importer".
- **134/134 rows that display an uncertainty** reproduce
  `stderr = (1/T)·sqrt(Σ pᵢ(1−pᵢ)/(nᵢ−1))` to within 1e-9, with zero exceptions. The
  **8 rows displaying no uncertainty are exactly the 8 rows containing a task with fewer
  than 2 counted trials** (the `nᵢ−1` denominator). This closes the "±" question that L1
  had marked UNAVAILABLE and that a maintainer had described as "the standard error across
  five runs" — the rendered formula is a within-task Bernoulli SE over tasks, not a
  dispersion across five whole-benchmark runs. The maintainer's description and the
  rendered formula remain CONFLICTING; the formula is now settled.
- **Task content identity is stable across the entire board**: 89 distinct task names, and
  **0 tasks carry more than one checksum** across all 142 rows. An honest negative — the
  task-drift hazard that a three-row sample could not rule out does not appear here.

**Two findings that the reconstruction surfaced and that the board does not show:**

1. **Row identity collides.** 142 rows carry only **140 distinct display keys**. Two pairs
   (`gemini cli__gemini 3.1 pro`, `little-coder__qwen3.6-35b-a3b`) differ only by agent
   version, which the key omits. A per-row manifest must key on (agent, agent version,
   models); the published key is not an identifier.
2. **Two rows display a denominator about twice their public evidence.** For
   `Ante__Gemini-3-Pro-Preview` the row counts 887 trials while the submission folder
   contains 445 trial directories, its job `result.json` states `n_total_trials` 445, and
   its stats name exactly those 445 — a three-way internal agreement that the displayed
   row contradicts. `CodeBrain-1.5__GPT-5.3-Codex` shows the same shape (890 displayed,
   445 present). Either the importer counted one job twice or the rows draw on runs that
   were never published. Nothing on the page distinguishes these cases.

**Coverage is the larger finding.** Only **47 of 142 rows** could be matched to a public
submission folder at all, and 32 of the 75 folders match no displayed row. So for roughly
two thirds of the board there is no public evidence to reconcile a row against — before
any question of rules.

**The exclusion predicate is not uniquely recoverable.** Among folders that map to exactly
one row, per-task comparison of counted trials against job-level records fits
"count every trial in the job" for 1,248 task-rows and "count only trials that produced a
reward" for 1,312, with 181 fitting neither. No single rule fits. Of the matched folders,
21 show counted equal to trial directories, 18 show counted below (309 trials dropped in
total), and the two over-count rows above. **This is the preregistered outcome that argues
for prospective recording**: the drop decision is not inferable from what was retained.

## E1′ — denominators in 245 genuine Harbor jobs

Expected (`n_total_trials`) versus discovered (actual trial directories, listed from the
dataset rather than inferred):

- **240/243 jobs agree exactly.** Trials named in `reward_stats`/`exception_stats` also
  match the directory count in 240/243.
- **3 disagree (1.2%)**, none explained by pending or running trials: one job states 29
  against 89 directories; one states 445 against 130; one states 11 against 10.
- **1 job's `result.json` is unreadable** and **1 job states no `n_total_trials` at all** —
  the expectation itself is missing, which no delta rate would capture.
- **0 of 245 jobs record any retry.** `n_retries` is zero throughout; `n_cancelled` is
  zero throughout.
- Only **4 of 245 jobs carry `lock.json`**, all from 2026-05 — consistent with the job
  lock landing in Harbor on 2026-04-29. For the other 241 the harness version is
  unavailable from the artifact, as the study recorded.

**The retry result must not be over-read.** Zero retries does not test the retry-deletion
hazard; it shows this population never enabled retries (Harbor's `max_retries` defaults to
0). The mechanism verified in the study — a retried attempt's directory is removed before
the retry — remains untested against real usage, not refuted. A corpus that configures
retries is still needed to measure it.

**Survivorship limits the delta rate.** These are leaderboard *submissions*: runs their
authors chose to publish. Jobs abandoned, failed, or discarded never enter this corpus, so
1.2% is a lower bound on the delta rate in Harbor usage generally, not an estimate of it.
The 17 local oracle jobs measured alongside (Harbor 0.16.1, one trial each) agree
perfectly on every check — expected equals lock entries equals discovered equals
completed, means recompute under the null-to-zero rule, zero retries — but they are a
degenerate agent on one version and establish only a floor.

## What this changes

1. **The aggregate half of the record is cheap and works.** Publishing the per-task
   breakdown, as this board does, makes the number reconstructable by anyone: 142/142,
   exactly, including its uncertainty. This is the strongest available evidence that the
   per-row manifest is worth its cost, and it is already most of the way there.
2. **The selection half is not recoverable retrospectively.** The exclusion predicate,
   the row-to-evidence binding for two thirds of rows, and the reason two rows count double
   are all unavailable from public artifacts. These are exactly the fields the study named
   as publisher-owned, and they must be recorded when the row is made, not derived later.
3. **Harbor's job-level denominators hold up better than expected.** 98.8% exact agreement
   argues against a job-close manifest as a priority and for the smaller Harbor items the
   study listed (an attempt ordinal, a metric policy field, member digests). The three
   disagreements and the two missing-expectation jobs are the cases a checker should fail
   on, not a reason to rebuild the model.
4. **The study's §F recommendation is unchanged, and one item is now evidenced.** The
   read-only reconstruction checker (§F item 3) is the thing that found the row-identity
   collision, the double-counted rows, and the three denominator disagreements. Nothing
   here justifies a new schema, CLI, wire member, or adapter change.

## What remains unknown

- Why two rows count roughly double, and whether the importer or an unpublished run is
  responsible. The importer code is not public.
- The exclusion predicate itself; two candidate rules were tested and neither fits.
- Retry behaviour under real retry configuration (unmeasured, not refuted).
- Whether the 32 unmatched folders correspond to withdrawn rows, renamed agents, or rows
  that were never displayed; and what the 95 rows with no public folder rest on.
- Conflict frequency across retained sources (E2), still unrun.
- Whether these findings transfer to a second evaluator (E6), still unrun.

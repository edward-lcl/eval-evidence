# L7 — Failure-mode taxonomy from evidence

Lane: L7 of the "what evidence is required for an independent person to reconstruct an
evaluation claim?" investigation. Written 2026-08-16. All web sources fetched or searched
on 2026-08-16 unless stated. Labels used per lane rules: OBSERVED / DERIVED / ASSERTED /
CONFLICTING / UNAVAILABLE / HYPOTHETICAL.

Convention for this report: "OBSERVED" means I read the primary artifact myself in this
lane (an arXiv abstract page, a GitHub issue body via the GitHub API, a Harbor source
file at a pinned SHA, a vendor page). Numbers taken from a paper's own abstract are
OBSERVED-as-stated (I saw the abstract) but the *finding* itself is the paper's
ASSERTION; I write "OBSERVED (abstract) / ASSERTED (finding)" where the distinction
matters. Where I could only reach a secondary source, I say so and label ASSERTED.

---

## 1. Verdict

The public record contains many documented, primary-sourced cases in which a reported
evaluation number could not be reconstructed, or was later shown to mean something
different from what readers took it to mean, and the *dominant* missing information is
not the trial-level record. Of the ~35 cases catalogued below, the failures cluster at
(a) cohort→aggregate: denominator/subset/aggregation/uncertainty choices that were made
but not carried with the number (SWE-bench 477/489/500 subsets, Devin's 25% sample,
MATH-500 vs MATH, pass@1-averaged-over-k vs single-sample, cons@64 vs @1, HF v2
re-normalization, Terminal-Bench "±" being SE-across-5-runs); (b) aggregate→table:
leaderboard rows added, removed, deprecated, or re-scored with no public row-state
record (Chatbot Arena's 205 silent deprecations and 27 private Llama-4 variants; the
Terminal-Bench 2.0 rows that appear at rank 1 in archived snapshots and later vanish
with no public manifest; SWE-bench experiments' duplicated instance ids inflating a
published 10.51% that is really 9.29%); and (c) table→claim: instrument identity that
was silently different (harness prompt/scoring giving 63.6 vs 48.8 for the same model
on MMLU; o3-preview vs shipped o3 giving 76–88% vs 41–53% on the same ARC-AGI set and
25% vs 10% on FrontierMath; a Reflection-70B "API" that was another vendor's model).
Trial-level byte identity would have caught only a minority of these (test-file
modification inside patches, duplicated ids if bundled per attempt, repo-state leakage
if the environment digest were pinned, retry-deleted attempts if the bundle were made
before deletion). A larger share needs *campaign/claim structure* (expected vs included
attempts, named aggregation, subset id, uncertainty method, supersession/regrade links).
And a substantial share is *fundamentally external* to any evidence container: private
variant testing before disclosure, provider-side model substitution behind a stable
name, funder access to a benchmark, contamination in training data, and the
interpretive leap from a percentile to "passes the bar." Contamination is, on the
evidence, a claim-support failure, not a lineage failure — the lineage of a contaminated
run reconstructs perfectly. Existing mechanisms did catch a lot: community audits
(GitHub issues, third-party re-runs) caught nearly every case here; leaderboard policy
changes followed (LMArena, Terminal-Bench, SWE-bench, HF, ARC Prize); Harbor's own
`regrade` and `lock.json` already implement supersession lineage that Eval Evidence does
not consume. So: the proposed *per-trial* abstraction is necessary-but-small; the
missing artifact that would have prevented the largest number of documented failures is
a *row-level publication manifest* (attempt id → included/excluded/rescored, denominator,
aggregation, uncertainty formula, instrument identity), which is a leaderboard/publisher
concern, not a per-trial bundle concern.

---

## 2. Findings with labels and receipts

Each case: (1) what the reader saw, (2) what was missing/misleading, (3) lineage
transition, (4) recoverability, (5) evidence quality, (6) whether/how an existing
mechanism caught it.

### 2.A Trial → cohort (which attempts exist, which are the same trial, which were replaced)

#### A1. Harbor deletes a failed attempt's directory before retrying it (mechanism; harm HYPOTHETICAL)

- OBSERVED (source): local Harbor clone, `git show a27e9c2ae10a31c40b2dcef33ef5486bce36e185:src/harbor/trial/queue.py`, lines 200–222: the retry loop creates a `Trial`, runs it, and if `result.exception_info` is set and the exception type is retryable and `attempt < max_retries`, executes `shutil.rmtree(trial.paths.trial_dir, ignore_errors=True)` and sleeps before retrying. Same line 222 present at `origin/main` f03db62fd2ed2ed1f79aefe024cfcbc68a0d759e (2026-08-16). Introduced by commit `080a1cb30` "Simplify trial flow (#1672)" 2026-05-17 (`git log -S`).
- OBSERVED (source): `src/harbor/models/job/config.py` `RetryConfig`: `max_retries` default 0; default `exclude_exceptions` = {AgentTimeoutError, VerifierTimeoutError, RewardFileNotFoundError, RewardFileEmptyError, VerifierOutputParseError, ApiUsageLimitError, AgentSafetyRefusalError, AgentAuthenticationError, ModelNotFoundError}; when `include_exceptions` is None "retries all exceptions" not excluded.
- OBSERVED (source): `src/harbor/job.py` `_remove_completed_attempt_for_retry` (line ~690) pops the previous result from live rewards and job stats and increments `_n_retries`; the job `result.json` shape observed on genuine local job directories carries `stats.n_retries`, `stats.n_errored_trials`, `stats.n_cancelled_trials`, `n_total_trials` (key names only inspected).
- (1) Reader sees: a job directory with one directory per trial name and a `result.json` whose `stats.n_retries` is an integer. (2) Missing: the *content* of the replaced attempts (agent logs, partial verifier output, exception detail) — the count survives, the evidence does not. (3) trial→cohort. (4) Prospectively capturable (do not delete; or record the deleted attempt's digest and exception type in the lock/result); NOT retrospectively recoverable. (5) OBSERVED in code; I found no public incident where this changed a reported number → the harm is HYPOTHETICAL. (6) No mechanism catches it: nothing in the job record distinguishes "n_retries=3 for one flaky task" from "n_retries=3 for three tasks", and no digest of the deleted attempt exists.

#### A2. Harbor resume deletes trial directories that lack `result.json` (mechanism; harm HYPOTHETICAL)

- OBSERVED (source): `src/harbor/job.py` at a27e9c2, lines 252–260: on resume, `for trial_dir in self.job_dir.iterdir(): ... if not trial_paths.result_path.exists(): shutil.rmtree(trial_paths.trial_dir)`. Present at origin/main f03db62 (line 259).
- (1)(2) A partially executed attempt (agent ran, verifier never wrote result) is erased on resume; the resumed run then produces a fresh attempt under the same name. (3) trial→cohort. (4) Prospectively capturable; not retrospectively recoverable. (5) OBSERVED code path; no incident found → HYPOTHETICAL harm. (6) None.

#### A3. Same-task concurrent attempts collide on fixed container names/ports and are booked as agent errors (DOCUMENTED)

- OBSERVED (issue): https://github.com/harbor-framework/terminal-bench-1/issues/1430 (opened 2026-04-01, open). Body: with `--n-attempts 5 --n-concurrent 4` several tasks fail with "container name ... already in use" / "port is already allocated", "reported as unknown_agent_error", "These are infrastructure collisions, not model failures." Comment 2026-04-16: another user reports "447/640 trials failed as unknown_agent_error" on an `--n-attempts 8 --n-concurrent 20` run, eliminated by serializing same-task attempts. Comment 2026-07-04: PR #1450 proposed scheduler-level serialization.
- (1) Reader sees: per-task pass rates over k=5 attempts. (2) Missing: whether a failed attempt was an infra collision or a model failure — the failure category is coarse ("unknown_agent_error") and the collision is invisible unless the compose logs are kept and read. (3) trial→cohort (attempt validity) and cohort→aggregate (denominator: are collided attempts in the denominator?). (4) Retrospectively recoverable only if the environment/compose logs were retained; prospectively capturable as an explicit "attempt invalid: infra" state. (5) Primary GitHub issue with two independent reporters. (6) Caught by users re-running; no automated detection in harness at time of report.

#### A4. Leaderboard task page shows no trial rows for a task that is listed as run (DOCUMENTED, cause UNAVAILABLE)

- OBSERVED (issue): https://github.com/harbor-framework/terminal-bench-1/issues/1445 (2026-06-17, open). Reporter: on the TB 2.1 leaderboard a task page for one model has "no data on the failure across the 5 runs" while a sibling task page shows five rows with tokens/cost. Comment 2026-06-20 reproduces from public HTML: server-rendered `TrialDetailsTable` payload has an empty `data` array for one task hash and five trial rows for another; "I cannot tell from the public data whether the missing rows mean skipped/upload-failed trials, hidden results, or a join/indexing issue."
- (1) Score shown; (2) attempt records missing for a subset of tasks with no state explaining why; (3) trial→cohort; (4) UNAVAILABLE from public data (the issue is open, no maintainer answer as of fetch); (5) primary issue + independent reproduction; (6) not caught by any mechanism; surfaced by a reader.

#### A5. Duplicated instance ids in a leaderboard results file inflate a published score (DOCUMENTED, quantified)

- OBSERVED (issues/PR via GitHub API): https://github.com/SWE-bench/experiments/issues/301 (2025-07-27, closed 2025-08-25 by dedup commit 1fbb2b42daa8918549e0cbc46682fde9156f434c) — three instance ids each repeated 5 times under `resolved` in `evaluation/verified/20240402_sweagent_claude3opus/results/results.json`. https://github.com/SWE-bench/experiments/issues/463 (2026-07-30, open): the same submission under `evaluation/test/` still duplicated: `resolved` 241 entries / 213 unique / 28 duplicates; `generated` 2343 entries "against a 2294-instance split, which is consistent with the file having been assembled from two overlapping partial runs"; "241/2294 = 10.51%" vs "213/2294 = 9.29%". https://github.com/SWE-bench/experiments/pull/465 (2026-08-09, open): scan of all 254 submissions finds "nine lists across four submissions repeat instance ids"; PR "lowers a published score".
- (1) Reader sees 10.51% on the Test board. (2) Missing: uniqueness of attempt identity in the aggregation input; the file was apparently a union of two partial runs. (3) trial→cohort (identity) and cohort→aggregate (count over list not set). (4) Retrospectively recoverable — and it was recovered from the public artifact alone. (5) Primary. (6) Caught by community audit twice, a year apart; fix for one path did not cover the others; maintainers merged the first dedup.

#### A6. Harness reads the wrong reward key and mis-buckets successes (DOCUMENTED, downstream effect ASSERTED)

- OBSERVED (issues): https://github.com/harbor-framework/harbor/issues/2225 (2026-07-07, open) and PR https://github.com/harbor-framework/harbor/pull/2226 (2026-07-07, open): Harbor serializes `verifier_result.rewards`, but sweep pruning and `harbor traces --filter success/failure` read `verifier_result.reward`; "successful trials look unsuccessful in workflows that read serialized result.json"; "downstream pipelines can train on the wrong trajectories or assign the wrong labels without any runtime error."
- (1)(2) A consumer of the same bytes applied a different (wrong) extraction transform; bytes were intact. (3) trial→cohort (labeling) and cohort→aggregate. (4) Retrospectively recoverable (bytes exist) — but only if the transform is named. (5) Primary issue; no incident of a *published* number affected found. (6) Caught by a contributor; not by any harness check.

#### A7. Environment carries future repository state; agents read the gold fix from `git log --all` (DOCUMENTED)

- OBSERVED (issue): https://github.com/SWE-bench/SWE-bench/issues/465 (2025-09-03, closed 2026-03-24; 20 comments): trajectories (Claude 4 Sonnet on pytest-dev__pytest-6202; Qwen3-Coder-480B via OpenHands on django__django-13513) show `git log --all`/`git log --grep=<issue id>` revealing the future fix; maintainer 2025-09-04: "adapting the harness and building new images very shortly (fix/git-log-leak)". Related: https://github.com/SWE-bench/SWE-bench/issues/578 (2026-05-08, open): Multilingual images still leak git tags — "515 reachable commits" beyond HEAD in a public image (steps reproducible offline with `--network none`).
- (1) Reader sees resolved-rate. (2) Missing: identity of the *environment image contents* as part of the instrument; the images changed after the fix, so pre-fix and post-fix rows are not the same instrument. (3) trial→cohort (attempt validity) with effect at table→claim (which image built the number?). (4) Retrospectively recoverable per-trial only if trajectories were retained (they were, for these leaderboard rows) — the audit was done from trajectories; prospectively capturable as an image digest in the lock. (5) Primary. (6) Caught by external researchers reading trajectories; harness fixed; older rows not re-run (see also A9/C3).

#### A8. Task solution publicly available on the open internet (DOCUMENTED, TB3)

- OBSERVED (issues): https://github.com/harbor-framework/terminal-bench/issues/1541 (2026-08-10, open, label `task fix`) and siblings #1542, #1543, #1561, #1562 (all 2026-08-10): "tasks run with open internet, everything is fair game"; for `fix-uautomizer-soundness` "the injected bug is a revert of public code ... the correct code is verbatim in the public v0.2.4 tag ... an agent can diff the local source against upstream and recover the exact fix without doing the diagnosis"; "we might have to remove tasks that become trivial". Issues carry the footer "created by automatic analysis".
- (1)(2) Number is reconstructable; its *meaning* (diagnosis skill vs diff skill) is not. (3) claim→interpretation, with a cohort→aggregate consequence if tasks are removed. (4) Fundamentally external (world state) — capturable only as a dated network policy + allowed-hosts record. (5) Primary. (6) Caught by the maintainers' own automated scan; policy response pending.

### 2.B Cohort → aggregate (denominator, subset, aggregation rule, uncertainty)

#### B1. Devin: 13.86% on a random 25% subset (DISCLOSED denominator, comparison across settings)

- OBSERVED (vendor page): https://cognition.com/blog/swe-bench-technical-report (2024-03-15): "570 out of the 2,294" test instances, "79" resolved, "13.86%"; sampling "to reduce the time it takes for the benchmark to finish"; 45-minute runtime limit; compared with prior "assisted" 4.80% (Claude 2) and "unassisted" 1.96%.
- (1) Reader saw "13.86% vs 1.96%". (2) The denominator was disclosed; what was *not* comparable was the setting (agent with full repo & 45 min vs single-shot retrieval baselines) and the subset seed/ids. (3) cohort→aggregate and table→claim. (4) Subset ids: UNAVAILABLE from the post (I did not find the 570 ids listed there); prospectively capturable. (5) Primary. (6) No mechanism; comparison was accepted in press.

#### B2. SWE-bench Verified reported over 477, 489, or 500 problems by different labs (DISCLOSED in footnotes)

- OBSERVED (vendor page): https://www.anthropic.com/news/claude-4 (2025-05-22): "On all Claude 4 models, we report scores out of the full 500 problems. Scores for OpenAI models are reported out of a 477 problem subset." Scaffold: "a bash tool, and a file editing tool"; high-compute number "sampling multiple parallel attempts", discarding patches that break visible regression tests, "an internal scoring model to select the best candidate".
- ASSERTED (search-result summaries; primary Anthropic 3.7 and OpenAI 4.1 pages not fetched in this lane): Claude 3.7 Sonnet reported on n=489 "which work on Anthropic's infrastructure"; OpenAI on n=477 "validated on their internal infrastructure".
- (1) Reader sees a bar chart with one number per model. (2) Denominators differ by lab (500/489/477); high-compute numbers use best-of-N with an internal selector; the disclosure lives in footnotes, not in the number. (3) cohort→aggregate. (4) Retrospectively recoverable only if the excluded ids are published (I did not find them); prospectively capturable as a subset id. (5) Primary for Anthropic Claude 4; secondary for the 489/477 origins. (6) Footnotes are the mechanism; nothing machine-readable.

#### B3. ARC-AGI: incomplete run excluded from leaderboard, with the reason stated (POSITIVE case)

- OBSERVED (vendor page): https://arcprize.org/blog/analyzing-o3-with-arc-agi (2025-04-22): o3-high "37/100 responses, 82% accuracy"; "these runs were excluded from the leaderboard due to insufficient coverage"; partial data "should not be reported on" and is only "an upper bound".
- OBSERVED (vendor page): https://arcprize.org/policy: "$10,000 USD per run" cap; verified vs community leaderboards; "we do not verify submissions on the community leaderboard by default".
- (1)(2) Nothing misleading; included here as the counter-example: the exclusion, its reason, and the coverage denominator were published. (3) cohort→aggregate. (4) Prospective. (5) Primary. (6) Publisher policy is the mechanism.

#### B4. MATH-500 vs full MATH; pass@1 averaged over k samples vs a single sample (DISCLOSED in papers, easily lost downstream)

- OBSERVED (arXiv abs): https://arxiv.org/abs/2305.20050 (v1 2023-05-31) — "78% of problems from a representative subset of the MATH test set" (the subset now known as MATH-500).
- OBSERVED (arXiv html): https://arxiv.org/html/2501.12948v1 (DeepSeek-R1) — "we use a sampling temperature of 0.6 and a top-p value of 0.95 to generate k responses (typically between 4 and 64, depending on the test set size) for each question", "pass@1 = (1/k) Σ p_i", plus "cons@64" for AIME 2024.
- (1) Reader sees "MATH 78%" or "AIME pass@1 79.8%". (2) The subset (500 vs 5000) and the estimator (mean over k samples at T=0.6 vs one greedy sample) are in the methods text and are dropped when the number is copied into a table. (3) cohort→aggregate; the loss happens at table→claim when copied. (4) Prospectively capturable (subset id + estimator name); retrospectively recoverable only by reading the paper. (5) Primary. (6) None.

#### B5. Terminal-Bench "±" is standard error across 5 whole-benchmark runs; readers cannot tell (DOCUMENTED, CONFLICTING interpretations)

- OBSERVED (issues): https://github.com/harbor-framework/terminal-bench-1/issues/1256 (2025-09-24, closed 2025-10-07): what does the ± mean; maintainer: "we report the standard error across five runs". https://github.com/harbor-framework/terminal-bench-1/issues/1418 (2026-02-19, open, 0 comments): displayed errors 1–3% vs ~5% total SE from an external recomputation (https://all-the-noises.github.io/); "models that make deterministic predictions would have 0 error regardless of the size of the dataset by this reasoning"; asks where the formula is computed. Issue #1460 (below) also states the displayed ± "are not reproduced by a simple binomial 95% interval".
- (1) Reader sees "87.1 ± 2.1". (2) Missing: the uncertainty *formula* and its inputs (5 run-level scores vs 89×5 item-level outcomes) — CONFLICTING between the maintainer's stated method and the external recomputation; unresolved on the tracker. (3) cohort→aggregate. (4) Retrospectively recoverable from public per-trial artifacts *if* the formula is stated; prospectively capturable as "uncertainty method" in a publication manifest. (5) Primary. (6) Community question; no formula published in-line at time of fetch.

#### B6. Hugging Face Open LLM Leaderboard v2 changed the aggregation (normalize to random baseline before averaging) — v1 and v2 rows not comparable (DOCUMENTED, primary blog not fetchable here)

- ASSERTED (secondary; primary HF Space blog is client-rendered and returned only a header to WebFetch): https://www.infoq.com/news/2024/10/open-llm-leaderboard-v2-launch/ (2024-10-10): scores rescaled so "random performance is 0 points and max score is 100 points, before averaging"; "users are always very quick to flag models with suspicious performance/likely contamination". Blog title confirmed at https://huggingface.co/spaces/open-llm-leaderboard/blog ("Open-LLM performances are plateauing, let's make the leaderboard steep again"); HN thread https://news.ycombinator.com/item?id=40831322 (fetch 429).
- OBSERVED (HF blog, 2023-06-23): https://huggingface.co/blog/open-llm-leaderboard-mmlu — see D1.
- (1)(2) Same model, different average, different rank across leaderboard versions; the aggregation is versioned by the *leaderboard*, not by the row. (3) cohort→aggregate and aggregate→table. (4) Retrospectively recoverable (HF publishes raw per-task results datasets); prospectively capturable as a named/versioned aggregation. (5) Secondary for the v2 detail; primary for v1 MMLU. (6) Publisher disclosed the change; no per-row aggregation id.

#### B7. Grok 3 chart: cons@64 for one model, @1 omitted for the other (DOCUMENTED)

- OBSERVED (press, with links to primary X posts): https://techcrunch.com/2025/02/22/did-xai-lie-about-grok-3s-benchmarks (2025-02-22): xAI's AIME-2025 chart omitted o3-mini-high's cons@64; at "@1" Grok 3 Reasoning Beta and mini "fall below o3-mini-high"; Boris Power https://x.com/BorisMPower/status/1892407015038996740; Igor Babuschkin https://x.com/ibab/status/1892418351084732654 (X posts not fetched; TechCrunch reproduces the substance); Nathan Lambert on undisclosed "computational (and monetary) cost ... for each model to achieve its best score".
- (1) One bar per model. (2) Estimator (cons@64 vs single sample) not attached to each bar; cost undisclosed. (3) cohort→aggregate, presented at table→claim. (4) Prospective (estimator id + cost). (5) Primary X posts exist; I read them through TechCrunch (secondary). (6) Caught by a competitor's employee within days; no policy.

#### B8. Gemini Ultra 90.04% MMLU (uncertainty-routed CoT@32) vs GPT-4 86.4% (5-shot) (DOCUMENTED in the report's own table)

- ASSERTED (search-result summaries; primary is the Gemini 1 technical report PDF https://storage.googleapis.com/deepmind-media/gemini/gemini_1_report.pdf, not parsed in this lane): Gemini Ultra 90.04% CoT@32 vs 83.7% 5-shot; GPT-4 87.29% CoT@32 vs 86.4% 5-shot; the headline compared across estimators; with plain CoT@32 GPT-4 still led until "uncertainty routing" was added.
- (1) "Beats human experts on MMLU." (2) Estimator differs between the two headline cells. (3) cohort→aggregate. (4) Prospective. (5) Secondary in this lane. (6) Community readers of the appendix.

#### B9. Claude 4 "parallel test-time compute" number as a second operating point (DISCLOSED)

- OBSERVED: https://www.anthropic.com/news/claude-4 footnote (see B2). (1) Two bars per model, one much higher. (2) Selector model, sample count, and reject rule are described in prose, not as a machine-readable estimator. (3) cohort→aggregate. (4) Prospective. (5) Primary. (6) Footnote.

#### B10. Uncertainty not reported; reported gains inside seed/hardware noise (STUDIES)

- OBSERVED (abstracts): https://arxiv.org/abs/2411.00640 (Miller, 2024-11-01) — questions as "drawn from an unseen super-population"; formulas for SEM, paired comparison, power. https://arxiv.org/abs/2406.10229 (Madaan et al., 2024-06-14) — seed variance; "carefully factor in variance when comparing models". https://arxiv.org/abs/2504.07086 (Hochlehnert et al., 2025-04-09, COLM 2025) — benchmarks "highly sensitive to ... decoding parameters, random seeds, prompt formatting, and even hardware and software configurations"; "most reinforcement learning (RL) approaches yield only modest improvements—far below prior claims—and are prone to overfitting, especially on small-scale benchmarks like AIME'24".
- (1) Point estimates. (2) Missing: seeds, decoding params, hardware, n. (3) cohort→aggregate. (4) Prospectively capturable; retrospectively often UNAVAILABLE. (5) Primary abstracts. (6) Caught by re-evaluation studies, not by any leaderboard mechanism.

### 2.C Aggregate → table (row publication, mutable rows, selective disclosure)

#### C1. Chatbot Arena: private variants, best-of-N disclosure, silent deprecation (STUDY + INCIDENT)

- OBSERVED (arXiv abs + html): https://arxiv.org/abs/2504.20879 (v1 2025-04-29, v2 2025-05-12; NeurIPS 2025 poster https://neurips.cc/virtual/2025/poster/121845): "27 private LLM variants tested by Meta in the lead-up to the Llama-4 release"; "205 models have been silently deprecated, a number that substantially exceeds the 47 models officially marked as deprecated"; "testing just 20 variants yields a notable increase of approximately 50 points in the maximum score identified"; "there is no guarantee that the version appearing on the public leaderboard matches the publicly available API"; data-share estimates 19.2% (Google), 20.4% (OpenAI), 29.7% for 83 open-weight models combined; "relative performance gains of up to 112%".
- OBSERVED (secondary quoting primary): https://simonwillison.net/2025/Apr/8/lmaren/ quoting the lmarena.ai thread https://twitter.com/lmarena_ai/status/1909397817434816562 (2025-04-08): releasing "2,000+ head-to-head battle results for public review"; "updating our leaderboard policies to reinforce our commitment to fair, reproducible evaluations". ASSERTED (press): the public HF Llama-4-Maverick was later added and ranked far below the "Llama-4-Maverick-03-26-Experimental" row (search summaries cite rank #32 vs #2).
- (1) A leaderboard row labeled with a model name. (2) Missing: that the row's model was a chat-tuned variant not equal to the released weights; that N other variants were tested and withdrawn; that many rows were deprecated without notice. (3) aggregate→table (row provenance and selection) and table→claim (name ≠ released artifact). (4) Fundamentally external: only the operator and provider know the variant count; retrospectively partly recoverable from Arena's released battle data. (5) Primary study with counts; primary operator statement. (6) Caught by external researchers + community; policy changed by the operator; the released 2,000 battles are the audit artifact.

#### C2. Terminal-Bench 2.0/2.1 leaderboard: rows visible in archived snapshots, later absent, no public row-state record; per-row detail pages withdrawn; submission policy narrowed (DOCUMENTED, unresolved)

- OBSERVED (issue): https://github.com/harbor-framework/terminal-bench-1/issues/1460 (2026-07-10, open, 2 comments, no maintainer reply at fetch): a submission merged to the public HF submissions repo (`harborframework/terminal-bench-2-leaderboard`, commit `2ded16e9...`, PR #170) "appeared as rank 1 (~90.2% ± 2.1)" in a 2026-06-08 Wayback snapshot and is "absent from the 2026-06-10 archived snapshot onward"; a second top-2 row likewise absent; eight live rows whose displayed score matches none of {raw mean, pass@5, drop-no-verifier attempts/tasks, n, n−no_verifier}; the ± not a simple binomial interval; request for a "public manifest ... per leaderboard row: included/excluded, trials removed/corrected/rescored, reason, denominator and scoring policy, uncertainty formula, mapping to HF submission folder or commit". Independent comment same day: HF API lists 76 public submission dirs including the vanished ones; live HTML says 142 entries; no companion include/exclude/rescore manifest found in either repo.
- OBSERVED (issue): https://github.com/harbor-framework/terminal-bench-1/issues/1467 (2026-07-22, closed 2026-07-28 by reporter, "No response so far"): TB 2.1 leaderboard row detail pages began showing "No cached eval break down yet".
- OBSERVED (issue): https://github.com/harbor-framework/terminal-bench/issues/1507 (2026-08-09, open; maintainer-authored): TB 3 leaderboard "publicly auditable, but only accepting submissions from runs we made ourselves"; reason: "too many issues with community submissions with modified jobs / bad faith agents (e.g. shipping oracle trajectories in the agent harness)"; comment: "For 3.1 this should validate the versions of the task / submit to the correct version of the leaderboard".
- OBSERVED (PR): https://github.com/harbor-framework/harbor/pull/2358 (merged 2026-07-21, merge commit b3d5f5af62cc11ad42a7f7548cb64f3db6b15e94) adds `harbor job/trial regrade`; docs at pinned a27e9c2 `docs/content/docs/run-jobs/regrade.mdx`: "Source trials and jobs are never modified. Every regrade produces a new trial or job directory"; provenance `source_trial {action, type, trial_id, path}` in `config.json` and `lock.json`, source task lock copied verbatim; "the link back to the source lives in provenance, not the name". Related open items: #1767 (score against a new rubric without re-running), #2155 (WIP rescore CLI).
- (1) A leaderboard with rank-ordered rows and ±. (2) Missing: the row-state artifact (why a row left; whether it was rescored; how the ± is computed; the mapping from public submission to live row); and, later, the per-row breakdown itself. (3) aggregate→table. (4) Row inclusion/exclusion decisions are *fundamentally external* to trial evidence — recoverable only if the publisher records them; the per-trial artifacts are public and were successfully recomputed to 89.9% mean by the reporter (so the *cohort* was reconstructable; the *table state* was not). Regrade lineage is now prospectively capturable in Harbor. (5) Primary issues + Wayback URLs cited in-issue; the maintainer's motive statement in #1507 is primary. (6) Caught by external audit; the maintainers' response was a policy narrowing (self-run only, version-validated), not a manifest. Whether the two vanished rows were the "modified jobs / bad faith agents" of #1507 is UNAVAILABLE — the two issues do not reference each other.

#### C3. SWE-bench leaderboard: many submissions' patches edit the evaluation tests; older rows not re-evaluated (DOCUMENTED)

- OBSERVED (issue): https://github.com/SWE-bench/experiments/issues/217 (2025-05-07, closed 2025-07-05): "On the 61 submissions I analyzed, 42 contain at least 1 patch editing a test file, and 17 contain more than 10"; re-running with test edits filtered flips instances both ways (e.g., +1.9% for one Claude-3.7 row; OpenHands+Sonnet-4 "80/500 patches editing the tests", Anthropic Sonnet-4 "305/500"). Maintainer 2025-06-19: agrees; "I unfortunately don't think I'd have the bandwidth to re-evaluate older submissions".
- (1) A row's % resolved. (2) Missing: whether the patch touched files that the grader's `test_patch` overwrites — detectable from bytes, but the aggregation did not check it; and once found, older rows stay as-is. (3) aggregate→table (rows not uniformly re-scored) with a trial→cohort root. (4) Retrospectively recoverable per row (patches are public) — the reporter did it; not applied to the table. (5) Primary. (6) Community audit; harness fix requested; table not corrected for older rows.

#### C4. HF Open LLM Leaderboard flagged models (community mechanism)

- OBSERVED (HF discussion titles/URLs from search; not fetched in full): https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard/discussions/444 ("[FLAG] fblgit/una-xaberius-34b-v1beta"), https://huggingface.co/spaces/open-llm-leaderboard/open_llm_leaderboard/discussions/1022 ("FLAG - newsbang/Homer-v0.5-Qwen2.5-7B MATH contamination"), https://huggingface.co/spaces/open-llm-leaderboard/open_llm_leaderboard/discussions/472 (contamination techniques thread). ASSERTED (HF docs via search): flagged rows keep the row but mark it and link the discussion.
- (1)(2) Row stays visible with a flag; the *reason* lives in a discussion thread, not in the row's data. (3) aggregate→table. (4) Prospective (flag + reason id). (5) Primary URLs, content partly read. (6) This *is* the mechanism: community flag + operator label.

### 2.D Table → claim (instrument identity: prompt, harness, scoring, verifier, model version, funder)

#### D1. Same model, three MMLU implementations: 0.636 / 0.637 / 0.488 (DOCUMENTED, primary)

- OBSERVED (HF blog): https://huggingface.co/blog/open-llm-leaderboard-mmlu (2023-06-23; Fourrier, Habib, Launay, Wolf): LLaMA-65B MMLU = 0.636 (original implementation), 0.637 (HELM), 0.488 (lm-eval-harness Jan 2023 commit e47e01b); causes: prompt format differences (topic line, "Choices:" label, spacing) and scoring (letter log-prob vs generated text match vs log-likelihood of full answer strings); "very different numbers and even change the ranking order"; harness updated afterwards.
- (1) "LLaMA-65B MMLU 63.4" in the paper vs "48.8" on the leaderboard. (2) Missing from the number: harness commit + prompt template + scoring rule. (3) table→claim (and the copied-baseline problem: numbers copied across papers under different harnesses). (4) Prospectively capturable (harness id, prompt digest, scoring rule id); retrospectively recovered here by re-running. (5) Primary. (6) Caught by the leaderboard operators after community complaints; harness changed.

#### D2. API model behind a stable name changes over time; and the finding itself contested (DOCUMENTED, CONFLICTING interpretation)

- OBSERVED (arXiv abs): https://arxiv.org/abs/2307.09009 (Chen, Zaharia, Zou; v1 2023-07-18, v3 2023-10-31): March vs June 2023 snapshots of GPT-4/GPT-3.5; "GPT-4 (March 2023) was reasonable at identifying prime vs. composite numbers (84% accuracy) but GPT-4 (June 2023) was poor on these same questions (51% accuracy)".
- OBSERVED (blog): https://www.normaltech.ai/p/is-gpt-4-getting-worse-over-time (Narayanan & Kapoor, 2023-07-19; redirected from aisnakeoil.com): the 500 test numbers were all prime; "A model that has a capability may or may not display that capability in response to a particular prompt" — behavior change, not capability loss.
- (1) "GPT-4 got worse." (2) Missing at the provider layer: what changed behind the alias (fundamentally external); missing at the study layer: a balanced test set (claim-support). CONFLICTING: the two sources agree on the numbers and disagree on the interpretation. (3) table→claim (model identity) and claim→interpretation. (4) Provider change: fundamentally external, capturable only as a dated snapshot id/response-model header; the interpretation dispute is claim-level. (5) Primary both. (6) Community critique within a day; snapshot ids exist as a provider mechanism.

#### D3. o3-preview vs shipped o3: same benchmark names, different model and compute (DOCUMENTED, primary operator pages)

- OBSERVED (ARC Prize): https://arcprize.org/blog/oai-o3-pub-breakthrough (2024-12-20): semi-private 75.7% (6 samples, ~$26–27/task) and 87.5% (1024 samples, "172x" compute, above the $10k threshold); "OpenAI shared they trained the o3 we tested on 75% of the Public Training set". https://arcprize.org/blog/analyzing-o3-with-arc-agi (2025-04-22): released o3-low 41% ($1.22/task), o3-medium 53% ($2.52/task); "The production o3 uses a different model", multimodal, reduced test-time compute, "fine-tuned for chat and product applications".
- ASSERTED (search summaries; Epoch X post https://x.com/EpochAIResearch/status/1913379478778134941 not fetched): Epoch's own FrontierMath run of released o3 ≈10% (±2%) vs OpenAI's December "over 25%" claim; Epoch: difference "might be due to OpenAI evaluating with a more powerful internal scaffold, using more test-time computing, or because those results were run on a different subset".
- (1) "o3 scores 87.5% on ARC-AGI / 25% on FrontierMath". (2) Missing: that "o3" in December and "o3" in April are different artifacts, run at different compute and (for FrontierMath) possibly on a different subset with a different scaffold. (3) table→claim (model identity, budget, subset). (4) Fundamentally external for the model identity; the operator captured what it could (sample counts, cost, training-set exposure) — a good prospective-capture example. (5) Primary for ARC; secondary for Epoch's number. (6) Caught by the two independent evaluators re-running the released model.

#### D4. FrontierMath: benchmark funder had access to most problems; disclosure delayed by contract (DOCUMENTED)

- OBSERVED (Epoch page): https://epoch.ai/latest/openai-and-frontiermath (2025-01-23): "OpenAI commissioned Epoch AI to produce 300 advanced math problems"; OpenAI "has access to the problems and solutions, with the exception of a holdout set"; "finalizing a 50-problem set for which OpenAI will only receive the problem statements". ASSERTED (press): contract prevented earlier disclosure; o3 "25.2%" reported at the December announcement.
- (1) An independent-looking benchmark number. (2) Missing: instrument custody (who owns/has seen the items). (3) table→claim. (4) Fundamentally external; capturable only as a disclosure/policy field. (5) Primary operator statement. (6) Caught by a contractor's public post; operator disclosed and created a holdout.

#### D5. Reflection 70B: eval-code bug + hosted "API" not the released weights (DOCUMENTED, mostly secondary)

- ASSERTED (press; primary postmortem page not reachable — glaive.ai blog URL returned a generic company page; VentureBeat 429): announced 2024-09-05 with GSM8K 99.2 / MMLU 89.9 / HumanEval 91 / MATH 79.7; third parties (Artificial Analysis) could not reproduce with the HF weights; the private API was found to be a Claude-3.5-Sonnet wrapper filtering the word "Claude"; postmortem 2024-10 (Techmeme 2024-10-04 https://www.techmeme.com/241004/p2: "a bug in the initial code for benchmarking") gave corrected MATH 70.8 and GSM8K 95.22.
- (1) A table of SOTA numbers. (2) Missing: which artifact produced them (weights vs API vs another vendor), and a scoring bug in the harness. (3) table→claim (artifact identity) with a trial→cohort root (bad scoring). (4) Retrospectively recoverable only by re-running the released weights (which is what happened); prospectively capturable as response-model identity + harness digest. (5) Secondary; treat specific corrected numbers as ASSERTED. (6) Caught within 4 days by independent evaluators; no leaderboard involved.

#### D6. Verifier/task revision drift: the instrument was wrong and was later corrected (DOCUMENTED, several benchmarks)

- OBSERVED (arXiv abs): MMLU-Redux https://arxiv.org/abs/2406.04127 (2024-06-06): "5,700 manually re-annotated questions across all 57 MMLU subjects"; "6.49% of MMLU questions contain errors"; "57% of the analysed questions in the Virology subset contain errors".
- OBSERVED (arXiv abs): EvalPlus/HumanEval+ https://arxiv.org/abs/2305.01210 (2023-05-02): "80x" more tests; "reducing the pass@k by up-to 19.3-28.9%".
- OBSERVED (arXiv abs): GSM1k https://arxiv.org/abs/2405.00332 (2024-05-01): "accuracy drops of up to 8%"; "many models, especially those on the frontier, show minimal signs of overfitting"; Spearman r² = 0.36 between GSM8K generation likelihood and the gap.
- ASSERTED (search summaries; https://openai.com/index/introducing-swe-bench-verified/ returned 403): SWE-bench Verified (Aug 2024): 1,699 reviewed, 500 kept; 38.3% underspecified, 61.1% unfair tests, 68.3% filtered; GPT-4o 33.2% Verified vs 16% original.
- ASSERTED (search summaries; https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/ returned 403; a third-party note dates it 2026-02-24 https://github.com/AkihikoWatanabe/paper_notes/issues/4692; https://x.com/OpenAIDevs/status/2026002219909427270): of 138 problems o3 consistently failed, 59.4% have flawed tests; frontier models reproduce gold patches verbatim; OpenAI stops reporting SWE-bench Verified.
- ASSERTED (search summaries; https://www.futurehouse.org/research/hle-exam, 2025-07-23): "29 ± 3.7%" of 321 text-only bio/chem HLE answers conflict with peer-reviewed literature; HLE team's follow-up ~18% "problematic"; HLE-Verified https://arxiv.org/html/2602.13964v2.
- (1) A score on a named benchmark. (2) The benchmark's items/tests were partly wrong; every earlier score is on a different instrument than a later one; comparisons across the revision are silently invalid. (3) table→claim (instrument identity/version). (4) Prospectively capturable (dataset/verifier digest); retrospectively recoverable only if the old and new versions are both retained (they were, in these cases). (5) Mixed: arXiv abstracts primary; OpenAI pages secondary. (6) Caught by external audits; publishers issued new versions; leaderboards generally did not re-score old rows.

#### D7. Terminal-Bench dataset versions and Harbor regrade as the *positive* mechanism

- OBSERVED: TB2 repo PR "Terminal-Bench 2.1" https://github.com/harbor-framework/terminal-bench-2/pull/53 (2026-03-11, open at fetch — title only read); TB2 issue "RFC: digest-pin docker_image in task.toml" https://github.com/harbor-framework/terminal-bench-2/issues/66 (2026-05-13); TB1 #1507 comment: "validate the versions of the task / submit to the correct version of the leaderboard". Harbor #2231 (2026-07-08, open): version-pinned dataset run writes a `config.json` carrying both `version` and `ref` that "fails its own validation on reload" so `harbor upload`/`resume` crash — the lineage record itself is not reloadable without hand-editing.
- (1)(2)(3) table→claim: which task version graded which row. (4) Prospective (task digest in `lock.json` exists; leaderboard version validation planned). (5) Primary. (6) Harbor `lock.json` + `regrade` provenance are the mechanism; #2231 shows the record can be self-inconsistent.

#### D8. Verifier exploit found post hoc: Sakana "AI CUDA Engineer" (DOCUMENTED, secondary here)

- ASSERTED (press; TechCrunch 2025-02-21 https://techcrunch.com/2025/02/21/sakana-walks-back-claims-that-its-ai-can-dramatically-speed-up-model-training/): claimed 10–100× (headline 150×); third parties found kernels that exploited a memory bug in the evaluation harness to skip correctness checks; company statement 2025-02-24 acknowledging the reward hack and revising the paper.
- (1) A speedup table. (2) The verifier accepted incorrect kernels; the number reconstructs exactly and is wrong. (3) table→claim (verifier validity) — a claim-support failure, not a lineage failure. (4) Retrospectively recoverable (kernels + harness public); prospectively capturable only as verifier identity, not verifier *validity*. (5) Secondary. (6) Caught by external users within days.

### 2.E Claim → interpretation (number reproducible; meaning unsupported)

#### E1. GPT-4 "90th percentile" on the bar exam (DOCUMENTED, primary abstract via repository)

- OBSERVED (repository record): https://scholarship.law.tamu.edu/facscholar/2405/ — Martínez, "Re-evaluating GPT-4's bar exam performance," 33 A.I. & L. 581 (March 2024; Springer DOI 10.1007/s10506-024-09396-9): ~90th percentile relative to February Illinois *repeaters*; ~62nd percentile vs first-time takers (42nd on essays); ~48th percentile vs those who passed (15th on essays); July data: below 69th overall, 48th on essays; "several methodological issues in the grading of the MPT + MEE components ... call into question the validity of the reported essay score".
- (1) "GPT-4 passes the bar in the 90th percentile." (2) The raw score is not disputed; the *reference population* for the percentile and the essay-grading protocol were not documented. (3) claim→interpretation. (4) The reference-population choice is capturable as a claim parameter; the essay grading is UNAVAILABLE (undocumented). (5) Primary (repository abstract; SSRN/Springer/MIT PDF returned 403/405/redirect). (6) Caught by an academic re-analysis a year later.

#### E2. "Emergent abilities" as a metric artifact (DOCUMENTED)

- OBSERVED (arXiv abs): https://arxiv.org/abs/2304.15004 (Schaeffer, Miranda, Koyejo; 2023-04-28): "nonlinear or discontinuous metrics produce apparent emergent abilities, whereas linear or continuous metrics produce smooth, continuous predictable changes".
- (1) Sharp capability jumps. (2) The numbers reproduce; the metric choice (exact-match vs token-edit distance) drives the shape. (3) claim→interpretation (with a cohort→aggregate root: metric id). (4) Prospective (metric id is already in any decent record); the *interpretation* is external. (5) Primary. (6) Academic critique.

#### E3. SWE-bench Verified: memorization and contamination discovered post hoc (DOCUMENTED)

- OBSERVED (arXiv abs): https://arxiv.org/abs/2506.12286 (Liang et al., 2025-06-14): "up to 76% accuracy in identifying buggy file paths using only issue descriptions" on Verified vs ~53% elsewhere; "performance gains on SWE-Bench-Verified may be partially driven by memorization"; verbatim 5-gram similarity 35% vs 18%.
- Plus OpenAI's 2026-02 withdrawal (D6) and repo-state leakage (A7).
- (1) A resolved-rate. (2) Nothing about the run's lineage is missing; what is missing is *support* for the claim "resolves novel issues." (3) claim→interpretation. (4) Fundamentally external (training data). (5) Primary abstract. (6) Academic audit; the benchmark's own sponsor eventually stopped reporting it.

#### E4. "AI Scientist" claims vs audited output (DOCUMENTED)

- OBSERVED (arXiv abs): https://arxiv.org/abs/2502.14297 (Beel et al., 2025-02-20): "42% of experiments failed due to coding errors"; papers with "missing figures, repeated sections, and placeholder text like 'Conclusions Here'" and "hallucinated numerical results"; cost "USD 6 to 15 with 3.5 hours of human involvement".
- (1) "Fully automated scientific discovery." (2) The artifacts existed and were reproducible as artifacts; the claim about their scientific validity was not supported by them. (3) claim→interpretation. (4) External (expert judgment). (5) Primary. (6) Independent academic evaluation.

#### E5. Terminal-Bench grader asserts nothing about untouched state (DOCUMENTED, TB)

- OBSERVED (issue): https://github.com/harbor-framework/terminal-bench-1/issues/1459 (2026-07-09, open): reference solution + `rm -rf .git` scores reward 1 on `fix-git`; "40 of 83 (48%) survive at least one careless deletion inside the task's own workspace" on TB 2.1; receipts repo linked; independent source check in comments confirms `test_outputs.py` compares only two file hashes. Related: reward-hacking issue #1429 (closed 2026-04-01).
- (1) reward=1. (2) Nothing missing from lineage; the verifier's *frame* is narrower than the reader assumes. (3) claim→interpretation (what "pass" certifies). (4) External to lineage; capturable only as a documented verifier scope. (5) Primary with public receipts. (6) Community audit; opt-in `frame_gate` PR proposed in Harbor (#2266, not verified here).

### 2.F Reproducibility census (frequency evidence)

- OBSERVED (arXiv abs): https://arxiv.org/abs/2510.25506 (Angermeir et al., 2025-10-29): 85 LLM-centric ICSE/ASE 2024 papers; 18 used commercial LLM APIs and provided artifacts; 5 "sufficiently complete and executable"; 0 fully reproduced; "Two studies seemed to be partially reproducible, and three ... not".
- OBSERVED (arXiv abs): https://arxiv.org/abs/2405.14782 (Biderman et al., "Lessons from the Trenches", 2024-05-23): "sensitivity of models to evaluation setup, difficulty of proper comparisons across methods, and the lack of reproducibility and transparency".
- OBSERVED (arXiv abs): Hochlehnert et al. 2504.07086 (above): "Performance gains reported in recent studies frequently hinge on unclear comparisons or unreported sources of variance."
- ASSERTED (search summary; not fetched): a 72-paper security/SE audit found at least one LLM-specific pitfall in every paper, 15.7% of pitfalls discussed (source URL not captured; treat as unverified lead).

---

## 3. Explicit answers to the lane questions

**Retries replacing previous attempts.** Mechanism DOCUMENTED in code (A1: Harbor `rmtree` before retry, `n_retries` count survives, bytes do not; A2: resume deletes result-less dirs). Public incident where this changed a reported number: NOT FOUND → harm HYPOTHETICAL. Default `max_retries=0` limits exposure but leaderboard operators may set it higher (UNAVAILABLE: I did not find the TB leaderboard's retry setting published).

**Best-of-N / private testing then selective disclosure.** DOCUMENTED with counts (C1: 27 Meta variants; ~50-point gain from testing 20 variants; 205 silent deprecations; Llama-4 experimental row). Fundamentally external to any run record.

**Silent reruns.** No primary case found where a *published* row was silently re-run and replaced. Nearest: TB 2.0 rows disappearing between Wayback snapshots with no record (C2 — could be removal, rescoring, or rerun: UNAVAILABLE); SWE-bench experiments file "assembled from two overlapping partial runs" (A5). Otherwise HYPOTHETICAL.

**Changing prompts/harnesses.** DOCUMENTED, primary, quantified (D1: 63.6/63.7/48.8). Also B2 scaffolds, B4 estimators, B10 seeds/hardware.

**Model routing/fallback or provider-side change behind a stable name.** DOCUMENTED (D2 snapshots; D3 o3-preview vs o3; D5 Reflection API; C1 "no guarantee that the version appearing on the public leaderboard matches the publicly available API"). Fundamentally external; only a provider-emitted response-model identity mitigates.

**Task/verifier revision drift; regrading.** DOCUMENTED (D6 five benchmarks; D7 TB versions; Harbor regrade merged 2026-07-21 with explicit source-trial provenance; A7 image rebuild after git-leak). Regrade lineage is prospectively capturable and Harbor already does it; leaderboards mostly did not re-score old rows (C3 maintainer bandwidth statement).

**Filtering after results are seen / manual invalidation.** DOCUMENTED-but-opaque (C2: rows removed with no public reason; #1507 states bad-faith submissions existed). Positive counter-example B3 (ARC states the exclusion and reason).

**Missing failed trials.** DOCUMENTED at the display layer (A4: empty trial rows) and at the infra layer (A3: 447/640 infra failures booked as agent errors). Root cause in A4 UNAVAILABLE.

**Denominator drift.** DOCUMENTED and mostly *disclosed in prose* (B1 570/2294; B2 477/489/500; B3 37/100 excluded; B4 MATH-500; ARC public vs semi-private vs private tiers; FrontierMath 300 commissioned / 50 holdout). The failure is that the disclosure does not travel with the number.

**Duplicated trials.** DOCUMENTED and quantified (A5: 10.51% → 9.29%; nine lists in four submissions of 254).

**Changes in aggregation.** DOCUMENTED (B6 HF v2 normalization; B7/B8 estimator mismatch across bars). HELM "mean win rate" not re-verified in this lane (omitted rather than asserted).

**Missing uncertainty.** DOCUMENTED (B5 TB ± semantics unresolved; B10 studies).

**Mutable leaderboard rows.** DOCUMENTED (C1 deprecations; C2 TB rows; C3 SWE-bench rows not re-scored; C4 HF flags; A5 SWE-bench score to be lowered by PR).

**Multiple operating points summarized as one.** DOCUMENTED (B7 cons@64; B8 CoT@32-routed; B9 parallel compute; D3 o3 6 vs 1024 samples; cost/task disclosed only by ARC).

**Manuscript claims assembled from results under different configurations / baselines copied.** DOCUMENTED at the mechanism level (D1 is exactly "paper number vs harness number for the same model"; Hochlehnert "unclear comparisons"; Angermeir 0/5 reproduced). A single named paper caught copying a baseline under a mismatched config: NOT pinned in this lane (leads exist, see §4).

**Reasoning-model thinking budget hidden.** DOCUMENTED (D3: o3-preview compute "not available in the production o3"; B7 cost undisclosed). Harbor has an open PR to standardize reasoning-effort configuration across installed agents (https://github.com/harbor-framework/harbor/pull/2531, 2026-07-30, title only read) — i.e., the budget is not yet uniformly captured upstream.

**Contamination discovered post hoc — lineage or claim-support failure?** Claim-support. In every case (GSM1k, SWE-bench Illusion, OpenAI's Verified withdrawal, TB "solution available online") the run lineage was intact and the number reproduced; what failed was the inference from score to capability. Lineage can at most record *exposure facts* (ARC: "trained on 75% of the Public Training set"; FrontierMath: funder access) that a claim policy can then weigh.

**Number reproducible, interpretation unsupported.** DOCUMENTED (E1–E5, D2's prime test, D8's exact-but-wrong speedup).

---

## 4. What I could NOT establish, and where I looked

- The Terminal-Bench 2.0 leaderboard's reason for the two vanished rows, its scoring denominator policy, and its ± formula: not in terminal-bench-1 issues #1460/#1256/#1418, not in the HF submissions repo per the in-issue readback, no maintainer reply on #1460 at fetch. Whether #1507's "modified jobs / bad faith agents" refers to those rows: UNAVAILABLE.
- The cause of empty trial rows in #1445: UNAVAILABLE (open issue, no maintainer comment).
- OpenAI primary pages (SWE-bench Verified introduction; the 2026-02 withdrawal): HTTP 403 to WebFetch; figures carried as ASSERTED from search summaries.
- HF Open LLM Leaderboard v2 blog body: client-rendered Space, header only; HN thread 429; v2 details ASSERTED via InfoQ.
- Reflection 70B primary postmortem: glaive.ai URL resolved to an unrelated company page; VentureBeat 429; details ASSERTED via Techmeme/press.
- Martínez full text: SSRN 403, Springer login redirect, MIT DSpace 405; abstract obtained from the TAMU repository record.
- Gemini technical report Table 2 footnotes: not parsed; figures ASSERTED from search summaries.
- Epoch's own o3 FrontierMath 10% figure: X post not fetched; ASSERTED via press.
- A single named paper documented as copying a baseline under a mismatched configuration: not pinned. Leads: Hochlehnert et al. 2504.07086 §on baselines; Angermeir 2510.25506; the 72-paper pitfalls audit (URL not captured).
- HELM's aggregation ("mean win rate") and its later changes: not re-verified; omitted.
- Whether Terminal-Bench leaderboard runs use `max_retries>0`: not found in the repos searched.
- Frequency of retry-deleted attempts in real Harbor jobs: only `stats.n_retries` exists; no public census found. (E1 in the eval-evidence RESEARCH_MAP is exactly this measurement and is unrun.)
- laude-institute/harden-v0: `gh repo view` could not resolve it (private or moved); not used.

---

## 5. Emergent taxonomy and what would have detected each mode

The taxonomy below is organized by *what was missing*, derived from the cases, not from the prompt list. Detection columns: **T** = per-trial evidence bundle (byte identity + provenance states, as in eval-evidence today); **C** = campaign/claim structure (expected vs included attempts, denominator, aggregation id, uncertainty method, supersession/regrade links, instrument identity at row level); **X** = something else (publisher policy, provider disclosure, external audit, expert judgment).

| # | Missing-information class | Cases | T | C | X | Note |
|---|---|---|---|---|---|---|
| 1 | Attempt identity/uniqueness (dupes, unions of partial runs) | A5 | partial | yes | — | T catches only if each attempt is bundled with a stable id and the aggregator consumes bundles; C is where uniqueness must be enforced. |
| 2 | Attempt validity state (infra collision, upload failure, missing rows) | A3, A4 | no | yes | — | Needs an explicit "attempt invalid: reason" state and expected-vs-discovered counts; bytes of a collided attempt look like an ordinary failure. |
| 3 | Superseded/replaced attempts (retry deletes, resume deletes) | A1, A2 | only if sealed before deletion | yes | — | Prospective fix is upstream (do not delete; or record digest+reason). |
| 4 | Extraction/labeling transform mismatch on intact bytes | A6 | no | yes (named transform) | — | eval-evidence's "structured provenance" companion record (transform name/version) is the right shape here. |
| 5 | Environment/instrument content identity (image contents, task version, test edits, harness prompt/scoring) | A7, C3, D1, D6, D7 | yes for digests | yes for cross-row comparability | — | T proves *which* bytes; C proves *same instrument across rows*. Digest ≠ validity (D6/D8). |
| 6 | Denominator/subset identity | B1, B2, B3, B4, ARC tiers, FrontierMath holdout | no | yes | — | Prose disclosure exists in most cases; nothing carries it with the number. |
| 7 | Estimator/aggregation identity (pass@1-avg-k, cons@64, CoT@32-routed, best-of-N selector, normalization) | B4, B6, B7, B8, B9 | no | yes | — | A named, versioned aggregation per row. |
| 8 | Uncertainty method | B5, B10 | no | yes | — | Formula + inputs (run-level vs item-level). |
| 9 | Row publication state (included/excluded/rescored/deprecated, reason, mapping to artifacts) | C1, C2, C3, C4 | no | yes | policy | The single artifact whose absence recurs most across operators. |
| 10 | Model artifact identity behind a name (variant, snapshot, routed API, preview vs release) | C1, D2, D3, D5 | no | partly (record what provider emitted) | provider disclosure | Fundamentally external unless the provider emits a response-model id. |
| 11 | Budget/operating point (compute, samples, cost, reasoning effort) | B7, D3 | partly | yes | provider | Harbor is still standardizing reasoning-effort capture (PR 2531). |
| 12 | Instrument custody/exposure (funder access, training-set exposure, open-internet solutions) | D4, D3, A8, E3 | no | record only | disclosure + audit | Recordable facts; interpretation is a claim policy. |
| 13 | Verifier validity/scope (accepts wrong answers; asserts no frame) | D8, E5, D6 | no | no | audit | Digest establishes identity, never correctness — the lane's first epistemic rule, observed empirically. |
| 14 | Claim reference frame (percentile population, metric-induced "emergence", "resolves novel issues") | E1, E2, E3, E4, D2 | no | claim record can name the frame | expert judgment | Purely claim→interpretation. |

Counts (DERIVED from the table, one primary class per case, 35 cases incl. sub-cases): T alone would have *detected* ~4 (A5 partial, A7, C3, D1/D6/D7 digest-level); C would have detected or made explicit ~22; X was required for ~14 (some overlap). Frequency evidence from studies: 27 private variants and 205 silent deprecations (C1); 42/61 SWE-bench submissions with test-file edits (C3); 9 lists in 4/254 submissions with duplicate ids (A5); 6.49% MMLU items wrong (D6); 68.3% of SWE-bench filtered in Verified (D6, asserted); 29±3.7% HLE bio/chem answers contested (D6, asserted); 0/5 executable LLM-API SE papers fully reproduced (§2.F).

What actually caught things: community audit via GitHub issues or third-party re-runs in A3, A4, A5, A6, A7, C1, C2, C3, D1, D2, D3, D5, D8, E1–E5 (i.e., nearly all); operator policy in B3, C4, and post-hoc in C1/C2/TB #1507; harness features (Harbor regrade + lock provenance) exist but were built *after* most of these incidents and are not yet consumed by any of the leaderboards named here (UNAVAILABLE whether TB 3 leaderboard uses regrade provenance).

---

## 6. Implications for the central question

1. **The unit that failed most often is the row, not the trial.** The recurring missing artifact is a publication-time record per leaderboard row / per reported cell: attempt ids included, excluded ids with reasons, denominator, estimator/aggregation id, uncertainty formula, instrument identity (task version + verifier digest + harness/prompt digest + image digest), model artifact identity as emitted by the provider, budget/operating point, and links to superseding/regraded attempts. That is what #1460 asked Terminal-Bench for, what SWE-bench #217/#465 needed, what LMArena's 2,000-battle release approximated, and what ARC's policy page provides in prose. It is a leaderboard/publisher primitive; a per-trial bundle cannot supply it and should not try.

2. **Per-trial byte identity is necessary but small.** It is decisive exactly where the audit reduces to "which bytes" (test-file edits inside a patch, environment image contents, harness/prompt version, duplicated attempt ids if attempts are individually sealed, retry-deleted attempts if sealed before deletion). In this corpus that is a minority of failures, and in most of those the community recovered the answer from already-public bytes without a sealing layer (SWE-bench patches, TB per-trial `result.json`, HF submission dirs). The marginal value of sealing is therefore in *cheap, mechanical* audit and in archives that are not otherwise content-addressed — not in preventing the documented incidents.

3. **Provenance states earn their keep at the label boundary, not the digest boundary.** A6 (wrong key read as "no reward") and #2231 (a lock that cannot be reloaded) show that the honest state of a field ("observed from key X by transform Y" vs "unavailable") matters more than the digest of the file it came from. eval-evidence's conservative unavailable boundary and structured-provenance companion record address a real class (row 4). This is a point in favour of the abstraction, but it is a small, well-bounded feature.

4. **A large share is fundamentally external.** Private variants, provider substitution behind a name, funder access, training-set exposure, and interpretation frames are not in any run directory. The best any evidence layer can do is (a) record what the provider/operator *emitted* (response model id, snapshot, sample count, cost, training-exposure statement, network policy) with an explicit "asserted-by-provider" state, and (b) make the absence visible. Policy and disclosure did the rest in every documented case.

5. **Contamination and verifier validity are claim-support failures.** Every contamination/leak/exploit case reconstructs perfectly; the failure is that "reward=1" was read as "capable." This is consistent with the lane rule that a digest establishes identity, not correctness, and argues against building lineage machinery whose stated purpose is to make numbers "trustworthy." The right framing is: lineage makes claims *falsifiable*; audits falsify them.

6. **Is the proposed abstraction unnecessary?** As a *standalone per-trial envelope*, largely yes for the failure modes that actually occurred: Harbor already has `lock.json`, task digests, `source_trial` regrade provenance, retry counts, and job stats; the leaderboards' failures were at the row layer; the community found the bytes it needed. As a *small primitive* — a portable reference (digest + provenance state + named transform) that a row-level manifest can point at — it is useful and cheap, and it is the only piece of eval-evidence that this evidence base supports keeping. The measurement that would change this verdict is E1/E2 of the RESEARCH_MAP: if real Harbor archives show frequent retry deletion, resume deletion, or source conflicts that changed reported numbers, trial-level sealing moves from "small" to "load-bearing." No public case in this lane shows that yet.

7. **Concrete negative results worth keeping.** (i) No documented incident of a retry silently replacing an attempt in a published number — the mechanism exists (A1/A2) but the harm is unproven. (ii) No documented silent rerun of a published row with primary evidence — only unexplained disappearances. (iii) No named paper pinned as copying a baseline under a mismatched config — only aggregate reproducibility failures. These are the gaps a future lane should try to close with archive measurement rather than more literature.

---

## Appendix — source index (pinned)

- Harbor source: local clone, `a27e9c2ae10a31c40b2dcef33ef5486bce36e185` (files: `src/harbor/trial/queue.py` L200–222; `src/harbor/job.py` L252–260, ~L690; `src/harbor/models/job/config.py` `RetryConfig`; `docs/content/docs/run-jobs/regrade.mdx`); `origin/main` `f03db62fd2ed2ed1f79aefe024cfcbc68a0d759e` (2026-08-16); rmtree-on-retry introduced `080a1cb30` (2026-05-17, "Simplify trial flow (#1672)").
- Genuine Harbor job dirs (structure only): job `result.json` keys `n_total_trials`, `stats.{n_completed_trials,n_errored_trials,n_running_trials,n_pending_trials,n_cancelled_trials,n_retries,evals,...}`; `lock.json` keys `schema_version, created_at, harbor.{version,is_editable}, invocation, n_concurrent_trials, retry.*, trials`; trial dir has `config.json, result.json, agent/, verifier/{reward.txt,ctrf.json,test-stdout.txt}, artifacts/manifest.json, trial.log`.
- GitHub (read via `gh api` 2026-08-16): harbor-framework/terminal-bench-1 #527, #1256, #1418, #1430, #1445, #1459, #1460, #1467; harbor-framework/terminal-bench #1507, #1541 (+#1542, #1543, #1561, #1562); harbor-framework/terminal-bench-2 PR #53, #66; harbor-framework/harbor #1767, #2155, #2225, PR #2226, #2231, PR #2358 (merged b3d5f5af...), PR #2531; SWE-bench/experiments #217, #249, #301, #463, PR #465; SWE-bench/SWE-bench #465, #578. Note: laude-institute/terminal-bench redirects to harbor-framework/terminal-bench-1; harbor-framework/terminal-bench-3 redirects to harbor-framework/terminal-bench.
- Papers (arXiv abs pages fetched): 2504.20879 (v1 2025-04-29, v2 2025-05-12); 2307.09009 (v1 2023-07-18, v3 2023-10-31); 2406.04127 (2024-06-06); 2305.01210 (2023-05-02); 2405.00332 (2024-05-01); 2411.00640 (2024-11-01); 2406.10229 (2024-06-14); 2504.07086 (2025-04-09); 2510.25506 (2025-10-29); 2405.14782 (2024-05-23); 2304.15004 (2023-04-28); 2506.12286 (2025-06-14); 2502.14297 (2025-02-20); 2305.20050 (2023-05-31); 2501.12948v1 (html).
- Operator/vendor pages fetched: huggingface.co/blog/open-llm-leaderboard-mmlu (2023-06-23); arcprize.org/blog/oai-o3-pub-breakthrough (2024-12-20); arcprize.org/blog/analyzing-o3-with-arc-agi (2025-04-22); arcprize.org/policy; epoch.ai/latest/openai-and-frontiermath (2025-01-23); cognition.com/blog/swe-bench-technical-report (2024-03-15); anthropic.com/news/claude-4 (2025-05-22); simonwillison.net/2025/Apr/8/lmaren/ (2025-04-08); normaltech.ai/p/is-gpt-4-getting-worse-over-time (2023-07-19); techcrunch.com/2025/02/22/did-xai-lie-about-grok-3s-benchmarks (2025-02-22); infoq.com/news/2024/10/open-llm-leaderboard-v2-launch/ (2024-10-10); techmeme.com/241004/p2 (2024-10-04); scholarship.law.tamu.edu/facscholar/2405/.
- Fetch failures (recorded): openai.com (403 ×2); ssrn.com (403); law-ai.org (403); dspace.mit.edu PDF (405); link.springer.com (login redirect); huggingface.co Space blog (client-rendered); news.ycombinator.com (429); venturebeat.com (429); glaive.ai postmortem URL (unrelated page).

# C1 — Completeness and disagreement audit of lanes L1–L8

Date: 2026-08-16. Role: critic (completeness + disagreement + receipt spot-check + leak scan).
Inputs read in full: `L1-native-systems.md`, `L2-tb-leaderboard-walkback.md`, `L3-swebench-walkback.md`,
`L4-open-leaderboard-and-paper-table.md`, `L5-inhouse-paper-lineage.md`, `L6-prior-art.md`,
`L7-failure-modes.md`, `L8-adversarial-formulation.md` (all under `.../scratchpad/lanes/`).
Verification downloads made by this lane live in `.../scratchpad/lanes/C1work/` (public artifacts only).

Labels: OBSERVED / DERIVED / ASSERTED / CONFLICTING / UNAVAILABLE as in the lane rules. "CONFIRMED" below
means I re-fetched or re-read the primary artifact at the cited revision and it matches the lane's claim.

---

## 1. Verdict

The eight lane reports are, on spot-check, unusually well receipted: of 21 receipt groups I re-fetched or
re-read at the cited commit/URL (covering every lane), 18 reproduce exactly, and the three defects are
minor (one wrong line number in L1, one commit count in L5 that does not reproduce, one arithmetic slip
in L2 that does not affect its conclusion). I found **no leak of private benchmark data** — every
absolute path is either one the brief allowed or a third party's path inside a *public* HF submission,
and no task text, trajectory, or model output appears. There are, however, **three substantive
disagreements between lanes**, all on the Terminal-Bench 2.0 leaderboard: (i) L1 declares the "±"
column UNAVAILABLE while L2 derives it exactly (and I confirmed L2's receipt: the site's JS renders
`(100*stderr*1.96).toFixed(1)`, and L1's own computed 1.36 × 1.96 = 2.7 — L1 computed the right SE and
missed the display factor); (ii) L1 generalises TB 2.1's "errored trials count 0, pooled" rule to the 2.0
page, while L2 shows the 2.0 importer uses a *mean of per-task means* and *drops* some errored trials
(exact on 4 rows; I re-ran L2's rule on its own 445 downloaded NexAU trial records and reproduced
0.8471910112359547 vs the site's 0.8471910112359551); (iii) L7 carries the maintainer's 2025-10 statement
that ± is "the standard error across five runs", which conflicts with L2's derived fixed-tasks Bernoulli
formula — both are preserved, L2's receipt is stronger for the 2.0 page as of today. A fourth, smaller
disagreement: L8 says `response_model` has "no native source" at Harbor `a27e9c2`, whereas L1 shows
LiteLLM-driven agents write the provider-returned model id into ATIF steps (I confirmed the code
lines) — L1 is right for the trajectory, L8 is right for `result.json`/`lock.json`. Relative to the brief,
everything requested was attempted except **terminal-wrench** (zero mentions in any lane despite the
clone being offered), a real **Fortify run walk-back** (only the schema was inspected), an actual
**TB 2.1 row reproduction** (blocked by hub visibility, issue #177 — genuinely unavailable), and the
**8-outcomes / counterexamples** sections, which are argued rather than measured and are not
cross-mapped to the real cases the other lanes found. On the central question the lanes converge more
than they disagree: trial-level evidence is largely native; the missing record is a small
campaign/publication one (denominator, exclusion reasons, aggregation + uncertainty rule, instrument
pins, supersession); the residual dispute is only about *who owns it* and *what to call it*.

---

## 2. Findings with labels and receipts

### 2.A Disagreements between lanes (preserved, with the stronger receipt named)

**D1. TB 2.0 "±" column — L1 says UNAVAILABLE; L2 says DERIVED exactly.**
- L1 §2.11/§4: "None matches 2.7 exactly … ± is UNAVAILABLE from artifacts + public docs"; L1 lists the
  candidates it tried, including "TB2.1 per-task formula 1.36".
- L2 §2.1/§2.10: the ± cell renders as `(100*n*1.96).toFixed(1)` (site JS chunk
  `/_next/static/chunks/13e3e9ec63166a02.js`), and `stderr = (1/T)·sqrt(Σ p_i(1−p_i)/(n_i−1))`, exact to
  1e-17 on NexAU-AHE, GLM-5 and both Gemini CLI rows.
- CONFIRMED (this lane): fetched the page and the chunk on 2026-08-16; the chunk contains
  `children:["± ",null!=n?(100*n*1.96).toFixed(1):"N/A"]`. The Terminus 2 + Claude Opus 4.6 row in the RSC
  payload has `accuracy 0.6292134831460674` (= 280/445) and `stderr 0.013576456150106261`;
  100×stderr = 1.36 (L1's own "TB2.1 per-task formula" value) and ×1.96 = 2.66 → "2.7".
- Verdict: L2's receipt is stronger; L1's UNAVAILABLE is contradicted by an OBSERVED artifact. L1's
  sentence "the ± is most consistent with an sd over five runs under a run partition that the artifacts
  do not encode" should be withdrawn.

**D2. TB 2.0 aggregation rule — L1: pooled successes/total with errored=0 (imported from TB 2.1's
SUBMIT.md/metrics.py); L2: mean of per-task success rates with some errored trials dropped.**
- L1 §3: "tbench.ai TB2.0 accuracy: YES for the row I tested (280/445 = 62.9%) — but only after learning
  from the TB2.1 repo that errored trials count 0".
- L2 §2.6/§2.9: 2.0 importer drops trials whose verifier phase never started (observed:
  CommandExitException, TimeoutException, AddTestsDirError), keeps timeout trials as 0, and reports
  (1/89)Σ per-task rate; exact on 3 rows and consistent with all 142 detail pages; the NexAU row counts
  443 not 445.
- CONFIRMED (this lane): re-ran L2's rule over the 445 NexAU `result.json` files L2 left in `l2work/`
  → per-task-mean 0.8471910112359547 (site 0.8471910112359551), pooled 0.8449438 (= Harbor mean).
- Reconciliation: L1's row happened to have no dropped trials and equal per-task n, so pooled =
  per-task-mean there. L1's generalisation is contradicted for other rows. Also note the CONFLICTING
  comment inside TB 2.1's `metrics.py` ("matching the Harbor importer" = pooled) that L2 preserved
  (I confirmed the docstring lines 29–37 in `l2work/tb21src/metrics.py`).

**D3. What "±" means — L7 (maintainer assertion) vs L2 (derived formula).**
- L7 B5: `harbor-framework/terminal-bench-1#1256`, maintainer 2025-10-07: "we report the standard error
  across five runs" (CONFIRMED verbatim via `gh api …/issues/1256/comments`).
- L2 §2.10: fixed-tasks within-task Bernoulli SE (above); L1 §2.11 tested "sd of 5 run-means … 3.37"
  and it did not match.
- Verdict: CONFLICTING and both preserved. The maintainer's phrase (TB 1.0-era issue) is loosely
  compatible with a per-task variance estimated from 5 trials but does not literally match; L2's exact
  float reproduction on four rows is the stronger receipt for the 2.0 page as rendered today.

**D4. Provider-returned model identity at Harbor `a27e9c2` — L8: no native source; L1: in ATIF steps.**
- L8 F14: `response_model … have no source in TrialResult, TrialConfig, TrialLock, or JobLock` and §3A
  "`response_model` UNAVAILABLE at this commit"; F14 concludes a 14/20 ceiling for a Harbor bundle.
- L1 §2.7: `llms/lite_llm.py` sets `LLMResponse.model_name` from `response.model`; Terminus-2 writes it
  into ATIF `Step.model_name` (`terminus_2.py` L1366-1373, L1501-1508, L1832), landed `a5c775f9c`
  2026-03-17 (#1178).
- CONFIRMED (this lane): `git show a27e9c2:src/harbor/agents/terminus_2/terminus_2.py` lines 249, 1367,
  1502, 1832 (`model_name=self._last_response_model_name or self._model_name`); commit `a5c775f9c`
  dated 2026-03-17 "fix(llms): populate LLMResponse.model_name from provider response (#1178)".
- Verdict: both right within their scope — L8 about `result.json`/`config.json`/`lock.json`, L1 about
  `agent/trajectory.json` (which the eval-evidence adapter already requires and reads). Caveat L1 also
  gives: the `or self._model_name` fallback means a step's `model_name` may be the configured string,
  and pre-#1178 rows carry only the configured string. L8's "structurally unavailable" overstates.

**D5. Value of per-trial byte sealing — L5 (real archive) vs L3/L6 (public ecosystems).**
- L3 §5: "Per-trial sealing adds little … S3 ETag and git blob ids already give byte identity";
  L6 §6(d)7: "the trial-level byte-sealing bundle is the most redundant component"; L4 §5 (H3) "weakly
  supported and only in a specific place".
- L5 §5(1): content-addressed inputs "make duplicate ingests and cheat-mirrors an equality check
  rather than a heuristic key" — receipts: [in-house value redacted] mirrored as
  honest, and harness-dropped rewards found only by re-reading verifier files.
- Verdict: not a factual contradiction; a scope difference. L3/L6/L4 examined archives that are already
  content-addressed (git/S3/HF); L5 examined a directory-name-labelled archive that is not. L7 §6(2)
  states the reconciliation explicitly ("marginal value … in archives that are not otherwise
  content-addressed"). Preserve as a conditional, not a verdict.

**D6. Naming/ownership of the campaign record — L2/L6 vs L8 (semantic more than factual).**
- L2 §5(5): the TB 2.1 submission JSON "is the strongest evidence … that the abstraction is both
  necessary and cheap"; L6 §6(d)5: the "claim-specific 'required evidence → state → unresolved
  differences → decision' record … is the only part worth building".
- L8 §1/§5: "'Claim lineage' is not a missing *abstraction*; it is a missing *record*"; drop the term;
  EE should own only the status vocabulary, the content-reference primitive, and possibly a
  comparison-qualification check; Harbor emits the campaign record, the publisher attests it.
- Verdict: no receipt conflict; L2/L6/L8/L1/L3/L5/L7 all place the record at the campaign/publication
  layer. The open question is ownership (L8: not EE; L6/L2: unassigned) and vocabulary. Preserve.

**D7. Minor characterisation conflicts (lower stakes).**
- L2 §2.4 calls the oracle jobs' `lock.json` "a modern lock.json" and lists `invocation[]`; L1 §2.6 and L8
  F6 show those locks are `schema_version 1` (Harbor 0.16.1) and that `invocation` was removed by
  `b08e76513` (2026-06-29). CONFIRMED (this lane): 17/17 oracle job locks have `schema_version 1` and an
  `invocation` key; commit `b08e76513` dated 2026-06-29 "Write trial locks and remove invocation from
  job locks (#2138)". L1/L8 are right; L2's adjective is wrong.
- L1 §3 says TB 2.1 accuracy/SE/pass@k are reconstructable "while the hub serves the referenced trials",
  and L1 §2.11 documents that hub visibility lapsed on 2026-07-22 (`terminal-bench-2-1#177`, open, 0
  comments — CONFIRMED). So the conditional is currently false; L1's "YES" should read "YES in principle,
  UNAVAILABLE today". L2 §5(6) has the same slip ("I reproduced 83.82/1.16 from its own definitions in
  principle") — the numbers were OBSERVED in PR #75 bot comments, not reproduced.
- L6 §2.9 leaves the HF Open LLM Leaderboard results→row join UNAVAILABLE ("did not fetch the backend
  code"); L4 C4/C14 DERIVES the rule ("earliest sha, latest scores") by matching on five models and
  states the aggregator is not public. Not a conflict; L4 supersedes L6's UNAVAILABLE.
- L7 B6 has HF v2 normalisation ASSERTED (InfoQ); L4 C6 has it OBSERVED/DERIVED to the last digit. L4
  supersedes.
- L7 C2 (rank-1 row "~90.2% ± 2.1" vanished; reporter recomputed 89.9% mean) and L2 §2.2
  (`vix__claude-opus-4-7` merge-commit title "89.9% mean / 97.75% pass@5", not displayed): consistent,
  and L2's per-task-mean-with-drops rule would explain 89.9 → 90.2. Neither lane links the two; worth
  a note for the parent, not a conflict.

### 2.B Receipt spot-checks (what I re-checked, what I found)

| # | Lane / claim | How checked | Result |
|---|---|---|---|
| 1 | L7 A1 / L8 F3 / L1 2.3: `shutil.rmtree` before retry at `src/harbor/trial/queue.py:222`, introduced `080a1cb30` 2026-05-17 | `git show a27e9c2:…queue.py`; `git log -S` | CONFIRMED (line 222; single commit `080a1cb30 2026-05-17 Simplify trial flow (#1672)`) |
| 2 | L8 F4 / L1 2.2: `aggregate_reward_dicts` None→0 (`metrics/base.py:14-35`, `:25`, `:32`); `mean.py` divides by `len(values)` | `git show` | CONFIRMED verbatim |
| 3 | L1 2.6: `HarborLockInfo` at `models/job/lock.py L357-360, L855-949` | `git show … | grep -n` | **WRONG LINE NUMBERS** — file is 649 lines; `class HarborLockInfo` is at 58-61, populated at 556-609 (L8's refs are correct). Content of the claim is right |
| 4 | L1/L8 `job.py` refs (252-260, 690-701, 703-711, 921/928/964/993/1093, 940-944, 978, 1046-1085) and `result.py` (`increment` L129, `format_agent_evals_key` L60, `n_retries` L34) | `git show … | grep -n` | CONFIRMED |
| 5 | Commit dates: `7f6ae226b` 2026-04-29 job lock; `417a9815d` 2026-04-30 remove trial name from lock; `b08e76513` 2026-06-29 trial locks; `25165b932` 2026-06-30 upload requires trial lock; `d8c09832c` 2026-07-21 task version; `b3d5f5af6` 2026-07-21 regrade; `a5c775f9c` 2026-03-17 response model | `git log -1` | CONFIRMED all seven |
| 6 | L8 F1/F14: `adapters.py:378` required tuple; only one campaign/lock hit (`:538`); 20 `STANDARD_INSTRUMENT_FIELDS` | grep + python over eval-evidence `6d4a25b` | CONFIRMED (20 names; single hit at 538) |
| 7 | L8 F2/F6 & L1 2.6/2.10: 17 oracle jobs — 0/17 `agent/trajectory.json`, 0/17 trial `lock.json`, 17/17 job-lock `harbor.version`, 0 `git_commit_hash`, `schema_version 1`, `invocation` present, no `trial_results` key; the one errored trial has `verifier/reward.json` keys `{metric, reward, score, version}` + 7-byte `reward.txt`, `ValidationError`, evals `n_trials 0 / n_errors 1 / mean 0.0` | python over the job dirs (keys/counts only) | CONFIRMED on every point |
| 8 | L5 F3: `trials.parquet` sha256 `[in-house value redacted]` on main and at `[in-house value redacted]`; `[in-house value redacted]` on `origin/companion-site`; `[in-house value redacted]` not an ancestor of main; merge-base `[in-house value redacted]`; 28 commits `companion-site..main`; **97 commits `main..companion-site`** | `shasum`, `git merge-base`, `git rev-list --count` | Digests, ancestry, merge-base, and 28 CONFIRMED; **97 NOT REPRODUCED** — I get 120 (110 `--no-merges`, 106 `--first-parent`) against `[in-house value redacted]` |
| 9 | L4 C2/C3: `results_2025-02-13T18-27-04.338360.json` for Qwen2.5-72B-Instruct at `results@aa81ecc3…`: `git_hash 9694c56`, `model_sha d3d95115…`, `results.leaderboard_math_hard.exact_match,none 0.5981873111782477`, `groups… 0.012084592145015106`, `results.leaderboard… 0.0120845…`, stderr `0.00297719…`, `versions… 3.0` vs `configs.metadata.version 1.0` | re-fetched from HF | CONFIRMED to the last digit |
| 10 | L4 C1/C4: `contents@9c09a7ca…` row `Qwen/Qwen2.5-72B-Instruct`: 4,576×36; `Average 47.98046`, `Model sha a13fff9a…`, `Submission Date 2024-10-16`, MATH raw 0.598187, MMLU-PRO raw 0.562583, GPQA raw 0.375 | re-fetched parquet | CONFIRMED (sha from run 1, scores from run 2 rewrite) |
| 11 | L2 2.1: 142 rows; NexAU row object (`accuracy 0.8471910112359551`, `stderr 0.010659362899443975`, `agentVersion "unknown"`, `verified false`); Codex CLI GPT-5.5 `0.8224719…`/`0.01134775…` verified; 73 verified; 8 `stderr:null`; JS `(100*n*1.96)` and hover text | re-fetched page (563,171 bytes, same size) + chunk | CONFIRMED all |
| 12 | L1 2.2: HF TB2 `Terminus2__Claude-Opus-4.6` jobs `2026-02-05__17-41-47` (`n_total 356`, `n_trials 352`, `n_errors 66`, `mean 0.6151685393258427`) and `2026-02-05__16-08-28` (`89/89/15`, `mean 0.6853932584269663`); no `trial_results` key | re-fetched at HF sha `572b2614…` | CONFIRMED |
| 13 | L3 F2.4: S3 anonymous listing; ETags for `astropy__astropy-12907/{eval.sh,patch.diff,report.json,test_output.txt}` = `938755b8…`, `7e564045…`, `b179cca0…`, `58ed1f25…`; 1,981 log objects | curl S3 ListBucket (paginated) | CONFIRMED |
| 14 | L3 F1/F3/F4/F7/F8: site repo `data/leaderboards.json` @ `f42505b2` (7,270,245 bytes): 180 Verified rows; target row JSON; 6 rows with a string `checked`; 60 `checked: true`; 47 mini cross-listings; `20251127_openhands_claude-opus-4-5` absent; Kodu `warning: null` at 44.67; Test `20240402_sweagent_claude3opus` 10.51; gemini-3-pro-high 69.6; mini c3.7 52.8 | re-fetched raw JSON | CONFIRMED all |
| 15 | L3 F7 / L4 D2: `experiments@1faa91ca` `results.json` counts — openhands opus-4.5 `resolved 388`; sweagent_gpt4 `286` (+`no_generation 154`, `test_timeout 2`); rag_claude3opus `87`; livesweagent `396` (`no_generation 4`, `no_logs 1`); openhands `metadata.yaml` top-level keys `assets name org_logo oss site verified tags` (no `info:`) | raw GitHub | CONFIRMED |
| 16 | GitHub issues/PRs cited by L1/L3/L7: `SWE-bench/experiments#463` (241/213/28, 10.51/9.29), `terminal-bench-2-1#177` (open, 0 comments), `terminal-bench-1#1256` maintainer quote, `#1460` (title/manifest/90.2%/89.9%), `#1430`, `#1445`, `#1459`, `harbor#2225`, PR `#2226`, `#2231`, PR `#2358` merged 2026-07-21, `terminal-bench#1405` closed unmerged 2026-07-21, `#1390`, `#1507`, `#1541`, `harbor#2712` closed, `experiments#217`, `SWE-bench#465` | `gh api` | CONFIRMED (states, dates, titles) |
| 17 | L6 §2.9: Inspect `_log.py@7b17bdfe` `invalidation: ProvenanceData` (L508), `error_retries` (L514), `unscored_samples` (L743), `completed_samples` (L784), `class EvalRevision` (L909), `invalidated: bool` (L1153); `ProvenanceData`/`LogUpdate`/`invalidate_samples` in `_edit.py`; EEE `eval.schema.json@9bce4136` required list, `evaluator_relationship` enum, `"unknown"` convention | raw GitHub | CONFIRMED |
| 18 | L6 §2.1: PROV-DM REC-2013-04-30 quotes | fetched W3C page | Bundle and "does not attempt to specify the conditions" CONFIRMED verbatim; the invalidation quote is a **light paraphrase** (actual text: "no longer available for use (or further invalidation) after invalidation") — substance correct |
| 19 | L7 B3: ARC "37 out of 100 tasks, 82% accuracy … excluded from the leaderboard due to insufficient coverage … upper bound"; L6 §2.10 MLPerf "Results that cannot be replicated are not valid results" (`inference_rules.adoc` L99 @ `8cc76346`) | fetched | CONFIRMED |
| 20 | L4 D1: arXiv 2405.15793 v1/v2/v3 dates (2024-05-06/05-30/11-11) and v3 HTML contains "12.47" and "previous best resolve rate of … 3.8" | fetched abs + HTML v3 | CONFIRMED (numbers are inside MathML; present 3× and 1×) |
| 21 | L2 §2.3: NexAU 445 trials: rewards 376/65/4-null; exceptions `AgentTimeoutError 6, VerifierTimeoutError 2, TimeoutException 1, CommandExitException 1`; "AgentTimeoutError 6 (four of which still have a reward)" | recount over `l2work/nexau_trials` | Counts CONFIRMED except the parenthetical: **all 6** AgentTimeoutError trials have a reward (nulls are exactly the 2 VerifierTimeout + 1 TimeoutException + 1 CommandExit). Slip does not affect the rule or the 0.84719… reproduction |

Also re-read at `a27e9c2` for L1: `docs/content/docs/hub/index.mdx` L162 ("changes do not recompute row
metadata or metrics") and L66 (leaderboard-linked jobs cannot be deleted); `regrade.mdx` L10/L77;
`uploader.py` L752/L784 "Trial lock file is required for upload"; `_TRIAL_ARCHIVE_INCLUDES` at
`uploader.py:82` (includes `analysis.md`); `Task.checksum` deprecation docstring (`task.py:198-203`);
`BaseAgent.to_agent_info` builds `ModelInfo(name=self._parsed_model_name…)`; `TrialConfig.__eq__`
excludes `{trial_name, job_id}` (`trial/config.py:470-475`); `AgentConfig.skills/mcp_servers` have no
`exclude_if` (`:81`, `:148`) — all CONFIRMED (L1 2.7, 2.8, 2.9; L8 F7, F8, F11).

Net: 21 receipt groups checked; 18 exact; 3 defects, all minor (L1 lock.py line numbers; L5 "97
commits"; L2 "four of which"). One paraphrased quotation (L6). No OBSERVED/DERIVED claim I checked
was unsupported in substance.

### 2.C Coverage against the brief — what is missing, and whether it is unavailable or just not done

| Brief item | Status | Where covered | Gap and its nature |
|---|---|---|---|
| Native systems coverage (Harbor, TB, Fortify, leaderboard pipeline) | Mostly done | L1 (Harbor models/job/lock/upload/hub, TB1→2.0→2.1→TB3 pipeline, harden-v0 schema, TB3 fortify shim), L8 (Harbor at code level), L7 (Harbor issues) | **terminal-wrench: 0 mentions in any lane** although the clone was offered — *not done*. **Fortify:** only `harden/loop.py` `result.json` shape and `tools/fortify/fortify.py` were read; no genuine `/fortify` output (GitHub Actions artifact or PR comment) was walked — *not done, probably feasible via `gh run` artifacts if retention has not expired*. **Harbor Hub server-side "latest attempt" semantics** — *genuinely UNAVAILABLE* (Supabase RPC, L1). **Installed-agent ATIF converters and response-model ids** — *not done* (L1: out of budget). **TB3/Frontier-Bench leaderboard record** — *genuinely UNAVAILABLE* (L1: hub URL 404, PR #1405 closed unmerged, #1507). **eval-evidence sanitized fixture** — only L1's one-line note that its job `result.json` has a `trial_results` key current Harbor never writes; nobody re-ran `eval-evidence check`/`verify` on it — *not done, trivial* |
| ≥1 Terminal-Bench/Harbor claim walk-back | Done | L2 (TB 2.0 NexAU-AHE row, plus vendor numbers), L1 (Opus 4.6 row accuracy) | TB 2.1 row not reproduced from its own record — *genuinely UNAVAILABLE today* (hub trial visibility, #177) but should be labelled so (see D7) |
| Prior art with the 8 questions per candidate | Done | L6 table §3 (~25 candidates, Q1–Q8 each) | Rows marked NOT FETCHED (Kaggle/Codabench, Sacred, Neptune, Pachyderm, LakeFS, Sciunit, Snakemake report, noWorkflow/YesWorkflow, DISK internals, HAL upload keys, ProvONE authoritative text 503) — *not done, feasible*. Two "in-domain" precedents that other lanes rely on are not in L6's table at all: TB 2.1's `submissions/*.json` (L1/L2) and SWE-bench `experiments/` (L3) — *synthesis gap, not unavailability* |
| Failure taxonomy from evidence, hypothetical modes labelled | Done | L7 (~35 cases, 14 classes, T/C/X detection columns; A1/A2 harm explicitly HYPOTHETICAL) | Several rows rest on secondary sources (Gemini technical report Table 2, Reflection-70B, OpenAI Verified pages 403, Epoch o3 X post) — *not done for the Gemini PDF (public, parseable); genuinely blocked for the 403/429 pages via WebFetch*. No named paper pinned as copying a baseline under mismatched config — L7 states this as a negative result. L7's own §5 counts ("T ~4, C ~22, X ~14") are DERIVED by the lane's judgment, not from a stated rubric |
| Claim classes with mechanical-vs-inference boundary | Done | L8 §3A (C1–C6 → R/D/I) | Boundary drawn against Harbor only; not cross-checked against Inspect/lm-eval (E6 not run) — *not done, feasible with L6's Inspect receipts* |
| Missing-edge analysis (replay vs audit per transition) | Done | L8 §3B | Fields mapped to PROV; consistent with L6 §2.1 |
| The 8 possible outcomes tested | Partially done | L8 §3D (ranked with for/against/flip) | L8 says explicitly the ranking "is my judgment … not a measurement". No lane tests the outcomes against the *empirical* lanes (L2–L5, L7); e.g., outcome (7) "retrospective mostly impossible" is directly informed by L3 (per-instance re-derivation succeeded; instrument pins failed) and L4 (harness commit unresolvable, gated samples) but L8 does not cite them — *synthesis gap for the parent* |
| Counterexamples | Done (constructed) | L8 §3C (C-i…C-vi) | Only C-ii has a real anchor (ASSERTED via `docs/VISION.md`). Real analogues exist in other lanes and are not mapped: C-i ↔ L2 (Harbor mean 84.49 vs page 84.72; NexAU dropped trials) and L4 C3 (mixed-provenance HF file); C-iv ↔ L4 D8 (SWE-Bench+ re-read of an identical resolved set) and L3 F2.6 (dataset revision moves 79.2→79.4); C-v ↔ L7 A1 (no public incident). *Not done — synthesis* |
| Placement recommendation | Done | L8 §3F, L1 §5, L6 §6(d), L5 §5, L3 §5, L7 §6 | Convergent (see D6); ownership of the campaign record left open |
| Epistemic rules (labels, receipts, negatives) | Done | All lanes label; L2/L3/L4 carry explicit negative results with receipts | L2 §5(6) and L1 §3 conditional "YES" phrasing (D7) |
| Do not create files outside the assigned path | Deviated in a benign way | L1 (`harden-v0/`, and `tb21/` in scratchpad root), L2 (`l2work/`, 57 MB), L3 (`l3work/`, 491 MB incl. a venv with `swebench`), L4 (`L4work/`, 24 MB); this lane (`C1work/`) | Work directories under `lanes/` (or scratchpad root for `tb21`) rather than only the report file; all contents are public artifacts or scripts. No repo modified |

### 2.D Private-data leak scan

Method: grep of all eight reports for absolute paths (`/Users`, `/Volumes`, `/private/tmp`, `/root`,
`/workspace`), for trajectory/prompt/task-text patterns, and a read-through for quoted model output.

- **No trajectory, prompt, task instruction text, or model output** appears in any report. L3 F2.7 and L4
  D4 describe the *structure* of public eval logs (public S3 objects) and say so.
- Absolute paths found: `L1:9` and `L1:15` (harbor clone, oracle_runs glob) and `L6:4`/`L8:7`
  (eval-evidence path) — all listed in the brief as allowed; `L2:4` (its own scratchpad work dir);
  `L2:38/49` `/root/agentic-harness-engineering/…/code_agent.yaml` and `L2:60`
  `<submitter-local>/terminal-bench-2/<task>` — **third-party paths copied from public HF submission
  configs** (public artifacts, not private benchmark data; flag only if the parent wants third-party
  machine paths scrubbed from a shareable version).
- Borderline, not a leak: L1 §2.10 quotes that a genuine local trial's exception "message mentions
  `VerifierResult`/`rewards`" (harness error text, not model output; keys and byte size only otherwise).
  L1/L8 report the oracle jobs' Harbor version string (`0.16.1`) — a version, not data.
- PII-adjacent inferences: L3 F8 speculates that commit authors "carlos"/"carlose" are "plausibly
  maintainer Carlos Jimenez" (public GitHub authorship); L2/L3 name public HF/GitHub committers
  (`alexgshaw`, `rebekahw`, `kiki842940`); L5 uses collaborator first names present in the repo's own
  docs. None is benchmark data; note for tone if published.
- The `l2work/nexau_trials/` (445 public TB2 `result.json`) and `l3work/` (public logs/trajs from a
  public S3 bucket) directories contain public third-party trajectories on disk; nothing was copied
  into the reports.

Nothing requires scrubbing under the brief's rule; the two `/root/...`/`/workspace/...` lines in L2 are
the only candidates if a stricter rule is applied.

---

## 3. Explicit answers to the lane questions

**(a) Where do lanes disagree, and who has the stronger receipt?** D1 (TB 2.0 ± — L2 stronger, L1
contradicted by an OBSERVED artifact), D2 (TB 2.0 aggregation — L2 stronger; L1's rule holds only on the
no-drop row it tested), D3 (± semantics — CONFLICTING maintainer assertion vs derived formula; keep
both; L2 stronger for the rendered page), D4 (`response_model` — L1 stronger for ATIF, L8 right for
`result.json`/locks), D5 (per-trial sealing value — scope difference, reconcile as conditional on
whether the archive is content-addressed), D6 (naming/ownership — semantic), D7 (four minor
characterisations: "modern lock", "YES while hub serves", "reproduced in principle", HF join rule).

**(b) OBSERVED/DERIVED claims not supported by their receipt.** Only three defects in 21 groups, all
minor: L1 §2.6 line numbers for `HarborLockInfo` (58-61, not 357-360); L5 F1 "97 commits
an in-house branch" (a different count today; the digests, merge-base and the reverse count reproduce); L2 §2.3 "four of which
still have a reward" (all six do). One light paraphrase in quotation marks (L6, PROV invalidation). No
claim was wrong in substance.

**(c) Missing relative to the brief.** Genuinely unavailable: Harbor Hub RPC semantics; TB3 leaderboard
record; TB 2.1 row trial visibility (#177); OpenAI pages via WebFetch. Not done but feasible:
terminal-wrench (nobody looked); a real Fortify run walk-back; installed-agent ATIF response-model
check; the NOT-FETCHED prior-art rows; Gemini report footnotes; running `eval-evidence` on the
sanitized fixture; and — most decision-relevant — a cross-lane synthesis that maps L8's six
counterexamples and eight outcomes onto the real cases in L2–L5/L7, and adds TB 2.1's submission JSON
and SWE-bench `experiments/` to L6's prior-art table.

**(d) Leaks.** None under the brief's rule. Two third-party absolute paths in L2 (lines 38, 49, 60) come
from public HF configs and are the only scrub candidates under a stricter rule.

---

## 4. What I could NOT establish, and where I looked

- L5's branch commit count — I tried `rev-list --count` plain, `--no-merges`,
  and `--first-parent` against the in-house branch tip (same SHA by either name); none
  gives 97. UNAVAILABLE what L5 counted.
- Whether L1's wrong `lock.py` line numbers came from a different file — I checked only
  `src/harbor/models/job/lock.py` at `a27e9c2` (649 lines) and `origin/main`; not resolved (irrelevant to
  substance).
- The one L2 arithmetic slip's origin (six vs "four of which") — recount from L2's own files is
  unambiguous; the sentence should read "all six still have a reward (4 pass? / 2 fail? — not
  re-derived here)". I did not re-derive the pass/fail split among them.
- I did not re-run L2's `stderr` formula on rows other than reading L2's numbers, but I confirmed the
  ×1.96 rendering and the exact `stderr` values for the two rows relevant to D1.
- I did not re-fetch vendor pages (OpenAI 82.7 / Anthropic 69.4-65.4) or the HF PR #176 403; L2's
  receipts there stand unverified by me (they are OBSERVED-by-L2 via browser/PNG).
- I did not open `l3work/rederive.py` results or the HF parquet digests in L3 Appendix B; L3's 79.2→79.4
  drift claim is unverified by me (its per-file sha256 list is a strong receipt for a future check).
- terminal-wrench: I confirmed only that no lane mentions it; I did not examine the clone myself (out
  of the critic role).

---

## 5. Implications for the central question

1. **The lanes' evidence base is sound enough to build on.** Eighteen of twenty-one spot-checked receipt
   groups reproduce exactly across code (Harbor at `a27e9c2`, eval-evidence at `6d4a25b`), data (HF
   parquet/JSON, S3, GitHub raw), and pages (tbench.ai, swebench.com, arXiv, ARC, W3C). The parent can
   cite L2, L3, L4, L8's numeric receipts without re-deriving them; the three defects are cosmetic.

2. **The one place a lane got the answer wrong is itself the central lesson.** L1 concluded the TB 2.0 "±"
   was unrecoverable after computing the correct SE, because the display transform (×1.96) was
   undocumented and lived in minified JS. L2 recovered it only by reading the JS. That is the "aggregate
   → table cell" edge in L8's missing-edge table (transform + version not recorded), reproduced by two
   independent investigators on the same row. It argues for recording the display/uncertainty rule with
   the number, and against any lane's confidence that "the artifacts do not encode it" without checking
   the renderer.

3. **The lanes converge on the abstraction question, and the convergence survives the disagreements.**
   L1, L3, L4, L6, L7, L8 all say the per-trial layer is largely native (Harbor locks/results, lm-eval
   JSON, SWE-bench logs) and that the missing record is campaign/publication-level and small: expected
   vs included attempts with reasons, denominator, named aggregation + missing-data + uncertainty rule,
   instrument pins, supersession. L2 and L5 supply the two real-data receipts that the campaign layer is
   where the numbers actually moved (443 vs 445; [in-house value redacted] ). L5
   is also the only lane with a receipt that per-trial content addressing would have caught something
   (duplicate ingests, cheat mirrors) — which reconciles with the others once "is the archive already
   content-addressed?" is made explicit (D5). No lane argues for a new per-trial abstraction, and none
   argues that a claim-level record is unnecessary; the residual is naming (L8: drop "claim lineage") and
   ownership (L8: not eval-evidence; L2/L6: unassigned).

4. **What the parent still lacks is synthesis, not evidence.** The counterexamples and the eight outcomes
   are argued (L8) rather than tested against the cases the empirical lanes found; the prior-art table
   omits the two in-domain precedents (TB 2.1 submission JSON, SWE-bench experiments layout) that L1–L3
   describe in detail; and terminal-wrench and a genuine Fortify output were never examined. Those are
   cheap to close and would change no lane's verdict, but they are the difference between "eight
   consistent reports" and "one reconstructable answer".

5. **On the framing:** willing to say plainly, with the lanes, that the proposed *per-trial* abstraction is
   unnecessary as new information (custody at most), that a small *campaign/publication* record is
   necessary and is already half-implemented by the maintainers themselves (TB 2.1, Inspect), and that
   the epistemic rule the brief imposed — recorded evidence is not truth — was empirically vindicated
   in every walk-back (L4's exact 47.98… reproduction, L3's byte-stable logs, L2's exact 84.72… all
   certify arithmetic, not correctness; L7 E-series and D8 show reproducible numbers with unsupported
   meanings).

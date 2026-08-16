# Claim reconstruction study: what evidence is required to reconstruct an evaluation claim?

Status: research finding, 2026-08-16. This is a study result with receipts, not a
schema, a product decision, or a paper claim. It answers the question the research
plan left open above the trial layer and decides what — if anything — Eval Evidence
should own there.

Baseline reviewed: eval-evidence `main` at `6d4a25b5f288f9646f30e0d1c9f5923cc6c1ec8c`.
Companion receipts (lane reports, one per investigation lane, and two critic audits)
are in [`claim-reconstruction/`](claim-reconstruction/README.md); every number below is
traced there to a URL, commit, file, or issue. The in-house paper-lineage lane (L5)
examined a private research repository and is summarised here in aggregate only; its
full report stays outside this public repository.

## 0. Verdict

The question was whether "claim lineage" — why a particular collection of trials,
retries, revisions, exclusions, transformations, and aggregation decisions became a
particular reported number — is a real missing abstraction above per-trial evidence.

It is not a missing abstraction. It is a missing **record**, and the record is small,
PROV-shaped, and mostly owned by other layers. Five real reported numbers from five
ecosystems (a Terminal-Bench 2.0 row, a SWE-bench Verified row, a Hugging Face Open LLM
Leaderboard row, a paper table cell, and an in-house paper number) were all reproduced to
full precision from retained per-instance artifacts — and **none of the five reproduced
from a written rule.** In every case the aggregation rule, exclusion predicate, or
uncertainty formula was recovered by numerical matching against candidate policies, and
in every case at least one instrument identity (harness commit, image digest, dataset
revision, provider-returned model) was unavailable or had moved. Per-trial verification
was the easy part everywhere. The failures lived at the row: which attempts counted, how
they were aggregated, what the interval means, whether the row is still the row.

Consequences for this repository: the per-trial envelope duplicates native state that
Harbor already writes (and in one measured case discovers 0 of 17 genuine trials while
declaring "unavailable" a harness version present in 17 of 17 job locks); the layers
called "campaign lineage" and "claim lineage" collapse into one campaign-provenance
record that Harbor should emit and publishers should extend; "claim support" is real but
is argumentation, not infrastructure. Eval Evidence should own less: the per-field
evidence-state vocabulary with source pointers, the content-reference primitive, and a
read-only reconstruction checker that recomputes a number under a declared rule and
checks an expected set against a discovered set. Nothing here justifies a new schema,
CLI, DAG engine, or wire change.

## 1. Method and epistemic rules

Eight independent research lanes ran in parallel with no shared state, followed by two
critics (a completeness/receipt audit that re-fetched 21 receipt groups — 18 reproduced
exactly, 3 minor defects, no private-data leaks — and an adversarial judge that
re-derived the load-bearing numbers). Lanes: L1 native systems (Harbor, Terminal-Bench,
Fortify/harden-v0, the leaderboard pipeline); L2 Terminal-Bench 2.0 row walk-back; L3
SWE-bench Verified row walk-back; L4 Open LLM Leaderboard row and a paper table cell; L5
in-house paper lineage; L6 prior art; L7 failure modes from documented cases; L8
adversarial formulation (claim classes, missing edges, counterexamples).

Every step is labelled OBSERVED (seen in a primary artifact), DERIVED (computed from
observed material), ASSERTED (author/provider/maintainer says so), CONFLICTING (two
sources disagree; both kept), or UNAVAILABLE (looked, could not establish; where we
looked is recorded). A digest establishes byte identity, not correctness. Reconstruction
never invented history. Negative results are kept.

Pinned revisions: Harbor `a27e9c2ae10a31c40b2dcef33ef5486bce36e185` (2026-08-14) and
`origin/main` `f03db62fd2ed2ed1f79aefe024cfcbc68a0d759e` (2026-08-16; the two differ by
one enum line in the paths inspected); Terminal-Bench 2.1 leaderboard tooling
`harbor-framework/terminal-bench-2-1@7131e4375048a0e408a8fb404b5f499d726b695b`; TB2.0
submissions dataset `harborframework/terminal-bench-2-leaderboard@572b2614be2c…` (HF,
lastModified 2026-05-15); SWE-bench `experiments@1faa91cade05…`; Inspect AI
`7b17bdfed616e6284c7550f585e4552636f75ee7`; harden-v0 `few-sh/harden-v0@342b8474e0…` (the
`laude-institute/harden-v0` path named in the lane brief returns 404; the pinned SHA
resolves in `few-sh/harden-v0` — CONFLICTING repository identity, resolved to `few-sh`); 17 genuine local Harbor oracle job directories (Harbor
0.16.1; structure and counts only).

One caveat on independence: every lane read this repository's research docs, which
already state the counter-hypothesis (DECISION_GATE §6). The *language* of "shrink" is
therefore partly primed. The empirical walk-backs (L2–L5, L7) are not, and they
independently locate the failures at the row layer and at instrument pins. We weight the
receipts, not the vocabulary.

## A. What we learned

**A1. Arithmetic reconstructs; rules do not.** Five of five reported numbers reproduced
exactly from per-instance records; zero of five from a written rule.

| Case (lane) | Displayed | Reproduced | How the rule was recovered | Instrument identity unavailable |
|---|---|---|---|---|
| TB2.0 rank-1 row NexAU-AHE / GPT-5.5 (L2) | 84.7% ± 2.1 | `0.8471910112359551`, SE `0.010659…`, exact | Matching candidate rules over three rows plus the successor (2.1) leaderboard's public code | Harbor version (job predates job `lock.json`, added 2026-04-29), agent code revision (`agentVersion "unknown"`, local YAML path), model snapshot/effort, image digests, exact drop predicate; HF PR #176 review closed (HTTP 403) |
| SWE-bench Verified rank-1 live-SWE-agent + Claude 4.5 Opus (L3) | 79.20 | 396/500 from 495 per-instance `report.json` (PR ref `refs/pull/388/head` and public S3, byte-identical); re-parsed from raw `test_output.txt` with `swebench` 4.1.0 = 396 | Disclosure for the parse; dataset revision by trying revisions until the number matched | Harness version, Docker image digest (`:latest` re-pushed 2026-08-16), the meaning of "verified submission" |
| HF Open LLM Leaderboard v2 row Qwen2.5-72B-Instruct (L4) | 47.98045991216864 | Exact, from `results_2025-02-13T18-27-04.338360.json` | File 4 of 4 for the row (displayed model sha is file 1's); key `results.<task>` not `groups`/stderr (stale after two in-place rescorings); found by trying both | lm-eval `git_hash 9694c56` resolves to no public commit; results→table aggregator not public; per-sample details gated |
| SWE-agent paper cell 12.47% vs 3.8% (L4) | 286/2294; 87/2294 | Exact from public `results.json` | Disclosure for the count; population unclean (12 duplicated ids, 28 absent, 154 empty patches in the denominator); baseline cited to a paper that says 1.96% (citation ≠ source) | Harness commit (pre-Docker conda harness), duplicate adjudication, README 12.29% → paper 12.47% unexplained, pre-2024-10-15 history reset |
| In-house paper numbers (L5, aggregate only) | as stated | Re-derived from the frozen trial table in ~20 lines | Middle of the chain fully scripted; both ends not | Denominator of the headline count stated nowhere; snapshot id hashes one file while the input set drifted; one confidence-interval method has no committed code |

**A2. The failures live at the row, not the trial.** Across ~35 documented public cases
(L7), per-trial byte identity alone would have detected about 4; campaign/publication
structure about 22; and about 14 needed policy, provider disclosure, or external audit.
The single most recurrent missing artifact is a per-row publication state: which
attempts were included, which excluded and why, the denominator, the aggregation and
uncertainty rule, instrument identity at row level, and supersession links.

**A3. Native systems already hold most trial-level and much campaign-level state — and
destroy some by design.** Harbor at `a27e9c2` writes per-trial `result.json` and
`config.json`, per-job and per-trial `lock.json` (task content digest, task version,
Harbor version and commit-when-known, resolved agent/environment/verifier config, retry
policy, regrade `source_trial`), and a job `result.json` whose `stats.evals[*].metrics`
is exactly recomputable from trial files. It also (a) `shutil.rmtree`s the directory of a
failed attempt before retrying it (`src/harbor/trial/queue.py:222`, introduced
`080a1cb30` 2026-05-17; only `stats.n_retries` survives), (b) deletes trial directories
without `result.json` on resume (`src/harbor/job.py:252-260`), (c) coerces
errored/cancelled trials to reward 0 inside the job-level `mean`
(`src/harbor/metrics/base.py`) with no policy field, and (d) never writes `trial_results`
into the job `result.json`, so aggregate→trial membership is a list of trial *names*
(`reward_stats`), not content identities. Default `max_retries=0` limits (a); no public
incident of (a) changing a published number was found — harm HYPOTHETICAL.

**A4. The publication layer is where the maintainers themselves are converging.** The
Terminal-Bench 2.1 leaderboard replaced "PR a folder of Harbor jobs" with a per-row JSON
(`source_jobs`, `source_filter{agent, agent_version, model_name, reasoning_effort}`,
`disqualified_trials[{trial_id, reason, judge_trial}]`, `trials[]`, `metrics`) plus
~250 lines of public metric code with an explicit rule ("Errored trials count as reward
0") and SE formula, leaderboard-owned trial clones, and a git history per row. That is,
field for field, the "minimal campaign record to test" in `UPSTREAM_MAP.md` — living in
the leaderboard layer. Its residual gaps are also instructive: a row was merged past six
"renders a submission invalid" judge flags with no recorded rationale (PR #75); a cost was
backfilled after merge and now differs between the row and the Hub; the "±" glyph means
1.96×SE on the 2.0 page and 1×SE on the 2.1 page of the same site; and hub trial
visibility lapsed on 2026-07-22 (`terminal-bench-2-1#177`, rows report `n_trials: 0`),
so the record's provenance depends on hosted-service availability.

**A5. Prior art supplies the vocabulary, not the solution.** PROV-DM (W3C REC 2013) has
every relation the record needs (`wasDerivedFrom`, `wasRevisionOf`, `wasInvalidatedBy`,
`Collection`/`hadMember`, `Plan`, `Bundle`) and states validity ≠ truth; Inspect AI's log
already carries per-sample `invalidation{author, reason, timestamp}`, `log_updates`,
`error_retries`, and total/completed/scored/unscored counts — the exclusion/denominator
half of the record, in-domain; MLPerf is the only mature governance system that enforces
"row ⇐ evaluations" (mandated logs + a re-deriving checker + peer objection), as
procedure, not format; in-toto/DSSE would bind and sign a transition chain if signing is
ever wanted; Every Eval Ever is a reported-score record with `source_type`,
`evaluator_relationship`, `uncertainty{se, ci, method, num_samples}`. **No surveyed system
has a per-field "unavailable" state or an unresolved "two retained sources disagree"
state.** Workflow Run RO-Crate is a poor fit as-is: skipped steps "SHOULD NOT be
included" and unspecified status implies success.

**A6. Interpretation is out of scope, and that is not a loophole.** Every contamination,
verifier-exploit, and reference-frame case (GSM1k, SWE-Bench+, HLE, the AI CUDA Engineer,
the bar-exam percentile) reconstructs perfectly and means something else. Lineage makes
such claims falsifiable; audits falsify them. A tool that markets lineage as trust is
mis-selling.

## B. The evidence stack that survived

Three layers, not four.

| Layer | What it answers | Where its state lives today | Boundary |
|---|---|---|---|
| **1. Trial evidence** | What happened in one run: task/verifier content identity, resolved configuration, agent/model as configured and as reported, budgets, timings, verifier outputs, byte identity of retained files | Harbor `result.json`, `config.json`, trial `lock.json` (v0.17.0+), ATIF trajectory, `verifier/`; SWE-bench per-instance logs/patches; lm-eval results JSON | Mostly native. Marginal value of a separate envelope = normalization, honest per-field state, safe references. Five of Eval Evidence's twenty instrument fields (`agent_binary_sha256`, `system_prompt_sha256`, `policy_profile_id`, `environment_image_digest`, a separate `verifier_digest`) have no source in any Harbor artifact at `a27e9c2`, and `response_model` appears only in ATIF steps written by LiteLLM-driven agents since 2026-03-17 (not in `result.json` or the locks) — prospective capture for the rest |
| **2. Campaign provenance** (formerly "campaign lineage" + "claim lineage") | Why these attempts became this number and this row: expected attempts, occurred states, retries/regrades/supersession, inclusion with reasons, denominator, named/versioned aggregation and null policy, uncertainty method, publication pointer, adjustments, actor, time | Harbor job `lock.json` (`trials[]` = expected multiset), job `result.json` (`n_total_trials`, `stats.*`, `reward_stats`), regrade `source_trial`; publisher record (TB2.1 `submissions/*.json` + `metrics.py`; SWE-bench `results.json` + `get_results.py`) | Real, small, PROV-shaped. Harbor should emit the job-close half; the publisher extends it. Nothing here is different in kind from Entity/Activity/Agent/Plan/attribute (L8 §B) |
| **3. Claim support** | Which evidence, controls, assumptions, and unresolved alternatives warrant a stated interpretation | Papers, registered reports, GRADE-style rubrics, nanopublications/Micropublications | Out of infrastructure scope except for citation edges from a claim to a layer-2 record |

Why 2 and 3 merged: every field proposed for "claim lineage" (retained trials → eligible
attempts → included cohort → transformations → aggregation → reported number → table
location → claim) maps to a PROV node, edge, role, or attribute; the transitions differ
in *who* records them (runner vs publisher), not in kind. Naming a fourth layer implied
a distinction the evidence does not support.

## C. Minimal evidence per claim class

Three classes replace the six-way starting taxonomy. Boundaries were tested against
Harbor's models at `a27e9c2` and the five walk-backs.

**R — record claims** ("this run produced X"; "this campaign produced aggregate X").
Minimal evidence: content identities of `result.json`, `config.json`, trial `lock.json`,
verifier output; `TaskLock.digest`; `HarborLockInfo.{version, git_commit_hash}`;
`AgentInfo`; resolved timeout components; and for the campaign, job `config.json` +
`lock.json` (`trials[]`, `retry`, `harbor`) + job `result.json` (`n_total_trials`,
`stats.*`) + the set of trial directories with digests + the Harbor code revision
(because the null policy lives in code) + an admission that per-attempt retry history is
gone if `n_retries > 0`. Mechanical derivation stops at: recompute `mean` from
`reward_stats` and check it equals `metrics[0].mean`; check `len(trial dirs with
result.json) == n_completed_trials`; check `n_total_trials == len(lock.trials)`; match
trial dirs to lock entries by config equality (the lock carries no trial name). Inference
begins at: "deleted retries would not have changed the aggregate", "errored trials are
correctly scored 0", "no trial dir was removed after job close". Three genuine holes:
retry tombstones, member-trial content digests in the job record, and an explicit
null-policy/denominator/version field on the metric.

**D — derived claims** ("A outperformed B"; "this row is supported by these
evaluations"; "changing X caused Y"). Minimal evidence: two R records; equality of
`TaskLock.digest` sets; equality of `TrialLock` fields other than the intended difference
(Harbor's own `JobConfig.__eq__`/`TrialConfig.__eq__`/`TaskLock.__eq__` are the equality
keys); equal per-task denominators; the comparison statistic with its uncertainty method;
and, for a row, a publisher pointer from the cell to the submitted tree (digest or
Merkle root), the validator version and result, the aggregation rule + null policy, and
an adjustment log (judge zeroing, regrade supersession). Mechanical derivation stops at
"the two locks differ only in field set S; denominators D_A, D_B; statistic f(·)=v; row
score == agg(submitted result files)". Inference begins at "S is immaterial" — a
materiality policy is the only genuinely new artifact, and it is a Plan on the comparison
activity, not a schema — and at "the submitter did not cherry-pick jobs", which no
lineage record can see. "This row is supported by these evaluations" is not a distinct
class: it is a campaign record plus a publisher agent and an attestation bundle. "X caused
Y" is a comparison with a controlled diff; the unavailable prospective-only fields
(prompt digest, agent binary, response model) matter most here.

**I — interpretive claims** (a scientific conclusion built from several experiments).
Infrastructure owns only the citation edges from each cited number to a D or R record.
Everything past that is argument. No tool in this repository should own it.

**Completeness is claim-relative.** The same missing edge (three deleted retry attempts)
is immaterial for an aggregate claim and fatal for a first-attempt-success or cost claim.
This is why a uniform `available_fraction` is the wrong instrument (its ceiling for a
Harbor bundle is about 0.70 — 14 or 15 of 20 fields — even with perfect mapping) and why claim-specific required
evidence should be expressed as *which edges must be present*, not as a schema per class.

## D. Where current systems already solve the problem

**Harbor** (`a27e9c2`; concept → where preserved → reachable state → gap; L1 §3 has the
full table):

| Concept | Where preserved | State | Gap |
|---|---|---|---|
| Task content identity | `result.json:task_checksum` (dirhash, deprecated) and `lock.json:task.digest` (Packager allowlist hash), `task.version` (v0.21.0+), `task_id.git_commit_id` | OBSERVED, CONFLICTING algorithms | Two unlabelled hashes over two file sets; verifier bytes not separable from the task |
| Harness identity | `lock.json:harbor.{version, git_commit_hash?, is_editable}` | OBSERVED for jobs ≥ 2026-04-29 (job lock) / ≥ 2026-06-29 (trial lock); UNAVAILABLE before | pip installs record no commit; the 17 oracle jobs (0.16.1) have version only |
| Configured vs provider-returned model | configured: `agent_info.model_info`, `config.agent.model_name`, ATIF `agent.model_name`; provider-returned: ATIF `steps[].model_name` for LiteLLM agents since `a5c775f9c` (2026-03-17) | OBSERVED (agent-dependent) | Not in `result.json` or the Hub `model` table; installed agents unverified |
| Expected vs completed | `n_total_trials`, `lock.json:trials[]`, `stats.{n_completed,n_errored,n_cancelled,n_running,n_pending,n_retries}` | OBSERVED/DERIVED | `n_completed` includes errored; lock entries not joinable by name; never-started trials are a count, not records |
| Retry lineage | `stats.n_retries`; Hub `attempts=all` only if uploads streamed | count only | prior attempt dir `rmtree`'d |
| Aggregation | `stats.evals[k].{metrics, reward_stats, exception_stats, n_trials, n_errors}`; rule in code (`aggregate_reward_dicts`, None→0) | DERIVED; rule ASSERT-by-code | no policy field; evals key omits agent version/effort |
| Regrade lineage | `config.json:source_jobs`, trial `lock.json:source_trial{trial_id, path, task}` (v0.21.0+) | OBSERVED | forward pointer only; no "superseded_by" on the source |
| Exclusion / publication state | none in Harbor; TB2.1 `submissions/*.json` + Hub row (`metadata, metrics, status, trial_ids`; "Trial changes do not recompute row metadata or metrics") | OBSERVED at the leaderboard | metrics on Hub are declared, not recomputed; trials referenced by hosted UUID |
| Source conflicts | model name ×4; task hash ×2; `reward.json` beats `reward.txt`; token totals in `result.json` vs ATIF | OBSERVED | Harbor resolves by precedence, not comparison. Note: `config.json` and `result.json:config` are one object serialized twice; the real structure is requested-vs-agent-reported |

A live instance of the reward-file conflict: one genuine oracle trial carries a
`verifier/reward.json` with provenance keys (`reward, score, metric, version`) that
failed Harbor's typed parse (`ValidationError` → reward None → 0 in `mean`) although a
numeric `reward.txt` existed — the tension in `harbor-framework/terminal-bench#1390`
(score provenance) observed in data.

**Terminal-Bench / Fortify.** Task version ↔ digest registry, verifier score-component
provenance (#1390), and hardening acceptance evidence belong there. harden-v0 retains a
per-task `result.json` (status, iterations, hack/replay rewards), journals, and patches;
its nested Harbor jobs carry whatever locks the Harbor version wrote (the TB3 fortify shim
pinned Harbor 0.13.1, pre-trial-lock). No link exists from a merged task's version to
the fortify run that hardened it. The TB3 leaderboard record is publicly UNAVAILABLE
(PR #1405 closed unmerged; issue #1507: maintainer-run only).

**Prior art to reuse rather than reinvent** (L6): PROV-DM terms for the lineage graph;
Inspect's `invalidation`/`log_updates`/`error_retries` shape for exclusions and edits;
Every Eval Ever for the reported-score record; in-toto Statement/DSSE only if signing is
ever wanted; MLPerf as the template for a re-deriving checker; lm-eval-style content
hashes for task identity. Not reusable as-is: Provenance Run Crate (drops skipped steps),
OpenTelemetry (transport only), MLflow/W&B/DVC/OpenLineage (run-level, no reasons, no
unavailability).

## E. Where reconstruction fails

Concrete cases, by transition, with recoverability class (RR = retrospectively
recoverable from public artifacts; PC = prospectively capturable; EX = fundamentally
external). Full case list with URLs: L7; walk-back detail: L2–L4.

| Transition | Case | What was missing | Class |
|---|---|---|---|
| trial → cohort | Harbor retry `rmtree` (`queue.py:222`); resume deletes result-less dirs (`job.py:252-260`) | the replaced attempt's evidence; only a count survives | PC (tombstone); harm HYPOTHETICAL |
| trial → cohort | SWE-bench experiments: duplicated instance ids from a union of partial runs inflate a Test row 10.51% → 9.29% actual (`experiments#463`, PR #465 open); nine lists in 4/254 submissions | attempt uniqueness in the aggregation input | RR (found from the public file) |
| trial → cohort | Same-task concurrent attempts collide on container names/ports and are booked as agent errors (`terminal-bench-1#1430`; one report: 447/640 trials) | an "attempt invalid: infra" state; expected-vs-discovered counts | RR only if compose logs kept; PC |
| cohort → aggregate | TB2.0: importer drops trials whose verifier never started, keeps timeouts as 0, averages per-task rates; Harbor's own `mean` gives 84.49, the page 84.72; 63/142 rows count < 445 trials; 3 rows have 1 trial/task; 8 rows "± N/A" for an unstated reason (k−1 = 0 in one task) | a written exclusion predicate and aggregation rule | RR by matching; PC |
| cohort → aggregate | TB "±": maintainer says "standard error across five runs" (`terminal-bench-1#1256`); the 2.0 page renders `(100*stderr*1.96).toFixed(1)` over a within-task-only SE (site JS chunk `13e3e9ec63166a02.js`); 2.1 renders 1×SE | the uncertainty formula and display transform | RR (from the renderer); CONFLICTING semantics preserved |
| cohort → aggregate | Denominators disclosed only in prose: SWE-bench Verified reported over 500/489/477 by different labs; MATH-500 vs MATH; pass@1 averaged over k samples vs single sample; cons@64 vs @1 in a vendor chart | subset id and estimator id carried with the number | PC |
| aggregate → table | HF Open LLM Leaderboard: rows silently replaced by re-runs under a new model revision; two in-place batch rescorings patched only `results.<task>` leaves (`groups`, stderr, `configs.*.metadata.version` stale); displayed model sha is the first run's, scores are the last rewrite of the second | per-value source pointer and transform version; a recorded results→row join | RR (by matching); PC |
| aggregate → table | TB2.0 rows at rank 1 in Wayback snapshots vanish with no public include/exclude/rescore record (`terminal-bench-1#1460`, no maintainer reply); 21 merged HF folders undisplayed; ForgeCode rows rescored to 0 per a blog post, not a commit | a row-state artifact | PC; row-state EX to trial evidence |
| aggregate → table | SWE-bench: a merged 388/500 = 77.6% row is absent because malformed `metadata.yaml` is swallowed by `except: continue`; 6 rows show a false "checked" badge (truthy template string); a "removed" row still displays (flag on the wrong key); 47/180 rows take their % from a hand-typed field, 3 contradicting their own artifacts | an expected-set invariant (merged == displayed) and a row ↔ evidence binding | RR (found here); PC |
| aggregate → table | Chatbot Arena: 27 private Meta variants, 205 silent deprecations vs 47 official, ~50-point gain from testing 20 variants (arXiv 2504.20879); Llama-4 experimental row ≠ released weights | a registry of all runs; row ↔ artifact identity | EX (operator/provider) |
| table → claim | Same LLaMA-65B, MMLU 0.636 / 0.637 / 0.488 across original / HELM / lm-eval-harness (HF blog 2023-06-23) | harness commit + prompt template + scoring rule with the number | PC |
| table → claim | o3-preview (6 vs 1024 samples, above the $10k cap) vs shipped o3 (41–53%); "The production o3 uses a different model" (ARC Prize) | model artifact identity behind a name; sample count and cost | EX unless provider emits it; ARC recorded what it could |
| table → claim | Vendor Terminal-Bench numbers: OpenAI GPT-5.5 "82.7%" vs the maintainer-run Codex CLI row 82.2% ± 2.2 (no harness/attempts disclosed); Anthropic Opus 4.6 65.4% under "1× guaranteed / 3× ceiling" resources (forbidden by leaderboard rules) vs the leaderboard's 62.9%; identical third-party numbers republished by both vendors without provenance | harness, attempts, exclusion, aggregation, resources | EX (private infrastructure); footnotes at best |
| table → claim | Instrument custody: FrontierMath funder had access to most problems (Epoch, 2025-01-23) | a disclosure field | EX |
| claim → interpretation | Bar-exam "90th percentile" was relative to February repeaters (Martínez 2024); "emergent abilities" as a metric artifact; SWE-Bench+ re-read of an identical resolved set 12.47% → 3.97%; verifier exploit in the AI CUDA Engineer | nothing in lineage; the reference frame or verifier validity | EX (claim support) |

**Emergent taxonomy** (L7, 14 classes; the ones a record can address): attempt
identity/uniqueness; attempt validity state; superseded/replaced attempts;
extraction/labelling transform mismatch on intact bytes; environment/instrument content
identity; denominator/subset identity; estimator/aggregation identity; uncertainty
method; row publication state; model artifact identity behind a name; budget/operating
point; instrument custody/exposure. Two classes no record addresses: verifier
validity/scope and claim reference frame.

**Counterexamples that survive the strongest formulation** (a claim-class-specific
required-edge set + a PROV-shaped per-transition record emitted as a diff against the
trivial case + per-field evidence state; C2 §4):

1. **Completeness of the transition set.** A per-transition record certifies each
   recorded transition; it cannot certify that none was omitted (the silently absent
   77.6% row; 21 undisplayed folders; a scan that stopped at part of its universe). The
   only fix is an *expected set* at each layer held by a different actor than the record
   — Harbor has it for trials (`lock.trials`, `n_total_trials`); no leaderboard studied
   has it for rows. **A record without an expected-set check is decoration.**
2. Externalities: private variants, provider identity, funder access, contamination.
   The record can hold `provider_asserted` facts and make absence visible; it cannot
   verify. Policy and audit did the work in every documented case.
3. Retrospective retry/rerun/disposition history: gone by construction or never written.
4. Materiality and human dispositions: representable, never mechanical.
5. Closure of the input identity: a snapshot id that hashes one file while the input
   closure drifts (L5) — a digest scheme was present and still under-identified.

Everything else in the counterexample list (null-as-zero means; same task name with
different digests; timeout multiplier differences; regrade vs source; mixed-provenance
rows; in-place rescoring; hand-typed denominators) is either caught by the formulation
or represented by it with a human decision attached.

**Honest negatives.** No documented public incident of a retry silently replacing an
attempt in a published number (mechanism verified; harm unproven). No documented silent
rerun of a published row with primary evidence — only unexplained disappearances. No
named paper pinned as copying a baseline under a mismatched configuration; the SWE-agent
case is a citation-target error (the 3.8% is not in the cited paper), not a config
mismatch. No real-archive conflict-frequency measurement yet (RESEARCH_MAP E2 unrun).
Nothing in any lane shows trial-level sealing *preventing* a documented failure; the one
archive where per-trial content identity would have directly helped (duplicate ingests,
cheat-mirrors, a 56-trial ingest defect, L5) is not content-addressed.

## F. What Eval Evidence should own

Less than now. Ranked by value the receipts support over cost and overlap:

1. **Per-field evidence state with source pointer** — `observed | derived |
   operator_asserted | provider_asserted | unavailable`, plus unresolved `conflicting`,
   with `{input, json_pointer, input digest, transform name/version}` (the
   structured-provenance companion in RESEARCH_MAP). No surveyed standard has it; three
   lanes (L4 mixed-provenance row, L6, L7 class 4) converge on it as the class where the
   honest *status* of a field mattered more than the digest of its file. Change: express
   conflicts as typed roles (requested / agent-reported / provider-returned) rather than a
   symmetric "unavailable + conflict list" — two of the adapter's four "independent"
   model-identity candidates are the same in-memory object serialized twice
   (`harbor/trial/trial.py:725-745`).
2. **Content-reference primitive** (`safe_run_path`, `file_record`,
   `verify_referenced_files`) — small, portable, and exactly what a per-*row* offline
   bundle needs when the hub goes dark (`#177`) or an archive is not content-addressed
   (L5). Own it as a library function, not as a bundle product.
3. **A read-only reconstruction checker** for Harbor job dirs (optionally plus a
   leaderboard submission JSON): recompute `mean`/accuracy under *declared* policies, emit
   the per-transition record as a diff against the trivial case, list `unavailable` edges,
   and check `expected == discovered == included` wherever an expected set exists
   (`lock.trials`, `n_total_trials`, submission `trials[]`). This is E1 in executable
   form; its output is a proposal to Harbor and the leaderboards, not a format.
4. **Comparison qualification** (lock diff + declared materiality policy + unresolved
   differences), consuming Harbor's own equality keys — only after 3 and only if the
   Inspect translation (E6) shows the shape is not Harbor-specific.

Fixes, not research (each has a receipt above; each requires the adapter-change review
surface in `ARCHITECTURE.md`): read `lock.json` (job and trial) and `result.json:config`
before declaring `harness_version`, `harness_commit`, `tools`, `network_policy`
unavailable; stop requiring `agent/trajectory.json` for discovery (0/17 genuine oracle
trials discovered) or hand discovery to Harbor's job record and only verify against it;
retire the uniform `available_fraction` gate in the next wire-breaking release.

Do not own: the campaign record format (Harbor should emit expected attempts — has;
retry tombstones — missing; member-trial digests at job close — missing; metric transform
version + null policy — missing; regrade lineage — has); the publication manifest (TB2.1's
`submissions/*.json` + `metrics.py`, SWE-bench's `get_results.py`/`get_leaderboard.py`,
plus the missing "merged == displayed" invariant and offline member digests). Do not
build a lineage vocabulary, a signing scheme, a DAG engine, a registry, or a dashboard.
Do not present trial-level byte sealing as the headline; keep it as an optional integrity
signal for archives that lack content addressing. `attestation.signature` stays null
until a signer exists.

Wire contract: unchanged. No question in this study required a new bundle member; the
questions that could not be answered were answered by other layers' records or by
nothing.

## G. What to test next

Ranked by information value; dependencies and acceptance evidence are explicit. Items 1
and 2 decide the direction; the rest refine it.

| # | Experiment | Decides | Dependencies | Acceptance evidence |
|---|---|---|---|---|
| 1 | **E1′ — version-stratified denominator and aggregate reconstruction on genuine Harbor jobs** (the 17 oracle jobs plus the private archive; read-only). Per job: `n_total_trials` vs `len(lock.trials)` vs discovered trial dirs vs `n_completed/n_errored/n_cancelled/n_retries`; recompute `mean` under None→0 and compare to `stats.evals[k].metrics`; count `n_retries > 0`; flag reported reward vs `verifier/reward.json` disagreements | Whether retrospective campaign evidence is fine (unexplained expected-vs-discovered deltas rare, retries rare → a small Harbor PR + publisher checklist) or whether tombstones and a job-close manifest are needed | Private archive access; handling of lock schema v1 vs v3 | A table per Harbor version with counts and unexplained-delta rate; the 56-trial ingest defect reproduced or refuted from raw verifier files; no private values in the report |
| 2 | **Row-manifest retro-fit over all 142 TB2.0 rows** (public HF dataset + tbench.ai detail payloads). Emit per row `{source_jobs, counted trials/task, dropped trials + exception type, per-task rate, accuracy, SE, ×1.96}`; test the two candidate drop predicates over all 76 folders; list rows that reproduce under neither | Whether the per-row manifest is sufficient retrospectively and whether the exclusion predicate is uniquely recoverable — if not, that is the strongest argument for prospective recording | Public data only; ~1 day | Rows with an HF folder reproduce exactly under one predicate, or the ambiguous rows are named; a filed issue on the 2.1 tooling repo with the manifest shape (body via file, no shell interpolation) |
| 3 | **E5′ — prospective capture cost in Harbor, oracle agent only**: retry tombstone instead of bare `rmtree`, member-trial `result.json` digests at job close, `MetricConfig` null-policy/denominator/version fields, an attempt ordinal on `TrialConfig`; count LOC/storage | Whether the three Harbor gaps close cheaply (then "publication tooling is the only hole" becomes true in practice) | Fresh Harbor clone; oracle runs are model-free but Docker execution — confirm permission or unit-test only | Draft PR text + LOC + a job dir with tombstones/digests/policy populated; no PR opened without maintainer consent |
| 4 | **Structured-provenance-per-field companion on two public mixed-provenance cases** (HF Qwen row: `contents` vs `results`, four files; SWE-bench bash-only rows: `per_instance_details.json` vs `info.resolved` vs S3) | Whether item F1 earns its keep beyond prose | Public files only; ~1 day | The record flags "sha from file 1 / scores from file 4", "`groups` stale", and "47 rows with no input digests" mechanically; false-flag rate on the clean rows reported |
| 5 | **E6′ — Inspect translation of the campaign edges only** (`total_samples/completed_samples`, `scored/unscored_samples`, `invalidation{author, reason, timestamp}`, `error_retries`, `log_updates`, `revision{commit, dirty}` → the per-transition record) from a synthetic public `.eval` log | Whether the portable layer is real and small, or coerced (then rename/redesign, do not abstract) | Synthetic log; no model calls | A two-column mapping with a "coerced" flag per field; ≤ 2 coerced fields |

Cheap and worth doing alongside: file the SWE-bench "merged ≠ displayed" invariant
(`20251127_openhands_claude-opus-4-5`) and the truthy-`checked` template string as
issues on `SWE-bench/experiments` — each is a live instance of the deepest survivor
in §E.

## H. Language decision

Drop "claim lineage" as a named layer. It implies a layer distinct from provenance and a
reach into interpretation that the evidence does not support. Use:

- **campaign provenance** for layers 2+3 merged (Harbor-emitted, PROV-shaped, mostly
  derivable today; wrongly implies a formal PROV serialization — acceptable cost);
- **publication record** (or attestation, once a signer exists) for the publisher's
  pointer + aggregation rule + null policy + supersession + adjustments;
- **comparison qualification** for the matched-field policy + unresolved differences;
- **claim support** for layer 3, explicitly out of infrastructure scope.

## I. What could not be established

- The exact TB2.0 exclusion predicate (two candidate rules fit every observation; the
  importer code is not public) and whether the 2.0 importer is per-task-mean or pooled as
  a matter of code (the 2.1 `metrics.py` comment "matching the Harbor importer" is
  CONFLICTING with observed 2.0 behaviour on rows with dropped trials).
- Harbor Hub server-side "latest attempt" semantics (Supabase RPC); whether TB2.1 hub
  visibility (#177) has been restored; the TB3/Frontier-Bench leaderboard record.
- Whether installed-agent ATIF converters preserve provider-returned model ids.
- Real-archive conflict frequency (E2) and retry-deletion frequency (E1) — both unrun.
- Whether a second evaluator breaks the per-transition record (E6 unrun).
- Whether Harbor's hub archive/leaderboard clones already make trial sealing redundant
  (E4 unrun; the allowlist and clone mechanism were observed, no mutation study).
- terminal-wrench was not examined; no genuine Fortify run output was walked (schema
  only); several prior-art candidates were not fetched (Kaggle/Codabench, Sacred, Neptune,
  Pachyderm, LakeFS, Sciunit, ProvBook, Kepler/Taverna/noWorkflow/YesWorkflow).
- The lanes' convergence cannot be de-primed beyond weighting receipts over language.

## J. Paper implication

On these receipts the truthful paper is a negative one: campaign accounting and native
prospective capture subsume most of a per-trial evidence envelope; the missing artifact
is a per-row publication record with an expected-set check plus three Harbor fields; the
one novel portable piece is per-field evidence state. It should not be written until
experiments 1–2 above produce a measured result. `DECISION_GATE_2026-08-15.md` §10 stands.

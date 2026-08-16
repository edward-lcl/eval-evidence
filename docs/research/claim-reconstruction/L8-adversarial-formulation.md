# L8 — Adversarial / conceptual lane: is "claim lineage" a real missing abstraction, and where is the smallest useful boundary?

Date: 2026-08-16. Author role: designated skeptic + designated formalizer.

Sources pinned in this report:

- eval-evidence local checkout: `<eval-evidence-checkout>` at `6d4a25b5f288f9646f30e0d1c9f5923cc6c1ec8c` (OBSERVED via `git rev-parse HEAD`); `eval_evidence.__version__ == "0.2.0rc1"` (OBSERVED, `eval_evidence/__init__.py:3`).
- Harbor: `https://github.com/harbor-framework/harbor` at `a27e9c2ae10a31c40b2dcef33ef5486bce36e185` (all `file:line` cites below are `git show a27e9c2…:<path>` on the local partial clone unless stated otherwise).
- TB2 leaderboard submission repo: `https://huggingface.co/datasets/harborframework/terminal-bench-2-leaderboard` at sha `572b2614be2c0cb2527e14f5b1e4026f1072e6c1`, lastModified `2026-05-15T21:18:55Z` (OBSERVED via HF API).
- TB leaderboard integrity post: `https://www.tbench.ai/news/leaderboard-integrity-update`, dated 2026-04-19 (ASSERTED by page).
- W3C PROV-DM: `https://www.w3.org/TR/prov-dm/`, W3C Recommendation 30 April 2013 (OBSERVED via fetch).
- Genuine local Harbor oracle jobs: 17 job directories under a private worktree path (structure and counts only; no values copied).

---

## 1. Verdict (one paragraph)

"Claim lineage" is not a missing *abstraction*; it is a missing *record*, and the record is a plain PROV-style derivation graph over a small number of typed nodes. Every transition in the proposed four-layer stack (trial → campaign membership → aggregate → table cell → comparative claim → interpretation) decomposes into `used / wasGeneratedBy / wasDerivedFrom` edges plus a named activity with a plan, a collection-with-membership, `wasRevisionOf` for regrade/supersession, and `wasInvalidatedBy` for exclusion — all of which exist verbatim in PROV-DM §5. The one thing PROV does not give you is a slot for *unresolved alternative explanations*, and that belongs to argumentation (layer 4), not infrastructure. The empirical part of this lane is stronger than the conceptual part: at Harbor `a27e9c2`, the job layer already retains expected count (`n_total_trials`), per-reward-value trial membership (`reward_stats`), per-exception membership (`exception_stats`), retry count, cancellation count, resolved-input locks with content digests, harness version/commit, and regrade lineage — but it (a) **deletes** the directory of every failed attempt that is retried (`src/harbor/trial/queue.py:222`), (b) **coerces errored trials to reward 0** inside the job-level `mean` (`src/harbor/metrics/base.py:23-34`), and (c) writes `job/result.json` with `trial_results` always excluded (`src/harbor/job.py:921-1093`, five call sites), so the aggregate's membership is a list of trial *names*, not content identities. Meanwhile eval-evidence at `6d4a25b` is strictly per-trial, never reads `lock.json`, and — on 17 genuine oracle jobs — discovers **0 of 17** trials because it requires an ATIF trajectory. The publication layer (TB2 leaderboard) requires `config.json` + trial `result.json`s + "other artifacts", validates a handful of config invariants, and does not document how the row's number is computed, whether errored trials count as 0, or how reruns/regrades supersede. So: the smallest useful boundary is a **campaign-provenance profile** (a PROV profile with maybe six node types and four edge types) that Harbor could emit natively at job close, plus a **publication attestation** that a leaderboard/paper signs pointing at those artifacts. Eval Evidence should own less than it does now: the evidence-state vocabulary, the content-reference primitive, and possibly the comparison-qualification record; it should not own the campaign record, and "claim lineage" as a fourth named layer should be dropped in favour of "campaign provenance" (layers 2+3 merged) and "claim support" (layer 4, out of infrastructure scope).

---

## 2. Findings with labels and receipts

### F1 — Eval Evidence today is per-trial only; there is no job/campaign/comparison code path. (OBSERVED)

- `grep -n -iE "campaign|compare|comparison|job|aggregate|denominator|lock\.json"` over `eval_evidence/__main__.py core.py adapters.py demo.py` returns exactly one hit: the prose string at `adapters.py:538` ("comparison readiness is unresolved"). No code constructs, reads, or verifies a job/campaign object.
- CLI subcommands are `check`, `bundle`/`build`, `inspect`, `verify`, `audit` (alias), `demo` (`__main__.py:304-342`). None takes two bundles or a job.
- The bundle's required top-level members are `schema_version, source, inputs, instrument_manifest, execution, outcome, item_validity, verifier_evidence, attestation, extensions, bundle_digest` (`eval_evidence/schemas/eval-evidence-bundle-v0.1.schema.json`, `$id: urn:eval-evidence:schema:bundle:v0.1`). No member for membership, inclusion, retries, supersession, aggregation, or comparison.
- The Harbor adapter's hashed references are `result.json`, `config.json`, `agent/trajectory.json` (required) and `verifier/reward.txt`, `verifier/ctrf.json`, `verifier/test-stdout.txt`, `artifacts/manifest.json` (optional) (`adapters.py:638-646`). `lock.json` (trial or job) is never referenced or read.

### F2 — The Harbor adapter's discovery gate excludes real Harbor trials; on 17 genuine oracle jobs it discovers 0 trials. (OBSERVED)

- `HarborAdapter.required = ("result.json", "config.json", "agent/trajectory.json")` (`adapters.py:378`); `detect()` requires all three (`:383-384`).
- Read-only count over 17 genuine oracle job directories (each `jobs/oracle/` with `config.json`, `lock.json`, `result.json`, `job.log`, one trial dir): 17 trial dirs, 0 with `agent/trajectory.json`, `discover_runs()` raises "No supported evaluation run" for 17/17 jobs. The trial dirs contain `agent/` (a non-ATIF file), `verifier/{reward.txt,ctrf.json,test-stdout.txt}`, `artifacts/manifest.json`, `result.json`, `config.json`, `trial.log`.
- Meanwhile each job's `result.json` reports `n_total_trials` and stats keys `n_completed_trials, n_errored_trials, n_running_trials, n_pending_trials, n_cancelled_trials, n_retries, evals, n_input_tokens, n_cache_tokens, n_output_tokens, cost_usd` (OBSERVED key names).
- Consequence: a directory-level `eval-evidence check` on these jobs would report *nothing*, while Harbor's own job record reports a complete campaign. Adapter discovery is not a denominator (the STATE_REGISTER already says this; the 0/17 is a real-data receipt for it, not a synthetic one). Oracle is a degenerate agent, but the failure mode generalises to any agent that does not emit ATIF.

### F3 — Harbor deletes the trial directory of a failed attempt before retrying; only an integer survives. (OBSERVED)

- `src/harbor/trial/queue.py:200-232`: for each `attempt in range(max_retries+1)`, run the trial; if it errored and the exception is retryable and attempts remain, `shutil.rmtree(trial.paths.trial_dir, ignore_errors=True)` at `:222`, sleep, loop. The next attempt reuses the same `trial_config.trial_name`, so it writes to the same directory path.
- Job side: `src/harbor/job.py:690-701` `_remove_completed_attempt_for_retry` pops the previous result from live rewards, calls `stats.remove_trial(previous_result)`, and increments `self._n_retries`. `JobStats.n_retries` (`src/harbor/models/job/result.py:34`) is the only surviving trace.
- Also on `harbor job resume`: `src/harbor/job.py:252-259` — any trial dir without `result.json` is `shutil.rmtree`'d.
- Consequence for the stack: per-attempt retry lineage is **UNAVAILABLE retrospectively by construction** at this Harbor revision. Any "campaign lineage" that promises attempt-level retry history is either prospective (change Harbor to keep the failed dir or write a tombstone) or impossible. This is decisive for outcome D(7).

### F4 — Harbor's job-level `mean` counts errored/cancelled trials as reward 0, silently. (OBSERVED)

- `src/harbor/job.py:940-944`: `_live_rewards[evals_key][trial_name] = rewards if verifier_result is not None else None`. Trials with an exception and no verifier result are stored as `None`.
- `src/harbor/metrics/base.py:14-35` `aggregate_reward_dicts`: `values = [0 if reward is None else …]` (`:25`) and `reward.get(key, 0)` (`:32`). `src/harbor/metrics/mean.py:5-12` divides by `len(values)`.
- `src/harbor/job.py:681-688` `_refresh_metrics_for_eval` computes `metrics = [metric.compute(rewards_list)]` over *all* live rewards for the evals key, i.e. denominator = completed + errored (+ cancelled, since `CancelledError` trials also have `exception_info`, `result.py:158-159`).
- But `AgentDatasetStats.n_trials` (`src/harbor/models/job/result.py:147-148`) counts only trials whose `verifier_result.rewards is not None`. So `job/result.json` reports `n_trials` (rewarded trials) next to `metrics: [{"mean": …}]` whose denominator is `n_trials + n_errors`. The metric name is the only descriptor; there is no `denominator`, `null_policy`, or `version` field in `MetricConfig` (`src/harbor/models/metric/config.py:8-10`, fields `type`, `kwargs`).
- Consequence: an infra-failure-heavy job produces a lower "mean" than a reviewer who computes mean-over-rewarded would. This is a *policy* baked into aggregation and recorded only implicitly by the metric key. It is exactly the kind of transform-name/version + missing-data-policy field the campaign record must carry — but note it is *already* recoverable by reading Harbor's code at a pinned commit, i.e. "code revision" is doing the work that a "policy" field would otherwise do.

### F5 — Harbor's job result natively contains aggregate→trial membership, but by name, not by content identity, and never with per-trial results. (OBSERVED)

- `AgentDatasetStats.reward_stats: dict[str, dict[float|int, list[str]]]` maps `reward_key → reward_value → [trial_name…]` (`src/harbor/models/job/result.py:20-22`, populated `:149-150`). `exception_stats: dict[str, list[str]]` maps `exception_type → [trial_name…]` (`:23-25`, `:153-155`).
- `_write_job_result(exclude_trial_results=True)` is passed at every call site (`src/harbor/job.py:921, 928, 964, 993, 1093`) — `trial_results` never lands in `job/result.json`. OBSERVED on the 17 oracle jobs: `trial_results` absent / length 0.
- `n_total_trials = len(self._trial_configs)` (`src/harbor/job.py:978`) is the expected-attempt count. Expected attempts are enumerated in `lock.json.trials[]` (`JobLock.trials: list[TrialLock]`, `src/harbor/models/job/lock.py:243`) with per-trial task digest, agent config, environment, verifier lock, and (for regrades) `source_trial`. The lock does *not* carry `trial_name`, so lock entries are matched to trial dirs by config equality, not by identifier — `TrialConfig.__eq__` excludes `trial_name` and `job_id` (`src/harbor/models/trial/config.py:469-476`); `JobLock._equality_key` uses an *unordered* list (`lock.py:256, 260-261`).
- Consequence: Harbor already answers CAMPAIGN_MINIMUM questions 1, 2, 4 (as "everything with a result.json is included"), and 7 (as "the metric key"), partially 6 (regrade only). It answers them with trial names and a job UUID, not with digests, so "which bytes were aggregated" needs the trial dirs to still be present and unmodified. That is where a content-reference primitive is genuinely useful — and it is a small primitive.

### F6 — Harbor's lock layer already retains harness version/commit, task content digest, resolved config, skill digests, and regrade source; eval-evidence marks these unavailable. (OBSERVED)

- `HarborLockInfo {version, git_commit_hash, is_editable}` (`lock.py:58-61`), populated from package metadata / `direct_url.json` / `git rev-parse HEAD` (`lock.py:556-606`). `JobLock.harbor` (`:240`).
- `TaskLock.digest` (validated `sha256:<64hex>`, `lock.py:64-77`), computed by `Packager.compute_content_hash` (`lock.py:511-516`); `TaskLock.__eq__` is digest-only (`:79-86`).
- `TrialLock` (`lock.py:173-213`) freezes task, install_only, all timeout multipliers, extra_instructions (digested), agent config, skills (digested, with git url/commit), environment, extra_docker_compose (digested), verifier (+ resolved environment_mode), and `source_trial`. Written per trial at `src/harbor/trial/trial.py:748-757` (`lock_path`).
- eval-evidence marks `harness_version`, `harness_commit`, `verifier_digest`, `environment_image_digest` as unavailable ("not mapped", `docs/HARBOR_MAPPING.md` instrument table) and never reads `lock.json`. OBSERVED on the 17 oracle jobs (older Harbor: job lock `schema_version: 1`, keys `created_at, harbor, invocation, n_concurrent_trials, retry, schema_version, trials`; `harbor` keys `is_editable, version` — no `git_commit_hash` key): `harbor.version` is a string in 17/17 job locks. So `harness_version` is natively available in every genuine job inspected and the bundle says unavailable.
- Note the version drift: pinned commit `JobLock.schema_version = 3`, oracle jobs have `1` and an `invocation` key absent from the pinned model; pinned commit writes per-trial `lock.json`, oracle trial dirs have 0/17. Version-stratified recoverability is real (RESEARCH_MAP E1/E2 are right to stratify).

### F7 — Two of eval-evidence's four "independent" model-identity candidates are the same in-memory object serialized twice; the interesting disagreement is requested-vs-agent-reported, which the adapter flattens into a symmetric conflict. (OBSERVED + DERIVED)

- `Trial._init_result` (`src/harbor/trial/trial.py:725-745`) writes `config.json` from `self.config.model_dump_json(exclude_defaults=True)` and sets `TrialResult.config = self.config`; `_finalize` writes `result.json` from `self.result.model_dump_json(indent=4)` (`:419`). So `config.json:agent.model_name` and `result.json:config.agent.model_name` are one object, differing only in default elision.
- `agent_info` comes from `self.agent.to_agent_info()` (`:414`, `:733`) — the agent's own report; ATIF `agent.model_name` is written by the agent. So the real evidential structure is: {requested by operator} vs {reported by agent} vs {reported by provider — not captured}. eval-evidence `_resolve_candidates` (`adapters.py:117-138`) treats all candidates as peers, and on disagreement makes the field `unavailable` with a `source_conflicts` record.
- DERIVED: the conflict machinery is correct not to pick a precedence winner, but it discards a typed relation (requested → effective) that a reviewer would want as a *pair*, not as "unavailable". This is a design point against generic symmetric "conflict" and for typed provenance roles — again, PROV has this natively (`used` with a role vs `wasGeneratedBy`).

### F8 — The DECISION_GATE "absent list keys" fix is over-conservative at the pinned commit because `result.json:config` carries the explicit lists. (OBSERVED)

- `AgentConfig.skills`, `.mcp_servers`, `.extra_allowed_hosts` have `default_factory=list` with **no** `exclude_if` (`src/harbor/models/trial/config.py:81, 123, 148`); only `include_logs`, `exclude_logs`, `env` have `exclude_if` (`:130-147`). `result.json` is dumped without `exclude_defaults`, so `result.json:config.agent.skills` is an explicit `[]`.
- The adapter reads `tools`/`network_policy` from `config.json` only (`adapters.py:572-601`) and never falls back to `result.json:config.agent`. OBSERVED on 17 oracle trials (older Harbor): `result.json.config.agent` has `skills`, `mcp_servers`, `extra_allowed_hosts` in 17/17; `config.json.agent` has `skills` in 17/17 too, so the fixture's "absent key" case did not occur in this sample.
- Consequence: a claimed unavailability that native state resolves. Small, but it is a data point for D(8): the mapping is incomplete before Harbor is.

### F9 — The TB2 leaderboard (publication layer) requires job `config.json` + per-trial `result.json` + "other artifacts", validates config invariants, and does not document the score computation, error-trial policy, exclusion rules, or supersession. (OBSERVED from README at HF sha `572b2614…`)

- Verbatim structure: `submissions/terminal-bench/2.0/<agent>__<model>/metadata.yaml`, `<job-folder>/config.json`, `<trial-N>/result.json`. Validation rules: `timeout_multiplier` must equal `1.0`; no agent timeout overrides; no verifier timeout overrides; no resource overrides; all trial dirs must have valid `result.json`; "Trial directories must contain other artifacts from the run"; minimum five trials per task; no agent access to TB site/repo.
- No mention of `lock.json`, of how the leaderboard number is computed, whether errored trials count as 0, or whether a resubmitted/regraded job supersedes. Page banner: "SUBMISSIONS CLOSED", new process "will enforce the policies outlined in" the 2026-04-19 integrity post.
- Integrity post (ASSERTED by page): "ATIF trajectories are required for all passing trials"; reward hacking → trial reward 0; an agent judge reviews all passing trials; challenge process. It does not address lock files, harbor version, regrades, exclusions, error counting, or the score formula.
- Consequence: at the table-cell edge, the aggregation rule and null policy are ASSERTED by the maintainer (or implied by "we import your job/result.json"), not recorded. Combined with F4, a submitted job's `stats.evals[k].metrics[0].mean` already embeds a null-as-zero policy; whether the leaderboard re-aggregates or copies is UNAVAILABLE (see §4).

### F10 — Regrade lineage exists natively as derivation, but supersession (which of source vs regrade is *reported*) is not a Harbor concept. (OBSERVED)

- `SourceTrialConfig {action: "regrade", type: local|hub, trial_id, path}` (`src/harbor/models/trial/config.py:403-431`); `SourceJobConfig` (`src/harbor/models/job/config.py:315-341`); `SourceTrialLock` copies the source's `TaskLock` verbatim and keys equality on `(action, type, trial_id|path, source task digest)` (`lock.py:89-119`); `build_trial_lock` copies source skills verbatim (`lock.py:402-424`).
- `src/harbor/trial/regrade.py:4-12` (module docstring): copies `agent/` and `artifacts/` from the source into a fresh trial dir; "The source trial is never modified"; regradability is defined by the artifact manifest.
- Nothing in `JobResult`/`JobStats` marks a source trial as superseded. Both trials exist; both have rewards; which one a leaderboard row uses is a publication decision. That is `prov:wasRevisionOf` + a publication-layer choice, not a new Harbor field.

### F11 — Harbor already defines "replay identity" equality that excludes naming/logging fields. (OBSERVED)

- `JobConfig.__eq__` excludes `{job_name, debug}` (`src/harbor/models/job/config.py:500-507`); `TrialConfig.__eq__` excludes `{trial_name, job_id}` (`trial/config.py:469-476`); resume refuses a different config (`job.py:246-250`) and a different lock (`job.py:891-904`).
- Consequence: the "campaign identity" node already has a native definition (config equality modulo naming + lock equality). Eval Evidence need not define one.

### F12 — PROV-DM already has every relation the proposed stack needs except "unresolved alternatives". (OBSERVED via fetch of PROV-DM; mapping is DERIVED)

- Confirmed present in PROV-DM §5 (W3C Rec. 2013-04-30): `wasDerivedFrom` (5.2.1), `wasRevisionOf` (5.2.2), `wasQuotedFrom` (5.2.3), `hadPrimarySource` (5.2.4), `wasInvalidatedBy` (5.1.8), `Collection`/`hadMember` (5.6.1-5.6.2), `Plan` and `wasAssociatedWith(plan)` (5.3.3), `Bundle` (5.4), `alternateOf`/`specializationOf` (5.5).
- Mapping (DERIVED): trial output = Entity; expected attempt = Entity generated by planning Activity with the JobLock as Plan; retry = new Entity `wasRevisionOf` old, old `wasInvalidatedBy` retry Activity; regrade = Entity `wasDerivedFrom` source with Activity(regrade) and Plan(new task digest); included cohort = Collection with `hadMember`; exclusion = Entity `wasInvalidatedBy` selection Activity whose Plan is the inclusion rule (attribute: reason); aggregate = Entity `wasGeneratedBy` Activity(metric name/version) `used` collection; table cell = Entity `wasQuotedFrom` aggregate, `wasAttributedTo` publisher, in a Bundle (attestation); comparative claim = Entity `wasDerivedFrom` two cells with Activity(comparison, Plan = matched-fields policy). Actor/authority = Agent + `wasAttributedTo`/`actedOnBehalfOf`; timestamps = `prov:startedAtTime/endedAtTime`; provenance-of-provenance = Bundle.
- What is *not* in PROV: a first-class "unresolved alternative explanation" or "control that would invalidate the interpretation". That is argumentation/inference, not derivation. (ASSERTED, not fetched: nanopublications and micropublication/argumentation ontologies exist for this; I did not verify their current specs and do not rely on them.)

### F13 — The eval-evidence research docs already contain most of this skepticism; the missing thing is a decision, not more analysis. (OBSERVED)

- `docs/research/DECISION_GATE_2026-08-15.md` §6 lists "Current Harbor already has richer JobLock, TrialLock, JobResult, retry, task digest, and regrade-lineage primitives than Eval Evidence currently consumes" and "Campaign membership and aggregation can dominate trial-level correctness"; §8 assigns denominators/locks/regrade to Harbor and inclusion/aggregation to publication tooling; §11 says "Do not add … a comprehensive campaign platform".
- `docs/research/UPSTREAM_MAP.md` "Minimal campaign record to test, not yet build" is, field for field, a PROV profile (attempt identity, task digest, lifecycle state, trial evidence digest, included?+reason, retry/regrade/supersession links, transform name/version, ordered inputs, grouping/missing-data policy, reported value+uncertainty, matched conditions, unresolved differences).
- So this lane's job reduces to: (i) confirm with receipts that Harbor covers most of it (F3-F6, F10-F11 do), (ii) say whether the remainder is different in kind (F12: no), (iii) name the boundary.

### F14 — Coverage metric `available_fraction` is over 20 fixed fields regardless of claim; five of them are structurally unavailable from any Harbor artifact at this commit. (OBSERVED + DERIVED)

- `STANDARD_INSTRUMENT_FIELDS` has 20 names (`core.py:20-41`); `_instrument_manifest` sets absent ones unavailable and computes `available/len` (`core.py:126-143`); `verify_bundle` recomputes (`:287-327`).
- `response_model`, `agent_binary_sha256`, `system_prompt_sha256`, `policy_profile_id`, `environment_image_digest` are "not mapped" (HARBOR_MAPPING) and — DERIVED from the models read — have no source in `TrialResult`, `TrialConfig`, `TrialLock`, or `JobLock` at `a27e9c2` (no field for provider-returned model, agent binary hash, prompt hash, or resolved image digest). `verifier_digest` is partially covered by `TaskLock.digest` (task content includes tests) but not separately. So the ceiling for a Harbor bundle is 14/20 = 0.70 even with perfect mapping; the docs' E3 concern is well-founded.

---

## 3. Answers to the lane questions

### A. Claim classes: minimal mechanical evidence and where inference begins

Notation: `sha(x)` = SHA-256 of bytes; "H:" = Harbor field at `a27e9c2`; "EE:" = eval-evidence bundle field at `6d4a25b`; "PUB:" = publication artifact.

**C1 — "this single run produced X".**
Minimal mechanical evidence: `sha(result.json)`, `sha(config.json)`, `sha(lock.json)` (trial), `sha(verifier/reward.txt)` or the `verifier_result.rewards` mapping, `sha(agent/trajectory.json)` if the claim is about behaviour, `TaskLock.digest`, `HarborLockInfo.{version,git_commit_hash}`, `AgentInfo.{name,version,model_info}`, resolved timeout components. Mechanical derivation stops at: "these bytes exist and are internally consistent (reward in result == reward.txt; config == lock modulo defaults)". Inference begins at: "the verifier is correct", "the model named is the model that answered" (`response_model` UNAVAILABLE at this commit), "the environment was the declared image". EE covers this except it never reads `lock.json` (F6) and requires ATIF (F2). Verdict on C1: **already mostly native**; EE's marginal value is normalization + status vocabulary + safe path/reference handling.

**C2 — "this campaign produced aggregate X".**
Minimal: job `config.json` (with `exclude_defaults` caveat), job `lock.json` (`trials[]` = expected attempts, `retry`, `harbor`), job `result.json` (`n_total_trials`, `stats.*`, `stats.evals[k].{n_trials,n_errors,reward_stats,exception_stats,metrics}`), the set of trial dirs with their `sha(result.json)`, the Harbor code revision (because `mean`'s null policy lives in code, F4), and — if retries happened — an admission that per-attempt history is gone (F3). Mechanical derivation stops at: recompute `mean` from `reward_stats` and check it equals `metrics[0].mean`; check `len(trial dirs with result.json) == n_completed_trials`; check `n_total_trials == len(lock.trials)`; match each trial dir to a lock entry by config equality (F5, unordered, no trial_name in lock). Inference begins at: "the deleted retry attempts would not have changed the aggregate", "errored trials are correctly scored 0", "no trial dir was removed after job close" (nothing native protects against post-close deletion of a trial dir; `n_completed_trials` would then disagree with the directory count, which is detectable — good — but a re-run of `harbor job resume` would silently regenerate it, F3). Verdict: **mostly native**, with three genuine holes: (i) retry attempt tombstones, (ii) content identity of member trials in `job/result.json` (names only), (iii) explicit null/denominator policy field on the metric.

**C3 — "model A outperformed model B".**
Minimal: two C2 records; equality of `TaskLock.digest` sets across the two jobs (task content), equality of `TrialLock` fields *other than* `agent.model_name` (and whatever differs by design), equality of Harbor version or a statement of why version drift is immaterial, per-task denominators equal (5 vs 5, not 1/3/2 as the redacted comparison in `docs/VISION.md` found), and the comparison statistic with its uncertainty method (paired vs unpaired, bootstrap vs Wald, over tasks vs over trials). Mechanical derivation stops at: "the two locks differ only in field set S; the two denominators are D_A, D_B; the statistic is f(rewards_A, rewards_B) = v". Inference begins at: "S is immaterial to the comparison" (that is a *policy* — UPSTREAM_MAP's "unresolved material differences" — and it is exactly where reviewer judgment is irreducible), and at "the difference is not explained by task-version drift, prompt drift, or provider-side model change" (`response_model` UNAVAILABLE). Verdict: C3 = **C2 × 2 + a diff of locks + a declared statistic + a materiality policy**. The lock diff is mechanical and Harbor already gives equality keys (F11); the materiality policy is the only new artifact, and it is small.

**C4 — "this leaderboard row is supported by these evaluations".**
Minimal: the PUB row (agent, model, score, date), a pointer to the submitted job dir(s) with `sha` of each `result.json` (or a Merkle root over the submitted tree), the validator's version and its pass record, the leaderboard's aggregation function + null policy (F9: UNAVAILABLE today), and any post-hoc adjustments (judge-set-to-zero per the integrity post; regrade supersession F10). Mechanical derivation stops at: "row.score == agg(submitted result.jsons)". Inference begins at: "the submitter did not cherry-pick jobs" (unobservable without a registry of *all* jobs run, which is a prospective-capture / attestation problem, not a lineage-record problem). Verdict: **C4 is C2 plus a publication pointer plus the publisher's aggregation/adjustment record.** It is not a distinct claim class; it is C2 with an `Agent` (publisher) and a `Bundle` (attestation).

**C5 — "changing component X caused improvement Y".**
Minimal: C3 where the lock diff is exactly {X} and everything else — including seed/sampling if the provider honours it, task digests, Harbor commit, prompt hash (UNAVAILABLE), agent binary (UNAVAILABLE) — is equal, plus the number of paired trials and a paired statistic. Mechanical derivation stops at the same place as C3. Inference begins earlier and harder: "X is the *only* thing that changed" is unverifiable at this commit because prompt/agent-binary/response-model identity are not captured; the causal reading additionally needs "no time-varying confound" (provider-side model updates between the two jobs — timestamps help but do not settle it). Verdict: **C5 = C3 with a controlled diff**; nothing new in kind, but the unavailable fields matter most here.

**C6 — "a scientific interpretation built from multiple experiments".**
Minimal: a set of C2/C3/C5 records + the interpretation text + the list of controls run + the list of alternatives considered and how each was excluded. Mechanical derivation stops at "each cited number traces to a C2/C3/C5 record" — that is C4-shaped (publication pointers). Everything past that is argument. Verdict: **C6 is out of scope for infrastructure** except for its citation edges. Layer 4 ("claim support") is real but is not something a harness or a bundle tool should own; it is a paper/registered-report artifact.

**Revised taxonomy** (three classes, not six):
- **R** (record claim): C1 and C2 — "these bytes, these counts, this transform". Native to Harbor with three holes (F3, F5, F4-policy).
- **D** (derived claim): C3, C4, C5 — "these R-claims, this diff, this statistic, this publisher". New artifact = a diff-of-locks + declared statistic + publisher attestation. Small.
- **I** (interpretive claim): C6 — out of infrastructure scope; only its citation edges are infrastructure.

### B. The missing edge: replay vs audit, and is it different in kind from PROV?

For each transition: what must be preserved to REPLAY (re-execute the step and get the same output) vs to AUDIT (check that the recorded step is internally consistent and attributable without re-executing).

| Transition | REPLAY needs | AUDIT needs | Native today (Harbor a27e9c2 / TB2 PUB) |
|---|---|---|---|
| trial output → campaign membership | expected-attempt list (lock.trials), retry policy, the retry loop's code revision, per-attempt tombstones | trial `sha(result.json)`, matching lock entry, `n_total/completed/errored/cancelled/retries`, reason for absence of any expected attempt | lock.trials ✔ (unordered, no name); counts ✔; tombstones ✘ (F3); trial digest in job record ✘ (names only, F5) |
| membership → aggregate | ordered inputs (or a canonical order), transform name+version+params, null policy, code revision | `reward_stats` (value→names), `metrics`, ability to recompute, explicit denominator | reward_stats ✔; metric key ✔; version/null-policy field ✘ (F4, lives in code); denominator implicit |
| aggregate → table cell | publisher's import/re-aggregation code, adjustments (judge zeroing, regrade supersession) | pointer from cell to job dir(s) with digest, validator version + result, adjustment log, actor, timestamp | job dir required ✔; digest/Merkle ✘; aggregation rule ✘ (F9); adjustments announced not recorded (integrity post) |
| table cell → comparative claim | both cells' lineage, statistic code, matched-field policy | lock diff, denominators, statistic name+uncertainty method, list of unresolved differences | equality keys ✔ (F11); nothing publishes the diff |
| comparative claim → interpretation | n/a (not replayable) | citation edges to D-claims; controls run; alternatives considered | none; not infrastructure |

Fields listed in the lane brief, mapped to PROV-DM terms (all OBSERVED present in PROV-DM §5 per F12): input identities → Entity + `used`; selection rule → Plan of the selection Activity; transform name/version → Activity type + Plan; code revision → Plan (an Entity with a git SHA); parameters → Activity attributes / Plan; output identity → Entity + `wasGeneratedBy`; reason for inclusion/exclusion → attribute on `hadMember` / `wasInvalidatedBy`; actor/authority → Agent + `wasAssociatedWith`/`wasAttributedTo`/`actedOnBehalfOf`; timestamp → `startedAtTime/endedAtTime/generatedAtTime`; supersession/regrade → `wasRevisionOf` (+ `wasInvalidatedBy` if the old one is retired); uncertainty calculation → an Entity generated by an Activity(statistic) with a Plan; unresolved conflicts → *not in PROV* as first-class; representable as two `alternateOf` Entities with an attribute, but the semantics ("we do not know which is right") is argumentation.

**Is any of this different in kind from a generic PROV derivation edge?** No. Every field is a PROV node, edge, role, or attribute. The two things that *feel* new — (a) "reason for exclusion" and (b) "unresolved conflict/alternative" — are (a) an attribute on a standard edge and (b) an argumentation object outside provenance. Therefore: **call it "campaign provenance / PROV profile" and stop inventing.** The profile needs roughly: 6 entity types (expected-attempt, attempt-result, cohort, aggregate, cell, claim), 4 activity types (schedule, select, aggregate, publish/compare), 2 agent roles (runner, publisher), and the PROV edges above. It should be emitted by Harbor at job close (Entities for attempts and aggregate; Activity(schedule) with Plan = lock; Activity(aggregate) with Plan = metric name/version/null-policy + Harbor commit; retry tombstones as `wasInvalidatedBy`), and extended by the publisher (cell `wasQuotedFrom` aggregate, Bundle attribution, adjustments).

### C. Counterexamples

Each states which layer (1 trial evidence, 2 campaign lineage, 3 claim lineage, 4 claim support) would have caught it and whether a reviewer decision changes.

**C-i. Every recorded trial valid, aggregate misleading — the null-as-zero mean (F4).** Job of 10 trials on one task, 5 pass (reward 1), 5 raise `ModelNotFoundError` after a provider outage. Each `result.json` is internally valid. `metrics[0].mean = 0.5`; `n_trials = 5`, `n_errors = 5`. A leaderboard importing `mean` reports 0.5; a reviewer reading `reward_stats` sees 5/5 pass among rewarded trials. Caught by: layer 2 (denominator + null policy) — and *already catchable natively* from `stats.evals[k].{n_trials,n_errors,metrics}` if the reader knows Harbor's policy; layer 1 catches nothing. Reviewer decision changes: **yes** (0.5 vs 1.0 is a different row). But note the fix is a *policy field* on the metric or a documented convention, not a new abstraction. Real-data anchor: OBSERVED shape only — the 17 oracle jobs each have `n_trials`, `n_errors`, `metrics` keys; I did not inspect values.

**C-ii. Aggregate reproducible, comparison invalid — task-content drift.** Two jobs, same nominal task name, `TaskLock.digest` differs (the task's tests changed between runs). Each job's mean recomputes exactly from its own trials. Comparing them compares two verifiers. Caught by: layer 3 (lock diff shows `task.digest` ≠) — but the *evidence* is layer-2 native (`TaskLock.digest`, `TaskLock.__eq__` is digest-only, F6). Reviewer decision changes: **yes**. The redacted genuine comparison in `docs/VISION.md` ("same nominal task/revision traveling with two task checksums") is the ASSERTED real instance. Nothing new needed beyond *reading* the lock.

**C-iii. Number reproducible, interpretation unsupported — "model A is better at X" when A's trials had a different `agent_timeout_multiplier` or `extra_allowed_hosts`.** Both aggregates recompute; the lock diff shows `agent_timeout_multiplier` 1.0 vs 2.0 (or an extra allowed host). The number is right; "better" is not licensed. Caught by: layer 3 (diff) → but only if a *materiality policy* says timeout multiplier is material. TB2 PUB validation makes `timeout_multiplier == 1.0` a hard rule (F9), i.e. the publisher already encodes one materiality policy for one field. Reviewer decision changes: **yes**, and this is the one place where a small *new* artifact (matched-fields policy + unresolved-differences list) earns its keep. It is still not a new abstraction; it is a Plan attached to the comparison Activity.

**C-iv. Same retained evidence supports two plausible claims — regrade vs source (F10).** Task verifier fixed after the run; regrade job produces reward 0 where source produced 1 (or vice versa). Both trials retained, both valid, lineage explicit (`source_trial`). Claim A: "under the published verifier the model passed"; Claim B: "under the corrected verifier it failed". Caught by: layer 3 must state which is *reported* (`wasRevisionOf` + publisher choice); layer 2 shows both. Reviewer decision changes: **depends on the publisher's supersession rule**, which is UNAVAILABLE for TB2 (F9). No new abstraction; one publisher policy field ("regrades supersede: yes/no, as of date").

**C-v. Claim correct though part of its lineage unavailable — retries deleted (F3).** Job with `n_retries = 3`; all final attempts pass; the three deleted attempts were `AgentTimeoutError`s… except `AgentTimeoutError` is in `RetryConfig.exclude_exceptions` by default (`job/config.py:285-303`), so by default they would not have been retried — say they were network errors. The aggregate is correct for the attempts that count; the *retry* lineage is gone. Reviewer decision changes: **no** for the aggregate; **yes** for a cost/latency or "first-attempt success" claim. Layer 2 with a tombstone would record it; nothing retrospective can. This is the cleanest evidence that lineage completeness is *claim-relative* — the same missing edge is immaterial for one claim and fatal for another, which is why a fixed uniform coverage score (F14) is the wrong instrument.

**C-vi. Full lineage, large complexity, no decision change — a maintainer-run, single-Harbor-version, no-retry, no-regrade, all-completed campaign published by the runner.** Every PROV edge is trivially derivable from `lock.json` + `result.json` + the trial dirs; a full PROV graph adds thousands of triples and changes no reviewer decision. Layer 2/3 catch nothing because there is nothing to catch. This is the *modal* case for maintainer-run leaderboards (TB2.1: "only maintainer-run submissions", ASSERTED from search results), which argues that the campaign-provenance profile should be **emitted only where the native records are ambiguous** — i.e., it is a *diff against the trivial case*: retries, regrades, exclusions, version drift, publisher adjustments. When the diff is empty, the record is a one-line attestation ("no retries, no regrades, no exclusions, agg = mean over N, null policy = zero, Harbor commit = …").

### D. The eight outcomes — for, against, ranking, flip conditions

Ranking is provisional and is my judgment (DERIVED from F1-F14 + C-i…vi); it is not a measurement.

**(2) It is just campaign provenance and needs no new concept — RANK 1.**
For: F12 (every field maps to PROV-DM §5), F5/F6/F10/F11 (Harbor already holds most nodes and the equality keys), C-i…C-iv each resolve to a Plan/attribute/edge. Against: PROV as *serialization* is heavyweight and nobody in this ecosystem emits it; "no new concept" ≠ "no new record". Flip: if E1 (denominator reconstruction) finds membership cannot be stated even prospectively without a concept PROV lacks — I could not construct one.

**(8) Most necessary state already exists natively and Eval Evidence should become much smaller — RANK 2 (nearly tied with 2).**
For: F6 (harness version present 17/17, bundle says unavailable), F8 (list keys present in `result.json:config`), F5 (membership native), F11 (identity native), F1 (EE has zero campaign code so "shrink" costs nothing). Against: F14 (5-6 fields have *no* native source at this commit — prospective capture needed), F2 (EE's own gate is what excludes real trials — fixable, not structural), the evidence-state vocabulary is genuinely absent upstream. Flip: if E6 (Inspect translation) shows the vocabulary + content-reference primitive is portable *and* adopted, EE keeps a small stable core; if E5 shows Harbor will emit its own post-run manifest, EE shrinks to a verifier/normalizer or disappears.

**(7) Prospective capture solves it while retrospective reconstruction is mostly impossible — RANK 3 (true for a specific subset).**
For: F3 (retry dirs deleted → attempt-level history irrecoverable), F14 (`response_model`, prompt hash, agent binary, image digest have no retrospective source), version drift (job lock v1 vs v3; no per-trial lock in older jobs). Against: F5/F6 show *most* of C2 is retrospectively recoverable at the pinned commit; "mostly impossible" overstates — it is "impossible for attempt-level retry, provider identity, prompt identity; possible for membership/denominator/aggregate/lock". Flip: E1's unexplained-delta rate. If unexplained expected-vs-discovered deltas are rare (<5%) across versions, retrospective is fine for C2; if common, (7) rises to rank 1.

**(4) Only publication tooling is missing — RANK 4.**
For: F9 (leaderboard does not record aggregation rule, null policy, supersession, or content pointers), C-iii/C-iv are publisher-policy gaps. Against: F3/F4 are *Harbor* gaps (tombstones, policy field), so "only" is false. Flip: if Harbor ships tombstones + metric policy field, (4) becomes true.

**(6) Numerical claim reconstruction is tractable but interpretive claim support is not — RANK 5 (true but not decision-relevant).**
For: C6 analysis; PROV lacks "unresolved alternatives". Against: it is trivially true and no one proposed infrastructure for layer 4; the risk is scope creep, not a research finding. Flip: none needed; treat as a boundary statement.

**(1) Claim lineage is a useful missing abstraction — RANK 6.**
For: C-iii/C-iv show a comparison Plan and a supersession policy are needed and absent. Against: those are one Plan and one boolean, both PROV-shaped; the *record* is missing, the *abstraction* is not. Flip: a concrete field that cannot be expressed as an Entity/Activity/Agent/Plan/attribute — none found.

**(3) Existing provenance standards already solve it — RANK 7 (correct in theory, useless in practice).**
For: F12. Against: no adopter; W3C PROV serializations are not what Harbor/TB will emit; "solve" requires a *profile* and an *emitter*, which do not exist. Flip: if a lightweight JSON-LD PROV profile were adopted by Harbor, (3) and (2) merge.

**(5) The problem is evaluator-specific and cannot support a portable layer — RANK 8.**
For: F4/F3 are Harbor-specific policies; membership semantics differ (Inspect samples/epochs vs Harbor trials/attempts). Against: the *edge types* are evaluator-neutral (F12); only node payloads differ. Flip: E6 result — if the Inspect mapping needs coerced semantics for membership/retry/aggregation, (5) rises.

### E. Language

Proposed replacements for "claim lineage", with what each wrongly implies:

- **"campaign provenance"** — recommended for layers 2+3 merged. Wrongly implies: a formal PROV serialization (it need not be), and that a "campaign" is a Harbor concept (Harbor says "job"; a campaign may span jobs). Acceptable cost.
- **"result derivation record"** — accurate for the aggregate→cell edge. Wrongly implies: a single result; hides membership/exclusion.
- **"aggregate provenance"** — accurate for membership→aggregate. Wrongly implies: nothing about the cell/publication step or comparisons.
- **"reporting chain"** — good for aggregate→cell→claim. Wrongly implies: linearity (regrades and multi-job rows are DAGs) and that the chain starts at the aggregate.
- **"cohort manifest"** — good for the *included* set with reasons. Wrongly implies: a static list (retries/regrades make it temporal) and that exclusion reasons are part of it (they belong to the selection activity, not the cohort).
- **"publication attestation"** — good for the C4 edge (publisher signs a pointer + rule + adjustments). Wrongly implies: cryptographic signature (EE's `attestation.signature` is null; TRUST_MODEL defers it) and truth ("attested" ≠ "correct").
- **"claim lineage"** (the original) — wrongly implies a new layer distinct from provenance, and that lineage reaches into interpretation (layer 4). Drop it.
- **"claim support"** — keep for layer 4 only, explicitly out of infrastructure scope.

Net: **campaign provenance** (Harbor-emitted, PROV-shaped, mostly derivable today) + **publication attestation** (publisher-emitted pointer + aggregation rule + null policy + supersession + adjustments) + **comparison qualification** (matched-field policy + unresolved differences; the only piece EE might reasonably own as a portable check).

### F. Placement — what Eval Evidence should own

Given F1-F14:

**Eval Evidence should own (less than now):**
1. The evidence-state vocabulary `observed/derived/operator_asserted/provider_asserted/unavailable` and the contradiction rule (`_declared_evidence`, `adapters.py:57-76`) — genuinely absent upstream and portable.
2. The safe run-relative content-reference primitive (`safe_run_path`, `file_record`, `verify_referenced_files`, `core.py:89-115, 225-257`) — small, portable, and the thing F5 says the job record lacks (digests of member trials).
3. Optionally, a *comparison qualification* check: given two locks (or two lock-shaped records), emit the diff, apply a declared materiality policy, and list unresolved differences. This is the one C3/C5 artifact with no native home. It should consume Harbor's own equality keys (F11), not re-model config.
4. Nothing at the campaign layer. Do not build the "minimal campaign record" in EE; prototype it as a *reader* of `config.json + lock.json + result.json + trial dirs` that emits the PROV-profile diff-against-trivial (C-vi) and hands it to Harbor as a proposed native export.

**Harbor should own:** expected attempts (has), retry/cancel counts (has), retry attempt tombstones (missing — F3), member-trial content digests in `job/result.json` or a job-close manifest (missing — F5), metric transform version + null policy field (missing — F4), harness identity (has), task/verifier/environment digests (task has; verifier/image partial), provider-returned model identity (missing — F14, prospective only), regrade derivation (has).

**Terminal-Bench / Fortify should own:** task version ↔ digest registry, verifier score-component provenance (issue #1390 per UPSTREAM_MAP, ASSERTED), before/after hardening acceptance evidence.

**Publication tooling (leaderboard/paper) should own:** aggregation rule + null policy + denominator as recorded fields, supersession rule for regrades/resubmissions, content pointer (digest/Merkle) from row to submitted tree, validator version + result, adjustment log (judge zeroing), actor + timestamp. None of this exists in the TB2 README (F9).

**Which EE bundle fields duplicate Harbor lock/result state (OBSERVED cross-walk at the two pinned revisions):**

| EE bundle field | Duplicates Harbor native? | Where in Harbor |
|---|---|---|
| `source.run_id`, `source.task_id` | yes | `TrialResult.trial_name`, `.task_name` |
| `source.task_revision` | yes | `TaskLock.git_commit_id` / `TaskConfig.ref`; better: `TaskLock.digest` |
| `instrument.model_id`, `model_provider` | yes | `AgentInfo.model_info.{name,provider}`, `AgentConfig.model_name` |
| `instrument.agent_name`, `agent_version` | yes | `AgentInfo.{name,version}` |
| `instrument.harness_name` | derived constant | n/a |
| `instrument.harness_version`, `harness_commit` | **available natively, EE says unavailable** | `JobLock.harbor.{version,git_commit_hash}` (F6) |
| `instrument.tools` | yes (as digests of lists) | `AgentConfig.skills/mcp_servers`; better: `TrialLock.skills[].digest` |
| `instrument.max_turns`, `effort_or_thinking`, `sampling_parameters` | yes | `AgentConfig.kwargs` |
| `instrument.max_wall_time_s` | partial | multipliers in `TrialLock`; base in task.toml (not in trial dir) — EE's derivation is a genuine service |
| `instrument.task_checksum` | yes | `TrialResult.task_checksum`; `TaskLock.digest` |
| `instrument.network_policy` | yes | `EnvironmentConfig/AgentConfig.extra_allowed_hosts` |
| `instrument.verifier_digest`, `environment_image_digest`, `system_prompt_sha256`, `agent_binary_sha256`, `policy_profile_id`, `response_model` | **no native source at a27e9c2** | prospective capture only (F14) |
| `execution.started_at/finished_at`, `metrics.*` | yes | `TrialResult` timings, `AgentContext` totals |
| `outcome.reward/scores/termination_reason` | yes | `VerifierResult.rewards`, `ExceptionInfo.exception_type` |
| `inputs[]` (path, sha256, bytes) | **not duplicated** | Harbor has no trial-level file manifest except `artifacts/manifest.json` for artifacts |
| `instrument_manifest.*.status` | **not duplicated** | Harbor has no evidence-state vocabulary |
| `extensions.harbor.source_conflicts` | not duplicated, but see F7 | Harbor has no cross-source reconciliation |
| `item_validity`, `verifier_evidence` | not duplicated (and unavailable from Harbor) | Fortify/TB review outputs |
| `bundle_digest`, `attestation` | not duplicated | Harbor lock equality is structural, not byte-sealed |

So: ~14 of 20 instrument fields and all of `source/execution/outcome` duplicate Harbor; the non-duplicated core is `inputs[]` digests, the status vocabulary, and the sealed envelope. That is the "smaller EE".

---

## 4. What I could NOT establish, and where I looked

- **How the TB2 leaderboard computes the row number from submitted jobs** (mean over trials? over tasks? errored = 0? re-aggregated or copied from `job/result.json`?). Looked: HF dataset README at sha `572b2614…` (no formula), tree listing (only `submissions/`, `README.md`, `.gitattributes`, `.gitignore` — no scoring script), integrity post 2026-04-19 (no formula). UNAVAILABLE. Note it is `CONFLICTING` in potential only: Harbor's own `mean` uses null→0 (F4); whether the leaderboard does is unknown.
- **Whether the TB2/2.1 leaderboard treats regrades or resubmissions as superseding.** Looked: same sources. UNAVAILABLE.
- **Whether any Harbor revision retains failed-attempt directories or writes a tombstone.** Looked: `queue.py`, `job.py` at `a27e9c2` only. Not checked at `origin/main` `f03db62…` (out of budget). UNAVAILABLE beyond the pinned commit.
- **Actual conflict prevalence** (how often `agent_info.model_info.name` ≠ `config.agent.model_name` in real archives). Not measured; the 17 oracle jobs are a degenerate agent. UNAVAILABLE (RESEARCH_MAP E2 is the right instrument).
- **Whether `job/result.json` `metrics` values on the 17 oracle jobs equal recomputed means** — deliberately not inspected (would require reading reward values; the lane rules forbid copying values, and a pass/fail count of an oracle run is uninformative for this lane).
- **Whether the "absent list key" case (`config.json` missing `skills`) occurs in any real Harbor version.** Looked: 17 oracle trials (0 occurrences), pinned model (defaults serialized in `result.json:config`). UNAVAILABLE for other versions.
- **Whether Inspect AI (or any second evaluator) has membership/retry semantics that break the PROV profile.** Not examined (E6 is future work). UNAVAILABLE.
- **Whether nanopublication/argumentation ontologies are a fit for layer 4.** ASSERTED from prior knowledge only; not fetched; not relied upon.

---

## 5. Implications for the central question

The central question was: what evidence is required for an independent person to reconstruct an evaluation claim, given that verifying one trial is easy and reconstructing *why this collection became this number* is hard.

1. **The reconstruction problem is real but is not an abstraction problem.** Every "why" edge decomposes into PROV-DM relations (F12); Harbor already materialises most nodes (F5, F6, F10, F11). What is missing is (a) three specific Harbor records — retry tombstones, member-trial digests, metric policy field (F3, F5, F4) — and (b) a publisher record — aggregation rule, null policy, supersession, content pointer, adjustments (F9). Both are small.

2. **The proposed four-layer stack should collapse to three.** Layer 1 (trial evidence) is mostly native plus a status vocabulary; layers 2 and 3 are one thing (campaign provenance = PROV profile over job state + publisher attestation); layer 4 (claim support) is real but is argumentation, not infrastructure. "Claim lineage" as a named fourth layer should be dropped.

3. **Lineage completeness is claim-relative** (C-v): the same missing edge is immaterial for one claim and fatal for another. This kills uniform coverage as a readiness signal (F14) and supports the docs' E3 direction — but the "claim-specific required evidence" should be expressed as *which PROV edges must be present*, not as a new schema per claim class.

4. **Prospective vs retrospective is a per-field question, not a global verdict.** Attempt-level retry history, provider-returned model, prompt hash, agent binary, image digest are prospective-only (F3, F14). Membership, denominator, aggregate recomputation, lock diff, regrade derivation are retrospectively recoverable at `a27e9c2` and partially in older jobs (F5, F6). RESEARCH_MAP E1/E2 should report this per field and per Harbor version rather than as a single "recoverability" number.

5. **Eval Evidence should become smaller and should stop presenting itself as the place where campaign semantics will live.** Its defensible residue: the evidence-state vocabulary, the content-reference primitive, deterministic sealing/verification, and possibly a comparison-qualification check that consumes Harbor's own equality keys. Its Harbor adapter should read `lock.json` (job and trial) and `result.json:config` before declaring fields unavailable (F6, F8), and should stop requiring ATIF for discovery (F2) — or, better, hand discovery to Harbor's job record and only *verify* against it.

6. **The strongest single next observation** to flip the ranking is E1's unexplained expected-vs-discovered delta rate stratified by Harbor version: low → outcomes (2)/(8) hold and the work is a small Harbor PR + a publisher checklist; high → outcome (7) rises and the work is a Harbor job-close manifest with tombstones. Neither branch needs a standalone "claim lineage" package.

7. **Willing to say it plainly:** the abstraction is unnecessary. The record is necessary, it is PROV-shaped, and most of it should be emitted by Harbor and signed by the publisher. Eval Evidence's job is to make the *status* of each edge honest (observed/derived/asserted/unavailable), not to own the graph.

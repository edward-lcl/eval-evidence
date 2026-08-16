# Lane L3 — Real claim reconstruction, case B: one SWE-bench Verified leaderboard row

Date of observation: 2026-08-16 (all "today" references). Observer: lane L3 agent.
Working scratch: `.../scratchpad/lanes/l3work/` (leaderboard JSON extract, partial clone of
SWE-bench/experiments, HF parquet snapshots, re-derivation script `rederive.py`).

Pinned revisions used throughout (OBSERVED unless noted):

| Source | Identity |
|---|---|
| Leaderboard page | `https://www.swebench.com/` fetched 2026-08-16; leaderboard data is inline JSON in `<script type="application/json" id="leaderboard-data">` (4.19 MB page) |
| Site repo | `SWE-bench/swe-bench.github.io` master `f42505b2` (2026-08-10T02:03:02Z, "Sanitize names"); `data/leaderboards.json` 7,270,245 bytes, committed by hand (deploy.yml only runs `build.py`, does not regenerate it) |
| Experiments repo | `https://github.com/SWE-bench/experiments` `origin/main` = `1faa91cade0562ba62b66c1c99e71f7b72d96f13` (2026-08-09, "Clean up model display names in mini-SWE-agent metadata"); 409 commits; root commit `e6dd51f9e0e002faf7d542da5f63a923f01ef400` 2024-10-15 "Initial commit - reset history" |
| Target submission | `evaluation/verified/20251215_livesweagent_claude-opus-4-5` (PR #388, squash commit `a94b32fe8de3e1c26e35c41239a20fd07a4d92de`, 2026-01-25); pre-squash PR head commit `e67dde43` (2025-12-15) still fetchable as `refs/pull/388/head` |
| S3 artifacts | bucket `swe-bench-submissions` (us-east-1), prefix `verified/20251215_livesweagent_claude-opus-4-5/` — anonymously listable and readable over HTTPS |
| Dataset | HF `princeton-nlp/SWE-bench_Verified` (7 commits, HEAD `c104f840cc67` 2025-02-18) and `SWE-bench/SWE-bench_Verified` (11 commits, HEAD `78f471bf655a` 2026-08-16T04:23Z) — parquet downloaded at every revision, sha256 recorded below |
| Harness | PyPI `swebench` (latest 4.1.0, 2025-09-11) installed in a scratch venv for re-derivation; `SWE-bench/SWE-bench` main has commits dated 2026-08-16 |
| Docker image (one instance) | Docker Hub `swebench/sweb.eval.x86_64.astropy_1776_astropy-12907`: tags `v1` (2025-01-04), `v2` (2025-09-10), `latest` (re-pushed 2026-08-16T18:48Z, digest `sha256:e0829630…`) |

---

## 1. Verdict

The top row of SWE-bench Verified ("live-SWE-agent + Claude 4.5 Opus", 79.20 %) is
reconstructable to the per-instance level from public artifacts *without trusting the
submitter's summary numbers*: I fetched the pre-squash PR commit, read 495 per-instance
`report.json` files (396 resolved = 396/500 = 79.2 %, identical set to `results.json`),
then re-parsed the raw `test_output.txt` files with the pip-installed harness against
the 2024/2025 dataset revisions and got the same 396. That is genuinely rarer than for
most leaderboards. But the reconstruction is *conditional* on things the artifacts do not
record: (a) re-running the maintainers' own `get_results.py` today with the unpinned
`SWE-bench/SWE-bench_Verified` dataset gives **397/500 = 79.4 %**, because a
PASS_TO_PASS entry was dropped from `astropy__astropy-7606` on 2026-08-10; (b) the harness
version, sb-cli-vs-local, and the Docker image digest used to produce `test_output.txt`
are nowhere in the log, the metadata, or the PR, and the `:latest` image tag it would
have used was re-pushed today; (c) pass@1, no-test-use, no-hints and no-web are
self-attested checkboxes. Around the target row the same repo shows the failure modes the
central question is about: 47 of 180 Verified rows (the mini-SWE-agent cross-listings)
take their percentage from a hand-typed `info.resolved` field, not from per-instance
records; three of them contradict their own committed per-instance file or S3 reports
(52.8 % displayed vs 51/500 in-repo and 98/500 logs on S3; 69.6 % displayed vs 0/500
in-repo vs 353/500 on S3; 64.93 % = 324/499 against a stated /500 rule); a "removed"
entry (Kodu, Lite) is still displayed because the removal flag was written to the wrong
YAML key; six rows show a "checked by the SWE-bench team" badge because a template string
`"false (See README.md …)"` is truthy in JavaScript; a merged 388/500 = 77.6 % row
(`20251127_openhands_claude-opus-4-5`, would be rank 4) is silently absent from the page
because its metadata is mis-shaped and the generator swallows the exception; a Test row
displays 10.51 % computed over a duplicate-containing list whose set gives 9.29 %; and
the repo's own history was reset in 2024-10 so pre-reset row mutations are unrecoverable. The `experiments` layout is
de facto a claim-lineage record (retained trials → aggregate → row) and a good one for the
*trial → aggregate* half; what it lacks is instrument identity (harness/dataset/image
pins), a machine-checked included/excluded/denominator statement, any uncertainty, and
any binding between the row shown and the artifacts that justify it. On the central
question: the abstraction the evidence-bundle work proposes is *unnecessary* for the
per-trial half here (raw logs + a re-parser already do it) and *necessary but not
sufficient* for the campaign half; the highest-value missing pieces are pins and
denominators, not sealing.

---

## 2. Findings with labels and receipts

### F1. What a reader sees (OBSERVED, browser DOM on 2026-08-16)

Landing page `https://www.swebench.com/` defaults to the "Verified" tab **with the
"Bash Only" preset switched on** ("Verified is a human-filtered subset of 500 instances
(details). Defaults to bash-only setting (run with mini-SWE-agent).") — 47 rows visible,
columns `# | Model | Agent | % Resolved | Avg. $ | Trajs | Org | Date | Release`. Unticking
"Bash Only" shows 180 rows with columns `# | Model | Agent | % Resolved | Org | Date | Site`.
Top of the full board as rendered (rank, model, agent, % resolved, date, badges):

| # | Model | Agent | % Resolved | Date | badges shown |
|---|---|---|---|---|---|
| 1 | Claude 4.5 Opus (effort "medium") | live-SWE-agent | 79.20 | 2025-12-15 | none |
| 2 | Claude 4.5 Opus | Sonar Foundation Agent | 79.20 | 2025-12-05 | none |
| 3 | Doubao-Seed-Code | TRAE | 78.80 | 2025-09-28 | none |
| 4 | Gemini 3 Pro Preview | live-SWE-agent | 77.40 | 2025-11-20 | "The agent run was performed by or directly checked by the SWE-bench team" |
| 5 | Multiple | Atlassian Rovo Dev | 76.80 | 2025-09-02 | none |
| 6 | Claude 4 Sonnet | EPAM AI/Run Developer Agent | 76.80 | 2025-08-04 | none |
| 7 | Claude 4.5 Opus (high) | mini-SWE-agent | 76.80 | 2026-02-17 | none |
| 8 | Multiple | ACoder | 76.40 | 2025-08-19 | none |

No cost, no CI, no N, no harness version is shown for non-mini rows. Row fields present in
the embedded JSON per entry: `agent, agent_org, checked, cost, date, folder,
instance_calls, instance_cost, logo, logs, model_display, model_org, model_release_date,
name, os_model, os_system, reasoning_effort, resolved, site, tags, trajs, trajs_docent,
warning` (+ `mini-swe-agent_version`, `per_instance_details` for bash-only rows).
Target row JSON (OBSERVED): `{"name": "live-SWE-agent + Claude 4.5 Opus medium (20251101)",
"resolved": 79.2, "date": "2025-12-15", "checked": false, "os_system": true,
"os_model": false, "logs": "s3://swe-bench-submissions/verified/20251215_livesweagent_claude-opus-4-5/logs",
"trajs": "s3://…/trajs", "cost": null, "folder": "20251215_livesweagent_claude-opus-4-5",
"site": "https://github.com/OpenAutoCoder/live-swe-agent", "tags": ["Model:
claude-opus-4-5-20251101", "Org: UIUC", "System: Attempts - 1"], "warning": null,
"reasoning_effort": "medium"}`.

The `date` column is DERIVED by `get_leaderboard.py` from the first 8 characters of the
folder name (self-declared by the submitter); it is not the merge date. For the target
row: folder date 2025-12-15, PR opened 2025-12-15T07:02Z, merged 2026-01-26T02:12Z
(OBSERVED via `gh pr view 388`). All 180 Verified `date` values equal their folder prefix
(DERIVED).

### F2. The claim-lineage chain, step by step, for the target row

1. **Row → folder.** `folder` = `20251215_livesweagent_claude-opus-4-5` (OBSERVED in
   leaderboard JSON). Site data is a hand-committed `data/leaderboards.json` produced by
   `analysis/get_leaderboard.py` (ASSERTED by that script's docstring; consistent with the
   site repo's commit log — last regeneration 2026-08-10, experiments HEAD 2026-08-09).
2. **Folder at `origin/main`** contains only `README.md, logo.png, metadata.yaml,
   results/{results.json, resolved_by_repo.json, resolved_by_time.json}` — **no logs/,
   no trajs/, no preds** (OBSERVED, `git ls-tree`). The squash commit message records why:
   "Remove logs and trajs (Uploaded to shared s3 bucket)".
3. **results.json**: `{"no_generation": [4 ids], "no_logs": [1 id], "resolved": [396 ids]}`
   (OBSERVED). 396/500 = 79.2 (DERIVED). `README.md` and the PR body both paste the
   `get_results.py` output "Resolved 396 instances (79.2%)" (ASSERTED by submitter).
4. **Per-instance evidence** exists in three places, all byte-identical where compared:
   - GitHub PR ref `refs/pull/388/head` → commit `e67dde43` (pre-squash) still contains
     `logs/` (496 instance dirs; 495 with `eval.sh, patch.diff, report.json, test_output.txt`;
     one — `psf__requests-1142` — with only `patch.diff`), `trajs/` (500 files), and
     `preds.json` (OBSERVED via partial clone + sparse checkout: logs 42 MB, trajs 95 MB).
   - S3 `verified/20251215_livesweagent_claude-opus-4-5/`: 1,981 log objects (=495×4+1),
     500 traj objects, 1 preds object; per-object `LastModified` 2026-01-26T02:10:20Z;
     ETag (MD5) for `logs/astropy__astropy-12907/{eval.sh, patch.diff, report.json,
     test_output.txt}` = `938755b8…`, `7e564045…`, `b179cca0…`, `58ed1f25…` = local MD5 of
     the git blobs (OBSERVED; DERIVED equality).
   - The README says "You need an AWS account to download the logs" (ASSERTED) — the
     bucket is anonymously listable/readable over HTTPS (OBSERVED: `GET
     https://swe-bench-submissions.s3.amazonaws.com/?prefix=…` returns 200 with a
     `ListBucketResult`; direct object GET returns 200). CONFLICTING (docs vs behaviour).
5. **Recount from `report.json`** (DERIVED from 495 OBSERVED files): 396 with
   `resolved: true`, 99 with `resolved: false`; all 495 have `patch_is_None=false,
   patch_exists=true, patch_successfully_applied=true`; `report.json` inner keys are
   `patch_is_None, patch_exists, patch_successfully_applied, resolved, tests_status`
   with `tests_status.{FAIL_TO_PASS,PASS_TO_PASS,FAIL_TO_FAIL,PASS_TO_FAIL}.{success,failure}`.
   Set equality with `results.json.resolved`: **True**.
6. **Re-derivation from raw `test_output.txt`** (DERIVED, script `rederive.py`, swebench
   4.1.0 `make_test_spec` + `get_eval_report`), same 495 logs, dataset at five revisions:

   | dataset revision | resolved | % | equals results.json set |
   |---|---|---|---|
   | princeton-nlp `39bc39ab` (2024-08-13 initial) | 396 | 79.2 | yes |
   | princeton-nlp `c104f840` (2025-02-18, current) | 396 | 79.2 | yes |
   | SWE-bench `fd80552a` (2025-04-29) | 396 | 79.2 | yes |
   | SWE-bench `03e151cf` (2026-08-10) | **397** | **79.4** | no — `astropy__astropy-7606` becomes resolved |
   | SWE-bench `78f471bf` (2026-08-16, current) | **397** | **79.4** | no — same |

   `get_results.py` calls `load_dataset("SWE-bench/SWE-bench_Verified", split="test")`
   with no revision (OBSERVED in source), so **the maintainers' own re-derivation, run
   today, does not reproduce the displayed 79.2**. Cause: HF commit `96dae8dbbfc0`
   (2026-08-10, "Drop a PASS_TO_PASS entry with an empty parametrization that matches no
   test") removed one P2P test from `astropy__astropy-7606` (241 → 240) (OBSERVED by
   parquet diff).
7. **What the log does and does not show.** `test_output.txt` (2,453 lines for
   `astropy__astropy-12907`) is a `set -x` bash trace: conda activate, `git status`,
   `git show`, `git diff <base_commit>`, `pip install -e .[test]`, checkout of the test
   file at `base_commit`, `git apply` of the test patch (heredoc), the pytest invocation
   between `>>>>> Start Test Output` / `>>>>> End Test Output` markers, per-test
   `PASSED …` lines, `15 passed in 0.38s`, and the final checkout (OBSERVED; structure
   only). It contains **no** harness version, sb-cli marker, timestamp, hostname, Docker
   image name or digest (OBSERVED: grep for `docker|image|sha256|digest|swebench|harness|
   version` hits only compiler warnings and a FITS string). `run_instance.log` — the
   harness file that would name the image — is deleted on purpose by `get_results.py`
   ("Remove unnecessary evaluation artifacts"; maintainer confirms "by design", issue #52,
   2024-08-13).
8. **eval.sh consistency.** All 495 submitted `eval.sh` are identical (modulo whitespace)
   to `make_test_spec(instance).eval_script` from swebench 4.1.0 at each of the three
   dataset revisions tested (DERIVED). This shows the *script family* is the current-era
   harness, not *which* version. The new dataset column `eval_script` (added 2026-08-09
   "for the v5 harness") differs from the submitted `eval.sh` on **20/500** instances
   (e.g. `astropy__astropy-8707` gains `pip install -q 'pytest<7.2'`; `astropy__astropy-7336`
   renames a test file) — a future re-run would execute different scripts on those 20.
9. **Docker image identity.** swebench 4.1.0 names the image
   `sweb.eval.x86_64.astropy__astropy-12907:latest`; the 2026-08-09 dataset column names
   `swebench/sweb.eval.x86_64.astropy_1776_astropy-12907:latest` (OBSERVED). Docker Hub
   shows three tags with three digests, `latest` re-pushed **today** (OBSERVED). Which
   digest produced the December-2025 log: UNAVAILABLE (nothing records it).
10. **PR record.** PR #388 body: description, arXiv link, pasted `get_results` output,
    checklist with four `[X]` boxes (pass@1; no PASS_TO_PASS/FAIL_TO_PASS use; no hints;
    no web-browsing/steps taken) (ASSERTED by submitter). Maintainer comment 2026-01-26:
    "Just verified submission, uploaded logs, merged." (ASSERTED; what "verified" ran is
    not stated). Reviews: 0. `metadata.yaml`: `checked: false`, `os_system: true`,
    `os_model: false`, `system.attempts: 1`, `model: [claude-opus-4-5-20251101]`,
    `report: https://arxiv.org/abs/2511.13646` (OBSERVED).

### F3. Aggregation rule (OBSERVED in `analysis/get_leaderboard.py` at `1faa91ca`)

- For `verified|lite|test|multimodal`: `resolved = round(len(results.json["resolved"]) *
  100 / {500,300,2294,517}, 2)`. Missing/no-generation/no-log instances count as failures
  by omission from the list. `len()` of a **list**, so duplicates count (see F7).
- For `bash-only|multilingual`: `resolved = metadata["info"]["resolved"]` — a hand-typed
  number in YAML — and those 47 bash-only entries are **cross-listed into the Verified
  board** with `name = "mini-SWE-agent + " + name`, logo/site rewritten, and asset paths
  string-replaced `/bash-only/` → `/verified/`.
- `checked = metadata["tags"].get("checked", False)`; `warning = metadata["info"].get("warning")`.
- Consequences (DERIVED, verified against the live JSON): 47/180 Verified rows have no
  results.json behind their number; their leaderboard `logs`/`trajs` links point at
  `s3://swe-bench-submissions/verified/<folder>/…` prefixes that are **empty on S3**
  (OBSERVED: 0 objects for six probed folders under `verified/`, while `bash-only/<same>`
  has the artifacts). Issue #381 (2025-12-05, closed) documents users hitting this.

### F4. Bash-only rows: displayed number vs committed per-instance record vs S3

`analysis/bash_only_get_extra_info.py` builds `per_instance_details.json` from
`trajs/*.traj(.json)` and marks `resolved=False` whenever `logs/<id>/report.json` is
absent locally ("Warning: report.json not found … return False"); it prints a mismatch
warning if details and `info.resolved` differ by >0.1 but does not fail or correct
(OBSERVED in source). Cross-check of all 47 bash-only folders (DERIVED):

| folder | displayed % | per_instance_details.json | S3 `logs/` report.json | notes |
|---|---|---|---|---|
| `20250720_mini-v0.0.0-claude-3-7-sonnet-20250219` | 52.8 (=264/500) | 51 true / 449 false | **98** instances have logs; 51 resolved | 402/500 instances have no evaluation log anywhere public; displayed number unverifiable. Metadata `checked: true`. |
| `20260226_mini-v2.0.0_gemini-3-pro-high` | 69.6 (=348/500; PR #423 body says 348/500) | **0** true / 500 false (9 with cost 0) | 500 reports; **353** resolved (=70.6) | three sources, three numbers. CONFLICTING. |
| `20250726_mini-v1.0.0_claude-sonnet-4-20250514` | **64.93** | 324 true / 176 false | 499 reports; 324 resolved | 324/499 = 64.93 → denominator 499, contradicting maintainer "It's out of 500" (issue #367, open since 2025-11-12). Eight Verified rows show non-k/500 values (64.93, 39.58, 28.73, 23.94, 21.62, 21.04, 13.52, 9.06). |
| `20260219_mini-v2.0.0_gpt-5-2-codex` | 72.8 | file absent | 500 reports; 364 resolved (=72.8) | reconstructable only via S3 |
| `20250720_mini-v0.0.0-Llama-4-Scout-17B-Instruct` | 9.06 | file absent | 496 report.json | 9.06 ≠ k/500; UNAVAILABLE which denominator |
| 39 others | k/500 | matches | (not all probed) | consistent where probed |

`checked` for the 17 most recent bash-only rows is `null` (key present, empty) — the
site's `checked` filter treats them as unchecked even though these are maintainer-run
(OBSERVED in JSON; the site tooltip semantics "performed by or directly checked by the
SWE-bench team" would make them checked). CONFLICTING (semantics vs data).

### F5. Dataset revision history (OBSERVED via HF API + parquet diffs)

`princeton-nlp/SWE-bench_Verified`: `9f18a21f` initial (2024-08-13), `39bc39ab` upload,
`67358593`/`944835ee` README, `a9e03327` (2024-12-02, no content change), `5201ca8e`
(2025-02-13, **PASS_TO_PASS of `pylint-dev__pylint-7080` loses 1 test**), `c104f840`
(2025-02-18, adds `difficulty` column: `<15 min` 194, `15 min–1 h` 261, `1–4 h` 42,
`>4 h` 3). `SWE-bench/SWE-bench_Verified`: `fd80552a` (2025-04-29, identical rows to
`c104f840`), `880e3283`/`91aa3ed5` (2026-02, `eval.yaml`), `b6ee4b82` (2026-08-09, adds
`image, eval_script, log_parser, eval_type`), `aa227074` (2026-08-09, `image` re-pointed
for all 500 to `swebench/sweb.eval.x86_64.<repo>_<n>_<id>:latest`), `96dae8db`
(2026-08-10, `astropy__astropy-7606` P2P 241→240), `e33ae570` (2026-08-10,
`django__django-10097` P2P 1432→1427), `03e151cf` (2026-08-10, `eval_script` changed for
`astropy__astropy-8707`, `astropy__astropy-8872`), `78f471bf` (2026-08-16, F2P/P2P columns
change type from JSON-string to list; semantically identical). Instance ids and count
(500) never changed. The maintainers' scripts and docs name the dataset by repo id only,
never by revision. Parquet sha256 at each revision recorded in the scratch dir
(`hf/*.parquet`), e.g. `pn_39bc39abbbbb` = `e43d3822…`, `sb_78f471bf655a` = `030cfd7f…`.

### F6. Retry / attempt policy (ASSERTED in `checklist.md` and README; enforcement OBSERVED)

- Required: "Is a pass@1 submission (does not attempt the same task instance more than
  once)". Definitions: Pass@k not allowed; **Best@k allowed** ("a distinct module of your
  system decides which attempt to submit", tag `attempts: "2+"`); Best@1 = "single
  attempt … Across multiple runs, this is the # of instances solved in every single run"
  (an unusual definition — intersection over runs — that no artifact can evidence).
- Enforcement: PR-body checkboxes and a request that trajectories "reflect all rollouts +
  the mechanism for selecting" (ASSERTED). No script checks attempts. Of the 133
  non-mini Verified rows: 82 tagged `Attempts - 2+`, 49 `Attempts - 1`, 2 `Attempts - 2`
  (DERIVED). Of the top 20 external rows: 11 single-attempt, 9 multi-attempt; 1 checked.
- Re-submission of the same system is allowed and old rows persist as separate entries
  (e.g. `20250623_warp` and `20250901_warp`; `20250519_trae`, `20250612_trae`,
  `20250928_trae_doubao_seed_code`) (OBSERVED). No best-of-resubmissions rule stated.
- Test/hint/web-browsing prohibitions: self-attested. Historical enforcement was reactive
  (issue #230: `test_patch` found in Kodu logs by a third party; issue #217: 42/61
  submissions edit test files, maintainer asks reporter to fix the harness).

### F7. Row mutability and corrections (OBSERVED in git history and issues)

- **History reset**: root commit `e6dd51f9` 2024-10-15 "Initial commit - reset history".
  Any row change before that date is unrecoverable from this repo (UNAVAILABLE); the
  README's link to the April-2024 eval-bug write-up
  (`SWE-bench/SWE-bench/tree/main/docs/20240415_eval_bug`) returns 404 today.
- **No metadata.yaml has ever been deleted since the reset** (`git log --diff-filter=D`
  on `evaluation/*/*/metadata.yaml` is empty). Rows are not removed; they are flagged.
- **Kodu (Lite, `20241207_kodu_sonnet_v1`)**: issue #230 (2025-05-21) → maintainer:
  "Removing Kodu submission from the leaderboard for now" (2025-06-19) → commit `5c7a733f`
  adds top-level `warning: true` to metadata. `get_leaderboard.py` reads
  `metadata["info"]["warning"]`; the site hides rows with truthy `warning`
  (`mainResults.js: visibleResults = results.filter(item => !item.warning)`). The live
  JSON has Kodu with `warning: null` at 44.67 % — **the removal did not take effect**
  (OBSERVED, both in JSON and in the metadata at `origin/main`). Its metadata also still
  points at the old bucket `s3://swe-bench-experiments/…`, which returns `NoSuchBucket`
  today; the artifacts exist under the new bucket (OBSERVED).
- **Score corrections after merge** (results.json modified after its creating commit):
  `1fbb2b42` 2025-08-25 dedup `verified/20240402_sweagent_claude3opus` (issue #301:
  three ids ×5); `91c0ee88` 2025-06-19 fix `lite/20250111_moatless_deepseek_v3` shown as
  0 % (issue #242, "something funky with the results recreation on our side"); three
  submitter-driven updates in 2024–2025 (#97, #112, #158). Total: 6 modifications across
  ~320 folders (DERIVED).
- **Still-live defect**: `evaluation/test/20240402_sweagent_claude3opus/results/results.json`
  `resolved` list has 241 entries / 213 unique; the Test board displays 10.51 % (241/2294),
  the set gives 9.29 % (OBSERVED; issue #463 2026-07-30; PR #465 open since 2026-08-09).
- **Bulk metadata rewrites** touching every row: `5a10ff77` 2025-05-10 "Add tags to
  metadata" (this is where `checked: true` was set for 14 of the 30 external checked
  Verified rows), `6c148fe` 2026-01-05 bucket rename, `7b0ed877` 2026-08-09 "Update
  metadata" (agent/model display fields). Note the S3 bucket itself was renamed
  (`swe-bench-experiments` → `swe-bench-submissions`); the old name is dead.
- **Duplicate-folder cleanup**: `6454b49d`/`d637d1d3` 2025-09-30 "Remove duplicate
  folders with filename clashes / case sensitive issue" (only `git_peek…md` files
  deleted).
- **Merged but silently absent from the board**: `evaluation/verified/
  20251127_openhands_claude-opus-4-5` (PR #376, merged 2026-01-26 by the maintainer with
  "Submission validation checks out, uploaded logs and merged"; `results.json.resolved`
  has **388 ids = 77.6 %**, which would be rank 4) is not in the leaderboard JSON nor in
  the site repo's `data/leaderboards.json` (OBSERVED: 0 matches). Its `metadata.yaml`
  uses a non-conforming shape (`name`, `oss`, `verified`, `site` at top level; no `info:`
  block, no `tags.checked/os_system`), so `get_leaderboard.py` raises on
  `metadata["info"]["name"]`, prints "Error loading metadata", and `continue`s
  (OBSERVED in source; DERIVED cause). Reconciliation: 134 verified folders + 47
  bash-only = 181; 180 rows displayed. A merged row can therefore vanish from the page
  with no visible trace.

### F8. Manual transitions and what "checked" means

- README (ASSERTED): "If you are interested in receiving the 'verified' checkmark …
  1. Create an issue 2. … provide us instructions on how to run your model … 3. We will
  run your model on a random subset of SWE-bench and verify the results." Site tooltip
  (OBSERVED): "The agent run was performed by or directly checked by the SWE-bench team".
  Since 2025-11-18 (README note) Verified/Multilingual accept only academic/research
  submissions with a public report.
- Who sets the flag: of 30 external Verified rows with `checked: true`, the `+checked:
  true` diff first appears in a **submitter-authored** commit for 12 (e.g. `a577207` PR
  #327 OpenHands+GPT-5, `c1ab920` PR #237, `4ccc355` Moatless, `b2d4e3f` Skywork; two of
  the 12 are SWE-agent rows authored as "carlos"/"carlose", plausibly maintainer Carlos
  Jimenez, so 10 are clearly external-authored) and in a maintainer commit for 18 (14 of
  them the 2025-05-10 bulk "Add tags to metadata" commit `5a10ff77`) (DERIVED from
  `git log -p`). Whether an independent maintainer run happened for the 10–12 is
  UNAVAILABLE from the repo (no issue link, no subset list, no logs of the check).
- **Truthiness defect**: `checklist.md`'s template value is `checked: false (See README.md
  for info on how to get your results verified)`. Six Verified folders kept that literal
  string (`20251120_livesweagent_gemini-3-pro-preview` 77.4 %, `20250901_entroPO_…_tts`,
  `20250901_entroPO_…`, `20251110_frogboss-32b`, `20251110_frogmini-14b`,
  `20250806_SWE-Exp_DeepSeek-V3`) (OBSERVED in JSON). The site renders
  `${item.checked ? '<span … "Checked by the SWE-bench team">' : ''}`; the DOM on
  2026-08-16 shows **66 rows with the badge** = 60 `true` + 6 template strings, including
  rank 4 (OBSERVED via in-page JS). A false "checked" badge is thus displayed on a top-5 row.
- Merge is the transition; there are zero formal PR reviews on #388 and #327 (OBSERVED).
  The leaderboard JSON is regenerated by hand and committed to the site repo
  (last 2026-08-10).

### F9. Uncertainty

None displayed anywhere (OBSERVED). DERIVED: 396/500 → Wilson 95 % CI [75.4, 82.5].
Rank 1 vs rank 2 (both 396): they disagree on 36 instances, split exactly 18/18
(DERIVED from the two `results.json`), so the tie is also a tie under McNemar; issue #466
(2026-08-15, open) reports 129/133 adjacent pairs inseparable and ranks 1–8 inseparable
from #1 (ASSERTED by issue author; the 18/18 figure I recomputed matches). Rank 1 vs
rank 3 (TRAE, 394): 34 vs 32 disagreements (DERIVED).

### F10. Model / system identity ambiguity (OBSERVED in JSON)

35 of 133 external Verified rows carry no `Model:` tag at all; 46 display "Multiple" or
"Undisclosed"; rank 3 lists two models (`Doubao-Seed-Code`, `Doubao-Seed-1.6`); issue
#323 (TRAE) needed a maintainer ping to surface models. `os_system: true` for 69/133.
Harness identity for external rows: never recorded (issue #462, open, asks exactly this;
maintainer has not answered).

### F11. Integrity-event register (issues/PRs in SWE-bench/experiments; OBSERVED titles/dates)

| # | date | state | what |
|---|---|---|---|
| 6 | 2024-05-21 | closed | FAIL_TO_PASS incorrect entries for `django__django-14608` |
| 52 | 2024-08-12 | closed | `get_results` deletes `run_instance.log` — "by design" |
| 69–72 | 2024-09-01 | closed | gold patch fails / nonexistent P2P test (`astropy-8707`, `-7606`, `django-10097`) — the same three instances edited in the dataset on 2026-08-10 |
| 216 | 2025-05-06 | closed | sb-cli says 46.6 %, `get_results` says 0 % (logs missing) |
| 217 | 2025-05-07 | closed→moved | 42/61 submissions edit test files; ±1–2.6 pp swings; maintainer: "re run the top 1 or 2" |
| 230 | 2025-05-21 | closed | Kodu logs show `test_patch` applied; "removed" (see F7) |
| 242 | 2025-05-29 | closed | Moatless+DeepSeek shown 0 % — maintainer-side regeneration bug |
| 246–254 | 2025-06-02 | closed | series: logs missing / inverted / not following format / report.json missing or empty |
| 284 | 2025-06-28 | closed | evaluation traces for instances not in Verified — "not counted" |
| 301 | 2025-07-27 | closed | duplicated ids in `resolved` (×5) — deduped 2025-08-25 |
| 303 | 2025-08-01 | closed | 16 Verified submissions lack prediction files on S3 — "dig into the original PRs" |
| 323 | 2025-08-29 | closed | TRAE model undisclosed |
| 367 | 2025-11-12 | **open** | non-k/500 percentages — "It's out of 500 … we'll double check" |
| 381 | 2025-12-05 | closed | mini-SWE-agent Verified rows have no logs at the listed path — "download from bash-only/" |
| 417 | 2026-02-19 | **open** | same gold patch: local harness unresolved, sb-cli resolved (`sphinx-8595`) |
| 462 | 2026-07-27 | **open** | which harness version evaluated which submission? |
| 463 / PR 465 | 2026-07-30 / 08-09 | **open** | duplicates in Test results.json inflate 9.29 → 10.51 |
| 466 | 2026-08-15 | **open** | adjacent ranks not statistically separable |

---

## 3. Explicit answers to the lane questions

**Displayed row.** See F1. Name "live-SWE-agent + Claude 4.5 Opus medium (20251101)",
79.20 %, date 2025-12-15, `checked: false`, `os_system: true`, `os_model: false`, logs
and trajs links present (S3), no cost, tags `Model: claude-opus-4-5-20251101`, `Org:
UIUC`, `System: Attempts - 1`.

**Experiments folder / PR.** F2 items 1–4, 10. Metadata, README, results in git; logs,
trajs, preds only on S3 and (unofficially) on the retained PR head ref. PR #388, no
reviews, one maintainer comment.

**Harness version / "checked" semantics.** UNAVAILABLE for the target row: not in
metadata, PR, README, or logs; `eval.sh` matches the 4.x-era generator (DERIVED), which
brackets but does not pin. `checked` = "performed by or directly checked by the team";
target row is unchecked; 6 rows show the badge falsely; 12/30 external checked flags were
set by the submitter's own commit (F8).

**Dataset revision.** Not pinned by any script or doc (OBSERVED). Content changed
2025-02-13 (1 P2P test), 2026-08-10 (2 P2P edits, 2 eval scripts, 4 new columns), plus
representation changes; the current revision changes the target row's re-derived score
79.2 → 79.4 (F2.6, F5).

**Aggregation rule.** `len(resolved)/500`, rounded to 2 dp, missing = fail — for
verified/lite/test/multimodal; hand-typed `info.resolved` for the 47 cross-listed
bash-only rows; list length not set size (F3, F7).

**Retry policy.** pass@1 required, Best@k allowed with a tag, self-attested; multiple
submissions of the same system co-exist (F6). Trajectories are the only evidence and are
not machine-checked.

**Uncertainty.** None; ranks 1–2 tie at 396 with an 18/18 disagreement split (F9).

**Row mutability.** No deletions since the 2024-10 history reset; six results.json
corrections; one "removal" that silently failed; one duplicate-inflated Test row still
live; two bulk rewrites of every metadata file; bucket rename broke old links (F7).

**Manual transitions.** Fork → PR with pasted `get_results` output and four checkboxes →
maintainer merges (squash), uploads artifacts to S3, deletes them from git → later,
by hand, `get_leaderboard.py` → commit `leaderboards.json` in the site repo → GH Pages
build. `checked` is a YAML flag with no linked evidence of the check (F8).

**Independent verification of a claimed resolution.** Yes, at the level "the submitted
log shows the harness-generated `eval.sh` ran and pytest reported these tests PASSED, and
the harness's parser marks the instance resolved under dataset revision X" — I did this
for all 495 logged instances. No, at the level "this log was produced by harness version
V on image digest D": UNAVAILABLE. Nothing binds the log to an execution environment; the
image tag it would have used is a moving `:latest` that moved today (F2.7–9).

---

## 4. What could NOT be established, and where I looked

| Item | Where I looked | Result |
|---|---|---|
| Harness (`swebench`) version / sb-cli-vs-local for the target row | metadata.yaml, README.md, PR #388 body+comments, `test_output.txt` grep, `eval.sh`, `report.json` keys, `.cursor/rules/general.mdc`, checklist.md | UNAVAILABLE. Only bracketed by eval.sh equality with 4.1.0's generator |
| Docker image digest used for evaluation | test_output.txt, report.json, metadata, dataset `image` column (added 2026-08-09, `:latest`), Docker Hub tag list | UNAVAILABLE; `latest` digest changed 2026-08-16 |
| Whether `psf__requests-1142` (patch.diff only, in `no_logs`) was never evaluated or its log lost | PR head commit tree, S3 listing (1,981 objects) | UNAVAILABLE (both places lack it) |
| What the maintainer's "Just verified submission" consisted of | PR #388, README "Result Verification" section, git history of the folder | UNAVAILABLE |
| Whether the 12 submitter-set `checked: true` flags were backed by a maintainer re-run | git log -p on those metadata files, linked PRs (#327, #237, #297) bodies/comments | UNAVAILABLE |
| Origin of the displayed 52.8 % for `20250720_mini-v0.0.0-claude-3-7-sonnet-20250219` | per_instance_details.json (51 true), S3 logs (98 instances), metadata history back to `e56d229` (value present at bash-only split creation 2025-08-25) | UNAVAILABLE / CONFLICTING |
| Origin of 69.6 % for `20260226_mini-v2.0.0_gemini-3-pro-high` | PR #423 body (348/500 asserted), per_instance_details (0/500), S3 report.json (353/500) | CONFLICTING |
| Pre-2024-10-15 history of any row | experiments repo (history reset), README-linked eval-bug doc (404) | UNAVAILABLE |
| Whether the trajectories evidence a single attempt for the target row | not examined (content of trajectories is out of scope for this report; only counts recorded: 500 files) | not attempted |
| Whether the S3 objects for the target row were ever modified after upload | S3 `LastModified` all 2026-01-26T02:10:20Z, ETags match PR-head blobs | no evidence of modification (absence of versioning info; bucket versioning status not queryable anonymously) |

---

## 5. Implications for the central question

**Which of the 10 steps were recoverable here?**

| step | status for the target row | required trust |
|---|---|---|
| 1 display → identity | recoverable (folder name is the join key) | none |
| 2 folder artifacts | recoverable via S3 (anonymous) or PR head ref; not from `main` | that S3/PR-ref content is what was evaluated (byte-matched to each other, not to any run receipt) |
| 3 submission PR | recoverable | submitter's checkboxes |
| 4 harness version | **impossible** (bracketed only) | submitter + maintainer |
| 5 dataset revision | recoverable *for the tested question* only by trying revisions until the number matches; not recorded | none, but re-derivation drifts (79.2 → 79.4) |
| 6 aggregation | recoverable (script) | none |
| 7 retry policy | rule recoverable; compliance **impossible** to check mechanically | submitter |
| 8 uncertainty | absent; derivable from results.json | none |
| 9 row mutability | recoverable since 2024-10-15 only; one silent-failure "removal" | — |
| 10 manual transitions | partially recoverable (merge, S3 upload); the "checked" transition has no evidence | maintainer |

Fully recoverable: 1, 2, 3, 6, 8 (derivable). Trust-the-submitter: 4 (partly), 7, and
the meaning of `checked` for 12 rows. Impossible: image/harness binding (4), pre-reset
history (9), the check itself (10).

**More/less reconstructable than a typical benchmark.** More: per-instance raw logs +
patches are public and byte-stable across two hosts; the aggregate is *re-derived from
raw logs* by the maintainers' script rather than copied from a summary; results.json is a
list of instance ids, so paired comparisons and CIs are computable by anyone (issue #466
did exactly that); the dataset lives in git with a full commit history. Less: no pins
(harness, dataset, image); the archive is *reproducible-in-parsing* but not
*reproducible-in-execution*; a quarter of Verified rows (the bash-only cross-listings)
short-circuit the evidence path entirely; the leaderboard is a hand-committed snapshot
of a hand-run script; several small mistakes (wrong YAML key, truthy string, list vs set,
str.replace on S3 paths) leak straight onto the public page and stay for months. The
repo maintainers are candid and responsive, but the machinery has no invariant checks.

**Is `experiments/` a de facto claim-lineage record?** Yes for *retained trials →
aggregate*: `logs/<id>/{patch.diff,test_output.txt}` → `report.json` → `results.json` →
`%` is a real, re-runnable chain, and `get_results.py` explicitly ignores submitter
`report.json` and re-parses the raw log. What it lacks, in order of how often it bit
during this walk-back:

1. **Instrument pins.** No harness version, dataset revision, image digest, or parser
   version anywhere in the folder; the docs and scripts refer to mutable names
   (`SWE-bench/SWE-bench_Verified`, `:latest`). This is the single largest gap and it is
   cheap to close (three strings in `metadata.yaml`, or a `run_instance.log` that is not
   deleted).
2. **A denominator/membership statement.** "no_generation" and "no_logs" lists exist but
   nothing states the intended denominator (500 vs 499), whether missing means failed or
   excluded, or that the bash-only path uses a different rule.
3. **A binding from row to evidence, and from merged folder to row.** The row carries a
   folder name and S3 prefix; it carries no digest of `results.json`, no count of
   artifacts, no "this row was computed from commit X"; and nothing asserts that every
   merged folder produced a row. So a row can drift (Kodu, Test dupes, gemini-3-pro) or a
   merged 77.6 % submission can be missing (`20251127_openhands_claude-opus-4-5`) without
   any detectable inconsistency on the page.
4. **Evidence for the manual transitions.** `checked: true` and "verified submission" are
   flags/prose with no linked subset run, log, or commit.
5. **Uncertainty and comparability.** None on the page; cross-era comparability is an
   open question (#462) the repo cannot answer.

**On the proposed abstraction (evidence bundle with explicit states + byte identities).**
The evidence here argues both ways, and I think honestly it argues *against* the
per-trial half and *for* a much thinner campaign half:

- Per-trial sealing adds little: SWE-bench already retains the raw log, the patch, and a
  deterministic re-parser; S3 ETag and git blob ids already give byte identity; my
  reconstruction needed none of the bundle machinery. H3/H4 in the eval-evidence research
  map should count this as a data point that native content addressing + a re-parser is
  sufficient for the trial unit *when the raw log is retained*.
- What was missing was not "states" on values that exist but *values that were never
  captured* (harness/image/dataset pins) and *rules that were never written down*
  (denominator, list-vs-set, missing = fail). Explicit `unavailable` labels would have
  named the gaps (H1 supported in the weak sense that the archive does contain asserted
  and conflicting values that the page hides — F4, F8), but naming them does not fill
  them; prospective capture does (H6/E5 direction).
- The campaign half is where the damage was: 47/180 rows with hand-typed numbers,
  three of them contradicted by their own per-instance files, a failed removal, a
  duplicate-inflated row, and a re-derivation that drifts with an unpinned dataset. A
  minimal, machine-checked "included/excluded/denominator/aggregation-rule/instrument-pin"
  record next to `results.json` — plus a consistency check that fails the leaderboard
  build when the row, the results file, and the per-instance records disagree — would
  have caught every defect listed in F4 and F7 except the pre-reset history. That is
  closer to `CAMPAIGN_MINIMUM.md`'s nine questions than to a trial envelope, and it
  belongs in the leaderboard tooling (get_results/get_leaderboard), not in a standalone
  package.

Bottom line for the parent: SWE-bench Verified is the best case I know of for
retrospective per-trial verification and it still cannot bind a log to an execution
instrument, still lets a quarter of its rows bypass the evidence path, and still drifts
under its own scripts. The reconstruction problem the parent named — why *this*
collection became *this* number — is only solved here for the honest, well-formed
submissions and only for the parse-level question. What is needed is pins and a checked
denominator record; digests of trial files are the part that already works.

---

### Appendix A — commands that reproduce the key derived numbers

```
# leaderboard JSON extract
curl -sL https://www.swebench.com/ -o index.html   # then parse <script id="leaderboard-data">
# experiments partial clone + PR head
git clone --filter=blob:none --no-checkout https://github.com/SWE-bench/experiments.git
git fetch --filter=blob:none origin refs/pull/388/head:refs/remotes/pr/388
git sparse-checkout set evaluation/verified/20251215_livesweagent_claude-opus-4-5 analysis
git checkout e67dde4
# datasets at pinned revisions
https://huggingface.co/datasets/princeton-nlp/SWE-bench_Verified/resolve/39bc39abbbbb/data/test-00000-of-00001.parquet
https://huggingface.co/datasets/SWE-bench/SWE-bench_Verified/resolve/03e151cf5560/data/test-00000-of-00001.parquet
# re-derivation: swebench==4.1.0, make_test_spec + get_eval_report over logs/<id>/test_output.txt
# S3 anonymous listing
https://swe-bench-submissions.s3.amazonaws.com/?prefix=verified/20251215_livesweagent_claude-opus-4-5/logs/&max-keys=1000
```

### Appendix B — parquet sha256 by revision (OBSERVED)

```
princeton-nlp 39bc39ab e43d382299697127527b320062f508aefda4f4909188d94af467dc848079ffb3
princeton-nlp a9e03327 d8cf2347ece7e9f553bf8b3fc9df55e25b92cd057c3940e0c6c951a10ed6e31b
princeton-nlp 5201ca8e 56322c2e36cde2e0feea1603af6d89b668bcbd5bdd11be17aff003dea05021ab
princeton-nlp c104f840 a45b1fe4e2f0c8390b2b2938ac83e92ed5979000856808f3679c07812e9e6dcd
SWE-bench    fd80552a 43ed5a3d1d98da36472c1ade65ddd2085d7b4ff694fcaf6a023a07c5c1f32f21
SWE-bench    91aa3ed5 43ed5a3d1d98da36472c1ade65ddd2085d7b4ff694fcaf6a023a07c5c1f32f21  (same bytes)
SWE-bench    b6ee4b82 545d465341c039c18c3838d0facb895e6246206c0b94e7579b0560cbea41bdd8
SWE-bench    aa227074 21962896b4f9f8c6638657036ec0ced05da5005cce99b207858f8eff7989740e
SWE-bench    96dae8db 8bc48e03492818f0807365fb2f071288fbbf2db0b356a77dbe113559b661f6b8
SWE-bench    e33ae570 55c0c6ecfa947da105a9f8a1c3b3684ad4f83375d2510cfdae8e32a4fe9197fc
SWE-bench    03e151cf bb5b123d29ce70107cc0951cf444894241c570a11d76aec452332c65b01e06d8
SWE-bench    78f471bf 030cfd7f2a704c4c0226e7f104c725a3b41230b1d3517f9c915ad7ea5be3fa25
```

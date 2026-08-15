# Terminal-Bench 1 → 2 → 2.1 → 3 / Frontier-Bench: evidence evolution

## Access limitation and source notation

This analysis was produced with **no-web access and no live GitHub access**. It is an
analysis of the checked-out repository and the readable sibling archive, not a claim to
have surveyed today's web. Every factual claim is tagged:

- **[repo-artifact]** — this repository's code, docs, tests, or redacted artifacts.
- **[local-archive]** — a file under `../tbench3-archive`.
- **[model-knowledge, unverifiable]** — contextual memory that could not be checked in
  session. Such claims are not used to support the PR verdict.

The important progression is not simply “more tasks.” Each generation made a different
failure mode decision-relevant, while the record needed to audit that failure arrived
later.

## Generation 1 — Terminal-Bench 1: task plus verifier was not enough

**Locally established facts.** Terminal Wrench identifies 233 tasks in its
`TerminalBench-original` source corpus and includes 36 of those in its reward-hackable
dataset. **[local-archive:
`../tbench3-archive/sources/repos/terminal-wrench/README.md:26-35`]** Its introduction
says the retained trajectories can obtain reward without solving as intended and lists
concrete exploit categories. **[local-archive:
`../tbench3-archive/sources/repos/terminal-wrench/README.md:1-9,52-70`]** These are
properties of the later collected corpus, not proof that every original task or
verifier was weak.

**Failure mode that emerged.** A pass/fail reward can conflate intended completion with
a verifier exploit. Task name plus reward cannot distinguish a valid solve, hollow
implementation, output spoof, or verifier tampering. **[local-archive: same Terminal
Wrench introduction and category table]**

**Provenance record that would have exposed it.** Retain exact task and verifier bytes,
environment isolation/network state, full trajectory, reward-independent checks, and
an item-validity/adjudication record tied to that exact digest. The current project
expresses this need as separate instrument, item-validity, and verifier evidence rather
than treating reward as proof. **[repo-artifact: `docs/VISION.md:57-68`;
`docs/TRUST_MODEL.md:3-25`]**

**What remains unverifiable.** Exact public launch dates, leaderboard behavior, and the
complete TB1 release narrative are **[model-knowledge, unverifiable]** in this session.

## Generation 2 — Terminal-Bench 2: standardized execution exposed unstable validity

**Locally established facts.** Harbor's local README calls Harbor the official harness
for Terminal-Bench 2.0. **[local-archive:
`../tbench3-archive/sources/repos/harbor/README.md:9-30`]** Terminal Wrench records an
89-task TB2 source corpus and 14 included reward-hackable tasks, and warns that TB2 tasks
continued to change as issues were found. **[local-archive:
`../tbench3-archive/sources/repos/terminal-wrench/README.md:9,26-35`]** The “14” is a
selection into that dataset, not a complete prevalence estimate.

**Failure mode that emerged.** Standardizing the harness does not stabilize the
measurement object. Verifier soundness and task bytes can change while a nominal task
label persists; a requested model name also need not identify the backend response.
The repository's six-trial dogfood later observed two task checksums under one nominal
task/revision. **[repo-artifact:
`artifacts/real-comparison-redacted.md:33-47,60-69`]**

**Provenance record that would have exposed it.** Make the content digest primary and
record resolved task package, verifier identity, environment image, harness build,
prompt, requested model, and provider-returned response model. Harbor's current
`lock.json` already records a task digest, resolved configuration, Harbor version and
sometimes commit, but Eval Evidence does not map the job-level lock. **[local-archive:
`../tbench3-archive/sources/repos/harbor/src/harbor/models/job/lock.py:80-83,151-218,421-454`;
repo-artifact: `HarborAdapter` / `HarborAdapter.load()` normalization in `eval_evidence/adapters.py` and matrix (b) negative `lock.json|JobLock` package search]** The remaining standardized
capture ask is recorded in `docs/TBENCH_REVIEW.md` decision 4. **[repo-artifact]**

## Generation 2.1 — maintenance became benchmark identity

**Locally established facts.** The TB3 automation notes explicitly attribute package
pinning repairs for three tasks and bare-`nproc` repairs for two tasks to TB2.1 patches.
**[local-archive:
`../tbench3-archive/sources/repos/terminal-bench-3/TASK_REVIEW_AUTOMATION.md:167-181`]**
It also describes trial-time network fetches as flaky and as a reward-hacking surface.
**[local-archive: same file, lines 167-173]**

**Failure mode that emerged.** Dependency drift, host/resource assumptions, and
trial-time fetch behavior can change solvability or verifier behavior without changing
the human-facing benchmark family name. “TB2.1” is therefore not just a score label; it
must identify exact repaired task, verifier, and runtime states. This inference is
**[local-archive-derived]** from the cited repair record, not a claim about every 2.1
change.

**Provenance record that would have exposed it.** For every attempt, bind task-tree,
verifier, container-image and dependency-lock digests; resolved CPU/resource policy;
network phase policy; harness version; and a supersession link from old to repaired
measurement object. For every published slice, retain the exact digest set and
inclusion policy. The real comparison demonstrates why nominal revision is
insufficient. **[repo-artifact:
`artifacts/real-comparison-redacted.md:39-40,60-69,81-92`]**

## Generation 3 / Frontier-Bench: task production became an evidence-producing system

**Locally established facts.** The checked-out TB3 README says the repository is an
ongoing, work-in-progress construction effort. **[local-archive:
`../tbench3-archive/sources/repos/terminal-bench-3/README.md:23-38,59`]** Its automation
doc describes static checks, Docker/oracle/nop validation, honest agent trials,
adversarial cheat trials, LLM analysis, and two review labels. **[local-archive:
`../tbench3-archive/sources/repos/terminal-bench-3/TASK_REVIEW_AUTOMATION.md:23-38,87-95,205-209,215-283`]**
A local archive framing note records a frozen snapshot of 1,081 PRs, 639 scored tasks,
and 28,801 trials, plus the 125 all-fail decomposition: 78 certified-unsolved
candidates, 14 broken-oracle, 8 infrastructure-limited, 4 exploit-only, and 21
uncertified. **[local-archive:
`../tbench3-archive/docs/session-notes/2026-07-26-ivan-framing-response.md:9-15`]** These
counts are locally recorded research claims, not independently web-verified here.

The same note suggests the parenthetical “Terminal-Bench 3 (now Frontier-Bench).”
**[local-archive: same file, line 15]** Current public naming and continuity are
**[model-knowledge, unverifiable]** because no remote was consulted.

**Failure mode that emerged.** A zero reward now has multiple empirically recorded
causes; task review, controls, adversarial arms, re-evaluation, and human adjudication
are themselves provenance events. Per-trial integrity cannot show which attempts were
included, whether retries or cheat arms were pooled, which exact task state an
adjudication assessed, or whether a regrade superseded an outcome. The repository's
real comparison proves the campaign-unit problem on a smaller cohort: all six bundles
verified while 1/3/2 denominators, checksums, and budgets made the comparison not
comparable. **[repo-artifact:
`artifacts/real-comparison-redacted.md:14-29,39-54,81-92`]**

**Provenance record that would have exposed it.** Seal a job/campaign claim containing
all expected attempt identities and states, retry/exclusion/arm semantics, aggregation
rule and uncertainty, regrade/supersession lineage, and per-trial bundle digests. Bind
item adjudication to task digest, taxonomy version, protocol, reviewers/roles, evidence
references, disagreements, and source snapshot. Harbor already has job-level types and
a lock record, while v0.2 explicitly stops at discovered qualifying trials.
**[repo-artifact: `docs/TBENCH_REVIEW.md:36-41,62-70,87-112`;
`docs/HARBOR_MAPPING.md` (`Layout support and known gaps`); local-archive:
`../tbench3-archive/sources/repos/harbor/src/harbor/models/job/lock.py:209-218`]**

## The cross-generation result

The recurring blind spot is a one-generation provenance lag:

| Generation | Newly visible failure | Record needed at the time |
|---|---|---|
| TB1 | Reward can be obtained without intended completion. | Exact verifier/task bytes, trajectory, controls, adjudication. |
| TB2 | A common harness does not stabilize task/verifier/model identity. | Content-addressed instrument and provider-returned identity. |
| TB2.1 | Repairs and runtime drift are part of benchmark identity. | Immutable release slice plus dependency/image/network/resource lineage. |
| TB3 / Frontier | Claims depend on campaign selection and layered adjudication. | Job claim, complete denominator, regrade lineage, taxonomy-bound evidence. |

That result supports a narrow intervention: decide capture and claim contracts before
run-time facts evaporate, while leaving execution, dashboards, universal scores, and
signer governance to their proper owners. **[repo-artifact: `docs/VISION.md:18-29,57-68`;
`docs/LIFECYCLE.md:8-16,125-136`; `docs/TRUST_MODEL.md:29-43`]**

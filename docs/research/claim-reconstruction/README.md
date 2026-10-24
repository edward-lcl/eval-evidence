# Claim reconstruction study — lane reports and critic audits

Receipts for [`../CLAIM_RECONSTRUCTION.md`](../CLAIM_RECONSTRUCTION.md) (2026-08-16).
Each lane ran independently against the same brief and the same epistemic rules
(OBSERVED / DERIVED / ASSERTED / CONFLICTING / UNAVAILABLE; digest ≠ correctness; no
invented history; negatives kept). Two critics then audited the lanes. The reports are
reproduced here verbatim except that machine-local absolute paths were replaced with
placeholders (`<local-harbor-clone>`, `<local-oracle-runs>`, `<scratchpad>`,
`<submitter-local>`) and values from a private in-house research repository were
replaced with `[in-house value redacted]`. Working downloads referenced as
`<scratchpad>/lanes/*work/` were session-local public artifacts and are not included.

| File | Lane | Scope |
|---|---|---|
| [L1-native-systems.md](L1-native-systems.md) | L1 | Harbor (`a27e9c2`, `origin/main` `f03db62`), Terminal-Bench, harden-v0/Fortify, TB 1.0 → 2.0 → 2.1 → TB3 leaderboard pipeline; concept → location → state → gap table |
| [L2-tb-leaderboard-walkback.md](L2-tb-leaderboard-walkback.md) | L2 | Terminal-Bench 2.0 rank-1 row walk-back; vendor Terminal-Bench numbers; TB 2.1 submission record |
| [L3-swebench-walkback.md](L3-swebench-walkback.md) | L3 | SWE-bench Verified rank-1 row walk-back; `experiments/` repo as a de facto lineage record; integrity events |
| [L4-open-leaderboard-and-paper-table.md](L4-open-leaderboard-and-paper-table.md) | L4 | Hugging Face Open LLM Leaderboard v2 row; SWE-agent paper table cell; HELM contrast |
| (not included) | L5 | In-house paper lineage over a private research repository; summarised in aggregate in the main document only |
| [L6-prior-art.md](L6-prior-art.md) | L6 | PROV, ProvONE, RO-Crate, nanopublications, GRADE, MLflow/W&B/DVC/OpenLineage, OTel GenAI, in-toto/SLSA/Rekor, Inspect/HELM/lm-eval/EEE/MLPerf/ARC/Epoch/HAL; eight questions per candidate |
| [L7-failure-modes.md](L7-failure-modes.md) | L7 | ~35 documented cases by transition; emergent 14-class taxonomy; what would have detected each |
| [L8-adversarial-formulation.md](L8-adversarial-formulation.md) | L8 | Claim classes, missing-edge (replay vs audit) analysis, counterexamples, the eight outcomes, language, placement |
| [C1-completeness-critic.md](C1-completeness-critic.md) | critic | Lane-vs-lane disagreements preserved; 21 receipt groups re-checked (18 exact, 3 minor defects); coverage against the brief; leak scan |
| [C2-adversarial-judge.md](C2-adversarial-judge.md) | critic | Independent verdict on the eight outcomes; the strongest formulation broken against the counterexamples; ranked recommendation and next experiments |

Known defects recorded by C1 and left in place in the lane text (so the audit trail is
honest): L1 §2.6 cites wrong line numbers for `HarborLockInfo` (the class is at
`src/harbor/models/job/lock.py:58-61`); L1 §2.11 declares the TB2.0 "±" UNAVAILABLE where
L2 §2.10 derives it exactly (the site renders `1.96 × stderr`); L1 §3 generalises the TB
2.1 aggregation rule to the 2.0 page, contradicted by L2 on rows with dropped trials; L2
§2.3 says four of six `AgentTimeoutError` trials carry a reward (all six do); L8 F14 says
`response_model` has no native source, which holds for `result.json`/`config.json`/
`lock.json` but not for ATIF steps written by LiteLLM-driven agents (L1 §2.7).

One further correction, found in the 2026-08-16 pre-push review and **not** applied to
the critic text: C2 §2.2 states "0/5 reproduce from a record that states the rule". That
is too strong. SWE-bench's aggregation rule is readable in the maintainers' own
`analysis/get_leaderboard.py`, the HF normalization is documented, and HELM's aggregation
function is pinned — what those three lack is the *population* the rule applies to (which
artifact, which key, which instances count) and any statement of the rule beside the
published number. The main study document states the corrected version; C2's phrasing is
preserved here as the receipt it was.

Redactions applied to C1 and C2 beyond path scrubbing: values, digests, branch names, and
commit counts belonging to the private in-house repository examined by lane L5 are
replaced with `[in-house value redacted]` or generalised. The public argument does not
depend on them.

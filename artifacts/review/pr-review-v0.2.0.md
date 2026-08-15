# PR review: `release/v0.2.0-readiness`

## Verdict

**The two mapping-correctness blockers are resolved in the follow-up implementation;
approve the narrow per-trial prototype, but do not call it current-Harbor or
Terminal-Bench 3/Frontier-Bench ready.** It remains a deterministic, per-trial
retrospective sealer, not a campaign integrity contract. Timeout meaning and
provenance-free generic values now fail honestly, with regression coverage. The
remaining verified gaps are explicit compatibility/adoption blockers rather than an
invitation to expand this episode into a refactor.

This reconciles the prior **ARCHITECT approve-with-observations** and **BUILDER
request-changes** positions. The branch remains honest about G2, has useful dogfood
evidence, and does not implement dashboards/signing. Six of the BUILDER's seven
contested claims survived local verification; claim (d)'s overclaim charge was refuted
because the partial network surface is expressly disclosed, while claim (g) retains a
qualification on the exact `source_trial` wire name. The two surviving correctness
claims, (c) and (e), are now closed by code and tests. See
[`claim-verification-matrix.md`](claim-verification-matrix.md).

## Findings

| Severity | Finding | Evidence and disposition |
|---|---|---|
| **resolved blocker** | `max_wall_time_s` could call a cap the observed wall-time budget and omit Harbor's timeout multiplier. | `_harbor_agent_timeout` now derives `min(base, cap) * multiplier`, preserves components in `extensions.harbor.timeout`, leaves cap-only input unavailable, and keeps the legacy recorded fallback observed without multiplying it again. Covered by `test_harbor_override_only_uses_default_multiplier`, `test_harbor_cap_only_does_not_become_effective_wall_time`, `test_harbor_agent_timeout_uses_cap_and_agent_multiplier`, `test_harbor_agent_timeout_uses_global_multiplier`, and `test_harbor_wall_time_falls_back_to_result_timeout`. Matrix (c). |
| **resolved blocker** | A generic manifest value without provenance was silently upgraded to `observed`. | Generic instrument values and plain claims now default to `operator_asserted`; explicit declarations are preserved. Covered by `test_generic_values_without_provenance_are_operator_asserted`. Matrix (e). |
| **non-blocking for a per-trial prototype; blocking for current-Harbor readiness** | Current Harbor's rich job `lock.json` is ignored. | Model and fields: `../tbench3-archive/sources/repos/harbor/src/harbor/models/job/lock.py:30,80-83,151-164,209-218`; archive inclusion: `../tbench3-archive/sources/repos/harbor/src/harbor/upload/uploader.py:100-108`; no adapter reference. The job-level record needs a reviewed association, not an assumed per-trial join. Matrix (b). |
| **non-blocking for the prototype; blocking for campaign claims** | Discovery has survivorship bias: a trial lacking ATIF is absent rather than incomplete. | `HarborAdapter.required`, `HarborAdapter.detect()`, and `HarborAdapter.discover()` require `agent/trajectory.json` and `result.json` for detection; `docs/TBENCH_REVIEW.md:36-41` already admits no count reconciliation. This violates the product's visible-denominator goal. Matrix (a). |
| **note** | The `network_policy` field name is broader than its deliberately partial contents. | The `network_policy` mapping in `HarborAdapter.load()` marks the `extra_allowed_hosts` and `agent_extra_allowed_hosts` layers `derived` and explicitly notes they are not enforcement proof; `docs/HARBOR_MAPPING.md` (`Instrument fields`: `network_policy`) repeats that disclosure. Harbor's broader baseline/phase surface remains visible at `../tbench3-archive/sources/repos/harbor/src/harbor/models/task/config.py:43-53,126-175`. Matrix (d) therefore refutes the overclaim allegation; a narrower field name is only a clarity option. |
| **non-blocking known gap** | `available_fraction` is a coarse equal-weight count and can be moved by arbitrary generic fields. | `eval_evidence/core.py:126-141`, enforced at `eval_evidence/__main__.py:89-94`; `docs/TBENCH_REVIEW.md:69` already says it is not claim-specific. Do not use it as publication readiness; later replace with named policies. Matrix (f). |
| **non-blocking for declared single-step scope; adoption blocker** | Current multi-step outcomes are not represented, and regrade lineage is absent. | No `step_results`/`source_trial` under `eval_evidence/`; exclusions at `docs/HARBOR_MAPPING.md` (`Layout support and known gaps`: `Multi-step step_results` and `Regraded trials`); current multi-step model at `../tbench3-archive/sources/repos/harbor/src/harbor/models/trial/result.py:60-107`. Matrix (g). The exact current Harbor regrade field name is **unverified**, so this review does not assert a `source_trial` wire format. |
| **non-blocking** | Artifact closure stops at selected references; hashing `artifacts/manifest.json` does not hash each collected file. | `HarborAdapter.load()`'s optional `FileReference("artifacts/manifest.json", "artifact-manifest", False)`; Harbor manifest entries lack content digests at `../tbench3-archive/sources/repos/harbor/src/harbor/models/trial/artifact_manifest.py:6-19`. Document now; require recursive/Merkle closure only when a policy claims collected evidence is sealed. |
| **note** | Canonicalization is deterministic in Python but is not a named cross-language standard. | `eval_evidence/core.py:48-55` uses `json.dumps`. Defer RFC 8785/JCS until an independent native emitter is being frozen; do not imply byte interoperability before then. |
| **note** | The item-validity input cannot carry the full TB3 taxonomy protocol. | `eval_evidence/schemas/eval-evidence-run-v0.1.schema.json:66-85` leaves `claimInput` unconstrained and permits `adjudicated` without required taxonomy, protocol, reviewers, or evidence refs. That is acceptable only while the schema is described as a carrier, not a certification contract. |

## Findings retained from the approve position

- G2 is honestly `unmet`, despite a real local pass, because CI lacks the fixture:
  `docs/READINESS.md:8-22` and `artifacts/g2-blocker.md:1-27`.
- The real comparison refuses to rank models after finding checksum, denominator, and
  budget drift: `artifacts/real-comparison-redacted.md:39-54,81-92`.
- Token/cache semantics are explicitly documented in `docs/HARBOR_MAPPING.md` (`Other review-sensitive mappings`).
- Multi-step, regrade, and denominator exclusions are visible in
  `docs/HARBOR_MAPPING.md` (`Layout support and known gaps`: `Multi-step step_results`, `Regraded trials`, and `Job stats/retries/cancellations`); visibility does not make them supported.

## Scope of requested changes

This follow-up lands the maintainer-facing capture decision together with the two
semantic corrections and regression fixtures. A narrowly described single-step
release can merge with those blockers closed; G2 remains unmet, and the compatibility
statement must not imply current-Harbor or campaign completeness.

## Unverified/model-knowledge handling

No blocking finding rests on model knowledge. Claims about remote PR state, current
websites, industry adoption, Frontier-Bench's present release cadence, or history not
captured by local sources are **unverified model-knowledge** in this no-web session and
are deliberately excluded from the verdict.

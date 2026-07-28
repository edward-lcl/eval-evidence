# Eval Evidence owner dogfood report — TEMPLATE

Copy this file to a dated private working report. Publish only a redacted version
approved by the artifact owner. Do not paste prompts, trajectories, credentials,
benchmark contents, private paths, or stable private run/task identifiers.

## 1. Candidate and environment

| Item | Recorded value |
|---|---|
| Date/time (UTC) | TODO |
| Operator/reviewer | TODO |
| Git commit or release tag | TODO |
| Wheel filename | TODO |
| Wheel SHA-256 | TODO |
| Sdist filename/SHA-256 | TODO |
| `eval-evidence --version` | TODO |
| Python version | TODO |
| OS/architecture | TODO |
| Install source (wheel/sdist/tag) | TODO |
| Clean environment confirmed | yes/no |

## 2. Command ledger

Record the exact command, expected exit, actual exit, report location, and any
undocumented correction. Do not mark a corrected command as a clean pass.

| Step | Command (redacted) | Expected | Actual | Evidence file | Undocumented correction? |
|---|---|---:|---:|---|---|
| Install | TODO | 0 | TODO | TODO | TODO |
| Version | TODO | 0 | TODO | TODO | TODO |
| Generic demo/check/bundle/verify | TODO | 0 | TODO | TODO | TODO |
| Harbor demo/check/bundle/verify | TODO | 0 | TODO | TODO | TODO |
| Referenced-file tamper | TODO | 1 | TODO | TODO | TODO |
| Bundle-claim tamper | TODO | 1 | TODO | TODO | TODO |
| Genuine Harbor check | TODO | 0 | TODO | TODO | TODO |
| Genuine Harbor inspect | TODO | 0 | TODO | TODO | TODO |
| Genuine Harbor bundle/verify | TODO | 0 | TODO | TODO | TODO |

## 3. Genuine Harbor G2 evidence

| Check | Result | Redacted evidence pointer |
|---|---|---|
| Source confirmed as a genuine Harbor job | pass/fail | TODO |
| Data-owner approval and redaction constraints recorded | pass/fail | TODO |
| At least two trials discovered | pass/fail | TODO |
| At least one optional file absent | pass/fail | TODO |
| All generated bundles schema/digest valid | pass/fail | TODO |
| All preserved referenced files matched | pass/fail | TODO |
| Coverage/unavailable fields spot-checked | pass/fail | TODO |
| Cache-token fallback spot-checked | pass/fail | TODO |
| Exception/termination mapping spot-checked | pass/fail | TODO |
| ATIF `steps` shape/count spot-checked | pass/fail | TODO |
| Sanitized or secure fixture runs in regular CI without skip | pass/fail | TODO |

Mapping rows changed from `inferred` to `real-trial`:

- TODO (or `none`)

Corrections requested from Harbor/Terminal-Bench:

- TODO (or `none`)

## 4. Paired surprising-result review

State the claim without treating an expected model ordering as ground truth.

**Claim under review:** TODO

| Evidence dimension | Model A | Model B | Matched? | Evidence pointer / limitation |
|---|---|---|---|---|
| Run-specific model identity | TODO | TODO | yes/no/unknown | TODO |
| Provider-returned `response_model` | TODO | TODO | yes/no/unknown | TODO |
| Task ID/revision/checksum | TODO | TODO | yes/no/unknown | TODO |
| Attempted/failed/timed-out/excluded trials | TODO | TODO | yes/no/unknown | TODO |
| Agent name/version/binary | TODO | TODO | yes/no/unknown | TODO |
| Harness version/commit | TODO | TODO | yes/no/unknown | TODO |
| Tools and network configuration | TODO | TODO | yes/no/unknown | TODO |
| Turn/time/thinking budgets | TODO | TODO | yes/no/unknown | TODO |
| Sampling parameters | TODO | TODO | yes/no/unknown | TODO |
| System-prompt hash/policy profile | TODO | TODO | yes/no/unknown | TODO |
| Environment image digest | TODO | TODO | yes/no/unknown | TODO |
| Verifier digest/evidence | TODO | TODO | yes/no/unknown | TODO |
| Bundle and reference verification | TODO | TODO | yes/no/unknown | TODO |
| Compatibility warnings/unavailable-heavy | TODO | TODO | yes/no/unknown | TODO |
| Per-task repetitions/variance (external analysis) | TODO | TODO | yes/no/unknown | TODO |

### Classification

Select exactly one current conclusion:

- [ ] **Integrity failure** — quarantine/recover the result.
- [ ] **Not comparable** — re-run under matched conditions or qualify the claim.
- [ ] **Inconclusive evidence gap** — request missing run-time evidence.
- [ ] **Not falsified** — proceed to task validity, verifier construct, exclusions,
      contamination, and statistical review.

**Reason, with exact evidence pointers:** TODO

**What this conclusion does not prove:** TODO

## 5. Fresh-user comprehension

| Failure shown to a fresh user | Did they identify cause? | Did they identify next action? | Documentation issue |
|---|---|---|---|
| No run discovered | yes/no | yes/no | TODO |
| Malformed/truncated JSON | yes/no | yes/no | TODO |
| Missing required file | yes/no | yes/no | TODO |
| Referenced file changed | yes/no | yes/no | TODO |
| Bundle digest mismatch | yes/no | yes/no | TODO |
| Coverage policy missed | yes/no | yes/no | TODO |
| Unknown Harbor schema warning | yes/no | yes/no | TODO |

## 6. Final decision

- [ ] Ready to show Terminal-Bench (all sharing requirements in `READINESS.md` met).
- [ ] Not ready; blockers listed below.
- [ ] Ready only for a private mapping review, with limitations stated.

**Blockers:** TODO

- **Owner:** TODO
- **Second-person reviewer:** TODO
- **Date:** TODO

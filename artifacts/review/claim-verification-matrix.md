# Contested-claim verification matrix

All commands are relative to the `eval-evidence` repository root. Status applies to the
precise claim in REQ-5; qualifications prevent stronger claims than the local code
supports.

## Claim (a) — non-ATIF trials are silently undiscovered

**Status: confirmed.** `HarborAdapter.required` includes `agent/trajectory.json`,
`HarborAdapter.detect()` requires every member, and `HarborAdapter.discover()` retains
only parent directories containing `result.json` that pass `detect()`. Thus a directory
with `result.json` but no trajectory is omitted rather than represented as incomplete.
The limitation is also admitted in `docs/HARBOR_MAPPING.md` (**Layout support and
known gaps**: **Trial without `agent/trajectory.json`**).

```bash
grep -nE 'class HarborAdapter|required =|def detect|def discover|rglob\("result.json"\)' eval_evidence/adapters.py
```

## Claim (b) — current Harbor has `lock.json`, and the adapter does not read it

**Status: confirmed.** Harbor defines `LOCK_FILENAME = "lock.json"`,
`HarborLockInfo`, `TrialLock`, and `JobLock` at
`../tbench3-archive/sources/repos/harbor/src/harbor/models/job/lock.py:30,80-83,151-164,209-218`.
The job archive includes it at
`../tbench3-archive/sources/repos/harbor/src/harbor/upload/uploader.py:100-108`.
There is no `lock.json` or `JobLock` reference under `eval_evidence/`. Qualification:
this is a job-level record, `TrialLock` has no obvious trial-name key, and support must
not imply a trivial per-attempt join.

```bash
grep -nE 'LOCK_FILENAME|class HarborLockInfo|class TrialLock|class JobLock' ../tbench3-archive/sources/repos/harbor/src/harbor/models/job/lock.py
grep -n 'lock.json' ../tbench3-archive/sources/repos/harbor/src/harbor/upload/uploader.py
grep -RInE 'lock\.json|JobLock' eval_evidence || true
```

## Claim (c) — `max_wall_time_s` ignores current timeout cap/multiplier semantics

**Status: confirmed, then resolved.** The prior adapter selected
`override_timeout_sec`, then `max_timeout_sec`, then result timeout and labeled the
selected value observed. `_harbor_agent_timeout` now mirrors Harbor's
`min(base_sec, max_sec) * resolved_multiplier` formula when the trial config contains a
base, records the components in `extensions.harbor.timeout`, leaves cap-only input
unavailable, and does not reapply a multiplier to the legacy recorded result fallback.
The override-only default, cap-only, agent-multiplier, global-multiplier, and
legacy-fallback cases have named regression tests in `tests/test_product.py`.

```bash
grep -nE '_harbor_agent_timeout|override_timeout_sec|"max_wall_time_s"|timeout_components' eval_evidence/adapters.py
grep -nE '_resolve_timeout_sec|resolved_multiplier|return min|_compute_agent_timeout_sec|agent_timeout_multiplier' ../tbench3-archive/sources/repos/harbor/src/harbor/trial/trial.py
python3 -m unittest tests.test_product.ProductTests.test_harbor_override_only_uses_default_multiplier tests.test_product.ProductTests.test_harbor_cap_only_does_not_become_effective_wall_time tests.test_product.ProductTests.test_harbor_agent_timeout_uses_cap_and_agent_multiplier tests.test_product.ProductTests.test_harbor_agent_timeout_uses_global_multiplier tests.test_product.ProductTests.test_harbor_wall_time_falls_back_to_result_timeout
```

## Claim (d) — the `network_policy` mapping overclaims what it establishes

**Status: refuted.** The normalized value does contain only environment and agent
`extra_allowed_hosts`, but it is emitted as `derived`, not `observed`, and carries the
explicit note “Configured layers are not proof of effective enforcement” in
`HarborAdapter.load()`'s `network_policy` mapping. The mapping review makes the same
limitation explicit (`docs/HARBOR_MAPPING.md`: `Instrument fields`, `network_policy`). Current Harbor's broader
`network_mode`, `allowed_hosts`, baseline-resolution, and phase-override surface
(`../tbench3-archive/sources/repos/harbor/src/harbor/models/task/config.py:43-53,126-175`)
shows genuine incompleteness, but that incompleteness is disclosed rather than
misrepresented. The broad field name remains a naming concern, not the asserted
integrity overclaim.

```bash
grep -nE '"network_policy"|extra_allowed_hosts|agent_extra_allowed_hosts|Configured layers are not proof' eval_evidence/adapters.py
grep -nE 'class NetworkPolicy|class PhaseNetworkPolicyConfig|class BaselineNetworkPolicyConfig|network_mode|allowed_hosts' ../tbench3-archive/sources/repos/harbor/src/harbor/models/task/config.py
```

## Claim (e) — generic values without provenance default to observed

**Status: confirmed, then resolved.** Missing per-field provenance and plain
item-validity/verifier claims previously defaulted to observation. Both paths now call
`operator_asserted`; an explicit provenance object still preserves the emitter's
status and source. `test_generic_values_without_provenance_are_operator_asserted`
covers undeclared instrument and plain claim values plus an explicit observed value.

```bash
grep -nE 'def _evidence_claim|return operator_asserted|declaration is None|instrument\[name\] = operator_asserted' eval_evidence/adapters.py
python3 -m unittest tests.test_product.ProductTests.test_generic_values_without_provenance_are_operator_asserted
```

## Claim (f) — `available_fraction` equally counts every non-unavailable field

**Status: confirmed.** `_instrument_manifest` sums all fields whose status is not
`unavailable` and divides by all serialized fields (`eval_evidence/core.py:126-141`).
The CLI can enforce that fraction with `--min-coverage`
(`eval_evidence/__main__.py:89-94,310`). This confirms equal weighting and the ability
of generic extra fields to affect the fraction; it does not establish malicious use.

```bash
grep -nE 'available =|available_fraction|len\(serialized\)' eval_evidence/core.py
grep -nE 'min-coverage|available_fraction' eval_evidence/__main__.py
```

## Claim (g) — `step_results` and `source_trial` do not appear in Eval Evidence

**Status: confirmed.** The package search returns no match, while the gap is documented
at `docs/HARBOR_MAPPING.md` (`Layout support and known gaps`: `Multi-step step_results` and `Regraded trials`). Current local Harbor does define `step_results` at
`../tbench3-archive/sources/repos/harbor/src/harbor/models/trial/result.py:60-88`.
Qualification: no current Harbor result field literally named `source_trial` was found,
so the stronger claim that this exact regrade wire field exists in current Harbor is
**unverifiable**; only Eval Evidence's absence and stated regrade-lineage gap are
confirmed.

```bash
grep -RInE 'step_results|source_trial' eval_evidence || true
grep -nE 'Multi-step|Regraded|Job stats' docs/HARBOR_MAPPING.md
grep -nE 'class StepResult|step_results' ../tbench3-archive/sources/repos/harbor/src/harbor/models/trial/result.py
```

## Summary

| Claim | Result | Consequence for review |
|---|---|---|
| (a) discovery survivorship | confirmed | Current output can hide incomplete/non-ATIF attempts. |
| (b) job `lock.json` ignored | confirmed | Existing current-Harbor provenance is not mapped. |
| (c) timeout semantics | resolved | Effective, legacy-recorded, and unresolved cases are now distinct and tested. |
| (d) network completeness | refuted | Scope is disclosed in code and mapping; incompleteness is a documented gap, not an overclaim. |
| (e) generic provenance default | resolved | Undeclared operator input is no longer upgraded to observation. |
| (f) equal coverage fraction | confirmed | Coverage is coarse, not publication readiness. |
| (g) multi-step/regrade names absent | confirmed, qualified | Multi-step is current; exact `source_trial` wire claim is unverified. |

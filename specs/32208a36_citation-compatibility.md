# Plan: repair review citations and classify provenance compatibility

## Scope and guardrails

Update only the maintainer-facing review packet and the requested compatibility/release notes:

- `artifacts/review/pr-review-v0.2.0.md`
- `artifacts/review/claim-verification-matrix.md`
- `artifacts/review/blind-spot-register.md`
- `artifacts/review/tbench-evolution-analysis.md`
- `artifacts/review/tb3-needs-decision.md`
- `artifacts/review/gate-report.md`
- `docs/COMPATIBILITY.md`
- `CHANGELOG.md`

Do **not** change `eval_evidence/adapters.py`, its timeout or `operator_asserted` implementation, tests, schemas, wire IDs, fixture publication, `lock.json` integration, discovery behavior, campaigns, or any unrelated pre-existing worktree changes. Preserve the frozen five-item TB3 decision; correct its stale source location through an explicit erratum, not an unmarked edit of the decision text.

## Implementation steps

1. **Replace stale adapter line citations with durable source evidence across the active review packet.**
   - In `pr-review-v0.2.0.md`, revise the discovery, network-policy, and artifact-closure findings so they identify the intended Harbor code rather than the now-stale `adapters.py` line ranges:
     - discovery: `HarborAdapter.required`, `HarborAdapter.detect()`, and `HarborAdapter.discover()` (the required ATIF trajectory and `result.json` scan);
     - network policy: the `network_policy` mapping in `HarborAdapter.load()`, including `extra_allowed_hosts`, `agent_extra_allowed_hosts`, and its non-enforcement note;
     - artifact closure: `HarborAdapter.load()`'s optional `FileReference("artifacts/manifest.json", "artifact-manifest", False)`.
   - In `claim-verification-matrix.md`, make claims (a) and (d) use those named symbols/patterns instead of stale numeric ranges. Keep the existing executable `grep` evidence, but narrow or supplement it with stable patterns that demonstrate each claim (Harbor class/required/detect/discover/result scan for discovery; `network_policy`, both host fields, and the enforcement-disclaimer text for network policy). Retain the existing timeout and generic-provenance named checks unchanged.
   - In `blind-spot-register.md`, point ranks 3, 9, and 10 to the corrected matrix evidence or the same named Harbor mapping/reference patterns; do not alter their rankings, dispositions, triggers, or conclusions.
   - In `tbench-evolution-analysis.md`, replace the broad stale `adapters.py:201-376` citation in the Generation 2 `lock.json` discussion with the precise absence evidence: Harbor adapter/load normalization plus the matrix's negative `lock.json|JobLock` package search. Preserve the local-archive claim and all no-web qualifications.

2. **Publish a non-silent erratum for the frozen TB3 needs decision.**
   - Leave the five numbered needs, their ordering, justification, non-goals, and frozen-decision framing intact in `tb3-needs-decision.md`.
   - Append a clearly dated/labeled `Erratum` section stating that item 4's former numeric `adapters.py` citation was stale after the timeout/provenance follow-up shifted the file, and identifying the corrected discovery evidence by `HarborAdapter.required`, `detect()`, and `discover()`/the named matrix check.
   - State explicitly that the erratum repairs only the source locator, not the item-4 requirement, its priority, scope, or the frozen five-item decision. If retaining the historical numeric citation in the frozen text, mark it as superseded from the erratum so it cannot be mistaken for a current anchor.

3. **Make the gate report accurately separate what was checked.**
   - In `gate-report.md`, rename/reframe the current per-citation `test -f` section as path-existence verification and state that it proves only that a cited file is present, not that an individual line range or semantic anchor is current.
   - Replace the inaccurate blanket statement that line citations were reproduced with a distinct line-anchor/named-pattern verification section. Record the actual stable checks used for Harbor discovery, optional artifact-manifest reference, and partial network-policy mapping, and point readers to the matrix for their commands/results.
   - Preserve the existing heading-resolution results as exact-heading checks, retain the 34-test/one-expected-skip/G2-unmet result, and do not turn the report into a claim that unavailable external sources or remote/web facts were verified.

4. **Classify the generic-manifest default correction under the compatibility policy.**
   - In `docs/COMPATIBILITY.md` near the wire-breaking rules, add a narrowly defined pre-adoption exception/classification: the generic `eval-run.json` provenance-default correction from implicit `observed` to `operator_asserted` is a **pre-adoption breaking evidence-status semantic correction**. Explain that it changes emitted evidence status, serialized bundle bytes, and pinned digests for provenance-free input, but does not change the `eval-evidence.run/v0.1`, `instrument/v0.1`, or `bundle/v0.1` wire identifiers.
   - Make clear that this classification is limited to the unreleased/pre-adoption candidate correction, requires explicit compatibility and release-note disclosure, and must not be treated as a general exemption from the policy that normally requires a new wire version for evidence-status semantic changes. Do not alter any schema or wire version.
   - In `CHANGELOG.md`'s existing 0.2.0 generic-provenance bullet, add the same explicit classification and cross-reference to `docs/COMPATIBILITY.md`: it is breaking for prior candidate provenance-free outputs/expectations and digest pins, while wire versions remain unchanged. Keep the behavioral description and coverage-fraction statement accurate.

## Verification

1. Run `git diff --check`.
2. Run `python3 -m unittest discover -s tests -v`; expect the established suite result (34 tests, with only `test_real_harbor_archive_when_supplied` skipped when `EVAL_EVIDENCE_REAL_HARBOR_ROOT` is absent).
3. Re-run the review-packet evidence commands from the matrix, including stable Harbor patterns for:
   - `class HarborAdapter`, `required = ("result.json", "config.json", "agent/trajectory.json")`, `detect`, `discover`, and `rglob("result.json")`;
   - `"network_policy"`, both `extra_allowed_hosts` fields, and `Configured layers are not proof of effective enforcement`;
   - `FileReference("artifacts/manifest.json", "artifact-manifest", False)`;
   - the intentional negative `grep -RInE 'lock\.json|JobLock' eval_evidence || true`.
4. Review every `adapters.py` citation in the six requested review files. Each active citation must now resolve via a current named symbol/pattern or the matrix command; the frozen document's historical numeric locator, if present, must be explicitly superseded by its erratum rather than presented as live evidence.
5. Confirm the gate report labels `test -f` as path-existence-only, separately documents heading and named-pattern/anchor checks, and does not claim path checks validate line anchors.
6. Confirm `docs/COMPATIBILITY.md` and `CHANGELOG.md` both contain the exact pre-adoption-breaking classification, the `observed` → `operator_asserted` semantic effect, digest impact, and explicit no-wire-version-change statement. Inspect the final diff to ensure no out-of-scope implementation, fixture, manifest, or unrelated-worktree changes were made.

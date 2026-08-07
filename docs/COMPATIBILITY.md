# Compatibility and support policy

Eval Evidence has separate package and wire-contract versions. A package release may
add adapter recognition or fix diagnostics without changing any wire version.

## Wire contracts

The current contracts are `eval-evidence.run/v0.1`,
`eval-evidence.instrument/v0.1`, and `eval-evidence.bundle/v0.1`. Breaking changes
include removing or renaming a field, changing a required field or allowed type,
changing evidence-status semantics, changing canonical digest scope, or changing the
contract-level meaning of a normalized field. Adapter source corrections, compatibility
recognition, and safer redaction that preserve that meaning are package-level changes;
they are documented and may change deterministic bundle bytes. Additive optional data
is non-breaking only when older readers can safely ignore it.

### Pre-adoption semantic correction classification (0.2.0 candidate)

The generic `eval-run.json` provenance-default correction (shifting unannotated instrument
values and plain claims from implicit `observed` to `operator_asserted`) is explicitly
classified as a **pre-adoption breaking evidence-status semantic correction**. This change
alters emitted evidence status, serialized bundle bytes, and pinned digests for
provenance-free input. Because it corrects an unreleased candidate defect before public
adoption, it is released in 0.2.0 without bumping the `eval-evidence.run/v0.1`,
`eval-evidence.instrument/v0.1`, or `eval-evidence.bundle/v0.1` wire identifiers.

This classification is strictly limited to this pre-adoption release candidate. It
requires explicit release-note and compatibility disclosure and must not be treated as a
general exemption from the policy requiring a new wire version for post-adoption
evidence-status semantic changes.

The project will keep verification support for v0.1 bundles for at least 12 months
after a successor bundle contract is released. A planned removal receives at least 90
days' notice in `CHANGELOG.md` and the README. Security fixes may reject inputs that
were previously accepted when continued acceptance would violate the documented trust
boundary.

Compatibility metadata belongs in namespaced `extensions`; it does not by itself
change a wire contract. Detailed version-bump ownership is in `ADAPTERS.md`.

## Runtime support

CI covers CPython 3.11, 3.12, 3.13, and 3.14 on the current default operating-system
runner. Distribution dogfood covers Linux, macOS, and Windows. Support for a Python
minor ends no earlier than that version's upstream security support, with notice in the
changelog.

There is no fixed release cadence. Releases are cut for reviewed compatibility fixes,
security fixes, or coherent feature sets; release notes must identify schema and
adapter effects.

## Scale bounds for v0.1

The supported operating envelope is at most 10,000 discovered runs per archive, 50 MiB
per JSON document, and 10 GiB per referenced file. These are support bounds, **not
enforced security limits**. `--max-runs` limits checks after discovery and therefore
does not protect directory traversal from an adversarially large tree. Run the tool
with operating-system resource limits for untrusted archives.

A local 2026-07-28 measurement discovered 8,633 genuine Harbor runs in 5.248 seconds
with 44,761,088 bytes peak resident memory on CPython 3.14.5/macOS arm64. The redacted
source-checkout record is `artifacts/scale-measurement.txt`; it is not shipped in the
distribution and is a single-machine observation, not a latency guarantee. Inputs above
the bounds are best-effort and may exhaust time, memory, or I/O, as recorded in
`TRUST_MODEL.md`.

## Distribution status

While pull request #2 is open, the README intentionally installs the 0.2.0 candidate
from `release/v0.2.0-readiness`; `main` and the older `v0.1.0` tag lack the readiness
features. After review, pin the accepted commit or validated `v0.2.0` tag. The tag
becomes authoritative until the PyPI trusted publisher and project page are confirmed. Do not claim `pip install eval-evidence` availability based only
on the presence of the publishing workflow.

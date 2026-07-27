# Eval Evidence bundle v0.1

The canonical output is UTF-8 JSON serialized with sorted keys, no insignificant
whitespace, no NaN values, and a trailing newline when written by the CLI.

## Digest

`bundle_digest.value` is SHA-256 over the canonical bundle **before** the
`bundle_digest` member is added. It proves serialized-byte identity only.

## Top-level sections

- `source`: adapter, source format, run/task identity, task revision.
- `inputs`: run-relative file references with role, required/present state, byte size,
  and SHA-256. Paths may not be absolute, contain `..`, or escape through symlinks.
- `instrument_manifest`: field-level claims with `value`, `status`, `source`, optional
  `note`, and computed coverage.
- `execution`: timestamps and token/cost metrics.
- `outcome`: reward, other scores, and termination reason.
- `item_validity`: reported/adjudicated claims or an explicit unavailable record.
- `verifier_evidence`: verifier claims or an explicit unavailable record.
- `attestation`: content-digest-only in v0.1; signature is null.
- `extensions`: namespaced integration data that does not alter core semantics.

## Provenance statuses

`observed`, `derived`, `operator_asserted`, `provider_asserted`, and `unavailable` are
not interchangeable. Adapters must not upgrade assertions to observations. A transport
mapping must preserve unavailable state.

## Compatibility

The wire contract is `eval-evidence.bundle/v0.1`. Additive integration data belongs in
`extensions`. A breaking core change requires a new wire version and migration guide.
The schema `$id` is the document identity, not the wire-version value.

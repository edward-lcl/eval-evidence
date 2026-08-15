# Minimal campaign evidence question set

This is an experimental worksheet, not a wire format.

For one reported aggregate, a reviewer must be able to answer:

1. Which attempts were expected from the locked job configuration?
2. Which attempts reached pending, running, completed, errored, cancelled, or retried
   states?
3. Which retained trial corresponds to each expected attempt?
4. Which attempts were included in the reported claim?
5. Which were excluded, by whom or what policy, and why?
6. Which attempts supersede or regrade earlier attempts?
7. What named and versioned aggregation transformed the included attempts?
8. What missing-data and uncertainty policy was applied?
9. For a comparison, which instrument fields match and which unresolved differences
   are material to the claim?

The reconstruction experiment should answer these questions using current Harbor
`config.json`, `result.json`, `lock.json`, and trial directories before any new schema
is proposed. An answer of "not retrospectively recoverable" is a valid and important
result.

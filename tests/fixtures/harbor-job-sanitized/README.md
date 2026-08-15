# Sanitized Harbor structural fixture

This fixture preserves the directory and JSON-key structure observed in two genuine
Harbor trials from the frozen local archive identified by snapshot
`3c5be84efd707da8`. It contains no copied task text, prompt text, response text,
trajectory content, credentials, private paths, benchmark identifiers, or measured
scores. Every scalar value was replaced, timestamps and UUIDs are synthetic, steps
were reduced to inert placeholders, and filenames outside the adapter's structural
surface were omitted.

The `conflict-error` trial was then adversarially modified so retained model, agent,
and token sources disagree. This modification is synthetic and exists to falsify
silent precedence. The `completed` trial omits optional verifier/artifact outputs and
Harbor default-valued list keys, matching the `exclude_defaults=True` persistence
shape used by current Harbor.

This fixture establishes reproducible structural CI coverage. It does not establish
that the synthetic values are representative, that private source trials may be
redistributed, or that every Harbor version/layout is supported.

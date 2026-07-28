# Adapter guide

Adapters convert evaluator-specific run artifacts into `NormalizedRun`; bundle hashing,
schema validation, and path enforcement remain centralized.

## No-code integration

Prefer `eval-run.json` when possible. Its schema is packaged at
`eval_evidence/schemas/eval-evidence-run-v0.1.schema.json`. This is the stable
framework-neutral input contract.

## Python adapter contract

An adapter provides:

```python
class RunAdapter(Protocol):
    name: str
    def detect(path: Path) -> int: ...       # 0 means unsupported
    def discover(path: Path) -> list[Path]: ...
    def load(path: Path) -> NormalizedRun: ...
```

Rules:

1. Detection must be deterministic and side-effect free.
2. `load` must not execute models, verifiers, shell commands, or network requests.
3. Every referenced path must be run-relative; central bundle construction rejects
   traversal and symlink escape.
4. Preserve provenance: observed, derived, operator/provider asserted, unavailable.
5. Missing item-validity or reward-independent verifier evidence remains unavailable.
6. Harness-specific data belongs under a namespaced `extensions` key.

## Built-in adapters

- `generic`: confidence 100 when `eval-run.json` exists.
- `harbor`: confidence 80 for the Harbor result/config/ATIF trajectory shape. Its
  field-by-field review surface is [`HARBOR_MAPPING.md`](HARBOR_MAPPING.md).

Highest-confidence detection wins. Equal-confidence ambiguity fails closed. A future
plugin entry-point mechanism should be added only after a third evaluator proves the
in-process adapter contract; v0.1 intentionally avoids arbitrary plugin loading.

## Harness release compatibility

Adapters ignore unknown source fields: retaining a new field must not cause an older
reader to fail. A missing or unknown Harbor trajectory `schema_version` is different:
it is preserved under `extensions.harbor.adapter_compat` and surfaced by `check` as a
compatibility warning. The warning does not change bundle validity or the command's
exit code. The Harbor adapter recognizes `ATIF-v1.5`, `ATIF-v1.6`, and
`ATIF-v1.7` for the root agent, steps, and final-metrics fields it reads. This is not a
claim that Eval Evidence validates the complete ATIF document; Harbor owns that
validation.

Wire-contract versioning follows these rules:

- changing generic `eval-run.json` keys, required values, or their meaning moves
  `eval-evidence.run/v0.1`;
- changing instrument field shape, evidence statuses, or field meaning moves
  `eval-evidence.instrument/v0.1`;
- changing bundle shape, canonical digest scope, or the contract-level meaning of a
  normalized field moves `eval-evidence.bundle/v0.1`.

Source-harness recognition, fallback corrections, and safer adapter redaction that
preserve the normalized field's contract-level meaning are tool compatibility updates.
They are recorded in the package changelog and deterministic golden tests because they
can change bundle bytes. A mapping change that changes what a normalized field means
requires the applicable wire `schema_version` bump; ordinary run-to-run value
or source-selection differences do not. See
[`COMPATIBILITY.md`](COMPATIBILITY.md) for support and deprecation policy.

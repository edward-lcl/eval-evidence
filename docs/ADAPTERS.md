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
- `harbor`: confidence 80 for the Harbor result/config/ATIF trajectory shape.

Highest-confidence detection wins. Equal-confidence ambiguity fails closed. A future
plugin entry-point mechanism should be added only after a third evaluator proves the
in-process adapter contract; v0.1 intentionally avoids arbitrary plugin loading.

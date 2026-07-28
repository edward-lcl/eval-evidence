# Dogfood and real-Harbor validation

This is the release-evidence protocol. For the operator-facing sequence—from a clean
install through application integration and a surprising model-result comparison—use
[`OWNER_WALKTHROUGH.md`](OWNER_WALKTHROUGH.md) alongside it.

## Distribution smoke and tamper matrix

Build and audit the artifacts, install the wheel into a clean environment, then run the
same script CI uses:

```bash
python -m build --wheel --sdist --outdir /tmp/ee-dist
python scripts/audit_distribution.py /tmp/ee-dist
python -m venv /tmp/ee-venv
/tmp/ee-venv/bin/python -m pip install /tmp/ee-dist/*.whl
work="$(mktemp -d)"
# The script requires an empty path, so use a child of mktemp's directory.
bash scripts/dogfood.sh /tmp/ee-venv/bin/python "$work/run"
```

On Windows, pass the venv's `Scripts/python.exe`. The script executes the complete
`demo` → `check` → `bundle` → `verify --run-root` sequence for generic and Harbor
inputs. It then checks both negative cases:

1. change bytes in `generic/outputs/scores.json`; verification exits 1 and names that
   reference;
2. edit a claim in the Harbor bundle without recomputing its digest; verification exits
   1 with `Bundle digest mismatch`.

The generated `reference-tamper.json` and `bundle-tamper.json` are the machine-readable
transcript. CI regenerates them; they are not release artifacts.

## G2 genuine Harbor protocol

A genuine Terminal-Bench/Harbor job is not included in this repository. Obtain a
redacted job archive with at least two trials and at least one absent optional output.
Do not copy benchmark data, prompts, trajectories, or credentials into this repo.

```bash
export EVAL_EVIDENCE_REAL_HARBOR_ROOT=/secure/redacted-harbor-job
export EVAL_EVIDENCE_REAL_HARBOR_TRANSCRIPT=/tmp/harbor-readiness.json
python -m unittest \
  tests.test_readiness.ReadinessTests.test_real_harbor_archive_when_supplied -v
eval-evidence check "$EVAL_EVIDENCE_REAL_HARBOR_ROOT" \
  | tee /tmp/harbor-check.json
eval-evidence inspect "$EVAL_EVIDENCE_REAL_HARBOR_ROOT" --explain \
  | tee /tmp/harbor-inspect.json
```

Before marking G2 met:

- compare every available instrument source/value with the redacted source JSON;
- confirm `unavailable` values really are absent rather than missed by the adapter;
- review agent wall-time fallbacks, `n_cache_tokens`,
  `exception_info.exception_type`, and the ATIF `steps` shape;
- confirm missing optional references are reported as absent without invalidation;
- redact roots, run IDs, task IDs, and any sensitive values from the transcript;
- update `HARBOR_MAPPING.md` rows supported by the review from `inferred` to
  `real-trial`;
- give regular CI an approved sanitized structural fixture or a secure fixture source
  so the named G2 test runs without a skip; only then change G2 in `READINESS.md` to
  `met`.

A manually redacted transcript is review evidence, but by itself it cannot make the
machine-enforced gate `met`: `tests/test_readiness.py` deliberately rejects a skipped
`met` test. If the data owner cannot approve either a sanitized fixture or secure CI
access, keep G2 `unmet` and describe the external manual result separately.

The automated test proves structural loading and integrity only. The source/value
spot-check is a required human review because an internally consistent wrong mapping
can still hash and validate successfully.

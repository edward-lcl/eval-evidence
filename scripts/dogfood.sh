#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "usage: $0 /path/to/installed/python /path/to/empty/work-directory" >&2
  exit 2
fi

PYTHON="$1"
WORK="$2"
if command -v cygpath >/dev/null 2>&1 && [[ "$PYTHON" =~ ^[A-Za-z]:\\ ]]; then
  PYTHON="$(cygpath -u "$PYTHON")"
fi
PYTHON_DIR="$(cd "$(dirname "$PYTHON")" && pwd)"
PYTHON="$PYTHON_DIR/$(basename "$PYTHON")"
if [[ -e "$WORK" ]] && [[ -n "$(find "$WORK" -mindepth 1 -maxdepth 1 -print -quit)" ]]; then
  echo "dogfood work directory must be empty: $WORK" >&2
  exit 2
fi
mkdir -p "$WORK"
WORK="$(cd "$WORK" && pwd)"
CLI="$PYTHON_DIR/eval-evidence$("$PYTHON" -c 'import os; print(".exe" if os.name == "nt" else "")')"
cd "$WORK"

run() {
  "$CLI" "$@"
}

for format in generic harbor; do
  run demo --format "$format" -o "$WORK/$format"
  run check "$WORK/$format"
  run bundle "$WORK/$format" -o "$WORK/$format.bundle.json"
  run verify "$WORK/$format.bundle.json" --run-root "$WORK/$format"
done

# A source byte changed after bundling must fail reference verification and name it.
printf '\n' >> "$WORK/generic/outputs/scores.json"
set +e
run verify "$WORK/generic.bundle.json" --run-root "$WORK/generic" \
  > "$WORK/reference-tamper.json"
reference_status=$?
set -e
if [[ $reference_status -ne 1 ]]; then
  echo "expected referenced-file tamper verification to exit 1, got $reference_status" >&2
  exit 1
fi
grep -q 'outputs/scores.json' "$WORK/reference-tamper.json"

# A bundle claim changed without re-digesting must fail bundle verification.
"$PYTHON" - "$WORK/harbor.bundle.json" <<'PY'
import json
import sys
from pathlib import Path
path = Path(sys.argv[1])
bundle = json.loads(path.read_text(encoding="utf-8"))
bundle["outcome"]["reward"] = 0.125
path.write_text(json.dumps(bundle, indent=2, sort_keys=True) + "\n", encoding="utf-8")
PY
set +e
run verify "$WORK/harbor.bundle.json" > "$WORK/bundle-tamper.json"
bundle_status=$?
set -e
if [[ $bundle_status -ne 1 ]]; then
  echo "expected bundle tamper verification to exit 1, got $bundle_status" >&2
  exit 1
fi
grep -q 'Bundle digest mismatch' "$WORK/bundle-tamper.json"

echo "dogfood passed; tamper reports:"
echo "  $WORK/reference-tamper.json"
echo "  $WORK/bundle-tamper.json"

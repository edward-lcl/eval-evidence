# Figure remediation — resolved implementation receipt

## Root cause

The original lifecycle PNG visibly clipped the `INTEGRITY FAILURE` detail because the
outcome card rendered one unwrapped line inside a fixed-width card.

The old builder rendered `item["detail"]` as one 22 px text element inside a card with
approximately 300 px of usable width. The phrase `referenced bytes no longer match`
exceeded that budget. The stage cards already used pre-wrapped `detail_lines`; the
outcome cards did not. This diagnosis is historical—the canonical outputs now contain
the resolved layout below.

## Resolution

The repair is implemented in the repository-native figure pipeline:

1. `figures/eval-evidence-lifecycle.figure.json` is brief version 2 and preserves the
   single-line `detail` alongside deterministic `detail_lines`.
2. `scripts/build_figure.py` renders every outcome through the wrapped line structure.
3. `scripts/verify_figure.py` applies a fixed Arial-width proxy and rejects any outcome
   line exceeding the 300 px content budget.
4. `tests/test_figure_pipeline.py` proves the verifier rejects an overflowing fixture.
5. The canonical SVG and 3200 × 2000 PNG were regenerated and inspected at README and
   full size; the detail remains inside the card at both sizes.

## Companion teaching artifact

The command switchboard adds the layer the lifecycle visual cannot carry without
mixing questions. Its frozen brief maps `demo`, `check`, `bundle`, and `verify
--run-root` to their actions, outputs, proof boundaries, and source paths. Exact labels
and topology are deterministic SVG; no generated-image text or arrows are trusted.

Verification command:

```bash
python3 scripts/verify_figure.py
```

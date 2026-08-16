# Static figures

This directory contains five single-question figures designed to be read at three
speeds:

- `eval-evidence-lifecycle`: What does the current release do to a retained run?
- `eval-evidence-envelope-anatomy`: What stays separate inside `evidence.json`?
- `eval-evidence-command-path`: Do I need a report now or a saved baseline for later?
- `eval-evidence-evidence-states`: How does each field say how it is known?
- `eval-evidence-tamper-story`: What happens when a referenced file later changes?

Each `.figure.json` file is the frozen, portable semantic brief and source map. It
validates against `figure-brief.schema.json`, the same contract used by the global
`visual-system-explainer` skill. The paired `.render.json` contains only the deliberate
layout vocabulary needed by this renderer: canvas, line wraps, colors, and structured
rows/cards. Both inputs are content-addressed after checkout line-ending normalization
in the SVG comment and checked together, so the human render cannot silently drift
from the agent-readable contract or appear stale only because Git used CRLF on Windows.

Each story has two layouts generated from the same semantic brief and render manifest:
a wide overview and a content-sized `-mobile` portrait sequence. The SVG is canonical
and keeps its text selectable; the PNG is a 2x raster rendition for contexts that
require one. Mobile changes reading order only: titles, takeaways, labels, example
digests, and claims come from the same inputs and are verified against them. Exact
labels and topology are generated deterministically rather than delegated to an image
model.

All five figures share one high-contrast dark canvas and restrained teaching palette.
Color is always paired with numbering, lane position, geometry, or exact labels. The
figures intentionally do not share a mandatory proof-boundary footer: long limits live
in adjacent prose so each image can answer one question cleanly.

From the repository root, rebuild and validate deterministically:

```bash
python3 scripts/build_figure.py
python3 scripts/build_command_figure.py
python3 scripts/build_story_figures.py
python3 scripts/build_mobile_figures.py
python3 scripts/render_figure.py
python3 scripts/verify_figure.py
```

Rendering requires the local `rsvg-convert` and system-font identity pinned in
`renderer.lock`; `scripts/render_figure.py --check-provenance` fails closed when either
resolves differently. PNG digests are reproducible only in that declared local
environment; this project does not claim cross-platform PNG byte identity or bundle the
system font. `verify_figure.py` checks source/SVG digest linkage, accessibility,
required and prohibited claims, source-map paths, minimum text size, a text-node density
budget, complete mobile title/takeaway rendering, canonical SVG reproducibility,
desktop/mobile dimensions, renderer/font provenance, the exact five evidence states,
and shared tamper-story digests.

At README width, each figure retains one thesis and one dominant reading direction. At
full size, exact commands, status strings, file identities, and source-backed labels are
readable. Detailed `check` internals remain developer prose in `docs/ARCHITECTURE.md`;
they are not forced into the command-choice image. Numbered objects and named lanes keep
meaning independent of color or prior implementation knowledge.

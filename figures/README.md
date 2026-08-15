# Static figures

This directory contains two figures designed to be read at three speeds:

- `eval-evidence-lifecycle` answers what happens to a reported result after a run;
- `eval-evidence-command-path` answers which command to run, what it produces, and
  what its result does and does not prove.

Each `.figure.json` file is the frozen, portable semantic brief and source map. It
validates against `figure-brief.schema.json`, the same contract used by the global
`visual-system-explainer` skill. The paired `.render.json` contains only the deliberate
layout vocabulary needed by this renderer: canvas, line wraps, colors, and structured
rows/cards. Both inputs are content-addressed after checkout line-ending normalization
in the SVG comment and checked together, so the human render cannot silently drift
from the agent-readable contract or appear stale only because Git used CRLF on Windows.

The SVG is canonical and keeps its text selectable; the PNG is a 2x raster rendition
for contexts that require one. Exact labels and topology are generated deterministically
rather than delegated to an image model.

From the repository root, rebuild and validate deterministically:

```bash
python3 scripts/build_figure.py
python3 scripts/build_command_figure.py
python3 scripts/render_figure.py
python3 scripts/verify_figure.py
```

Rendering requires the local `rsvg-convert` and system-font identity pinned in
`renderer.lock`; `scripts/render_figure.py --check-provenance` fails closed when either
resolves differently. PNG digests are reproducible only in that declared local
environment; this project does not claim cross-platform PNG byte identity or bundle the
system font. `verify_figure.py` checks the frozen-source/SVG digest link, SVG
accessibility structure, required and prohibited claims, font-size and contrast proxies,
source-map paths, deterministic text bounds, canonical SVG reproducibility,
renderer/font provenance, and PNG dimensions. It
deliberately does not make visual claims about physical truth, model quality, or
cross-run comparability.

At README width, the lifecycle thesis and the command/output distinction remain
visible. At full size, every edge, proof limit, evidence category, and source-backed
annotation is readable. Solid horizontal arrows in the command switchboard mean
“produces”; its dotted vertical spine is recommended learning order, not a runtime
dependency.

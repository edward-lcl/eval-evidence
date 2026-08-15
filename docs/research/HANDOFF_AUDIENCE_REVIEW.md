# Handoff review at multiple altitudes

Status: 2026-08-15 outside-perspective sanity check.

| Reader | What they can decide now | What remains missing | Safe handoff route |
|---|---|---|---|
| New teammate | What problem is being tested, current authority, which gates pass, and the next bounded experiment | Oral confirmation that the private archive is accessible to them | `docs/START_HERE.md` -> `PROJECT_HANDOFF.json` -> selected work item's `start_at` |
| Developer/owner | Exact semantic invariants, adapter boundaries, regression tests, and release authority | Canonical CI confirmation, upstream review, and future release decisions | `docs/ARCHITECTURE.md`, `docs/HARBOR_MAPPING.md`, adversarial tests |
| Agent | Machine-readable gates, ordered tasks, owners, blockers, and acceptance evidence | Credentials or authority for private data, publishing, or upstream writes | `AGENTS.md` and `PROJECT_HANDOFF.json` |
| Terminal-Bench/Harbor maintainer | A narrow mapping to red-line, reproducible sanitized conflict fixture, and small placement questions | Confirmation of task identity, lock joining, capture-time fields, and campaign membership semantics | `docs/TBENCH_REVIEW.md` and `docs/research/UPSTREAM_MAP.md` |
| Paper reviewer | The falsifiable thesis, counter-hypotheses, experiment denominators, failure conditions, and epistemic boundary | Frozen manuscript revision and empirical study results | `docs/PAPER_ALIGNMENT.md` and `docs/research/RESEARCH_MAP.md` |
| Capital allocator | Current phase, stop conditions, next information-producing experiments, and reasons not to fund product expansion yet | Measured adoption value, prospective cost, conflict prevalence, and paper-quality results | `docs/research/DECISION_GATE_2026-08-15.md` |
| Mobile/quick reader | The lifecycle figures, short README claim, gate table, and one-page decision gate | Detailed evidence is intentionally one link deeper | README figures -> decision gate headings -> exact test/doc links |

## Outside-perspective verdict

The handoff is now safe for development continuation: the current state, known gaps,
research choices, and next experiments no longer depend on the original author being in
the room. It is not safe to present as a finished product, upstream-endorsed design, or
fundable standalone business. The path forward is clear precisely because those claims
remain withheld until the campaign, conflict, cost, and portability studies produce
evidence.

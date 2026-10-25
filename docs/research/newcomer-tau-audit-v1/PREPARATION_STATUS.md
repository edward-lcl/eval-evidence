# Preparation status

**Prepared and reviewed by the parent assistant, not handed off and not a study result.** Participant interest and organizer acceptance remain pending. Parent clarified the one-page entry point and recorded the verified repository-level MIT license in COORDINATOR.md; no cases or judgments were added.

Inventory: 10 files total: 9 Markdown documents and 1 header-only CSV. Seven files are in student/; the root holds tutoring boundaries, private coordinator guidance and this status. No actual data packet, source records, fixtures, extractor or reveal file is included.

Actual activity: 0 real cases selected, 0 real trials inspected or run, 0 rewards calculated, 0 trajectories annotated/ranked, 0 student judgments. The proposed six-record set is not frozen. Blank templates are not evidence of participant contribution.

Preparation-mechanics check: run the read-only standard-library Python command below from this directory. It validates the exact inventory, local Markdown links, no symlinks, CSV header shape and absence of judgment rows. It does not inspect sources or validate research results. No installation is required; manual reading remains the default.

```sh
python3 -B - <<'PY'
from pathlib import Path
import csv, re
root = Path.cwd().resolve()
expected = {'AGENTS.md', 'COORDINATOR.md', 'PREPARATION_STATUS.md'} | {
    'student/' + name for name in (
        'START_HERE.md', 'CODEX_PROMPT.md', 'STUDY_PLAN.md',
        'JUDGMENTS.csv', 'RUBRIC.md', 'CONTRIBUTIONS.md', 'REPORT_TEMPLATE.md')}
paths = list(root.rglob('*'))
assert not any(p.is_symlink() for p in paths), 'symlink in packet'
actual = {str(p.relative_to(root)) for p in paths if p.is_file()}
assert actual == expected, (actual - expected, expected - actual)
links = 0
for p in paths:
    if p.suffix == '.md':
        for href in re.findall(r'\]\(([^)]+)\)', p.read_text()):
            assert '://' not in href, 'unexpected external link'
            target = (p.parent / href.split('#')[0]).resolve()
            assert target.is_relative_to(root) and target.is_file(), href
            links += 1
with (root / 'student/JUDGMENTS.csv').open(newline='') as f:
    rows = list(csv.reader(f))
header = 'case_id,phase,recorded_at,author,rubric_version,judgment,policy_citation,trajectory_citation,reasoning,uncertainty,prior_exposure,ai_assistance,supersedes_entry'.split(',')
assert rows == [header], 'CSV must contain the exact header and no judgments'
print(f'PASS: {len(actual)} files; {links} local links; {len(header)} CSV columns; 0 judgment rows; no symlinks')
PY
```

Executed builder preparation-mechanics check: exit 0. Output: `PASS: 10 files; 7 local links; 13 CSV columns; 0 judgment rows; no symlinks`. After the parent entry-point edits, the parent independently repeated the check: `PASS: 10 files; 8 local links; 13 CSV columns; 0 judgment rows; no symlinks`. These are document/CSV checks, not evaluation results.

Remaining gates: owner review; participant interest and informed agreement; actual organizer requirements/acceptance or extension; source/license/privacy and AI-sharing permission review; student-agreed criterion; reward-independent case selection/freeze; audited Phase A export; separate authorized reveal. No data-readiness claim is made.

Only this new directory was written. The packet builder opened no real records, used no network and treated source identities as parent-supplied. The parent subsequently reviewed the packet and retrieved the repository-level license at the pinned revision; the earlier public-main observation was parent-verified. These checks do not authenticate historical run contents. No changes to existing project files, frozen ledger, original sole-authored submission, branches, public site, poster or form. No installations, commits, pushes, external messages or research schedules.

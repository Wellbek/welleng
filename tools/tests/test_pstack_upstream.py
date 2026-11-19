"""scripts/pstack-upstream-diff.py maps upstream changes to the adapted local files."""

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("pstack_upstream_diff", ROOT / "scripts" / "pstack-upstream-diff.py")
diff = importlib.util.module_from_spec(spec)
spec.loader.exec_module(diff)


def test_changes_name_the_local_counterpart_and_skip_other_plugins():
    upstream = json.loads((ROOT / "claude-plugin" / "pstack-upstream.json").read_text())
    compare = {
        "files": [
            {"filename": "pstack/skills/tdd/SKILL.md", "status": "modified"},
            {"filename": "pstack/skills/new-skill/SKILL.md", "status": "added"},
            {"filename": "pstack/skills/why2/SKILL.md", "status": "renamed", "previous_filename": "pstack/skills/why/SKILL.md"},
            {"filename": "other-plugin/README.md", "status": "modified"},
        ]
    }
    assert diff.changes(upstream, compare) == [
        "modified  pstack/skills/tdd/SKILL.md -> claude-plugin/skills/tdd/SKILL.md",
        "added     pstack/skills/new-skill/SKILL.md -> not adapted",
        "renamed   pstack/skills/why2/SKILL.md -> claude-plugin/skills/why/SKILL.md",
    ]

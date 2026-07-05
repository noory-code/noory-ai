"""Monthly team skill-usage totals: for the given month (default: this month),
gather the per-person comments (hidden data JSON) of the aggregation ticket and
print per-team-skill totals + unused candidates. Read-only (gh lookup only).

Pure stdlib + ``gh`` subprocess — cross-platform (no jq/date/bash).

Usage: ``python3 team-usage-report.py [YYYYMM]``
No shebang (CLAUDE.md).
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

LABEL = "skill-usage"


def _gh(proj: str, args: list[str]) -> "str | None":
    try:
        r = subprocess.run(["gh", *args], cwd=proj, text=True,
                           capture_output=True, timeout=60)
    except Exception:
        return None
    return r.stdout if r.returncode == 0 else None


def _list_all_skills(proj: str) -> set[str]:
    """Run the sibling list-all-skills.py and return the deduplicated skill set."""
    script = Path(__file__).with_name("list-all-skills.py")
    if not script.is_file():
        return set()
    try:
        r = subprocess.run([sys.executable, str(script)], text=True,
                           capture_output=True, timeout=30,
                           env=dict(os.environ, CLAUDE_PROJECT_DIR=proj, CODEX_PROJECT_DIR=proj))
    except Exception:
        return set()
    return {ln.strip() for ln in r.stdout.splitlines() if ln.strip()}


def main() -> int:
    month = sys.argv[1] if len(sys.argv) > 1 else datetime.now(timezone.utc).strftime("%Y%m")
    proj = os.environ.get("CLAUDE_PROJECT_DIR") or os.environ.get("CODEX_PROJECT_DIR") or os.getcwd()

    if not shutil.which("gh"):
        print("gh is required.")
        return 1

    listing = _gh(proj, ["api", f"repos/{{owner}}/{{repo}}/issues?labels={LABEL}&state=all&per_page=100"])
    num = ""
    if listing:
        try:
            for issue in json.loads(listing):
                if issue.get("title") == month:
                    num = str(issue.get("number") or "")
                    break
        except json.JSONDecodeError:
            pass
    if not num:
        print(f"No aggregation ticket: {month} (this month's records may not be reflected yet)")
        return 0

    # gather each person's hidden data (JSON) into team totals {skill: {count, last}}
    comments_raw = _gh(proj, ["api", f"repos/{{owner}}/{{repo}}/issues/{num}/comments", "--paginate"]) or "[]"
    try:
        comments = json.loads(comments_raw)
    except json.JSONDecodeError:
        comments = []

    team: dict = {}
    for c in comments:
        body = c.get("body") or ""
        m = re.search(r"<!-- data: (.*?) -->", body)
        if not m:
            continue
        try:
            person = json.loads(m.group(1))
        except json.JSONDecodeError:
            continue
        for k, v in person.items():
            pc = (team.get(k) or {}).get("count", 0)
            pl = (team.get(k) or {}).get("last")
            lasts = [x for x in (pl, v.get("last")) if x is not None]
            team[k] = {"count": pc + v.get("count", 0), "last": max(lasts) if lasts else None}

    print(f"# Team skill-usage totals — {month} (ticket #{num})")
    print()
    print("| skill | total uses | last |")
    print("|---|---:|---|")
    for k, v in sorted(team.items(), key=lambda kv: -kv[1]["count"]):
        print(f"| {k} | {v['count']} | {v['last']} |")

    print()
    print("## Unused candidates (installed but 0 uses this month)")
    used = set(team.keys())
    for s in sorted(_list_all_skills(proj)):
        if s not in used:
            print(f"- {s}")
    print()
    print("> Limitation: built-in·connector skills with no SKILL.md on disk don't show in the list, so "
          "they aren't flagged as 'unused' (their absence doesn't guarantee they're unused).")
    return 0


if __name__ == "__main__":
    sys.exit(main())

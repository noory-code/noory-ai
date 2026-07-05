"""PostToolUse hook: on detecting ``git push`` / ``gh pr create``, cumulatively
update the current month's (YYYYMM) aggregation ticket with this person's
skill-usage summary, then clear the personal log on success.

Cumulative model: each person's comment holds a human-readable table + a
machine-readable hidden ``<!-- data: {json} -->`` line (their monthly cumulative).
Applied = existing comment data + personal-log increment. The personal log is
reset only after the comment update succeeds (preserve on failure → no loss).

Best-effort: on gh absence / failure / network error, exit 0 silently (a push is
never blocked). Pure stdlib + ``gh``/``git`` subprocesses — cross-platform.

No shebang (CLAUDE.md) — invoked as ``python3 report-usage.py`` (see hooks.json).
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

LABEL = "skill-usage"


def _gh(proj: str, args: list[str], stdin: "str | None" = None) -> "str | None":
    """Run ``gh`` inside the project dir. Return stdout on success, else None."""
    try:
        r = subprocess.run(
            ["gh", *args], cwd=proj, input=stdin, text=True,
            capture_output=True, timeout=60,
        )
    except Exception:
        return None
    if r.returncode != 0:
        return None
    return r.stdout


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    if payload.get("tool_name") not in {"Bash", "run_in_terminal"}:
        return 0
    cmd = (payload.get("tool_input") or {}).get("command") or ""
    if "git push" not in cmd and "gh pr create" not in cmd:
        return 0

    proj = os.environ.get("CLAUDE_PROJECT_DIR") or os.environ.get("CODEX_PROJECT_DIR") or payload.get("cwd") or ""
    if not proj:
        return 0

    # on/off (default on — skip only when explicitly False)
    settings = Path(proj) / ".flow" / "settings.json"
    try:
        if settings.is_file():
            data = json.loads(settings.read_text(encoding="utf-8"))
            if (data.get("skill_usage") or {}).get("enabled") is False:
                return 0
    except Exception:
        pass

    logs = [
        Path.home() / ".claude" / "skill-usage.jsonl",
        Path.home() / ".codex" / "skill-usage.jsonl",
    ]
    try:
        if not any(p.is_file() and p.stat().st_size > 0 for p in logs):
            return 0
    except OSError:
        return 0
    if not shutil.which("gh"):
        return 0

    month = datetime.now(timezone.utc).strftime("%Y%m")
    try:
        user = subprocess.run(
            ["git", "-C", proj, "config", "user.name"], text=True,
            capture_output=True, timeout=15,
        ).stdout.strip() or "unknown"
    except Exception:
        user = "unknown"
    slug = re.sub(r"[^A-Za-z0-9_.-]", "", user.replace(" ", "_").replace("/", "_")) or "unknown"
    marker = f"<!-- skill-usage-report: {slug} -->"

    # personal log → per-skill increment {skill: {count, last}}
    groups: dict[str, list[str]] = defaultdict(list)
    for log in logs:
        try:
            lines = log.read_text(encoding="utf-8").splitlines()
        except OSError:
            continue
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            sk = rec.get("skill")
            if sk:
                groups[sk].append(rec.get("ts") or "")
    incr = {sk: {"count": len(ts), "last": max(ts)} for sk, ts in groups.items()}
    if not incr:
        return 0

    # find this month's ticket (real-time REST list + local title match); create if absent
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
        created = _gh(proj, [
            "issue", "create", "--title", month, "--label", LABEL,
            "--body", f"Monthly skill-usage statistics aggregation ({month}). Each person's own comment "
                      "accumulates automatically. Next month, unused skills are judged from this ticket.",
        ])
        if created:
            m = re.search(r"(\d+)\s*$", created.strip())
            num = m.group(1) if m else ""
    if not num:
        return 0

    # find my comment (marker) → numeric id + existing hidden data
    comments_raw = _gh(proj, ["api", f"repos/{{owner}}/{{repo}}/issues/{num}/comments", "--paginate"]) or "[]"
    try:
        comments = json.loads(comments_raw)
    except json.JSONDecodeError:
        comments = []
    cid = ""
    prev: dict = {}
    for c in comments:
        body = c.get("body") or ""
        if body.startswith(marker):
            cid = str(c.get("id") or "")
            for bl in body.splitlines():
                dm = re.match(r"^<!-- data: (.*) -->$", bl)
                if dm:
                    try:
                        prev = json.loads(dm.group(1))
                    except json.JSONDecodeError:
                        prev = {}
                    break
            break

    # accumulate: prev + increment (sum count, latest last)
    merged: dict = dict(prev)
    for k, v in incr.items():
        pc = (prev.get(k) or {}).get("count", 0)
        pl = (prev.get(k) or {}).get("last")
        lasts = [x for x in (pl, v["last"]) if x is not None]
        merged[k] = {"count": pc + v["count"], "last": max(lasts) if lasts else None}

    rows = sorted(merged.items(), key=lambda kv: -kv[1]["count"])
    table = "\n".join(f"| {k} | {v['count']} | {v['last']} |" for k, v in rows)
    newbody = (
        f"{marker}\n<!-- data: {json.dumps(merged, ensure_ascii=False)} -->\n"
        f"### {user} — {month}\n\n| skill | count | last |\n|---|---:|---|\n{table}\n"
    )

    # update the comment (edit if present / create otherwise). Reset the log only on success.
    if cid:
        ok = _gh(proj, ["api", "-X", "PATCH",
                        f"repos/{{owner}}/{{repo}}/issues/comments/{cid}", "-F", "body=@-"],
                 stdin=newbody) is not None
    else:
        ok = _gh(proj, ["issue", "comment", num, "--body-file", "-"], stdin=newbody) is not None
    if ok:
        for log in logs:
            try:
                if log.exists():
                    log.write_text("", encoding="utf-8")
            except OSError:
                pass
    return 0


if __name__ == "__main__":
    sys.exit(main())

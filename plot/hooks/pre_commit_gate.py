#!/usr/bin/env python3
"""PreToolUse hook for Plot — gate ``git commit`` on type-check + tests.

When the assistant attempts to run ``git commit`` (or ``git push``) and
Plot's viewer or MCP source has staged changes, this hook runs the
relevant checks first:

- ``viewer/`` staged changes ⇒ ``cd plot/viewer && npx tsc --noEmit``
  and ``npx vitest run``.
- ``plot_mcp/`` staged changes ⇒ ``cd plot && uv run pytest``.

If any check fails, the commit is blocked with a permissionDecision
of ``deny`` and the failure output is returned so the assistant can
fix and retry.

Cross-platform via Python stdlib + subprocess. Skips itself when the
staged paths are outside Plot or when no relevant files are staged.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path


# Patterns that, if matched anywhere in the bash command, indicate a
# write to the public history (commit / push) where we want to gate.
GATING_COMMAND_RE = re.compile(
    r"\bgit\s+(commit|push)\b",
    re.IGNORECASE,
)


# Cross-cutting visual SSOT files. Bundling any of these with a
# feature change in one commit is the v0.13.10 anti-pattern (see
# D-2026-05-11-C). Pre-commit gate blocks the bundle; the visual
# fix ships in its own atomic commit with its own D-id.
CROSS_CUTTING_VISUAL_CODE = frozenset({
    "viewer/src/styles.css",
})


def find_plot_root() -> Path | None:
    plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if plugin_root:
        candidate = Path(plugin_root)
        if (candidate / "viewer").exists() and (candidate / "plot_mcp").exists():
            return candidate
    here = Path(__file__).resolve()
    for parent in [here.parent.parent, here.parent.parent.parent]:
        if (parent / "viewer").exists() and (parent / "plot_mcp").exists():
            return parent
    return None


def staged_paths(repo_root: Path) -> list[str]:
    """Return staged file paths (relative to repo root)."""
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_root), "diff", "--cached", "--name-only"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            return []
        return [line.strip() for line in result.stdout.splitlines() if line.strip()]
    except FileNotFoundError:
        return []


def viewer_changes_staged(staged: list[str], plot_root: Path) -> bool:
    rel = plot_root.name + "/viewer/"
    return any(p.startswith(rel) for p in staged)


def mcp_changes_staged(staged: list[str], plot_root: Path) -> bool:
    rel = plot_root.name + "/plot_mcp/"
    return any(p.startswith(rel) for p in staged)


def cross_cutting_bundle_check(
    staged: list[str], plot_root: Path
) -> str | None:
    """Return a deny message if cross-cutting visual code and feature
    code are both staged in the same commit. Returns None when OK.

    Cross-cutting visual code = CROSS_CUTTING_VISUAL_CODE (currently
    just ``viewer/src/styles.css``). Feature code = any other file
    under ``viewer/`` or ``plot_mcp/`` (tests excluded — they ship
    with their target). Docs-only commits are never blocked.
    """
    prefix = plot_root.name + "/"
    rel = [p[len(prefix):] for p in staged if p.startswith(prefix)]
    visual = {p for p in rel if p in CROSS_CUTTING_VISUAL_CODE}
    feature = [
        p
        for p in rel
        if (p.startswith("viewer/") or p.startswith("plot_mcp/"))
        and p not in CROSS_CUTTING_VISUAL_CODE
        and not p.startswith("viewer/tests/")
    ]
    if not (visual and feature):
        return None
    feature_preview = feature[:5] + (["…"] if len(feature) > 5 else [])
    return (
        "### Cross-cutting visual change bundled with feature change\n\n"
        f"- Visual (cross-cutting SSOT): {sorted(visual)}\n"
        f"- Feature: {feature_preview}\n\n"
        "Split this into two atomic commits per D-2026-05-11-C:\n"
        "1. Visual fix only — own D-YYYY-MM-DD-X entry in DECISIONS.md.\n"
        "2. Feature change — depends on (1).\n"
        "\n"
        "Rationale: bundling a cross-cutting visual change with a\n"
        "feature change makes post-hoc causation unreadable (see\n"
        "v0.13.10). The cursor flicker → auto-layout misattribution\n"
        "that drove this gate is documented in D-2026-05-10-G and\n"
        "D-2026-05-11-C.\n"
    )


def run_check(command: list[str], cwd: Path) -> tuple[bool, str]:
    """Run a shell command, return (success, combined_output)."""
    try:
        result = subprocess.run(
            command,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            check=False,
            timeout=180,
        )
    except subprocess.TimeoutExpired as exc:
        return False, f"timeout running {' '.join(command)}: {exc}"
    output = (result.stdout or "") + (result.stderr or "")
    return result.returncode == 0, output


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        print(json.dumps({"continue": True}))
        return 0

    tool_name = payload.get("tool_name", "")
    if tool_name != "Bash":
        print(json.dumps({"continue": True}))
        return 0

    command = (payload.get("tool_input") or {}).get("command", "")
    if not GATING_COMMAND_RE.search(command):
        print(json.dumps({"continue": True}))
        return 0

    plot_root = find_plot_root()
    if plot_root is None:
        # Outside a Plot working tree
        print(json.dumps({"continue": True}))
        return 0

    repo_root = plot_root.parent  # noory-ai/
    staged = staged_paths(repo_root)
    if not staged:
        print(json.dumps({"continue": True}))
        return 0

    failures: list[str] = []

    if viewer_changes_staged(staged, plot_root):
        viewer_dir = plot_root / "viewer"
        ok, out = run_check(["npx", "tsc", "--noEmit"], cwd=viewer_dir)
        if not ok:
            failures.append(
                f"### viewer tsc --noEmit failed\n\n```\n{out.strip()[-2000:]}\n```"
            )
        ok, out = run_check(["npx", "vitest", "run"], cwd=viewer_dir)
        if not ok:
            failures.append(
                f"### viewer vitest run failed\n\n```\n{out.strip()[-2000:]}\n```"
            )

    if mcp_changes_staged(staged, plot_root):
        ok, out = run_check(["uv", "run", "pytest"], cwd=plot_root)
        if not ok:
            failures.append(
                f"### plot_mcp pytest failed\n\n```\n{out.strip()[-2000:]}\n```"
            )

    bundle_msg = cross_cutting_bundle_check(staged, plot_root)
    if bundle_msg:
        failures.append(bundle_msg)

    if failures:
        message = (
            "**Plot pre-commit gate blocked the commit.**\n\n"
            "Fix the failures below, re-stage, then retry the commit. The gate is "
            "registered in `plot/hooks/hooks.json` (PreToolUse on Bash, matcher = "
            "`git commit|push`).\n\n"
            + "\n\n".join(failures)
        )
        output = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": message,
            }
        }
        print(json.dumps(output))
        return 0

    print(json.dumps({"continue": True}))
    return 0


if __name__ == "__main__":
    sys.exit(main())

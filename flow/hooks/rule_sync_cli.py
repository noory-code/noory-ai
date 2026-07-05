"""CLI entry point — rule sync detect/apply invoked by the /flow-upgrade command.

Syncs plugin rules/ (canonical source) → project .claude/rules/ (propagation-rule copy) (propagation-rule model).
The judgment/apply logic SSOT = _flow_state (shared with the SessionStart hook). This file is just a thin
wrapper for calling those helpers from the command — do not reimplement the logic.

  detect            → drift judgment JSON (in_sync/stale/missing_new/orphan/protected/plugin_version)
  apply [--suffix S] [--applied-at TS]
                    → auto-sync propagation rules (override + orphan deletion + .gitignore registration), record state, summary JSON
  register-override --rule NAME [--detail]
                    → register a propagation rule in .gitignore per-file (usually apply does this automatically — for manual registration)

Workspace root = CLAUDE_PROJECT_DIR (cwd if absent) — resolve_workspace_root SSOT.
No shebang (CLAUDE.md) — invoke via `uv run --no-project python <this>`.
"""
from __future__ import annotations

import argparse
import json
import sys

from _flow_state import (
    apply_rule_upgrade,
    detect_rule_drift_all,
    load_sync_state,
    register_rule_override,
    resolve_plugin_upgrade_commands,
    resolve_workspace_root,
    seed_settings_defaults,
)


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # Prevent Windows cp949 mojibake

    parser = argparse.ArgumentParser(prog="rule_sync_cli")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("detect", help="drift judgment (read-only)")
    sub.add_parser(
        "upgrade-plan",
        help="Resolve CLI auto-upgrade commands (marketplace update + plugin update argv when stale)",
    )
    sub.add_parser(
        "seed-settings",
        help="Seed config-defaults.json defaults into settings.json (idempotent, non-destructive)",
    )
    ap = sub.add_parser("apply", help="Apply sync (propagation rules automatic — no approval argument)")
    ap.add_argument("--suffix", default="bak", help="Backup file suffix")
    ap.add_argument("--applied-at", default="", dest="applied_at", help="ISO8601 apply timestamp")
    rg = sub.add_parser(
        "register-override",
        help="Register a propagation rule in .gitignore per-file (usually apply does this automatically)",
    )
    rg.add_argument("--rule", required=True, help="Rule filename (e.g. flow-rules.md)")
    rg.add_argument("--detail", action="store_true", help="Specify if it is a rule-details domain")
    args = parser.parse_args()

    workspace_root = resolve_workspace_root({})

    if args.cmd == "detect":
        # rules/ + rule-details/ merged drift (rule-details items use the 'rule-details/' prefix).
        drift = detect_rule_drift_all(workspace_root, load_sync_state(workspace_root))
        report = {
            k: drift[k]
            for k in (
                "in_sync",
                "stale",
                "missing_new",
                "orphan",
                "protected",
                "plugin_version",
            )
        }
        print(json.dumps(report, ensure_ascii=False))
        return

    if args.cmd == "upgrade-plan":
        # CLI auto-upgrade plan (concrete commands to run when stale) — a pre-step of /flow-upgrade.
        print(
            json.dumps(
                resolve_plugin_upgrade_commands(), ensure_ascii=False
            )
        )
        return

    if args.cmd == "seed-settings":
        # Plugin internal defaults → settings.json seed (idempotent, non-destructive). Step 0.5 of /flow-upgrade.
        print(json.dumps(seed_settings_defaults(workspace_root), ensure_ascii=False))
        return

    if args.cmd == "register-override":
        added = register_rule_override(workspace_root, args.rule, is_detail=args.detail)
        print(
            json.dumps(
                {"rule": args.rule, "detail": args.detail, "added": added},
                ensure_ascii=False,
            )
        )
        return

    # apply — auto-sync propagation rules (override + orphan deletion + registration). No approval argument.
    result = apply_rule_upgrade(
        workspace_root,
        suffix=args.suffix,
        applied_at=args.applied_at,
    )
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()

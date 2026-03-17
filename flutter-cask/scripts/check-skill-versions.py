#!/usr/bin/env python3
"""Flutter skill package version checker.

Compares documented versions in SKILL.md files against latest versions
from pub.dev API. Cross-platform replacement for check-skill-versions.sh.

Usage: python check-skill-versions.py
"""

from __future__ import annotations

import json
import re
import time
import urllib.request
from pathlib import Path

SKILLS_DIR = Path("skills")
OUTPUT_FILE = Path("version-report.md")

PACKAGE_MAP: dict[str, str] = {
    "flutter-riverpod": "flutter_riverpod",
    "flutter-freezed": "freezed",
    "flutter-go-router": "go_router",
    "flutter-hive": "hive",
    "flutter-secure-storage": "flutter_secure_storage",
    "flutter-firebase-analytics": "firebase_analytics",
    "flutter-firebase-crashlytics": "firebase_crashlytics",
    "flutter-firebase-messaging": "firebase_messaging",
    "flutter-firebase-performance": "firebase_performance",
    "flutter-screenutil": "flutter_screenutil",
    "flutter-shimmer": "shimmer",
    "flutter-svg": "flutter_svg",
    "flutter-google-fonts": "google_fonts",
    "flutter-pinput": "pinput",
    "flutter-quill": "flutter_quill",
    "flutter-image-picker": "image_picker",
    "flutter-cached-image": "cached_network_image",
    "flutter-webview": "webview_flutter",
    "flutter-local-notifications": "flutter_local_notifications",
    "flutter-geolocator": "geolocator",
    "flutter-package-info": "package_info_plus",
    "flutter-connectivity": "connectivity_plus",
    "flutter-quick-actions": "quick_actions",
    "flutter-share": "share_plus",
    "flutter-admob": "google_mobile_ads",
    "flutter-in-app-purchase": "in_app_purchase",
    "flutter-talker": "talker",
    "flutter-fvm": "fvm",
    "flutter-melos": "melos",
}


def get_latest_version(package_name: str) -> str | None:
    """Fetch latest version from pub.dev API."""
    url = f"https://pub.dev/api/packages/{package_name}"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            return data.get("latest", {}).get("version")
    except Exception:
        return None


def get_doc_version(skill_dir: Path) -> str | None:
    """Extract documented version from SKILL.md metadata."""
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.exists():
        return None
    content = skill_file.read_text(encoding="utf-8")
    match = re.search(r'version:\s*"([^"]*)"', content)
    return match.group(1) if match else None


def main() -> int:
    from datetime import datetime, timezone

    lines: list[str] = [
        "# Flutter Skill Version Check Report",
        "",
        f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
        "",
        "| Skill | Package | Documented | Latest | Status |",
        "|-------|---------|-----------|--------|--------|",
    ]

    exit_code = 0

    for skill_name, package_name in sorted(PACKAGE_MAP.items()):
        skill_dir = SKILLS_DIR / skill_name
        if not skill_dir.is_dir():
            continue

        print(f"Checking: {skill_name}")
        latest = get_latest_version(package_name)

        if latest is None:
            lines.append(f"| {skill_name} | {package_name} | - | API error | unknown |")
            continue

        doc_version = get_doc_version(skill_dir)

        if doc_version != latest:
            lines.append(
                f"| {skill_name} | {package_name} | {doc_version} | {latest} | needs update |"
            )
            exit_code = 1
        else:
            lines.append(
                f"| {skill_name} | {package_name} | {doc_version} | {latest} | up to date |"
            )

        time.sleep(0.5)  # API rate limiting

    lines.extend(["", "---", ""])
    if exit_code == 0:
        lines.append("## Result: All skills are up to date")
    else:
        lines.append("## Result: Some skills need updates")
        lines.append("")
        lines.append("Check the skills that need updates and use `update-flutter-skills`.")

    report = "\n".join(lines) + "\n"
    OUTPUT_FILE.write_text(report, encoding="utf-8")
    print(report)

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

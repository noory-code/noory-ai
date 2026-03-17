#!/usr/bin/env python3
"""Flutter Cask - New skill generator.

Cross-platform replacement for new-skill.sh.

Usage: python new-skill.py <skill-name> <package-name>
Example: python new-skill.py flutter-dio dio
"""

from __future__ import annotations

import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) < 3:
        print("Usage: python new-skill.py <skill-name> <package-name>")
        print("Example: python new-skill.py flutter-dio dio")
        return 1

    skill_name = sys.argv[1]
    package_name = sys.argv[2]
    skill_dir = Path("skills") / skill_name
    template_file = Path("skills") / "template" / "SKILL.md"

    if skill_dir.exists():
        print(f"Error: Skill directory already exists: {skill_dir}")
        return 1

    if not template_file.exists():
        print(f"Error: Template file not found: {template_file}")
        return 1

    # Title case for package name
    title_case = package_name[0].upper() + package_name[1:] if package_name else package_name

    # Read template and replace placeholders
    content = template_file.read_text(encoding="utf-8")
    replacements = {
        "{{SKILL_NAME}}": skill_name,
        "{{PACKAGE_NAME}}": package_name,
        "{{DESCRIPTION}}": f"Flutter {package_name} package usage guide",
        "{{TITLE}}": f"Flutter {title_case}",
        "{{SHORT_DESCRIPTION}}": f"Flutter development guide using {package_name} package",
        "{{TRIGGER_KEYWORDS}}": package_name,
        "{{COMMON_ISSUE}}": "Package installation error",
        "{{FIX_DESCRIPTION}}": "Run flutter pub get and restart",
    }
    for placeholder, value in replacements.items():
        content = content.replace(placeholder, value)

    # Create skill directory and write file
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(content, encoding="utf-8")

    print(f"\nSkill created successfully!")
    print(f"\nLocation: {skill_dir}/")
    print("Next steps:")
    print(f"   1. Edit {skill_dir}/SKILL.md with package-specific details")
    print("   2. Add code examples to Quick Reference section")
    print("   3. Update Common Issues table with real issues")
    print("   4. (Optional) Create references/ directory for additional docs")
    print("\nSee CONTRIBUTING.md for skill structure guidelines")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

---
name: update-flutter-skills
description: Update all Flutter skills in the flutter-cask plugin. Reflect latest docs, add new skills, improve existing skills.
metadata:
  version: "1.2.0"
  category: meta
  type: composite
  style: procedural
  triggers: [update flutter skills, update-flutter-skills, flutter package guide update, skill update]
  uses: []
---

# Update Flutter Skills

> Keep Flutter skills in the `flutter-cask` plugin up to date.

## Input

```yaml
input:
  required: []
  optional:
    - name: target
      type: string
      desc: Specific skill name (e.g., flutter-freezed). If not specified, all skills are targeted.
    - name: action
      type: enum
      values: [update, add, list, check]
      desc: "update: update an existing skill | add: add a new skill | list: list all skills | check: check if up to date"
```

## Output

```yaml
output:
  side_effects:
    - updated: noory-ai/flutter-cask/skills/{skill-name}/SKILL.md
    - updated: noory-ai/flutter-cask/skills/{skill-name}/references/*.md
```

## Actions

```yaml
actions:
  - action: list
    do: retrieve skill list
    pseudo: |
      ls noory-ai/flutter-cask/skills/
      for each skill: read SKILL.md metadata (name, version, triggers)
      print summary table

  - action: check
    do: check if latest
    pseudo: |
      for each skill in target:
        read SKILL.md version
        search latest docs (context7, pub.dev)
        compare major version changes
        report outdated skills

  - action: update
    do: update skill
    pseudo: |
      for each skill in target:
        fetch latest documentation (context7)
        update SKILL.md (installation, usage, common issues)
        update references/*.md (code examples, patterns)
        bump version if changed

  - action: add
    do: add new skill
    pseudo: |
      create noory-ai/flutter-cask/skills/{name}/
      create SKILL.md (frontmatter + guide)
      create references/ (if needed)
```

## Skill Structure Rules

```yaml
structure:
  required:
    - SKILL.md: frontmatter(name, description, version, metadata) + guide
  optional:
    - references/: detailed code examples, pattern docs

frontmatter:
  name: kebab-case
  metadata:
    category: flutter | test | infra | ...
    type: unit
    style: guide
    triggers: [keyword list]
```

## Completion Checklist

- [ ] Target skill identified
- [ ] Latest docs verified (context7, pub.dev)
- [ ] SKILL.md updated (installation, usage)
- [ ] references/ updated (code examples)
- [ ] version bumped

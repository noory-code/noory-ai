---
name: update-flutter-skills
description: flutter-cask 플러그인의 Flutter 스킬 전체 업데이트. 최신 문서 반영, 새 스킬 추가, 기존 스킬 개선.
metadata:
  version: "1.2.0"
  category: meta
  type: composite
  style: procedural
  triggers: [flutter 스킬 업데이트, update-flutter-skills, flutter 패키지 가이드 업데이트, 스킬 최신화]
  uses: []
---

# Update Flutter Skills

> `flutter-cask` 플러그인의 Flutter 스킬을 최신 상태로 유지한다.

## Input

```yaml
input:
  required: []
  optional:
    - name: target
      type: string
      desc: 특정 스킬명 (예- flutter-freezed). 미지정 시 전체 스킬 대상.
    - name: action
      type: enum
      values: [update, add, list, check]
      desc: update(업데이트), add(새 스킬 추가), list(목록), check(최신 여부 확인)
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
    do: 스킬 목록 조회
    pseudo: |
      ls noory-ai/flutter-cask/skills/
      for each skill: read SKILL.md metadata (name, version, triggers)
      print summary table

  - action: check
    do: 최신 여부 확인
    pseudo: |
      for each skill in target:
        read SKILL.md version
        search latest docs (context7, pub.dev)
        compare major version changes
        report outdated skills

  - action: update
    do: 스킬 업데이트
    pseudo: |
      for each skill in target:
        fetch latest documentation (context7)
        update SKILL.md (설치, 사용법, 주의사항)
        update references/*.md (코드 예시, 패턴)
        bump version if changed

  - action: add
    do: 새 스킬 추가
    pseudo: |
      create noory-ai/flutter-cask/skills/{name}/
      create SKILL.md (frontmatter + guide)
      create references/ (필요 시)
```

## 스킬 구조 규칙

```yaml
structure:
  required:
    - SKILL.md: frontmatter(name, description, version, metadata) + 가이드
  optional:
    - references/: 상세 코드 예시, 패턴 문서

frontmatter:
  name: kebab-case
  metadata:
    category: flutter | test | infra | ...
    type: unit
    style: guide
    triggers: [키워드 목록]
```

## Completion Checklist

- [ ] 대상 스킬 식별 완료
- [ ] 최신 문서 확인 (context7, pub.dev)
- [ ] SKILL.md 업데이트 (설치, 사용법)
- [ ] references/ 업데이트 (코드 예시)
- [ ] version 범프

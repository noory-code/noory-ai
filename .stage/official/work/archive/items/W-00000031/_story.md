---
id: W-00000031
title: 이 저장소에서 Stage 플러그인 로컬 비활성화 (C4 게이트 수술 안전망)
kind: chore
venue: codex
source:
status: archived
verification: passed
retrospective: completed
retrospective_ref: R-00000030
promotion: not_applicable
review: not_required
scope: .claude/settings.local.json
promotes:
decision_refs:
---

# W-00000031 이 저장소에서 Stage 플러그인 로컬 비활성화 (C4 게이트 수술 안전망)

## Purpose

C4는 살아있는 쓰기/커밋 게이트를 레지스트리로 재배선한다. 이 저장소에 한해 Stage 플러그인을 끄면(프로젝트 로컬 settings) C4가 게이트를 잘못 건드려도 실제 커밋이 잠기지 않는 안전망이 된다. 사용자(대욱) 명시 요청 2026-07-13. 전역이 아닌 프로젝트 로컬로만 끈다.

## Scope


## Success criteria


## Related truth


## Progress


## Verification


### Executed at close — 2026-07-13

```
$ python3 -c "import json,sys; d=json.load(open('.claude/settings.local.json')); sys.exit(0 if d['enabledPlugins'].get('stage@noory-ai') is False else 1)"
[exit 0]

```

## Retrospective


## Promotion decision

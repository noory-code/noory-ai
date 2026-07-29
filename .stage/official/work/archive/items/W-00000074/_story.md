---
id: W-00000074
title: 스킬이 자기 플러그인의 스크립트를 가리키는 방법
kind: design
venue: claude
source:
autonomous: false
acceptance: []
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000073
promotion: approved
review: not_required
scope: .stage/decisions/pending/
promotes: .stage/official/decisions/records/DE-00000031.md
decision_refs: DE-00000031
---

# W-00000074 스킬이 자기 플러그인의 스크립트를 가리키는 방법

## Purpose

스킬 문서가 같은 플러그인 안의 스크립트를 실행하라고 안내할 때 쓸 경로 표기를 정한다. 현재 관행인 CLAUDE_PLUGIN_ROOT 변수는 에이전트가 명령을 돌리는 셸에 존재하지 않아 빈 문자열로 풀린다.

## Scope


## Success criteria


## Related truth


## Progress


## Verification


### Executed at close — 2026-07-26

```
$ python3 stage/scripts/audit_stage.py --project-root .
[exit 0]
Stage audit: /Users/woogis/Workspace/repo/noory-ai/.stage
OK: no findings
Summary: errors=0, warnings=0
```

## Retrospective


## Promotion decision

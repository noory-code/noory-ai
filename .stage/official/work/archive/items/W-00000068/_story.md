---
id: W-00000068
title: 버전을 올린 뒤 위임하면 막히는 것을 문서에 적는다
kind: documentation
venue: claude
source:
autonomous: false
acceptance: []
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000068
promotion: not_applicable
review: not_required
scope: stage/skills/stage-handoff/, stage/CHANGELOG.md, stage/.claude-plugin/plugin.json, stage/.codex-plugin/plugin.json
promotes:
decision_refs:
---

# W-00000068 버전을 올린 뒤 위임하면 막히는 것을 문서에 적는다

## Purpose

오늘 두 번 걸렸고 두 번 다 사람이 기억해서 풀었다. 어느 문서에도 없어 다음 세션이 또 헤맨다

## Scope

`stage-handoff`의 위임 실행 절에 절 하나. 코드는 없다 — 고칠 수 있는 것이 이쪽에 없다.

## Success criteria

- 위임하려다 막힌 사람이 증상만 보고 원인과 대응을 안다.
- 특정 다리(코덱스)에 Stage가 기대지 않는다. 일반적인 성질로 쓰고 관측 사례로만 이름을 든다.

## Related truth

P-00000001이 이 문제의 진단과 이력을 소유한다. 이 카드는 위임할 때 무엇을 하라는 것만 적는다.

## Progress

오늘 위임이 두 번 막혔다. 둘 다 원인은 같다 — Stage 버전을 올리면, 이미 떠 있던 다리 프로세스가
시작할 때 잡아 둔 경로를 계속 찾는다. 그 폴더는 이미 없다. 실행하는 쪽은 첫 명령에서 죽고,
오늘은 보낸 카드를 읽지도 못했다.

두 번 다 사람이 한 시간 전 일을 기억해서 풀었다. 저장소 어디에도 적혀 있지 않으니 다음 세션은
처음부터 다시 찾아야 한다. 그래서 위임 문서에 넣었다.

일반적인 성질로 썼다 — "시작할 때 플러그인 경로를 잡아 두는 다리는 전부 같다"로 쓰고, 코덱스는
관측된 사례로만 들었다. Stage가 특정 다리에 기대면 안 된다.

## Verification


### Executed at close — 2026-07-25

```
$ python3 stage/scripts/audit_stage.py --project-root .
[exit 0]
Stage audit: /Users/woogis/Workspace/repo/noory-ai/.stage
OK: no findings
Summary: errors=0, warnings=0
```

## Retrospective


## Promotion decision

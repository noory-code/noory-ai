---
id: W-00000063
title: 위임 실행 루프를 문서로 못 박는다
kind: documentation
venue: claude
source:
autonomous: false
acceptance: []
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000062
promotion: not_applicable
review: not_required
scope: stage/skills/stage-handoff/, stage/CHANGELOG.md, stage/.claude-plugin/plugin.json, stage/.codex-plugin/plugin.json
promotes:
decision_refs:
---

# W-00000063 위임 실행 루프를 문서로 못 박는다

## Purpose

다른 창에 코딩을 맡길 때 누가 커밋하고 누가 검토하는지가 문서에 없어 매번 즉흥으로 굴러간다

## Scope

`stage-handoff` 스킬의 위임 실행 절에 순서를 명시한다. 검토 태도는 `operations/review.md`가,
커밋·닫기·보관의 순서는 `operations/after.md`가 이미 소유하므로 그쪽은 건드리지 않는다 —
빠진 것은 "위임했을 때 누가 커밋하는가" 하나다.

## Success criteria

- 위임 실행 절만 읽고도 실행하는 쪽과 주관하는 쪽이 각각 무엇을 하는지 알 수 있다.
- 실행하는 쪽에 커밋을 시키지 않는 이유가 함께 적혀 있다.

## Related truth

`operations/review.md`(교차 검토), `operations/after.md`(소스 커밋 → 닫기 → 보관 순서).
오늘의 실제 사례는 W-00000057과 R-00000057에 있다.

## Progress

오늘 코덱스에 구현을 맡기면서 커밋까지 시켰다. 구현·테스트·감사를 다 끝낸 뒤 마지막에
`.git`에 쓸 권한이 없어 막혔다. 남은 단계가 하필 그쪽이 할 수 없는 단계였다.

문서를 뒤져 보니 검토 태도와 커밋 순서는 이미 적혀 있었다. 없던 것은 위임했을 때의 역할 분담
하나였다. 그래서 위임 실행 절에 다섯 단계를 넣었다 — 주관하는 쪽이 카드를 스스로 설명되게
만들고 제약을 함께 넘긴다, 실행하는 쪽은 카드를 시작해 변경만 만들고 커밋하지 않은 채 멈춘다,
주관하는 쪽이 성공 기준에 대고 검토하며 검사를 직접 다시 돌린다, 카드가 열린 채로 커밋한다,
그다음 닫고 보관한다.

권한 문제로만 적지 않았다. 자기 작업을 증명하는 기록을 자기가 쓰면 안 된다는 것이 더 근본적인
이유이고, 그것도 함께 적었다.

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

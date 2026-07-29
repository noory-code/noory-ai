---
id: W-00000066
title: P-00000001에 오늘 재발 증거와 더 나은 완화책을 붙인다
kind: documentation
venue: claude
source:
autonomous: false
acceptance: []
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000065
promotion: not_applicable
review: not_required
scope: .stage/proposals/
promotes:
decision_refs:
---

# W-00000066 P-00000001에 오늘 재발 증거와 더 나은 완화책을 붙인다

## Purpose

이미 기록된 문제가 오늘 실제로 위임을 통째로 막았고, 전보다 나은 대응도 찾았다

## Scope

P-00000001에 재발 절과 갱신된 상태. 코드 조치는 없다 — 근본 수정은 Codex 쪽 몫이라는 판단이
2026-07-13에 이미 내려져 있다.

## Success criteria

- 다음에 같은 증상을 만난 사람이 원인을 다시 조사하지 않는다.
- 대응 방법이 적혀 있고, 그것이 이전 완화책보다 나은 이유도 함께 있다.

## Related truth

W-00000064(오늘 막혔던 위임), R-00000063.

## Progress

오늘 위임이 시작조차 못 하고 막혔다. Codex가 없어진 0.39.1 폴더의 훅을 찾았고, 그날 버전을
0.40.0과 0.40.1로 두 번 올린 것이 원인이었다. 캐시에는 이미 0.40.1이 있었으므로 동기화가
늦은 것이 아니라, 떠 있던 프로세스가 옛 경로를 붙들고 있었다.

이번 재발에서 새로 안 것 둘을 적었다. 파일 쓰기만이 아니라 읽기까지 막혀 위임이 통째로
죽는다는 것, 그리고 Stage를 끄는 대신 그 저장소의 Codex 프로세스만 내리면 풀린다는 것.
후자가 낫다 — Stage를 끄면 그 세션에서 게이트가 전부 사라진다.

우선순위도 올렸다. 위임 실행이 정식 흐름이 된 지금 이건 간헐적 불편이 아니라 흐름을 막는
요인이다.

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

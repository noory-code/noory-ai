---
id: W-00000123
title: 겹치지 않는 Stage 작업이 동시에 돈다
kind: development
venue: codex
milestone:
priority: 1
autonomous: false
acceptance: []
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000122
promotion: not_applicable
review: not_required
scope: stage/, .stage/, CLAUDE.md
promotes:
decision_refs:
---

# W-00000123 겹치지 않는 Stage 작업이 동시에 돈다

## Purpose

DE-00000040 을 코드에 싣는다. 스토리 셋이 순서대로: 릴리스 시점 버전 매기기(이것이 병렬을 여는 열쇠), worktree 로 여러 드라이버 띄우기, 겹치면 시작 거절.

이 카드는 에픽이다. 자기가 직접 하는 일은 없고 밑의 여섯 장이 끝나면 끝난다.

## Stories

계획은 셋이었고 여섯으로 끝났다. 늘어난 셋은 즉흥이 아니라, 매번 리뷰가 바로 앞 스토리가
들여온 실제 결함을 찾아서다.

| 스토리 | 무엇 | 회고 |
|---|---|---|
| W-00000124 | 버전을 카드가 아니라 릴리스가 정한다 — 병렬을 여는 열쇠 | R-00000116 |
| W-00000127 | 그 규칙이 여섯 플러그인 전부에서 참이 되게 한다 | R-00000117 |
| W-00000125 | 카드마다 자기 작업 트리에서 드라이버가 돈다 | R-00000118 |
| W-00000128 | 병렬 실행이 안전하게 멈추고 되돌아온다 | R-00000119 |
| W-00000126 | 겹치는 카드는 시작을 거절한다 | R-00000120 |
| W-00000129 | 정리가 리뷰어와 커밋 안 된 일까지 본다 | R-00000121 |

## User value

겹치지 않는 카드 여럿이 동시에 돈다. 지금은 카드마다 실행자가 6~10분 걸리는 것이 그대로
벽시계 시간이 된다.

덤으로 P-00000001 이 적어 둔 압력이 사라졌다 — 버전이 카드마다 안 올라가므로, 마켓플레이스가
다시 당기면서 돌던 작업이 훅을 못 찾고 죽는 사고가 안 난다. 2026-07-29 하루에만 두 번 겪었다.

## Scope

### Included

`stage/scripts/` 의 릴리스 명령과 병렬 실행 명령, `stage/skills/stage-drive/`,
`stage/CHANGELOG.md`, 루트 `CLAUDE.md` 의 Plugin Changes 규칙.

### Excluded

따로따로 띄운 드라이버 둘이 서로를 아는 일. 실행 등록부가 필요해 축이 다르고, 지금은 사람이
명령 하나로 여럿을 거는 흐름뿐이다(W-00000126 이 적어 둠).

## 남은 한계

- 지금 열린 드라이버 카드들은 전부 `drive.py` 를 만져 서로 진짜로 겹친다. 병렬은 서로 다른
  영역일 때 값을 한다.
- 시간이 다 됐을 때 무엇이 돌던 중인지를 로그 제목으로 짐작한다(O-00000010). 제대로 고치려면
  시도 기록에 도는 역할을 적어야 하고 그것은 `drive.py` 몫이다.
- 병합에서 `.stage/work/active.md`·`review.md` 의 행이 부딪친다. 사람이 푼다.


## Risks


## Success criteria


## Next action

## Progress

스토리 여섯이 전부 끝났다(2026-07-29 하루). 드라이버 감독 실행으로 돌렸고, 여섯 중 셋이
두 바퀴, 셋이 한 바퀴에 끝났다.

## Verification

밑의 여섯 장이 각자 인수 검사와 독립 리뷰를 통과했다. 에픽 자체가 직접 하는 일은 없다.

### Executed at close — 2026-07-29

```
$ python3 stage/scripts/audit_stage.py
[exit 0]
Stage audit: /Users/woogis/Workspace/repo/noory-ai/.stage
OK: no findings
Summary: errors=0, warnings=0
```

## Retrospective

[R-00000122](../../retrospectives/R-00000122.md)

## Promotion decision

not_applicable — 계약은 DE-00000040 이 이미 official 로 갖고 있다.

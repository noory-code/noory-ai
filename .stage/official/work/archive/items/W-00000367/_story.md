---
id: W-00000367
title: 여러 세션이 목록 파일과 카드 번호에서 부딪히지 않게 설계한다
kind: design
venue: claude
milestone: M-00000005
autonomous: false
acceptance: []
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000367
promotion: deferred
review: not_required
scope: .stage/decisions
promotes:
decision_refs: DE-00000091, DE-00000092
---

# W-00000367 여러 세션이 목록 파일과 카드 번호에서 부딪히지 않게 설계한다

## Purpose

두 세션이 동시에 카드를 등록하고 닫아도 손으로 고칠 충돌이 생기지 않는 방법을 정한다

## Actions

이 카드는 결정만 한다. 구현은 W-00000377 와 W-00000378 가 한다.

## User value

맥북 세션과 다른 세션이 같은 날 따로 일한 뒤 브랜치를 합칠 때, 목록 파일을 손으로 합치거나 겹친 번호를
다시 매기는 일을 하지 않는다.

## Scope

### Included

- 과거 머지에서 어느 파일이 몇 번 충돌했는지 센다.
- 목록 파일과 기록 번호 각각에 대해 설계안을 만들고, 고르기 전에 실제로 실행해 본다.
- 사용자가 고른 방법을 결정 기록으로 쓰고 구현 카드를 등록한다.

### Excluded

- 구현. 코드와 설정 파일은 고치지 않는다.

## Risks

- 설계안을 실행해 보지 않고 고르면 구현 카드가 만들 수 없는 것을 받는다. 고르기 전에 과거 머지와 빈
  저장소로 실행했다.

## Success criteria

- 사용자가 설계안을 보고 하나를 골랐고 그 결정이 결정 기록에 있다
- 고른 방법을 구현하는 카드가 계획된 카드로 등록되어 있다

## Next action

W-00000377 와 W-00000378 를 시작한다. 두 카드는 고치는 파일이 겹치지 않는다.

## Related truth

## Progress

- 이 저장소의 머지 136건을 처음 상태에서 다시 실행했다. 27건에서 충돌이 났고, 충돌한 파일은
  `stage/CHANGELOG.md` 14번, `active.md` 8번, `review.md` 7번, `planned/index.md` 2번, 보관 목록 2번,
  `decisions/index.md` 1번, 목록이 아닌 파일 두 개가 1번씩이다.
- 목록 파일 전부를 union 으로 합치는 안을 같은 머지에 실행했다. 더하기만 하는 파일은 16번 모두 줄이
  맞았다. 줄을 지우는 파일은 18번 가운데 13번에서 사람이 지운 줄이 되살아났다.
- 번호를 원격에 잡는 안을 빈 원격 저장소와 클론 두 개로 실행했다. 받아 오지 않은 두 번째 클론은
  거절됐다.
- 사용자가 2026-11-21 에 두 안을 보고 골랐다. 목록은 "더하기만 하는 파일은 union, 줄을 지우는 파일은
  카드에서 만든다"(DE-00000091), 번호는 "등록할 때 원격에 잡는다"(DE-00000092)이다. 사용자의 답은
  "네, 그렇게 정해요"였다.
- 구현 카드 두 장을 계획된 카드로 등록했다. W-00000377 는 목록 파일, W-00000378 는 번호다.
- 범위 밖으로 나간 것: 계획된 카드 두 장과 회고, 이 카드 파일은 `.stage/decisions` 밖에 있다. 시험은 임시
  폴더의 저장소로 했고 이 저장소의 파일은 고치지 않았다.

## Verification

맥북(macOS)에서 실행했다.

| 명령 | 결과 |
|---|---|
| 과거 머지 136건을 union 없이, union 을 걸고 다시 실행하는 스크립트 | 충돌 27건에서 2건, 줄이 다른 결과 13번 |
| 빈 원격 저장소에 두 클론이 같은 ref 를 만드는 명령 | 두 번째가 거절됨 |
| `python3 stage/scripts/audit_stage.py --project-root .` | 오류 0건 |

- 목록을 카드에서 만드는 쪽은 실행하지 않았다. 구현 카드가 확인한다.
- GitHub 의 머지 버튼이 union 을 따르는지, GitHub 이 `refs/stage-ids/` 를 받아 주는지는 확인하지 않았다.
  두 구현 카드의 끝나는 조건에 넣었다.
- 시험에 쓴 스크립트는 저장소에 두지 않았다. 결과는 두 결정 기록의 표에 있다.

- Checks at close 2026-11-21: 2 passed — `python3 -m unittest discover -s stage/hooks/tests -q`; `python3 stage/scripts/audit_stage.py --project-root .`

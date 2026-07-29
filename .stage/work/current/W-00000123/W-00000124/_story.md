---
id: W-00000124
title: 버전을 카드가 아니라 릴리스가 정한다
kind: development
venue: codex
milestone:
priority:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -q"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: not_required
scope: stage/scripts/, stage/scripts/tests/, stage/CHANGELOG.md, stage/skills/, CLAUDE.md
promotes:
decision_refs:
---

# W-00000124 버전을 카드가 아니라 릴리스가 정한다

## Purpose

DE-00000040 §1. 플러그인 카드가 버전을 올리지 않는다 — CHANGELOG 의 미출시 절에만 적고, 릴리스 명령이 버전을 정해 매니페스트 둘을 고친다. 이것이 병렬을 여는 열쇠다: 두 카드가 같은 다음 버전을 집는 충돌이 사라지고, 무엇보다 도는 동안 버전이 안 바뀌어 마켓플레이스 재당김이 돌던 작업을 죽이는 사고(P-00000001, 오늘 두 번)가 원천 차단된다. CLAUDE.md 의 Plugin Changes 규칙을 같이 고친다 — 사용자 확인 완료(2026-07-29).

## Actions

- 릴리스 명령을 만든다(`stage/scripts/` 아래, 파이썬). 플러그인 이름을 받아 `CHANGELOG.md` 의
  미출시 절을 읽고, 다음 버전을 정해 그 절에 제목을 붙이고, `.claude-plugin/plugin.json` 과
  `.codex-plugin/plugin.json` 의 `version` 을 같은 값으로 고친다.
- 버전 단계는 미출시 절의 내용이 아니라 **인자**로 받는다(patch/minor/major). 산문에서 의도를
  읽어내면 O-00000004 가 보인 함정을 되풀이한다.
- 미출시 절이 비어 있으면 거절한다. 낼 것이 없는데 버전을 올리는 것은 사실이 아니다.
- `stage/CHANGELOG.md` 맨 위에 미출시 절을 만든다. 다른 플러그인의 CHANGELOG 는 이 카드가
  안 건드린다 — 그쪽 작업이 시작될 때 같은 모양으로 연다.
- `CLAUDE.md` 의 Plugin Changes 절을 고친다: 카드는 미출시 절에만 적고, 버전과 매니페스트
  둘은 릴리스 명령이 정한다. 사람 확인 완료(2026-07-29, DE-00000040).
- 테스트를 쓴다.

## User value

두 작업이 동시에 돌아도 같은 다음 버전을 집어 부딪히지 않는다. 무엇보다 **도는 동안 버전이
안 바뀌므로**, 마켓플레이스가 다시 당기면서 옛 캐시 폴더가 사라져 돌던 작업이 죽는 사고가
없어진다 — 오늘 두 번 겪고 카드 시도 하나를 날린 그 사고다.

## Scope

### Included


### Excluded


## Risks

- 지금 매니페스트 버전(0.54.4)과 CHANGELOG 의 마지막 절이 어긋나면 다음 릴리스가 엉뚱한
  버전을 낸다. 명령이 매니페스트의 현재 값을 기준으로 다음을 정하고, CHANGELOG 의 마지막
  출시 절과 다르면 거절한다.
- 규칙을 바꾸는 동안 다른 창이 옛 규칙대로 버전을 올릴 수 있다. `CLAUDE.md` 수정이 같은
  커밋에 들어가야 두 진실이 공존하는 창이 안 생긴다.

## Success criteria

- 릴리스 명령이 미출시 절에 제목을 붙이고 매니페스트 둘을 같은 값으로 고친다. 그 동작을
  고정하는 테스트가 있다.
- 미출시 절이 비면 거절하고, 매니페스트와 CHANGELOG 의 현재 버전이 어긋나도 거절한다. 두
  거절을 각각 고정하는 테스트가 있다.
- 버전 단계를 인자로 받는다 — 산문에서 추측하지 않는다.
- `stage/CHANGELOG.md` 에 미출시 절이 서 있고, 그 위에 이 카드의 항목이 적혀 있다.
- `CLAUDE.md` 의 Plugin Changes 절이 새 규칙을 말한다 — 카드는 미출시 절에만 적고 버전은
  릴리스가 정한다.
- `python3 -m unittest discover -s stage/scripts/tests -q` 가 통과한다.

## Next action

끝나면 사람이 `stage` 외 다섯 플러그인의 CHANGELOG 를 언제 같은 모양으로 열지 정한다. 지금
여는 것은 쓰지 않는 문서를 미리 고치는 일이라 이 카드가 안 한다.

## Progress

## Verification

## Retrospective

## Promotion decision

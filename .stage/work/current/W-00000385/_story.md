---
id: W-00000385
title: 메인 세션이 서브세션에 일과 번호 묶음을 나눠 주는 방법을 설계한다
kind: design
venue: claude
environment: cloud
milestone: M-00000005
autonomous: false
acceptance: []
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: pending
scope: .stage/decisions,.stage/work
promotes:
decision_refs: DE-00000094
---

# W-00000385 메인 세션이 서브세션에 일과 번호 묶음을 나눠 주는 방법을 설계한다

## Purpose

메인 세션이 여러 서브세션에 카드를 나눠 맡길 때, 번호가 겹치지 않고 각 서브세션이 받은 카드만 하고 결과를 메인 세션에 돌려주는 방법을 Stage 가 정한다

## Actions


## User value

사용자가 2026-11-21 에 "stage 가 서브세션을 잘 이용했으면 좋겠다"고 했다. 그날 메인 세션
(session_018VXR6Pgir7NPX45jvBQqYs)이 클라우드 서브세션 셋에 W-00000377, W-00000378, W-00000380 을 맡겼다.
겪은 일은 아래와 같다.

- 번호: 클라우드 서브세션은 `refs/stage-ids/` 로 번호를 원격에 잡지 못한다. 프록시가 세션 브랜치 밖의 push 를
  403 으로 막는다(W-00000378). 메인 세션은 프롬프트에 "새 카드를 등록하지 마라"고 손으로 적어서 겹침을 피했다.
  W-00000378 서브세션이 낸 대안 1번이 "메인 세션이 서브세션을 만들 때 번호 묶음을 미리 나눠 준다"였다.
- 보고: 서브세션은 `send_message` 로 메인 세션에 PR 링크와 결정을 보냈다. 사용자 확인이 필요한 일(DE-00000087)은
  메인 세션이 사용자에게 묻고 되돌려 보냈다. 이 흐름은 Stage 문서에 없고 프롬프트에만 있었다.
- 병합 순서: 세 PR 이 같은 파일(`register_work.py`, `parallel-sessions.md`, `CHANGELOG.md`, 보관 목록)을 고쳤다.
  메인 세션이 머지 순서를 정하고 "main 을 합쳐라"를 서브세션에 따로 알렸다.
- 닫기: 세 서브세션 모두 닫기 리뷰가 HEAD 커밋만 본다는 문제(O-00000058)를 로컬 squash 커밋으로 돌아갔다.
  메인 세션이 프롬프트에 그 방법을 적어 줬다.
- 비용: 서브세션 셋이 약 32 달러(W-00000377 19.3, W-00000380 8.8, W-00000378 4.0)를 썼다.
- 이 세션에서는 다른 세션이 이미 끝낸 카드를 메인 세션이 다시 시작했다가 되돌린 일도 있었다(W-00000367).
  누가 어떤 카드를 맡았는지 Stage 가 모른다.


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 사용자가 설계안을 보고 하나를 골랐고 그 결정이 결정 기록에 있다
- 고른 방법을 구현하는 카드가 계획된 카드로 등록되어 있다

## Next action

## Related truth

## Progress

## Verification

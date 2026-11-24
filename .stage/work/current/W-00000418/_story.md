---
id: W-00000418
title: 기계에서만 보이는 성공 기준을 카드에 기록된 확인으로 닫기 리뷰가 판정하게 한다
kind: fix
venue: claude
environment: cloud
milestone:
autonomous: false
acceptance: []
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: pending
scope: stage/operations/review.md,stage/operations/cloud-execution.md,stage/templates/v4/project-stage/settings.jsonc,.stage/settings.json,stage/scripts/subsession_brief.py,stage/scripts/tests,stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000418 기계에서만 보이는 성공 기준을 카드에 기록된 확인으로 닫기 리뷰가 판정하게 한다

## Purpose

사용자의 기계에서만 보이는 성공 기준을 가진 카드가, 그 확인이 카드에 기록된 뒤에는 닫기 리뷰를 통과해 닫힐 수 있다

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 리뷰 규칙이 카드의 ## Verification 에 날짜·기계·명령·결과가 적힌 기기 확인이나 사용자 판정을 read 로 판정하게 허용한다
- 그런 기록이 없는 기계 전용 기준은 지금처럼 FAIL 이다
- W-00000407 이 이 규칙으로 닫기 리뷰를 다시 받는다

## Next action

W-00000407 의 재리뷰 결과를 본 뒤 사용자의 확인을 받고 닫는다(DE-00000087).

## Related truth

## Sessions

- session_018VXR6RqorVPW78Q1Ns72B6 — work — 2026-11-24 — opened from the index: O-00000062

## Progress

- 2026-11-24 지휘 세션 session_018VXR6NxmjDnZJNGb3TZWco 가 등록하고 시작했다. W-00000407 의 닫기 리뷰가 두 기준을 `unable` 로 반려한 것이 계기다. `stage/operations/review.md` 는 검증 세션의 관찰만 `read` 로 판정하게 하고, `cloud-execution.md` 의 "Merge a card that waits for the user's machine" 은 확인이 도착하면 닫기 리뷰가 모든 기준을 판정한다고 해서, 기계 전용 기준을 가진 카드는 닫히지 않는다. 사용자가 절차를 고치는 길을 골랐고("1"), 목적과 성공 기준은 지휘 세션의 초안을 사용자가 그대로 승인했다("초안대로 등록").
- 닫기 절차를 바꾸는 카드다. DE-00000087 에 따라 사용자 확인 뒤에 닫는다.
- 셋째 기준(W-00000407 의 재리뷰)은 지휘 세션이 이 카드의 변경을 받은 뒤에 한다. 작업 세션은 하지 않는다.
- 새 기록 번호는 잡아 두지 않았다. 이 카드는 새 기록을 만들지 않는다.
- 2026-11-24 작업 세션 session_018VXR6RqorVPW78Q1Ns72B6 가 2f467bf5 를 보고했다. 첫째와 둘째 성공 기준을 채웠다고 했다. `review.md` 에 "A check recorded on the card" 를 더했고, 리뷰 명령 여섯 개와 템플릿, `cloud-execution.md`, 작업 브리핑이 따라간다. 줄의 형식은 `- Checked` 와 `- User verdict` 둘로 고정했다. `- Checked ... did not hold` 뒤의 `- User verdict ... held` 는 사용자의 판정이 정한다. 범위 밖으로 `stage/skills/stage-orchestrate/SKILL.md` 를 고쳤다(사용자의 답을 `- User verdict` 줄로 적으라는 문장). 실제 리뷰어가 새 문장을 따르는지는 돌려 보지 않았다고 했다.
- 2026-11-24 지휘 세션이 squash 커밋 0dab111 에서 훅 시험(489 통과), 스크립트 시험(1025 통과), `audit_stage.py`(오류 0)를 다시 돌렸다.
- 2026-11-24 지휘 세션이 W-00000407 의 확인을 새 줄 형식으로 옮기고 그 카드의 닫기 리뷰를 다시 돌린다(셋째 기준).
- Follow-up candidate: `read` 로 통과한 기계 전용 기준 뒤에 `- Checked`/`- User verdict` 줄이 있는지 `close_work.py` 나 audit 가 본다. 또는 기록된 확인과 기록의 사실을 가르는 표시를 둔다.
- Follow-up candidate: 다른 프로젝트(Dasina 등)는 리뷰 명령에 새 문장 넷을 넣어야 한다. 빠져도 audit 가 알리지 않는다(REVIEW003 은 method 낱말만 본다).
- Follow-up candidate: `claude_review_companion.py` 의 REVIEWER_RULES 가 기록된 확인의 예외를 말하게 한다.
- Follow-up candidate: `.stage/operations/verification.md` 의 "Windows 동작 확인" 이 `- Checked` 형식을 가리키게 한다.

## Verification

---
id: W-00000403
title: 실행 방식 지시(B11)를 빼 보고 하중을 본다
kind: development
venue: claude
environment: cloud
milestone: M-00000006
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -q"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: pending
scope: stage/skills/stage-drive,stage/templates,.stage/settings.json,stage/CHANGELOG.md,.stage/research/claude-fit
promotes:
decision_refs:
---

# W-00000403 실행 방식 지시(B11)를 빼 보고 하중을 본다

## Purpose

실행자에게 일하는 절차를 지시하던 문장 없이 드라이버가 돌고, 그 장치가 받던 하중이 있었는지 기록으로 안다 (DE-00000098)

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- stage-drive 스킬과 실행자 프롬프트에서 일하는 절차를 지시하는 문장이 빠지고, 시간 제한과 보고 계약은 남아 있다
- 뺀 뒤 돈 카드들의 Driver failure, 리뷰 FAIL, 재시도를 빼기 전과 비교한 결과가 연구 자료에 있다

## Next action

사용자의 답 세 가지를 받아 작업 세션에 전하고, 그 뒤 8c3dda6 을 가져와 검사를 다시 돌리고 닫기 리뷰로 넘긴다.

- Waiting on user: 둘째 성공 기준(빼기 전후 비교)은 클라우드 세션에서 채울 수 없다. 드라이버 기록이 커밋되지 않는 `.stage/.runtime/driver/logs/` 에만 있고, 뺀 뒤 드라이버로 돈 카드가 0장이며, 요즘 카드는 드라이버 없이 클라우드 작업 세션으로 돈다. 기준을 "방법과 빈 기준선을 기록했다"로 고치고 비교를 뒤 카드로 옮기는가, 로컬 기계에서 기준선을 센 뒤에 닫는가?
- Waiting on user: 뺀 실행자 문장("실패한 기준이 예시 입력을 인용하면 그 종류의 입력을 모두 고친다")에는 사고 출처(Dasina R-00000028, R-00000031)가 있다. 뺀 채로 두는가, 그 한 문장을 되돌리는가?
- Waiting on user: 드라이버 코드의 기본 시간 제한(선언한 크기 x 900초)도 B11 에 드는가? 작업 세션은 남겼다.

## Related truth

- DE-00000098

## Progress

- 2026-11-23 지휘 세션 session_018VXR6RJwybKUJRATYqvEuM 이 99f82735 에서 카드를 시작하고 작업 세션 session_018VXR6PA9aonbDLPim8LtfB (`claude/w403-drop-execution-instructions`)를 띄웠다. 번호 묶음은 잡지 않았다.

- 2026-11-23 작업 세션 session_018VXR6PA9aonbDLPim8LtfB 가 8c3dda6 을 보고했다. 성공 기준 1 을 주장했고, 기준 2 는 채우지 못했다고 보고했다(scripts 908, hooks 467 통과, audit 오류 0. 범위 밖 변경 없음).
- Follow-up candidate: 드라이버 기록이 있는 로컬 기계에서 `b11-load.md` 의 표로 빼기 전 기준선을 세고, 뺀 뒤 드라이버 카드가 돌면 결과 표를 채운다.
- Follow-up candidate: 요즘 흐름(클라우드 작업 세션, 드라이버 없음)에서 B11 의 하중을 잴 수 있는지, 작업 세션 브리핑의 지시가 지금의 B11 인지 정한다.
- Follow-up candidate: 닫을 때 사라지는 회차별 증거(시도 수, FAIL 회차, Driver failure)를 커밋되는 카드에 작게 남긴다.
- Follow-up candidate: `mechanisms.md` 의 B11 행에 Dasina 사고 출처를 적는다.
- Follow-up candidate: 뺀 문장을 자기 설정에 복사해 둔 다른 프로젝트(Dasina)의 실행자 설정을 고친다.

## Verification

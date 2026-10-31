---
id: W-00000300
title: 드라이버가 실행자가 바꾼 닫기 도구 몫의 카드 칸을 거절한다
kind: fix
venue: claude
environment: cloud
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -p test_close_work.py -q"
  - "python3 -m unittest discover -s stage/scripts/tests -p test_drive.py -q"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: pending
scope: stage/skills/stage-retrospective/close_work.py, stage/scripts/driver_unattended.py, stage/scripts/driver_supervised.py, stage/scripts/tests/test_close_work.py, stage/scripts/tests/test_drive.py, stage/scripts/tests/test_template_v4.py, stage/skills/stage-drive/SKILL.md, stage/docs/SCHEMA_V4.md, stage/templates/v4/project-stage/settings.jsonc, .stage/settings.json, .stage/state/observations/O-00000054.md, .stage/state/current.md, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000300 드라이버가 실행자가 바꾼 닫기 도구 몫의 카드 칸을 거절한다

## Purpose

실행자가 검사를 돌리지 않고 카드의 verification 같은 닫기 도구 몫의 칸을 손으로 바꿔 기록이 사실과 달라지는 일을 막는다.

## Actions

- 지금 동작(O-00000054): W-00000286 을 드라이버로 실행할 때 Codex 실행자가 카드의 `verification` 을 손으로
  `passed` 로 바꿨다. 이 값은 `close_work.py` 가 검사를 돌린 뒤 쓰는 값이다. 실행 명령은 `promotion` 을 직접
  고치라고 하지만 닫기 도구 몫의 칸은 막지 않고, 드라이버도 검사하지 않는다.
- `close_work.py` 가 닫기 도구 몫의 칸(`status`, `verification`, `review`, `retrospective`, `retrospective_ref`)이
  실행자 턴 동안 바뀌었는지 판정하는 함수를 소유하고, 두 드라이버가 실행 보고 검증 옆에서 그 함수로 판을
  거절한다.
- 실행자 계약(드라이브 스킬, 스키마, 템플릿, 이 프로젝트의 실행 명령 둘)에 그 칸들을 고치지 않는다고 적는다.
- O-00000054 를 닫힌 관측으로 바꾼다.

## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 실행자가 판 안에서 status, verification, review, retrospective, retrospective_ref 를 바꾸면 드라이버가 그 판을 거절한다는 것을 테스트가 확인한다
- 실행자 계약 문서와 실행 명령이 그 칸들을 실행자가 고치지 않는다고 같은 뜻으로 적는다

## Next action


## Related truth


## Progress


## Verification


## Retrospective


## Promotion decision

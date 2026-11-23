---
id: W-00000413
title: 리뷰와 닫기의 증거가 빠짐없이 남고 다른 프로젝트가 올릴 길이 있다
kind: development
venue: claude
environment: cloud
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -q"
  - "python3 -m unittest discover -s stage/hooks/tests -q"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: pending
scope: stage/scripts,stage/skills/stage-retrospective,stage/skills/stage-audit,stage/hooks,stage/templates,stage/docs/BLUEPRINT.md,stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000413 리뷰와 닫기의 증거가 빠짐없이 남고 다른 프로젝트가 올릴 길이 있다

## Purpose

닫힌 카드의 기록만으로 리뷰어가 무엇을 실행했고 몇 번 만에 닫혔는지 알 수 있고, 다른 프로젝트가 이 판으로 올릴 때 막히는 자리를 도구가 알려 준다

## Actions


## User value


## Scope

### Included


### Excluded

- 닫은 뒤 뒤집힌 판정을 세는 일(DE-00000101 의 3-다), `review.strengths` 의 TIER007, 다른 브랜치에 파일 이름으로만 있는 옛 너비의 번호.
- 다른 프로젝트(Dasina)의 저장소를 고치는 일.


## Risks


## Success criteria

- audit 가 하중 줄이 없는 완료 카드와, 판정 방법(method)을 말하지 않는 리뷰 명령을 알린다
- import_executor_report.py 가 시도 수를 남기고 work_load.py 가 닫힌 카드의 ran, read, unable 수를 센다
- 닫기가 돌린 검사의 출력이 리뷰어에게 넘어간다
- 다른 프로젝트가 올릴 때 쓰는 명령 하나가 결정 색인과 작업 보관 색인의 제목을 채운다
- LiveReviewerWriteProbeTest 를 실제로 돌린 결과가 보고에 있다
- 열린 관측 O-00000058, O-00000059, O-00000060 마다 고침이 들어갔거나 고치지 않는 까닭이 보고에 있다

## Next action


## Related truth

- W-00000405, W-00000408, W-00000409 의 후속 후보, DE-00000101
- O-00000058(닫기 리뷰는 맨 위 커밋이 고친 파일만 본다), O-00000059(드라이버가 닫는 카드는 손으로 닫는 카드와 두 군데가 다르다), O-00000060(열린 카드가 없으면 관문이 머지 커밋도 막는다)
- 사용자가 2026-11-23 에 남은 후보도 카드로 만들어 자율로 진행하라고 했다("남은 후보들도 카드로 만들어서 자율로 진행하세요"). 목적과 성공 기준은 지휘 세션이 후보 목록에서 옮겨 적었다.


## Sessions


## Progress


## Verification

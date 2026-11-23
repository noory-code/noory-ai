---
id: W-00000412
title: 지휘와 닫기 절차가 오늘 손으로 메운 자리를 말한다
kind: development
venue: claude
environment: cloud
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -q"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: pending
scope: stage/skills,stage/operations,stage/scripts/subsession_brief.py,stage/scripts/tests,stage/docs/BLUEPRINT.md,stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000412 지휘와 닫기 절차가 오늘 손으로 메운 자리를 말한다

## Purpose

다음 지휘자가 브리핑을 넘기고, 반려된 카드를 다시 가져오고, 기계 확인이 남은 카드를 병합하고, 릴리스를 낼 때 오늘처럼 스스로 길을 만들지 않는다

## Actions


## User value


## Scope

### Included


### Excluded

- 지휘 세션과 기기의 세션이 서로 모르고 카드를 여는 문제. 설계가 필요해 이 카드에서 다루지 않는다.
- `Order:` 줄을 스키마 필드로 바꾸는 일.


## Risks


## Success criteria

- 스킬과 브리핑 생성기가 작업 세션이 같은 명령으로 브리핑을 스스로 내어 읽는 길을 말하고, 토론, 계획, 규칙 후보 정리 세션의 브리핑을 생성한다
- cloud-execution.md 가 닫기 리뷰가 반려된 뒤 두 번째로 가져올 때 할 일과, 성공 기준이 사용자의 기계에서만 채워지는 카드를 열어 둔 채 병합하는 길을 말한다
- 릴리스 절차가 릴리스 커밋을 만들기 직전에 기본 브랜치를 받으라고 말한다
- stage-orchestrate 스킬이 이 카드를 시작할 때보다 길지 않다

## Next action


## Related truth

- O-00000061 의 "카드 여덟 장과 릴리스 하나를 묻지 않고 끌고 가며 본 것", W-00000406, W-00000410 의 후속 후보
- 검증 세션을 띄운 카드를 닫기 전에 `- Observed` 줄이 카드에 있는지 보는 것(W-00000408 의 후속 후보)도 절차에 넣을 수 있으면 넣는다.
- 사용자가 2026-11-23 에 남은 후보도 카드로 만들어 자율로 진행하라고 했다("남은 후보들도 카드로 만들어서 자율로 진행하세요"). 목적과 성공 기준은 지휘 세션이 후보 목록에서 옮겨 적었다.


## Sessions


## Progress


## Verification

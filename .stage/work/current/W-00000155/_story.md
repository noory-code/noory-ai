---
id: W-00000155
title: 반려한 계획 카드를 보관으로 빼는 길을 만든다
kind: fix
venue: codex
milestone:
priority:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -q"
  - "python3 -m unittest discover -s stage/hooks/tests -q"
  - "python3 stage/scripts/audit_stage.py"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: not_required
scope: stage/skills/stage-archive/archive_work.py, stage/skills/stage-archive/SKILL.md, stage/hooks/stage_runtime.py, stage/scripts/audit_stage.py, stage/scripts/tests/test_archive_work.py, stage/scripts/tests/test_audit_stage.py, stage/hooks/tests/test_stage_guard.py, stage/docs/SCHEMA_V5.md, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000155 반려한 계획 카드를 보관으로 빼는 길을 만든다

## Purpose

반려는 사람이 "이건 하지 않는다"고 내리는 결정이다. 끝난 상태다. 그런데 계획 단계에서 반려한
카드를 계획 목록에서 빼는 길이 하나도 없다. 사람이 승인한 결정을 도구가 실행하지 못한다.

이 저장소에 그런 카드가 하나 있다 — W-00000092, 2026-07-29 에 반려했고 아직 계획 목록에 앉아
있다. 네 가지 방법을 다 시도해 봤고 각각 다른 이유로 막혔다(실측 2026-07-30).

- 보관 명령에 번호를 주면 `no present item file` — 진행 중 폴더만 찾는다.
- 보관 인텐트를 만들면 `work_item ... was not found` — 계획 카드를 작업 항목으로 안 센다.
- 카드를 손으로 보관 위치에 옮기고 상태를 고치려 하면 `an archive-located work item must keep
  status archived` — 이미 보관 상태여야 고칠 수 있다.
- 시작 명령으로 진행 중으로 옮기려 하면 `status rejected is not a startable planned status`.

규칙 충돌도 하나 있다. 보관은 회고가 끝나 있어야 한다고 요구하는데, 반려한 계획 카드는 회고를
갖지 않는 것이 지금 설계다. W-00000092 본문이 그렇게 적어 놨고, 반려 이유도 그 본문에 있다.

## Actions

사람이 정한 규칙은 이것이다: **반려는 종료다. 종료된 카드는 계획 목록에 남지 않는다.**

- 보관 명령이 계획 폴더의 종료 상태 카드도 찾게 한다. 진행 중 폴더에 없으면 계획 폴더를 본다.
- 시작한 적 없는 반려 카드는 회고를 요구하지 않는다. 판단 기준은 카드가 진행 중 단계를 거친
  적이 있는지다 — 계획 폴더에서 바로 반려된 카드에는 회고가 없고, 반려 이유가 카드 본문에 있다.
  진행 중 카드의 반려는 지금처럼 회고를 요구한다.
- 보관 게이트가 그 이동을 허용한다. 계획 폴더의 카드를 보관 인텐트의 작업 항목으로 찾을 수 있게
  하고, 옮기는 중간 상태를 거부하지 않게 한다.
- **시작 명령은 그대로 둔다.** 반려된 카드를 시작할 수 있게 만들지 않는다. 반려는 시작이 아니라
  보관으로 간다.
- **감사도 시작한 적 없는 반려를 알아본다.** 지금 감사는 보관된 모든 기록에 완료된 회고와
  `retrospective_ref` 를 조건 없이 요구하고(ARCHIVE003), 진행 관련 칸(`verification`,
  `retrospective`, `promotion`, `scope`)도 다 채워져 있으라고 요구한다(WORK001·004·005·006).
  계획에서 바로 반려된 카드에는 그 칸들이 없다. 보관 명령이 찍어 두는 `terminal_disposition:
  rejected` 로 그 카드를 알아보고 두 요구에서 뺀다. 진행 중 카드의 반려는 그대로 요구한다.
- 진행 중 카드의 반려가 막히는 보장을 v5 배치로 집는 시험을 더한다. 지금 그 시험 둘은 v3 배치로
  쓰여 있어, 이 프로젝트가 실제로 쓰는 배치를 집는 시험이 없다.
- 보관 절차 문서와 스키마 문서의 조건 서술을 실제 동작과 맞춘다.

## User value

계획 목록을 열면 앞으로 할 일만 보인다. 하지 않기로 한 카드는 보관에 남아 이유째로 찾아갈 수
있다. 지금은 하나씩 열어 봐야 구분되고, 빼려면 사람이 규칙을 우회해야 한다.

## Scope

### Included

- 보관 명령의 카드 찾기와 회고 요구 조건.
- 보관 게이트의 작업 항목 찾기와 상태 검사.
- 회귀 시험 — 계획 폴더의 반려 카드가 보관되고, 진행 중 카드의 반려는 여전히 회고를 요구한다.
- 보관 절차 문서와 스키마 문서, 미출시 절.

### Excluded

- 시작 명령. 반려된 카드는 시작 대상이 아니다.
- W-00000092 를 실제로 옮기는 일. 코드가 들어온 뒤 사람이 명령을 돌려 확인한다.
- 계획 인덱스의 `rejected` 상태 값 자체. 카드가 보관으로 나가면 그 행도 함께 사라진다.

## Risks

- 회고 요구를 느슨하게 하면 진행 중 카드가 그 구멍으로 회고 없이 보관될 수 있다. 조건을 "계획
  폴더에서 바로 반려된 카드"로 좁혀야 하고, 진행 중 카드의 반려가 여전히 막히는 시험이 필요하다.
- 보관 게이트를 넓히면 승격 게이트가 함께 느슨해질 수 있다. 두 게이트는 같은 함수를 지나므로,
  일반 승격 인텐트가 계획 카드를 대상으로 삼지 못하게 유지해야 한다.
- 카드 본문의 상대 경로 링크가 보관 위치에서 깨진다. W-00000092 본문에 결정 기록을 가리키는
  링크가 있다.

## Success criteria

- 계획 폴더에서 반려된 카드에 번호를 주면 보관 명령이 그 카드를 보관으로 옮긴다.
- 그 카드에 회고가 없어도 보관된다. 반려 이유는 카드 본문에 남는다.
- 진행 중 카드의 반려는 여전히 회고 없이는 보관되지 않는다 — 시험으로 못 박는다.
- 일반 승격 인텐트는 계획 카드를 대상으로 삼을 수 없다.
- 보관 절차 문서의 조건 서술이 코드와 같다.
- 사람이 겪는 결과: 계획 목록에서 W-00000092 가 사라지고, 보관 인덱스에서 `rejected` 로 찾힌다.
  이 확인은 코드가 들어온 뒤 사람이 명령을 돌려서 한다.

## Next action

보관 명령의 카드 찾기 시험을 먼저 쓴다 — 계획 폴더의 반려 카드를 주면 찾아야 한다.

## Progress

## Verification

## Retrospective

## Promotion decision

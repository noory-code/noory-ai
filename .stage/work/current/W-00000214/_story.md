---
id: W-00000214
title: 초기화 스킬의 손 작업 문장이 현재 세대 트리를 가리키게 한다
kind: documentation
venue: claude
milestone:
autonomous: false
acceptance:
  - "python3 stage/scripts/audit_stage.py --project-root ."
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: not_applicable
review: not_required
scope: stage/skills/stage-init/SKILL.md, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000214 초기화 스킬의 손 작업 문장이 현재 세대 트리를 가리키게 한다

## Purpose

초기화 스킬의 손 작업 대비 문장이 한 세대 전 템플릿 트리를 가리켜 그대로 따라 만든 .stage 가 게이트에 거부되므로, 그 문장이 현재 세대 트리를 가리키고 이전 세대 트리의 쓰임을 같은 자리에서 밝히게 한다

## Actions

없음 — 스킬 문서의 문장 하나를 고치고 설명 한 줄을 더하는 한 덩어리다.

## User value

헬퍼 없이 손으로 `.stage` 를 만드는 사람이 따라 하는 문장이 지금은 현재 게이트가 거부하는
구조를 만들게 시킨다. 그 사람은 헬퍼가 안 되는 상황에 있으므로, 거부를 만난 뒤 혼자 원인을
찾아야 한다. 고치면 문장을 따라 만든 구조가 그대로 통과한다.

## Scope

### Included

- `stage/skills/stage-init/SKILL.md:37` 근처의 손 작업 대비 문장이 현재 세대 트리
  (`templates/v4/project-stage/` — `init_stage.py:14-15` 가 실제로 배포하는 뿌리)를 가리키게
  한다. 같은 파일 41행부터의 "Required structure" 블록과 같은 세대가 되게 한다.
- 이전 세대 트리(`templates/project-stage/`)가 왜 남아 있는지 — v3 프로젝트의 감사와
  이행이 쓴다(`audit_stage.py:16-17`, `migrate_stage.py:159`) — 를 그 자리에서 한두 문장으로
  밝힌다. 별도 소유 문서는 새로 만들지 않는다.

### Excluded

- 두 세대 트리의 구조 자체는 안 바꾼다. 문서만 고친다.
- 두 트리의 쓰임을 소유하는 문서를 새로 세우는 길(O-00000014 의 둘째 후보)은 안 간다 —
  읽는 사람이 필요한 것은 그 자리의 한두 문장이고, 새 소유 자리는 유지 비용만 늘린다.

## Risks

- 스킬 문서는 매 세션 로드되는 지시문이다. 문장을 고치며 뜻을 넓히거나 좁히면 초기화 동작이
  달라질 수 있으므로, 가리키는 주소와 설명만 바꾼다.

## Success criteria

- 손 작업 문장이 가리키는 트리와 같은 파일의 필요한 구조 블록이 같은 세대를 말한다
- 이전 세대 트리가 왜 남아 있는지 그 자리에서 알 수 있다

## Next action

`stage/skills/stage-init/SKILL.md` 의 37행 문장을 현재 세대 주소로 고치고 쓰임 설명을 붙인다.

## Related truth

- O-00000014 — 어긋난 문장과 두 트리의 실제 쓰임을 실측으로 적어 둔 기록. 이 카드가 닫히면
  그 관측을 닫는다.


## Progress

초기화 스킬의 손 작업 문장은 헬퍼가 배포하는 트리(`templates/v4/project-stage/`)와 언어별
덧씌우기 자리를 가리키고, 이전 세대 트리가 남아 있는 이유를 바로 다음 줄이 밝힌다. 같은 파일의
필요한 구조 블록은 결정·상태·제안 보관 칸을 포함해 그 트리와 같은 칸을 말한다.

## Verification


## Retrospective


## Promotion decision

not_applicable — 이 카드는 결정 기록을 걸지 않고 승격 경로도 선언하지 않는다
(`promotes`, `decision_refs` 둘 다 비어 있음).

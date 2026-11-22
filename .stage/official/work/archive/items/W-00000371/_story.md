---
id: W-00000371
title: 회고에 남길 칸을 정한다
kind: planning
venue: claude
environment: cloud
milestone: M-00000005
autonomous: false
acceptance: []
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000371
promotion: deferred
review: passed
scope: .stage/decisions,.stage/work,stage/operations/retrospective.md,stage/templates
promotes:
decision_refs: DE-00000093
---

# W-00000371 회고에 남길 칸을 정한다

## Purpose

회고를 쓸 때 나중에 실제로 읽히는 칸만 채운다

## Actions


## User value

DE-00000089 가 덜어낼 것 다섯 가지 가운데 4번(회고의 칸)을 미뤘다. 회고의 규칙 후보를 규칙으로 올리는 일을
한 번 해 본 뒤에 다시 보기로 했고, 그 일이 W-00000364 였다.

W-00000364 에서 본 것(R-00000364): 규칙을 찾는 데 쓴 칸은 `## Rule candidate` 하나였다. `## Next changes` 는
그 카드의 뒷일이라 쓰이지 않았다. DE-00000089 는 4번을 하면 `## Principles applied` 가 사라진다고 적었고,
계약은 회고마다 원칙을 인용하라고 한다.


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 사용자가 회고에 남길 칸을 골랐고 그 결정이 결정 기록에 있다
- 고른 대로 고치는 카드가 계획된 카드로 등록되어 있거나 고치지 않기로 한 이유가 결정 기록에 있다

## Next action

## Related truth

## Progress

### Executor report at close — 2026-11-22

```
What changed: Both retrospective templates and the project's refreshed template now have only Decision points, Context that was missing, and Rule candidate; operations/retrospective.md records those three and names which records own the dropped facts; the retrospective SKILL.md and rule-promotion.md send next work to a planned card or a state/ record instead of Next changes; driver_lifecycle.RETRO_SECTIONS and its machine-written text cover the three sections; drive.py drops its duplicate RETRO_SECTIONS; stage/CHANGELOG.md has an Unreleased entry.
Why: The user chose the three-section option for W-00000371 on 2026-11-22, recorded in DE-00000093; the dropped sections had no reader or repeated the card, the decision record, or a planned card.
Decisions made: Implemented the change inside W-00000371 instead of registering a separate implementation card, because the card's scope already covered stage/templates and stage/operations/retrospective.md and the user asked to finish the queued work; archived retrospectives are left unchanged and stay valid; crossed the card scope into stage/scripts/drive.py and stage/scripts/driver_lifecycle.py (the driver writes retrospectives from its own section list), stage/skills/stage-retrospective (the skill and rule-promotion.md pointed at Next changes), and stage/CHANGELOG.md (repository rule for any change under stage/).
Work not done: None.
```

## Verification

- 환경은 `cloud` 다. 닫기 리뷰는 같은 모델의 리뷰이고 교차 venue 리뷰가 아니다.
- 성공 기준 1: 사용자가 2026-11-22 에 세 칸 안을 골랐다("2는 1번"). DE-00000093 에 있다.
- 성공 기준 2: 고친 카드를 따로 등록하지 않고 이 카드에서 고쳤다(커밋 6de6fcb3). 이유는 실행 보고의 Decisions made 에 있다.
- 바꾼 뒤 `python3 -m unittest discover -s stage/hooks/tests -q` 통과, `python3 -m unittest discover -s stage/scripts/tests -q` 821개 통과, 감사 오류 0건.

- Checks at close 2026-11-22: 2 passed — `python3 -m unittest discover -s stage/scripts/tests -p test_drive*.py -q`; `python3 stage/scripts/audit_stage.py --project-root .`
- Review at close 2026-11-22 by claude_review_companion: approved (1 PASS, 2 PASS)

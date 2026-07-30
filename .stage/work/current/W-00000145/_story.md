---
id: W-00000145
title: 결정 하나를 카드 여럿이 참조할 수 있는가
kind: design
venue: claude
milestone:
priority:
autonomous: false
acceptance: []
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: not_required
scope: .stage/decisions/pending/
promotes:
decision_refs:
---

# W-00000145 결정 하나를 카드 여럿이 참조할 수 있는가

## Purpose

감사는 결정의 `work_item` 이 그 결정을 `decision_refs` 로 참조하는 **모든** 카드와 같기를
요구한다(`stage/scripts/audit_stage.py:455-462`, WORK015). 그래서 결정 하나를 카드 둘이 참조하면
어느 쪽을 적어도 오류가 난다.

그런데 "결정을 제기한 카드"와 "결정을 실행한 카드"가 갈리는 것이 자연스럽게 생긴다. 하루에 두 번
겪었다:

- novel-workspace: DE-00000003 을 W-00000130(제기)과 W-00000133(실행·종결)이 둘 다 참조한다.
  고치려면 보관된 카드를 열어야 하는데 보관 게이트에 막혔다(W-00000144).
- 이 저장소: 설계 카드 W-00000141 이 DE-00000042 를 낳고, 구현 카드 W-00000142 가 그것을
  실행한다. 구현 카드에 `decision_refs` 를 적으니 WORK015 로 막혀 본문 링크로 우회했다.

물음: **`decision_refs` 가 무엇을 뜻하는 칸인가.** "이 카드가 낳은 결정"인가, "이 카드를 구속하는
결정"인가. 둘 다면 두 칸이 필요하고, 하나면 나머지 관계를 어디에 적는지 정해야 한다.

## 후보

- **지금대로 1:1 유지** — `decision_refs` 는 낳은 카드만. 구속받는 쪽은 본문에서 링크한다.
  기계가 못 따라가지만 감사 규칙이 단순하다. (오늘 이 저장소가 쓴 우회)
- **칸을 둘로 나눈다** — `decision_refs`(낳음)와 `governed_by`(구속받음). 관계가 명시되지만
  스키마가 늘고 마이그레이션이 딸린다.
- **1:N 허용** — 결정의 `work_item` 을 주 소유자로 두고, 참조는 방향만 검사한다. 규칙이
  느슨해지는 대신 승격·보관 판정에서 누가 주인인지 다시 물어야 한다.


## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria


## Next action

## Progress

## Verification

## Retrospective

## Promotion decision

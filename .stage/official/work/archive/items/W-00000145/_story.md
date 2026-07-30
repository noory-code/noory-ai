---
id: W-00000145
title: 결정 하나를 카드 여럿이 참조할 수 있는가
kind: design
venue: claude
milestone:
priority:
autonomous: false
acceptance: []
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000145
promotion: promoted
review: not_required
scope: .stage/decisions/pending/
promotes: .stage/official/decisions/records/DE-00000046.md, .stage/official/decisions/index.md
decision_refs: DE-00000046
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

- 감사 규칙을 코드에서 읽는다 — `decision_refs` 가 무엇을 검사하는지, 그 검사에 무엇이 매달려
  있는지.
- 결정 기록을 세운다. `decision_refs` 의 뜻을 정하고, 뜻이 하나면 나머지 관계를 어디에 적는지 정한다.
- 겪은 사례 셋(novel-workspace 하나, 이 저장소 둘)이 그 규칙으로 전부 풀리는지 확인한다.

## User value

다른 프로젝트가 감사 오류 하나를 못 고치고 남겨 뒀다. 이 저장소도 구현 카드마다 우회로 적고 있다.
규칙이 정해지면 둘 다 풀린다.

## Scope

### Included

`.stage/decisions/pending/`.

### Excluded

- 코드 변경. 결론이 "규칙은 옳았고 문서가 안 적어 뒀다"이므로 감사는 안 건드린다.
- 문서 반영. 별도 카드로 세운다.

## Risks

느슨하게 푸는 길(1:N 허용)이 venue 예외의 안전 검사를 깨뜨린다. **결정이 카드를 지목하는 것으로
예외 대상을 특정하는데, 여럿을 허용하면 한 카드에 준 허가를 다른 카드가 주장할 수 있다.** 그 구멍을
못 보고 푸는 것이 이 카드의 가장 큰 위험이었다.

## Success criteria

- 결정 기록이 서고 `status: decided` 다.
- 결정이 **주인이 누구인지** 한 문장으로 정한다.
- 겪은 사례 셋에 그 규칙을 대 보고 각각 어떻게 풀리는지 결정 본문에 적는다.
- 1:N 을 안 받는다면 **왜 안 받는지**를 venue 예외 검사와 엮어서 적는다. 안 적으면 다음 사람이
  "그냥 느슨하게 하면 되잖아"로 다시 연다.
- 칸을 새로 안 만든다면 **다시 여는 조건**을 적는다.

## Next action

## Progress

## Verification

### Executed at close — 2026-07-30

```
$ python3 stage/scripts/audit_stage.py --project-root .
[exit 0]
Stage audit: /Users/woogis/Workspace/repo/noory-ai/.stage
OK: no findings
Summary: errors=0, warnings=0
```

## Retrospective

[R-00000145](../../retrospectives/R-00000145.md) — 규칙이 틀린 게 아니라 그 뜻을 아무도 안 적어
뒀다.

## Promotion decision

FINAL: promoted. DE-00000046 은 앞으로의 카드 작성을 구속하는 계약이므로 DE-00000030 의 판정에
따라 `official/decisions/records/` 로 승격한다.

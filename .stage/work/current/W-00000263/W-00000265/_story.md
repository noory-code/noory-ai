---
id: W-00000265
title: 스타일을 output style 로 낼 때 무엇을 어디에 둘지 정한다
kind: design
venue: claude
milestone:
autonomous: false
acceptance: []
status: completed
verification: passed
retrospective: completed
retrospective_ref: R-00000265
promotion: deferred
review: not_required
scope: .stage/decisions/pending/, plainly/
promotes:
decision_refs: DE-00000073
---

# W-00000265 스타일을 output style 로 낼 때 무엇을 어디에 둘지 정한다

## Purpose

스타일 파일의 자리와 고정 규칙의 단일 출처와 훅이 물러나는 조건과 스타일 선택을 적는 곳을 정한다.

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 결정 기록이 남고 사람이 그 결정을 승인한다
- 고정 규칙을 한 곳에서 관리하며 여러 스타일 파일에 넣는 방법이 결정에 적혀 있다
- 훅이 언제 물러나는지가 결정에 적혀 있다

## Next action


## Related truth


## Progress

결정을 DE-00000073 에 적었다. 스타일 파일은 `plainly/output-styles/` 에 두고, 고정 규칙은
`styles/` 가 소유하며 빌드 스크립트가 붙여서 커밋한다. 훅은 물러나는 게 아니라 없앤다. 스타일
선택은 클로드 코드의 `outputStyle` 설정이 갖는다. `force-for-plugin` 은 안 쓴다.

결정을 쓰기 전에 버리는 플러그인으로 한 번 돌려 봤다. 앞머리에 모르는 키를 넣어도 파일이 그대로
읽힌다는 것을 그때 알았다. 그래서 테스트가 "파일이 로드되는가"가 아니라 "키 이름이 글자 그대로
맞는가"를 보게 바꿨다. 읽기만 했으면 못 잡았을 자리다.

## Verification

사용자가 결정을 승인했다. 결정 기록이 고정 규칙의 단일 출처와 훅을 없애는 범위를 둘 다 담는다.
적용 자리 열여덟 군데를 세어 표로 적었고, 그중 `tests/test_plugin_contracts.py` 와
`stage/scripts/release_plugin.py` 는 실제로 구현에서 깨져서 표가 헛세지 않았음이 드러났다.

### Executed at close — 2026-09-06

```
$ python3 stage/scripts/audit_stage.py --project-root .
[exit 0]
k — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000034/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000035/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000036/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000037/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000038/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000039/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000048/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000055/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000061/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000074/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000080/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000090/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000123/_epic.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000137/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000154/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000159/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000160/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000189/W-00000191.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000189/W-00000192.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
Summary: errors=0, warnings=32
```

## Retrospective


## Promotion decision

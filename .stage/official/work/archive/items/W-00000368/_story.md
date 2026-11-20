---
id: W-00000368
title: 닫기와 보관을 한 번에 하게 고친다
kind: development
venue: claude
environment: local-no-codex
milestone: M-00000005
autonomous: false
acceptance: []
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000368
promotion: not_applicable
review: passed
scope: stage/skills/stage-retrospective,stage/skills/stage-archive,stage/scripts,stage/hooks,stage/operations,stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000368 닫기와 보관을 한 번에 하게 고친다

## Purpose

카드 한 장을 닫고 보관하는 데 기록만 고치는 커밋과 PR 이 따로 들지 않는다

## Actions


## User value


## Scope

### Included


### Excluded


## Risks

- 드라이버가 닫는 카드는 전과 같이 따로 보관해야 한다. 드라이버는 닫은 뒤에 `work/current/` 에 있는 카드를
  커밋하므로 `--archive` 를 넘기지 않는다.
- 이 카드는 닫는 절차를 바꾼다. 같은 모델의 리뷰만으로 닫지 않고 사용자 확인을 받는다(DE-00000087).


## Success criteria

- 카드를 닫는 명령 한 번으로 카드와 회고가 보관 자리까지 가고, 그 변경이 일을 한 PR 하나에 함께 실린다
- 리뷰는 전과 같이 일을 한 커밋의 변경을 판정한다
- 닫기와 보관이 지금 둘로 나뉜 이유를 확인해 카드에 적었고, 한 번에 할 수 없다고 드러나면 그 이유를 적고 이 카드를 거절한다

## Next action

## Related truth

- 덜어낼 것을 고른 결정: DE-00000089 의 5번.
- 닫는 절차: `stage/skills/stage-retrospective/SKILL.md` 의 `Close and archive in one command`.

## Progress

닫기와 보관이 둘로 나뉜 이유를 코드에서 확인했다. 한 번에 하지 못할 이유는 드라이버 한 군데뿐이다.

| 확인한 자리 | 알게 된 것 |
|---|---|
| `stage/hooks/stage_work.py` 의 `commit_blocker` | 관리 대상 파일을 커밋하려면 열린 카드가 있어야 한다. 손으로 할 때는 코드를 닫기 전에 커밋하므로 보관을 바로 해도 걸리지 않는다. |
| `stage/scripts/land_run.py` 의 `allowed_lifecycle_paths` | 드라이버는 닫은 뒤에 `work/current/` 의 카드와 `review.md` 를 커밋한다. 닫으면서 보관하면 이 걸음이 카드를 찾지 못한다. |
| `stage/hooks/stage_runtime.py` 의 `intent_validation_blocker` | 승격 의도는 보관된 카드도 찾는다. 보관이 승격을 막지 않는다. |
| `stage/scripts/audit_stage.py` 156~162줄 | 승격이 `approved` 인 채로는 카드를 닫을 수 없다. 닫힌 카드에 승격할 일이 남는 경우가 없다. |
| `stage/skills/stage-archive/SKILL.md` | 보관은 맨 위 카드 단위로만 한다. 에픽이나 스토리 아래의 카드는 혼자 보관되지 않는다. |

그래서 닫는 명령에 `--archive` 를 선택 사항으로 넣었다. 기본 동작은 그대로다.

- `close_work.py --archive`: 닫기가 성공하면 같은 명령이 `archive_work.archive_one` 을 부른다.
- 다른 카드 아래에 있는 카드에 `--archive` 를 주면 확인 명령을 실행하기 전에 거절한다.
- 닫기는 성공하고 보관이 실패하면 0 이 아닌 값으로 끝나고 다음에 실행할 명령을 알린다.
- 이미 닫힌 카드에 `--archive` 를 주고 다시 실행하면 보관한다.
- 테스트를 먼저 썼다. 고치기 전에는 6개 가운데 5개가 실패했고 고친 뒤에는 6개가 통과한다.
- `stage-retrospective` 와 `stage-archive` 스킬, 변경 기록을 고쳤다.

## Verification

맥북(macOS)에서 코드 커밋 `efb02c7b` 로 실행했다.

| 명령 | 결과 |
|---|---|
| `python3 -m unittest discover -s stage/scripts/tests -p test_close_work_archive.py` | 6개 통과 |
| `python3 -m unittest discover -s stage/hooks/tests -q` | 450개 통과 |
| `python3 -m unittest discover -s stage/scripts/tests -q` | 790개 통과, 2개 건너뜀 |
| `python3 stage/scripts/audit_stage.py` | 오류 0건, 경고 32건 |

- Windows 에서는 실행하지 않았다. 고친 코드는 경로를 `pathlib` 로 다루고 셸을 부르지 않는다.
- 드라이버로 카드를 닫는 흐름은 실제로 실행해 보지 않았다. 드라이버 코드는 고치지 않았고 테스트 모음이 통과한다.
- 닫기 리뷰는 맥북에서 Claude 대역(`claude_review_companion.py`)으로 받는다. 같은 모델의 리뷰다(DE-00000086).
- 사용자 확인 — 2026-11-21. 고친 내용, 확인한 것, 확인하지 않은 것(Windows, 드라이버 흐름, CI, 리뷰)을
  보고받고 "확인, 닫으세요" 라고 했다(DE-00000087).
- 이 카드를 `--archive` 로 닫는다. 실제 저장소에서 이 기능을 처음 쓰는 것이다.

### Executed at close — 2026-11-21

```
$ python3 -m unittest discover -s stage/scripts/tests -p test_close_work_archive.py
[exit 0]
......
----------------------------------------------------------------------
Ran 6 tests in 0.797s

OK

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 450 tests in 6.534s

OK

$ python3 stage/scripts/audit_stage.py
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

### Review at close — 2026-11-21

```
Review report: .stage/.runtime/driver/logs/W-00000368.md
Criteria:
- PASS: 카드를 닫는 명령 한 번으로 카드와 회고가 보관 자리까지 가고, 그 변경이 일을 한 PR 하나에 함께 실린다
  Reason: close_work.py --archive calls archive_work.archive_one after a successful close (and on rerun of a completed item), moving the card and retrospective into official/work/archive with index updates; I ran `python3 -m unittest discover -s stage/scripts/tests -p test_close_work_archive.py` and all 6 tests passed, including the close-and-archive and assert_archived checks; since close and archive happen in the working tree of one command, both land in the same commit/PR as the work, though the real-repo PR for this card is not yet opened.
- PASS: 리뷰는 전과 같이 일을 한 커밋의 변경을 판정한다
  Reason: The diff leaves the review path untouched: the review still resolves at close_work.py lines 1116-1169 against the HEAD commit's paths (line 740) and runs before the close, and archive_after_close runs only afterwards at line 1274; the failing-check test confirms nothing is archived when verification fails.
- PASS: 닫기와 보관이 지금 둘로 나뉜 이유를 확인해 카드에 적었고, 한 번에 할 수 없다고 드러나면 그 이유를 적고 이 카드를 거절한다
  Reason: The card's Progress table names five code locations (commit_blocker, land_run.allowed_lifecycle_paths, intent_validation_blocker, audit_stage 156-162, stage-archive top-level rule) and concludes only the driver landing step prevents a one-step archive, so the flag is opt-in and drivers keep the old flow; rejection was not needed because the manual path can be done in one step.
```

## Retrospective

## Promotion decision

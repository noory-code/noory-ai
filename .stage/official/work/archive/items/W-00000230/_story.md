---
id: W-00000230
title: 무인 실행 결과를 본 가지로 들인다
kind: ops
venue: codex
milestone:
autonomous: false
acceptance:
  - "python3 stage/scripts/audit_stage.py --project-root ."
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000229
promotion: not_applicable
review: not_required
scope: stage/scripts/drive_parallel.py, stage/scripts/tests/test_drive_parallel.py, stage/CHANGELOG.md, .stage/work/
promotes:
decision_refs:
---

# W-00000230 무인 실행 결과를 본 가지로 들인다

## Purpose

무인 실행은 카드를 스스로 닫고 격리된 가지에만 쓰므로 결과가 본 가지에 들어가려면 사람이 병합해야 하는데, 그 시점에는 열린 작업이 없어 커밋 게이트가 막으므로, 이 항목이 그 병합을 담아 결과를 들이고 병렬 실행이 만든 회고 번호 충돌을 푼다

## Actions

없음 — 병합 하나와 그 자리에서 드러난 것 둘을 기록하는 한 덩어리다.

## User value

무인 실행이 만든 결과가 실제로 쓰이는 자리에 도착한다. 격리된 가지에만 있으면 아무도 못 쓴다.

## Scope

### Included

- W-00000228 의 실행 가지를 본 가지에 병합하고, 그 시험이 본 가지에서 도는지 확인한다.
- 두 무인 실행이 같은 번호로 만든 회고를 서로 다른 번호로 나눈다.
- 병합에서 드러난 자리 둘을 관측으로 세운다(O-00000034·35).

### Excluded

- 드러난 두 자리를 고치지 않는다. 어느 길로 갈지는 아직 안 정했고, 관측이 그 갈림을 담는다.
- W-00000227 은 이 항목 전에 이미 병합·보관됐다(충돌이 없어 게이트에 안 걸렸다).

## Risks

- 보관된 회고와 같은 번호를 살아 있는 서랍에 남기면 감사가 중복으로 잡는다. 옮기는 쪽이
  맞다 — 보관된 기록은 안 건드린다.

## Success criteria

- W-00000228 의 무인 실행 결과가 본 가지에 들어가고 그 시험이 본 가지에서 통과한다
- 두 무인 실행이 같은 번호로 만든 회고가 서로 다른 번호를 갖는다
- 감사가 오류 없이 통과한다

## Next action

없음 — 병합 `04e01439` 로 끝났다.

## Related truth

- O-00000034 — 카드만 고친 실행자를 드라이버가 커밋 실패로 막는다(W-00000229 실행에서 드러남).
- O-00000035 — 무인 결과 병합 때 열린 작업이 없어 커밋 게이트가 막는다(이 항목이 그 실측이다).
- DE-00000055 — 무인 실행이 자기 작업 디렉터리에서 돈다. 그 격리 덕에 번호 충돌이 본 가지를
  안 깨고 병합 지점에서 보였다.


## Progress

병합 `04e01439`. W-00000228 의 무인 결과(병렬 명령의 무인 넘기기, 시험 33개)가 본 가지에
들어갔고 감독이 본 가지에서 다시 돌려 통과를 확인했다. 회고 번호 충돌은 W-00000228 의 것을
R-00000228 로 옮겨 풀었다 — W-00000227 의 것이 이미 R-00000226 으로 보관돼 있었다.

이 항목 자체가 O-00000035 의 실측이다. 게이트가 병합 커밋을 막았고, 아는 우회(충돌 없는
병합이나 `git merge --continue` 는 훅이 못 본다)를 쓰지 않고 게이트가 요구하는 대로 이
항목을 등록해 통과했다.

## Verification

성공 기준 셋 다 확인했다 — 본 가지에서 `test_drive_parallel.py` 33개 통과, 두 회고가
R-00000226·R-00000228 로 갈렸고, 감사 오류 0.


### Executed at close — 2026-08-06

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

$ python3 -m unittest discover -s stage/scripts/tests -p test_drive_parallel.py -q
[exit 0]
W-00000001: driver exited with status 0
Worktree: /private/var/folders/wg/6hnd_f255_z4ngk7ynwptym40000gn/T/tmpq0unrcwz/worktrees/W-00000001
Merge branch: stage/worktree/W-00000001
W-00000002: driver exited with status 0
Worktree: /private/var/folders/wg/6hnd_f255_z4ngk7ynwptym40000gn/T/tmpq0unrcwz/worktrees/W-00000002
Merge branch: stage/worktree/W-00000002
Removed worktree and branch for W-00000001
Removed worktree and branch for W-00000001
W-00000001: driver exited with status 0
Worktree: /private/var/folders/wg/6hnd_f255_z4ngk7ynwptym40000gn/T/tmp14tx9sxy/worktrees/W-00000001
Merge branch: stage/worktree/W-00000001
W-00000002: driver exited with status 0
Worktree: /private/var/folders/wg/6hnd_f255_z4ngk7ynwptym40000gn/T/tmp14tx9sxy/worktrees/W-00000002
Merge branch: stage/worktree/W-00000002
W-00000003: driver exited with status 0
Worktree: /private/var/folders/wg/6hnd_f255_z4ngk7ynwptym40000gn/T/tmp14tx9sxy/worktrees/W-00000003
Merge branch: stage/worktree/W-00000003
W-00000001: driver exited with status 0
Worktree: /private/var/folders/wg/6hnd_f255_z4ngk7ynwptym40000gn/T/tmptdj3b1dn/worktrees/W-00000001
Merge branch: stage/worktree/W-00000001
W-00000002: driver exited with status 0
Worktree: /private/var/folders/wg/6hnd_f255_z4ngk7ynwptym40000gn/T/tmptdj3b1dn/worktrees/W-00000002
Merge branch: stage/worktree/W-00000002
W-00000001: driver exited with status 0
Worktree: /private/var/folders/wg/6hnd_f255_z4ngk7ynwptym40000gn/T/tmpu5pur4ri/worktrees/W-00000001
Merge branch: stage/worktree/W-00000001
W-00000002: driver exited with status 0
Worktree: /private/var/folders/wg/6hnd_f255_z4ngk7ynwptym40000gn/T/tmpu5pur4ri/worktrees/W-00000002
Merge branch: stage/worktree/W-00000002
----------------------------------------------------------------------
Ran 33 tests in 4.112s

OK
```

## Verification


## Retrospective


## Promotion decision

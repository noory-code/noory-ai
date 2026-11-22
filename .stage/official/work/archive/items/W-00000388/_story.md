---
id: W-00000388
title: 메인 세션이 서브세션에 일을 맡기고 닫는 절차와 번호 묶음을 만든다
kind: development
venue: claude
environment: cloud
milestone: M-00000005
autonomous: false
acceptance: []
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000388
promotion: not_applicable
review: passed
scope: stage/skills/stage-handoff,stage/operations/cloud-execution.md,stage/scripts,stage/CHANGELOG.md,.stage/operations/parallel-sessions.md
promotes:
decision_refs:
---

# W-00000388 메인 세션이 서브세션에 일을 맡기고 닫는 절차와 번호 묶음을 만든다

## Purpose

메인 세션이 프롬프트를 손으로 쓰지 않고 Stage 절차대로 서브세션에 카드를 맡기고, 번호가 겹치지 않고, 돌아온 결과를 메인 세션이 닫는다

## Actions


## User value

DE-00000094 를 구현한다. 그 결정의 "Where this applies" 표에 고칠 자리가 있다. 서브세션은 만들기만 하고, 카드의 시작과 닫기와 보관은 메인 세션이 한다. 번호 묶음은 다른 세션이 fetch 한 뒤 쓰인 번호로 셀 수 있는 자리에 남겨야 한다. 2026-11-21 에 메인 세션이 서브세션 프롬프트에 손으로 적었던 것(번호를 고르지 말 것, 보고 형식, 닫기 방법)이 이 절차로 옮겨 와야 한다. W-00000387 이 먼저 끝나면 그 검사를 절차에 쓴다.


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 메인 세션이 남긴 번호 묶음을 다른 체크아웃의 stage_record_ids.py 가 fetch 뒤에 쓰인 번호로 세는 시험이 있고 통과한다
- stage-handoff 스킬에 서브세션에 맡기기, 보고 형식, 메인 세션의 닫기가 적혀 있다
- 서브세션 하나에 카드를 맡겨 이 절차대로 메인 세션이 닫은 기록이 카드에 있다

## Next action

## Related truth

## Progress

### Executor report at close — 2026-11-22

```
What changed: stage_record_ids.py counts ids in a card's `reserved_ids:` frontmatter as used, here and on fetched branches, and gains `--reserve-for <W-id> --count N` (main session holds a block on a started card) and `--from-card <W-id>` (sub-session takes its next unused id); the block functions live in the new stage_id_blocks.py; the new subsession_brief.py prints a sub-session's instruction from the card (read list with ancestors and decisions, checks, reserved ids, rules, report items); stage-handoff SKILL.md gains "Hand cards to cloud sub-sessions" with a split rule and the main session's steps; cloud-execution.md gains "Close a sub-session's card"; .stage/operations/parallel-sessions.md points at the procedure; stage/CHANGELOG.md has an Unreleased entry; two new test files.
Why: W-00000388 implements DE-00000094, which the user chose on 2026-11-22: sub-sessions build, the main session starts, holds ids, and closes.
Decisions made: Record a block on the handed card's frontmatter (`reserved_ids:`) rather than in a separate file, so the block travels with the card and other sessions count it after fetch; split the block functions out of stage_record_ids.py because it reached 517 lines; the main session closes by `git merge --squash` plus `git commit -C` of the sub-session's branch, so HEAD carries every changed path and the sub-session's report without a local-only commit; `--from-card` counts only real record ids, so a reserved id becomes used only when a record names it.
Work not done: The third success criterion (a sub-session run through this procedure and closed by the main session) is not met by this commit; the main session runs it next and records it on the card.
```

## Verification

- 환경은 `cloud` 다. 닫기 리뷰는 같은 모델의 리뷰이고 교차 venue 리뷰가 아니다.
- 성공 기준 1: `test_stage_id_blocks.py` 의 `test_another_clone_counts_the_pushed_block_after_fetch` 가 통과한다. 메인
  세션 클론이 묶음을 잡아 push 하면 다른 클론은 fetch 전에는 DE-00000004, fetch 뒤에는 DE-00000006 을 고른다.
  브랜치 쪽 묶음 세기를 끄면 이 시험이 실패한다.
- 성공 기준 2: `stage/skills/stage-handoff/SKILL.md` 의 "Hand cards to cloud sub-sessions" 에 나눌 기준, 시작, 번호 묶음,
  브리핑, 보고, 닫기가 있고, `stage/operations/cloud-execution.md` 의 "Close a sub-session's card" 에 닫는 순서가 있다.
- 성공 기준 3: W-00000383 을 이 절차로 맡기고 메인 세션이 닫았다.
  - 메인 세션이 카드를 시작하고 `--reserve-for W-00000383 --count 1 DE` 로 DE-00000095 를 잡아 push 했다(bbe3c9d6). 그
    뒤 이 체크아웃의 다음 DE 번호는 DE-00000096 이었다.
  - `subsession_brief.py` 의 출력을 고치지 않고 서브세션 session_018VXR6PfSTY9kta6NEXV8UR 의 첫 메시지로 보냈다.
  - 서브세션은 카드를 시작하거나 닫지 않고 커밋 하나(e5d73bad)를 push 한 뒤 보고 항목 일곱 가지를 모두 보냈다. 사용자
    확인이 필요한 것 하나를 올렸고, 메인 세션이 사용자에게 물어 확인을 받았다.
  - 메인 세션이 `git merge --squash` 와 `git commit -C` 로 받고(024cf7f3), 검사를 다시 돌리고, 리뷰를 받아 닫고
    보관했다(a1d99ae1). 서브세션 비용은 약 2.07 달러였다.
- 전체 시험: hooks 와 scripts 모두 통과, 감사 오류 0건(코드 커밋 08494f0b 기준).

- Checks at close 2026-11-22: 4 passed — `python3 -m unittest discover -s stage/scripts/tests -p test_stage_id*.py -q`; `python3 -m unittest discover -s stage/scripts/tests -p test_subsession_brief.py -q`; `python3 -m unittest discover -s stage/scripts/tests -p test_stage_record_ids.py -q`; `python3 stage/scripts/audit_stage.py --project-root .`
- Review at close 2026-11-22 by claude_review_companion: approved (1 PASS, 2 PASS, 3 PASS)
- 닫기 리뷰어는 이번에 명령 실행 승인을 받지 못해 시험을 직접 돌리지 못했다. 같은 시험은 닫기 검사 네 개로 통과했다.

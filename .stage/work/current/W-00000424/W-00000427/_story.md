---
id: W-00000427
title: 규칙: acceptance 명령에 한 사람의 기기 경로를 저장하지 않고 저장소 기준 상대 경로만 쓴다
kind: documentation
venue: claude
milestone:
autonomous: false
acceptance: []
status: completed
verification: passed
retrospective: completed
retrospective_ref: R-00000427
promotion: not_applicable
review: not_required
scope: stage/operations,stage/skills,.stage/operations,stage/docs,stage/scripts/tests,stage/hooks/tests,stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000427 규칙: acceptance 명령에 한 사람의 기기 경로를 저장하지 않고 저장소 기준 상대 경로만 쓴다

## Purpose

카드에 저장된 검사 명령이 다른 기기에서도 돈다

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 규칙 파일에 이 행동이 조건과 함께 적혀 있고 출처로 R-00000282 를 든다

## Next action

## Related truth

## Sessions

## Progress

- 2026-11-26 PM 세션 session_018VXR6PryFiaEHvhp1FXFX4 가 이 스토리의 커밋을 보고했고, PO 세션이 `6286875` 로 가져왔다(에픽 W-00000424 의 `## Progress` 에 결정이 있다). PO 세션이 가져온 여덟 커밋의 끝에서 훅 시험과 스크립트 시험, `audit_stage.py`(오류 0)를 다시 돌렸다.
- Follow-up candidates: registered 0, discarded 0
### Executor report at close — 2026-11-26

```
What changed: stage/skills/stage-work/SKILL.md, "Draft the item", the bullet about the stored command, gains a rule: never store a path of one person's machine in an `acceptance` command; a path in a stored command is written relative to the repository root, never as an absolute path, a home-folder path, or a path into another checkout; a check that belongs to another repository is not stored on this card, that repository's card owns it, and only its result is written under this card's `## Verification`. It says why (close_work.py and the driver re-run the stored command on whatever machine closes the card) and cites (R-00000282). stage/CHANGELOG.md has the entry under Unreleased.
Why: The story's success criterion: the rule file states this behavior with its condition and cites R-00000282. The stored command is written at registration, which stage-work owns (rule-promotion.md, "Where the rule goes").
Decisions made: (1) Settled by the PM session as a one-file how-detail and reported to the PO session before building: the rule goes into the stage-work bullet that describes the stored command, not into operations/verification.md, because that bullet is read when the command is written. (2) The retrospective shows one `/Users/<name>/...` path only; `~`, `/home/<name>`, `C:\Users\<name>` and "a path into another checkout" are this card's reading of "one person's machine path". (3) "write only the result under this card's `## Verification`" follows what the archived W-00000282 card did; the retrospective says only that the supervisor wrote the result. (4) "the command runs from that root" was checked in close_work.py, which runs each check with the project root as its working directory. (5) The story was written by a `writer` specialist sub-agent; the PM session read the diff against the retrospective and close_work.py and re-ran the check. (6) No path outside the story's scope changed. No record was created.
Work not done: Nothing refuses such a path: register_work.py, close_work.py and the audit accept an absolute path in `acceptance` as before, and no test pins the new sentences. That two cards were blocked rests on R-00000282's own sentence; the archived W-00000281 card no longer shows its first command. Nothing was run on Windows or macOS; the pull request's CI jobs are that check. Check run on Linux at this commit: python3 -m unittest discover -s stage/scripts/tests -p 'test_register_work.py' -q (48 tests, OK).
```

## Verification

2026-11-26 이 스토리는 닫을 때 리뷰를 받지 않았다(`review: not_required`). 닫기 리뷰는 에픽 W-00000424 가 닫힐 때 한 번 돌고, 그때 커밋 `6286875` 의 경로를 본다.

- Checks at close 2026-11-26: 2 passed — `python3 -m unittest discover -s stage/hooks/tests -q`; `python3 stage/scripts/audit_stage.py --project-root .`
- Load at close 2026-11-26: attempts 1, review FAIL rounds 0, repeated findings 0, driver rounds 0, driver failures 0 (timed out 0)

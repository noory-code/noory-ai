---
id: W-00000349
title: --scope 를 여러 번 넘기면 모든 경로를 카드에 담기
kind: fix
venue: claude
environment: local-no-codex
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest stage/scripts/tests/test_register_work.py -q"
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000349
promotion: not_applicable
review: passed
scope: stage/hooks/stage_work.py, stage/skills/stage-work/register_work.py, stage/scripts/start_work.py, stage/scripts/tests/test_register_work.py, stage/skills/stage-work/SKILL.md, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000349 --scope 를 여러 번 넘기면 모든 경로를 카드에 담기

## Purpose

register_work 와 start_work 에 --scope 를 여러 번 넘기면 경고 없이 마지막 경로만 카드에 남는 것을 고쳐, 넘긴 경로가 모두 카드 범위에 들어가게 한다.

## Actions

이 스토리는 작은 수정 하나라서 따로 나눈 액션이 없다.

## User value

카드를 등록하거나 시작하는 사람이 경로마다 `--scope` 를 따로 넘겨도 카드 범위가 넘긴 그대로 남는다.
범위가 잘못 남으면 그 카드의 쓰기가 모두 범위를 넘었다고 알려지고, 사람이 카드를 손으로 고쳐야 한다.

## Scope

### Included

- `register_work.py` 와 `start_work.py` 가 `--scope` 를 여러 번 받으면 모두 쉼표로 이어 카드에 적는다.
- 두 명령이 함께 쓰는 이어 붙이기 함수를 `stage_work.py` 에 둔다.
- 스킬 문서와 변경 기록에 적는다.

### Excluded

- 마일스톤을 만드는 `manage_roadmap.py create-milestone --scope` 는 경로 목록이 아니라 `## Scope` 절에 들어갈
  문장이다. 쉼표로 잇는 방식이 맞지 않아 이번에 바꾸지 않는다.

## Risks

- 쉼표로 이은 값 하나를 넘기던 기존 방식이 바뀌면, 이미 쓰는 사람의 카드가 달라진다.

## Success criteria

- register_work 에 --scope 를 두 번 넘기면 카드의 scope 줄에 두 경로가 모두 쉼표로 이어져 들어간다.
- start_work 에 --scope 를 두 번 넘겨도 두 경로가 모두 카드에 들어간다.
- 쉼표로 이은 값 하나를 넘기는 기존 방식은 그대로 동작한다.

## Next action

닫기 리뷰를 받고 닫는다.

## Related truth

- W-00000348 을 등록할 때 `--scope` 를 다섯 번 넘겼더니 마지막 경로 하나만 카드에 남았다(R-00000348).
- 사용자 결정(2026-11-17): "네, 고쳐요".

## Progress

- 커밋 `8ef87765`: 두 명령의 `--scope` 를 `action="append"` 로 바꾸고, 받은 값들을 `join_scope_args` 로
  쉼표로 이어 카드에 적는다. 값 하나는 앞뒤 공백만 지우고 그대로 둔다.
- 테스트 셋을 먼저 쓰고 돌렸다. 고치기 전에는 반복해 넘기는 두 테스트가 실패했고(마지막 경로만 남음),
  쉼표로 이은 값 하나 테스트는 통과했다. 고친 뒤에는 셋 다 통과한다.

## Verification

- `python3 -m unittest stage/scripts/tests/test_register_work.py`: 50개 통과.
- `python3 -m unittest discover -s stage/scripts/tests`: 761개 통과, 2개 건너뜀.
- `python3 -m unittest discover -s stage/hooks/tests -q`: 통과.
- `python3 -m unittest discover -s tests -q`: 통과.
- `python3 stage/scripts/audit_stage.py --project-root .`: errors=0.

### Executed at close — 2026-11-17

```
$ python3 -m unittest stage/scripts/tests/test_register_work.py -q
[exit 0]
----------------------------------------------------------------------
Ran 50 tests in 5.296s

OK

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 448 tests in 5.520s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (270 earlier lines omitted)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
[W-00000001] executor failed; retry 1/3
WARNING: preflights.codex is not configured; continuing without a venue health check
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1794861852
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1794861852. Human review + merge required; the base branch was not modified.
Removed unattended worktree: /private/var/folders/wg/6hnd_f255_z4ngk7ynwptym40000gn/T/tmp_ujwcadb/unattended/W-00000001-1794861852
Landed W-00000001 from stage/worktree/W-00000001 and removed its worktree and branch
Schema-v5 migration aborted; the exact pre-migration Stage tree was restored.
Schema-v5 migration aborted; the exact pre-migration Stage tree was restored.
Ignoring unrelated schema-v4 migration journal.
Schema-v5 migration complete: 3 flat work card(s) moved into the hierarchy.
This command does not commit. Its successful transaction journal was removed; review the working tree before committing.
Migration refused: Pending promotion machinery must finish before migration: .runtime/intents/W-00000001.json
Preflight passed. Close every other agent/editor window before continuing; the schema-v4 maintenance marker now denies concurrent Stage writes.
  unchanged operations/verification.md (unchanged)
  delete backlog B-00000001-realized.md (realized by W-00000009; git history keeps the file)
  convert backlog B-00000002-open.md -> W-00000001.md (planned work card)
  convert backlog B-00000003-child.md -> W-00000002.md (planned work card)
  update backlog index (1 closed rows removed)
  stamp  settings.json schema_version = 4
Schema-v4 responsibility relocation complete; continuing to schema v5.
Schema-v5 migration complete: 2 flat work card(s) moved into the hierarchy.
This command does not commit. Its successful transaction journal was removed; review the working tree before committing.
Stage project already uses schema v5; no migration needed.
Preflight passed. Close every other agent/editor window before continuing; the schema-v4 maintenance marker now denies concurrent Stage writes.
  unchanged operations/verification.md (unchanged)
  delete backlog B-00000001-realized.md (realized by W-00000009; git history keeps the file)
  convert backlog B-00000002-open.md -> W-00000001.md (planned work card)
  convert backlog B-00000003-child.md -> W-00000002.md (planned work card)
  update backlog index (1 closed rows removed)
  stamp  settings.json schema_version = 4
Schema-v4 responsibility relocation complete; continuing to schema v5.
Schema-v5 migration complete: 2 flat work card(s) moved into the hierarchy.
This command does not commit. Its successful transaction journal was removed; review the working tree before committing.
----------------------------------------------------------------------
Ran 761 tests in 147.184s

OK (skipped=2)

$ python3 -m unittest discover -s tests -q
[exit 0]
----------------------------------------------------------------------
Ran 7 tests in 0.001s

OK
```

### Review at close — 2026-11-17

```
Review report: .stage/.runtime/driver/logs/W-00000349.md
Criteria:
- PASS: register_work 에 --scope 를 두 번 넘기면 카드의 scope 줄에 두 경로가 모두 쉼표로 이어져 들어간다.
  Reason: I ran python3 -m unittest stage/scripts/tests/test_register_work.py -q (50 tests OK); test_repeated_scope_keeps_every_path asserts 'scope: src/a.py, src/b.py, docs/c.md', and against the pre-fix tree (8ef87765^) the same test failed with only 'src/b.py, docs/c.md' kept, so the check discriminates.
- PASS: start_work 에 --scope 를 두 번 넘겨도 두 경로가 모두 카드에 들어간다.
  Reason: I ran the same acceptance command (OK); test_start_with_repeated_scope_keeps_every_path asserts 'scope: src/a.py, src/b.py', and on the pre-fix tree it failed with only 'src/b.py' kept; start_work.py uses action=append and join_scope_args.
- PASS: 쉼표로 이은 값 하나를 넘기는 기존 방식은 그대로 동작한다.
  Reason: I ran the acceptance command (OK); test_single_comma_separated_scope_is_unchanged asserts 'scope: src/a.py, src/b.py' and passes on both the fixed and pre-fix trees, and join_scope_args only strips and joins values so a single value is kept as given.
```

## Retrospective

R-00000349 에 적었다.

## Promotion decision

not_applicable. 공식 기록으로 올릴 결정이 없다.

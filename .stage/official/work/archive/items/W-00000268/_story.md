---
id: W-00000268
title: 보관할 때 카드 폴더의 기록 아닌 파일도 함께 옮긴다
kind: fix
venue: claude
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -p test_archive_work.py -q"
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000268
promotion: not_applicable
review: passed
scope: stage/skills/stage-archive/archive_work.py, stage/scripts/tests/test_archive_work.py, stage/CHANGELOG.md
promotes:
decision_refs: DE-00000075
---

# W-00000268 보관할 때 카드 폴더의 기록 아닌 파일도 함께 옮긴다

## Purpose

카드 폴더에 둔 증거 파일이 보관과 함께 말없이 사라지지 않게 한다.

## Actions

- 지금 동작: `stage/skills/stage-archive/archive_work.py` 의 `archive_one()` 은 작업 기록
  (`record_data` 에 든 카드 `.md`)만 보관함에 새로 쓴다(450~472행 부근). 그다음
  `shutil.rmtree(source_unit)`(532행 부근)이 카드 폴더를 통째로 지운다. 그래서 작업 기록이
  아닌 파일은 보관함에 옮겨지지 않고 사라진다.
- 고칠 것: 카드 폴더 안에서 **보관할 때 다시 쓰는 작업 기록이 아닌 모든 파일**을 보관함의 같은
  상대 위치로 옮긴다. 이 종류에는 다음이 모두 들어간다.
  - `.md` 가 아닌 파일(예: `evidence.json`, 이미지)
  - 작업 기록이 아닌 `.md`(예: `notes.md`)
  - 하위 카드 폴더 안에 하위 카드 기록과 나란히 놓인 파일
  - 빈 하위 폴더를 뺀 모든 깊이의 하위 폴더 속 파일
- 작업 기록은 지금처럼 `status: archived` 로 바꿔 쓴다. 기록 아닌 파일은 내용을 바꾸지 않고
  바이트 그대로 옮긴다.
- 보관함에 같은 경로가 이미 있으면 지금의 "archive move unit already exists" 오류처럼 아무것도
  옮기기 전에 멈춘다. 일부만 옮긴 상태를 남기지 않는다.
- 카드 폴더가 아닌 단일 파일 카드(`source_unit` 이 파일)는 지금 동작을 유지한다.
- `stage/scripts/tests/test_archive_work.py` 에 위 종류마다 시험을 더한다.
- `stage/CHANGELOG.md` 의 `## Unreleased` 에 한 줄을 더한다(영어).

### 클라우드 세션 실행 계약 (DE-00000075)

이 카드는 Claude Code 클라우드 세션이 `claude/w268-cloud` 브랜치에서 실행한다. 클라우드에는
Stage 훅과 `.stage/.runtime/` 이 없다. 아래를 지킨다.

- 위 `scope` 의 세 파일만 바꾼다. 다른 파일을 바꿔야 하면 바꾸고 커밋 메시지에 그 경로와 이유를
  적는다. 이 카드의 `scope` 는 고치지 않는다.
- 이 카드의 frontmatter(`status`, `verification`, `review`, `promotion`, `retrospective`)와
  `.stage/` 아래 다른 파일은 건드리지 않는다. 판정·회고·닫기는 로컬에서 한다.
- 인수 명령과 scripts 전체 시험을 돌린다:
  `python3 -m unittest discover -s stage/scripts/tests -p test_archive_work.py -q`,
  `python3 -m unittest discover -s stage/scripts/tests -q`.
- 끝나면 `claude/w268-cloud` 브랜치에 커밋하고 push 한다. `main` 에는 push 하지 않는다.
- 커밋 메시지 본문에 `### Executor report` 를 쓴다. 칸은 `What changed:`, `Why:`,
  `Decisions made:`, `Work not done:`, `Changed paths (JSON):`(한 줄 JSON 배열),
  `Review request:` 이다. 보고할 것이 없는 칸은 `None` 으로 쓴다.
- 카드가 틀렸다고 판단하면 아무것도 바꾸지 말고 그 이유만 보고한다.

## User value

카드 폴더에 둔 실험 결과나 화면 캡처 같은 증거가 카드를 보관한 뒤에도 남는다. 보관한 카드를
다시 열었을 때 근거를 찾을 수 있다.

## Scope

### Included

- `archive_one()` 이 카드 폴더를 옮기는 방식
- 그 동작을 지키는 시험과 변경 기록 한 줄

### Excluded

- 회고 파일(`R-*.md`)과 결정 기록을 옮기는 방식. 지금 동작을 유지한다.
- 계획 카드(`planned`)를 거절해 보관하는 경로의 다른 동작
- 이미 보관된 카드에서 사라진 파일을 되살리는 일

## Risks

- 카드 폴더를 지우기 전에 옮기기가 중간에 실패하면 원본과 보관본이 둘 다 일부만 남을 수 있다.
  옮길 대상과 충돌을 먼저 모두 확인한 뒤 쓰기를 시작한다.

## Success criteria

- 카드 폴더 안의 `.md` 가 아닌 모든 파일(스토리 기록 옆, 하위 카드 기록 옆, 더 깊은 하위 폴더 속)이 보관함의 같은 상대 위치에 바이트 그대로 남는다는 것을 종류마다 시험이 확인한다
- 기록 파일은 지금처럼 status archived 로 바뀌고 기존 보관 테스트가 모두 통과한다

## Next action

클라우드 세션이 위 실행 계약대로 고치고 `claude/w268-cloud` 에 push 한다. 그 뒤 로컬에서
`claude --teleport <session-id>` 로 가져와 범위 대조(`git diff --name-only main...`), 인수 명령과
scripts 전체 시험, codex 판정을 하고 회고를 쓴 뒤 닫는다.

## Related truth


## Progress

- 2026-10-31 클라우드 세션 1회차(`dbaa56b7`)는 아무것도 바꾸지 않고 카드 전제 하나가 틀렸다고
  보고했다. 카드 폴더 안의 `.md` 는 모두 작업 기록으로 읽힌다(`stage/hooks/stage_record_paths.py`
  26행 `root.rglob("*.md")`). 그래서 감사와 보관이 그 파일을 막고, 말없이 사라지지 않는다.
  로컬에서 그 코드를 확인했다.
- 같은 세션에서 사용자가 1안(그 종류를 빼고 나머지를 고친다)을 골랐다고 2회차 실행 보고가
  적었다. 이에 따라 첫 번째 성공 기준에서 "작업 기록이 아닌 `.md`" 종류를 뺐다. 리뷰 전이라
  판 사이에 기준을 바꾸는 문제(O-00000052)에는 해당하지 않는다.
- 2회차(`0c2b194a`)가 고쳤다. 실행 보고 두 개는 커밋 메시지에서
  `.stage/.runtime/driver/logs/W-00000268.md` 로 옮겼다.
- 로컬 검증: 바뀐 경로 세 개가 모두 `scope` 안이다. 인수 명령 24개와 scripts 전체 663개가
  통과했다. `archive_work.py` 만 고치기 전으로 되돌리면 새 시험 두 개가 실패한다.


## Verification


### Executed at close — 2026-10-31

```
$ python3 -m unittest discover -s stage/scripts/tests -p test_archive_work.py -q
[exit 0]
----------------------------------------------------------------------
Ran 24 tests in 2.226s

OK

$ python3 -m unittest discover -s stage/scripts/tests -p test_archive_work.py -q
[exit 0]
----------------------------------------------------------------------
Ran 24 tests in 2.238s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (258 earlier lines omitted)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
[W-00000001] executor failed; retry 1/3
WARNING: preflights.codex is not configured; continuing without a venue health check
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1793423364
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1793423364. Human review + merge required; the base branch was not modified.
Removed unattended worktree: /private/var/folders/wg/6hnd_f255_z4ngk7ynwptym40000gn/T/tmphv03fcox/unattended/W-00000001-1793423364
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
Ran 664 tests in 117.369s

OK
```

### Review at close — 2026-10-31

```
Review report: .stage/.runtime/driver/logs/W-00000268.md
```

닫을 때 리뷰는 HEAD `0c2b194a` 를 대상으로 돌았다. 리뷰 명령과 모델 고정 시험은 W-00000286 커밋
`1ab2fdf5` 의 `.stage/settings.json` 과 `stage/scripts/tests/test_template_v4.py` 를 커밋하지 않고
덮어 쓴 상태였다(`standard` 프로필, `gpt-6-astra`, `--effort high`, `--write`). 이 브랜치의 설정으로는
리뷰가 승인해도 판정 파일을 쓰지 못해 닫기가 막혔다. 닫은 뒤 두 파일은 이 브랜치의 HEAD 로 되돌렸다.

## Retrospective

[R-00000268](../../retrospectives/R-00000268.md).

## Promotion decision

이 카드가 연결한 결정은 일회성 venue 예외(DE-00000075)뿐이므로 `not_applicable`이다.

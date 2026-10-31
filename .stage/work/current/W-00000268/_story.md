---
id: W-00000268
title: 보관할 때 카드 폴더의 기록 아닌 파일도 함께 옮긴다
kind: fix
venue: claude
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -p test_archive_work.py -q"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: pending
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

- 카드 폴더 안의 작업 기록이 아닌 모든 파일(`.md` 가 아닌 파일, 작업 기록이 아닌 `.md`, 하위 카드 폴더 안의 파일)이 보관함의 같은 상대 위치에 바이트 그대로 남는다는 것을 종류마다 시험이 확인한다
- 기록 파일은 지금처럼 status archived 로 바뀌고 기존 보관 테스트가 모두 통과한다

## Next action

클라우드 세션이 위 실행 계약대로 고치고 `claude/w268-cloud` 에 push 한다. 그 뒤 로컬에서
`claude --teleport <session-id>` 로 가져와 범위 대조(`git diff --name-only main...`), 인수 명령과
scripts 전체 시험, codex 판정을 하고 회고를 쓴 뒤 닫는다.

## Related truth


## Progress


## Verification


## Retrospective


## Promotion decision

---
id: W-00000125
title: 카드마다 자기 작업 트리에서 드라이버가 돈다
kind: development
venue: codex
milestone:
priority:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -q"
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000118
promotion: not_applicable
review: not_required
scope: stage/scripts/, stage/scripts/tests/, stage/skills/stage-drive/, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000125 카드마다 자기 작업 트리에서 드라이버가 돈다

## Purpose

DE-00000040 §2. 드라이버는 실행자 호출 전후로 저장소를 스냅샷 떠서 관측하므로(W-00000121), 둘이 같은 체크아웃에 있으면 서로의 변경을 자기 실행자 것으로 본다. git worktree 로 카드마다 트리와 브랜치를 주고 드라이버를 거기에 건다. 드라이버는 이미 --project-root 를 받으므로 가리키기만 하면 된다. 끝나면 어디를 병합하면 되는지 알려준다. 시도 기록은 .gitignore 라 트리마다 저절로 따로 논다.

## Actions

- 병렬 실행 명령을 만든다(`stage/scripts/` 아래, 파이썬). 카드 ID 를 여럿 받아 각각
  `git worktree` 와 브랜치를 만들고, 그 트리를 `--project-root` 로 삼아 드라이버를 건다.
- 트리와 브랜치 이름을 카드 ID 로 정한다. 사람이 나중에 보고 어느 카드의 것인지 알아야 한다.
- 끝나면 카드마다 결과와 **어느 브랜치를 병합하면 되는지** 알려준다. 병합은 사람이 한다 —
  드라이버가 커밋·닫기를 안 하는 것과 같은 이유다.
- 만들기에 실패하면 이미 만든 트리를 거둔다. 반쯤 만들어진 트리가 남으면 다음 실행이 그
  이름에 걸린다.
- `stage/skills/stage-drive/SKILL.md` 에 병렬로 도는 법과 그 한계를 적는다.
- `stage/CHANGELOG.md` 의 미출시 절에 적는다. **매니페스트 버전은 안 건드린다** —
  W-00000124 가 세운 새 규칙이다.

## User value

겹치지 않는 카드 여럿이 동시에 돈다. 지금은 하나가 끝나야 다음이 시작하므로, 카드마다
실행자가 6~10분 걸리는 것이 그대로 벽시계 시간이 된다.

## Scope

### Included


### Excluded


## Risks

- **worktree 안에서 훅이 다르게 동작할 수 있다.** Stage 훅은 작업 공간 뿌리에서 `.stage` 를
  찾는데, worktree 는 자기 `.stage` 사본을 갖는다. 실제로 worktree 에서 드라이버를 한 바퀴
  돌려 훅이 그 트리의 `.stage` 를 보는지 확인한다 — 코드를 읽어 추론하지 말고 돌려서 본다.
- 트리마다 카드 사본이 있으므로, 두 실행이 같은 카드를 집으면 둘 다 자기 사본을 고친다.
  겹침 거절은 W-00000126 이 하므로 이 카드는 **같은 카드를 두 번 걸면 어떻게 되는지**만
  밝혀 둔다.
- 병합에서 `.stage/work/active.md`·`review.md` 의 행이 부딪친다. 사람이 푸는 값이고 이
  카드가 없애지 않는다. 알려 주기만 한다.

## Success criteria

- 명령이 카드 여럿을 받아 각각 worktree·브랜치를 만들고 드라이버를 건다. 그 동작을 고정하는
  테스트가 있다.
- **worktree 에서 드라이버가 실제로 한 바퀴 돈 증거가 작업 로그에 있다** — 훅이 그 트리의
  `.stage` 를 보고, 실행자가 그 트리에서 일하고, 관측이 그 트리 기준으로 나온다. 코드 추론이
  아니라 실행 결과로 보인다.
- 만들기 중간에 실패하면 이미 만든 트리를 거둔다. 그 경우를 고정하는 테스트가 있다.
- 끝난 뒤 카드마다 병합할 브랜치 이름이 출력에 나온다.
- `stage/skills/stage-drive/SKILL.md` 가 병렬 실행법과 한계(같은 카드 중복, 인덱스 병합
  충돌)를 말한다.
- `python3 -m unittest discover -s stage/scripts/tests -q` 가 통과한다.
- `stage/CHANGELOG.md` 미출시 절에 항목이 있고 **매니페스트 버전은 그대로다**.

## Next action

끝나면 사람이 겹치지 않는 카드 둘을 실제로 동시에 걸어 본다. 그것이 이 에픽의 목적이
섰는지 보는 유일한 확인이다.

## Progress

드라이버 감독 실행 두 바퀴, 2026-07-29. 첫 바퀴는 리뷰어가 P1 으로 막았고 그 지적이 옳았다.
둘째 바퀴에서 기준 일곱 전부 PASS, APPROVED, 드라이버 판정도 통과. 테스트 432개.

## Verification

인수 검사 통과 — 스크립트 432개. 리뷰 판정: 기준 일곱 전부 PASS, APPROVED.

### 첫 바퀴가 막힌 이유 — 기준이 제 일을 했다

카드는 "worktree 에서 드라이버가 실제로 돌았다"를 코드 추론이 아니라 실행으로 보이라고
요구했다. 첫 실행자는 훅이 **허용**을 냈다는 것으로 증명하려 했는데, 리뷰어가 하네스 밖 빈
임시 폴더에서도 같은 허용이 나오는 것을 직접 돌려 보였다. 허용은 그 트리의 `.stage` 를
읽었다는 증거가 아니다.

리뷰어가 닫는 법까지 줬다 — 어느 카드 scope 에도 없는 경로에 쓰기를 넣고 **거절**을 확인하면
된다. 거절은 그 트리의 `.stage` 를 읽어야만 나온다. 둘째 바퀴가 그렇게 고쳤다.

**받았다.** 기준을 "코드로는 못 채우게" 쓴 것이 가짜 증거를 잡았다. 오늘 기준이 좁아서 목적을
못 세운 사례가 둘(W-00000116, W-00000124) 있었는데, 이번은 반대로 기준이 값을 했다.

### 리뷰 지적 처분 (기준 밖 여섯)

- **`claude` venue 경로는 검증 안 됐다 — 받는다, W-00000128 로.** probe 가 훅을 부르기 전에
  `CLAUDE_PROJECT_DIR`·`PROJECT_ROOT` 를 지우는데, 훅은 그 변수가 있으면 payload 의 `cwd`
  보다 먼저 쓴다. 즉 그 변수가 설정된 환경에서는 트리가 아니라 딴 곳의 `.stage` 로 판정할 수
  있다. 지금 이 환경에는 둘 다 없고 codex venue 는 그 변수를 안 쓰므로 무해하지만, `claude`
  venue 로 병렬을 돌리면 닿는다.
- **실행자 동시 개수에 상한이 없다 — 받는다, 같은 카드로.** 카드 10개를 걸면 실행자 10개가
  동시에 뜬다. `run_driver` 에 타임아웃도 없다. 상한 없는 팬아웃은 사고가 나면 크게 난다.
- **본 체크아웃이 더러우면 어느 트리도 그것을 못 본다 — 받는다, 같은 카드로.** 트리를 `HEAD`
  에서 만든다. `--unattended` 는 더러운 트리에서 거절하는데 이 명령은 검사도 경고도 없다.
- **드라이버 실패로 남은 트리를 거두는 명령이 없다 — 받는다, 같은 카드로.** 같은 카드를 다시
  걸려면 사람이 `git worktree remove` + `git branch -D` 를 손으로 해야 한다. O-00000007 과
  같은 모양이다 — 되돌리기가 명령이 아니면 사람이 손으로 상태를 맞춘다.
- **없는 카드 ID 를 넣어도 트리를 먼저 만든다 — 받는다, 같은 카드로.** 모양만 보고 존재를 안
  본다. 오타 하나로 트리와 브랜치가 남고 다음 실행이 그 이름에 걸린다.
- **정리 경로를 어느 테스트도 실행하지 않는다 — 안 받는다.** `cleanup_worktree` 를 mock 해서
  본문이 안 돈다. 리뷰어가 직접 돌려 동작을 확인했고, W-00000128 이 그 파일을 만지므로 그때
  실제 트리로 고정한다. 지금 따로 세우면 같은 파일을 두 번 여는 값이다.

### Executed at close — 2026-07-29

```
$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (132 earlier lines omitted)
Unattended run on isolated branch: stage/driver/W-00000001-1785314012 (base: main)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] close failed (acceptance or independent review); close_work output:
independent review did not pass; retry 1/2
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1785314012
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785314012. Human review + merge required; the base branch was not modified.
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
Ran 432 tests in 59.160s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (132 earlier lines omitted)
Unattended run on isolated branch: stage/driver/W-00000001-1785314071 (base: main)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] close failed (acceptance or independent review); close_work output:
independent review did not pass; retry 1/2
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1785314071
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785314071. Human review + merge required; the base branch was not modified.
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
Ran 432 tests in 59.074s

OK

$ python3 stage/scripts/audit_stage.py
[exit 0]
Stage audit: /Users/woogis/Workspace/repo/noory-ai/.stage
OK: no findings
Summary: errors=0, warnings=0
```

## Retrospective

[R-00000118](../../../retrospectives/R-00000118.md)

## Promotion decision

not_applicable — 플러그인 소스 수정이고 `.stage/official/` 로 올릴 것이 없다.

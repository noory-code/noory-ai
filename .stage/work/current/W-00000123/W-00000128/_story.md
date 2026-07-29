---
id: W-00000128
title: 병렬 실행이 안전하게 멈추고 되돌아온다
kind: fix
venue: codex
milestone:
source:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -q"
status: completed
verification: passed
retrospective: completed
retrospective_ref: R-00000119
promotion: not_applicable
review: not_required
scope: stage/scripts/drive_parallel.py, stage/scripts/tests/, stage/skills/stage-drive/SKILL.md, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000128 병렬 실행이 안전하게 멈추고 되돌아온다

## Purpose

W-00000125 가 병렬 실행을 열었지만 멈추는 자리와 되돌리는 자리가 비어 있다. 다섯을 닫는다. (1) claude venue 검증 구멍 — probe 가 CLAUDE_PROJECT_DIR·PROJECT_ROOT 를 지우고 훅을 부르는데, 훅은 그 변수가 있으면 payload cwd 보다 먼저 쓴다. 지우지 말고 트리와 같아야 한다고 주장해야 그 자리가 계약이 된다. (2) 실행자 동시 개수에 상한도 타임아웃도 없다 — 카드 10개면 실행자 10개. (3) 본 체크아웃이 더러우면 트리가 그것을 못 보는데 검사도 경고도 없다. (4) 드라이버 실패로 남은 트리를 거두는 명령이 없어 사람이 손으로 git worktree remove 를 해야 한다(O-00000007 과 같은 모양). (5) 없는 카드 ID 를 넣어도 트리를 먼저 만들고 나서 실패한다. 함께 정리 경로를 실제 트리로 고정하는 테스트를 넣는다.

## Actions

- probe 가 `CLAUDE_PROJECT_DIR`·`PROJECT_ROOT` 를 지우는 대신 **트리와 같아야 한다고
  주장**하게 바꾼다. 훅은 그 변수가 있으면 payload 의 `cwd` 보다 먼저 쓰므로, 지우면 그
  자리가 검증에서 빠진다. 주장으로 바꾸면 `claude` venue 로 병렬을 돌려도 트리가 지켜진다.
- 동시에 뜨는 실행자 수에 상한을 두고 인자로 받는다. `run_driver` 에 타임아웃을 건다.
- 시작할 때 본 체크아웃이 더러우면 멈춘다. 트리는 `HEAD` 에서 만들어지므로 커밋 안 한
  변경은 어느 트리에도 안 들어간다 — 조용히 빠지는 것이 가장 나쁘다.
- 남은 트리를 거두는 명령을 만든다. 사람이 `git worktree remove` + `git branch -D` 를 손으로
  하지 않게 한다.
- 카드 ID 의 **존재**를 트리를 만들기 전에 본다. 지금은 모양만 보고 만든 뒤에 실패한다.
- `cleanup_worktree` 본문을 실제 트리로 도는 테스트를 넣는다. 지금은 mock 이라 본문이 한
  번도 안 돈다.
- `stage/skills/stage-drive/SKILL.md` 에 상한·더러운 트리 거절·되돌리기 명령을 적는다.
- `stage/CHANGELOG.md` 미출시 절에 적는다. **매니페스트 버전은 안 건드린다.**

## Scope

`stage/scripts/drive_parallel.py` 와 그 테스트, `stage/skills/stage-drive/SKILL.md`,
`stage/CHANGELOG.md` 의 미출시 절.

**안 하는 것**: scope 겹침 거절 — W-00000126 이 한다. 드라이버 본체(`drive.py`) 수정.

## Success criteria

- probe 가 `CLAUDE_PROJECT_DIR`·`PROJECT_ROOT` 를 지우지 않고, 그 값이 트리와 다르면 실패로
  판정한다. 두 변수를 딴 뿌리로 걸어 놓고 돌려도 잡히는 것을 테스트가 고정한다.
- 동시 실행 수에 상한이 있고 인자로 바꿀 수 있다. 상한을 넘겨 걸면 나머지가 기다린다.
  테스트가 고정한다.
- 본 체크아웃이 더러우면 트리를 하나도 안 만들고 멈춘다. 메시지가 이유를 말한다. 테스트가
  고정한다.
- 없는 카드 ID 를 넣으면 트리를 **하나도 만들기 전에** 멈춘다. 테스트가 고정한다.
- 남은 트리를 거두는 명령이 있고, 실제 트리·브랜치를 만들어 지우는 것을 확인하는 테스트가
  있다. 그 테스트가 `cleanup_worktree` 본문을 실제로 돈다(mock 아님).
- `stage/skills/stage-drive/SKILL.md` 가 상한, 더러운 트리 거절, 되돌리기 명령을 말한다.
- `python3 -m unittest discover -s stage/scripts/tests -q` 가 통과한다.
- `stage/CHANGELOG.md` 미출시 절에 항목이 있고 매니페스트 버전은 그대로다.

### 되돌리는 명령이 되돌릴 수 없는 일을 하지 않는다

이 카드의 목적이 "안전하게 되돌아온다"이므로, 되돌리는 명령 자체가 안전해야 한다. 아래 넷을
같은 값으로 센다.

- **이 도구가 만들지 않은 것은 안 지운다.** git 의 워크트리 등록 정보로 확인하고, 등록된
  워크트리가 아닌 경로는 **거절한다**. 지금은 `git worktree remove` 가 실패하면 그 경로를
  통째로 `rmtree` 하므로, `--worktree-root` 를 잘못 적으면 엉뚱한 디렉터리가 사라지고 성공
  메시지가 나온다. 그 경우를 거절로 고정하는 테스트가 있다.
- **커밋된 일을 조용히 잃지 않는다.** 브랜치에 기준 브랜치로 안 들어간 커밋이 있으면 지우지
  않고 알린다. 없애려면 사람이 따로 밝혀야 한다. 안내된 흐름이 "사람이 커밋 → 병합"이므로 그
  창은 실제로 열린다. 그 경우를 고정하는 테스트가 있다.
- **없는 것을 지웠다고 하지 않는다.** 대상이 없으면 없다고 말한다.
- **`rmtree` 폴백 경로를 테스트가 실제로 돈다.** 가장 위험한 코드가 한 번도 안 도는 상태로
  남지 않는다.

### 시간이 다 돼도 밖에 뜬 것이 계속 돈다

`subprocess.run(timeout=)` 은 드라이버만 죽인다. 그 드라이버가 띄운 실행자·리뷰어는 살아서
그 트리에 계속 쓴다. 지금 명령은 그 사실을 안 알리고, 안내된 복구 수단(`--cleanup`)을 바로
돌리면 아직 쓰고 있는 트리를 밑에서 걷어낸다.

- 시간이 다 돼서 끊은 경우, 밖에 뜬 것이 아직 돌 수 있다는 것을 출력이 말한다. 그 상태에서
  바로 정리하지 말라고 알린다. 테스트가 그 메시지를 고정한다.
- 더 나아가 그 트리의 venue reaper 를 부를 수 있으면 부른다. 못 부르면 왜 못 부르는지
  출력에 남긴다 — 조용히 넘어가지 않는다.

## Related truth

- [DE-00000040](../../../official/decisions/records/DE-00000040.md) §2 — 병렬의 계약
- [R-00000118](../../../work/retrospectives/R-00000118.md) — 이 빈틈들이 드러난 경위
- [O-00000007](../../../state/observations/O-00000007.md) — 되돌리기가 명령이 아니면 사람이
  손으로 상태를 맞춘다. 남은 트리 정리가 같은 모양이다


## Progress

드라이버 감독 실행 두 바퀴, 2026-07-29. 첫 바퀴는 기준 여덟을 다 통과했으나 **안 닫았다** —
되돌리는 명령 자체가 위험했다. 기준 넷을 더하고 둘째 바퀴에서 열넷 전부 통과, APPROVED,
드라이버 판정도 통과. 테스트 437개.

## Verification

인수 검사 통과. 리뷰 판정: 기준 열넷 전부 PASS, APPROVED.

### 첫 바퀴를 왜 안 닫았나

리뷰가 APPROVED 를 냈고 기준 여덟이 다 섰는데, 기준 밖 지적이 이 카드의 목적을 깼다. 코드를
직접 열어 확인한 것 셋: `git worktree remove` 가 실패하면 그 경로를 통째로 `rmtree` 해서
`--worktree-root` 오타에 엉뚱한 폴더가 사라지고 성공 메시지가 나온다. `git branch -D` 가
미병합 커밋을 강제로 날린다. 시간이 다 돼도 밖에 뜬 실행자가 계속 도는데 출력이 그것을 안
말하고 정리를 권한다.

카드 제목이 "안전하게 멈추고 되돌아온다"이므로 이것은 기준 밖이 아니라 목적 그 자체다.
기준을 넷 더해 다시 돌렸다.

### 리뷰 지적 처분 (둘째 바퀴, 기준 밖 다섯)

- **리뷰어 venue 를 안 거둔다 — 받는다, W-00000129 로.** 시간이 다 됐을 때 도는 것이
  리뷰어일 수 있는데 코드가 카드 venue 로 reaper 를 고르고 역할을 executor 로 박는다.
  리뷰어는 계약상 다른 venue 라 살아남는다. 출력은 "executor or reviewer" 라고 말한다.
- **커밋 안 된 실행자 산출물을 말없이 지운다 — 받는다, 같은 카드로.** 미병합 커밋 보호가
  커밋된 것만 덮는다. 사람이 보라고 안내받은 그 변경이 경고 없이 사라진다.
- **트리만 사라지고 브랜치가 남으면 거둘 길이 없다 — 받는다, 같은 카드로.** 거절은 하지만
  메시지가 남은 브랜치가 아니라 없는 경로를 가리킨다.
- **SKILL.md 의 "그 실행이 만든 트리와 브랜치가 모두 제거된다"가 좁게 거짓 — 받는다, 같은
  카드로.** 브랜치를 만든 뒤 체크아웃에서 실패하면 브랜치가 남는다. 오류는 찍히므로 조용히
  남지는 않는다.
- **`git worktree list --porcelain -z` 가 옛 git 에서 안 된다 — 안 받는다.** 확인이 실패하면
  정리를 거절하므로 데이터는 안전하다. 이 호스트는 2.50.1 이다. 겪은 뒤에 본다.

### Executed at close — 2026-07-29

```
$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (142 earlier lines omitted)
Unattended run on isolated branch: stage/driver/W-00000001-1785316733 (base: main)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] close failed (acceptance or independent review); close_work output:
independent review did not pass; retry 1/2
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1785316733
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785316733. Human review + merge required; the base branch was not modified.
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
Ran 443 tests in 60.265s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (142 earlier lines omitted)
Unattended run on isolated branch: stage/driver/W-00000001-1785316793 (base: main)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] close failed (acceptance or independent review); close_work output:
independent review did not pass; retry 1/2
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1785316793
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785316793. Human review + merge required; the base branch was not modified.
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
Ran 443 tests in 60.245s

OK

$ python3 stage/scripts/audit_stage.py
[exit 0]
Stage audit: /Users/woogis/Workspace/repo/noory-ai/.stage
OK: no findings
Summary: errors=0, warnings=0
```

## Retrospective

[R-00000119](../../../retrospectives/R-00000119.md)

## Promotion decision

not_applicable — 플러그인 소스 수정이고 `.stage/official/` 로 올릴 것이 없다.

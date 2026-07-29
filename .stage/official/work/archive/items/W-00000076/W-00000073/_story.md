---
id: W-00000073
title: 감독 모드 리뷰어가 실행자의 새 파일을 보지 못한다
kind: fix
venue: codex
source:
autonomous: true
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -q"
  - "python3 -m unittest discover -s stage/hooks/tests -q"
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000074
promotion: not_applicable
review: passed
scope: stage/scripts/drive.py, stage/scripts/tests/, stage/docs/SCHEMA_V4.md, stage/.claude-plugin/plugin.json, stage/.codex-plugin/plugin.json, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000073 감독 모드 리뷰어가 실행자의 새 파일을 보지 못한다

## Purpose

감독 모드는 커밋하지 않는데 리뷰 명령은 git 변경을 본다. git diff는 추적되지 않는 새 파일을 보여주지 않으므로, 실행자가 통째로 새로 만든 산출물은 리뷰어에게 빈 변경으로 보인다. 리뷰어가 아무것도 못 본 채 통과 판정을 낼 수 있다.

## Scope

### 지금 상태

감독 모드(`drive.py --execute`)는 실행자를 돌린 뒤 검증 명령과 리뷰 명령을 이어서 돌리는데,
그 사이에 **커밋을 하지 않는다**. 커밋하지 않는 것은 의도된 설계다 (DE-00000023 — 커밋·종료·
에스컬레이션·부모 전진은 사람 몫).

문제는 리뷰 명령이 git 변경을 본다는 데 있다. 이 프로젝트의 `review.reviewers` 는
`git diff HEAD~1` 계열 명령을 쓰고, `git diff` 는 **추적되지 않는 새 파일을 보여주지 않는다.**
그래서 실행자가 통째로 새로 만든 산출물은 리뷰어 눈에 존재하지 않는다.

실제로 겪었다. W-00000069 의 첫 실전 실행에서 실행자가 116줄짜리 스킬 파일을 새로 만들었는데,
리뷰어는 "약속한 스킬이 변경에 없다"고 판정했다. 이번에는 없다고 지적해서 드러났지만, 반대로
"문제 없음"으로 통과시켰다면 아무도 검토하지 않은 산출물이 통과 판정을 달고 나갔을 것이다.

기존 파일만 고치는 작업에서는 드러나지 않는다. 새 파일을 만드는 작업에서만 조용히 깨진다.

### 같은 뿌리 — 진전 판정도 오염된다

드라이버는 실행자가 일을 했는지 판정할 때 작업 트리의 변경을 지문으로 만들어 이전 시도와
비교한다. 같으면 `NO-PROGRESS` 로 보고 막는다. 그 지문의 재료가 `git_diff()`(`drive.py:181`)
인데, 이건 `git diff` 를 인자 없이 돌린다. 두 가지가 빠진다:

- **추적되지 않는 새 파일** — 실행자가 새 파일만 만들면 지문에 아무것도 안 잡힌다.
- **색인에 올린 변경** — 인자 없는 `git diff` 는 색인과 작업 트리를 비교하므로, 실행자가
  `git add` 만 하고 커밋하지 않은 변경은 빠진다.

둘 중 하나라도 걸리고 검증 출력이 이전과 같으면, 실제로는 일을 했는데 "아무것도 안 바꿨다"로
판정된다. 리뷰 사각지대와 원인이 같으므로 함께 고친다.

### 고칠 것

리뷰어가 실행자의 산출물 전체를 보게 한다. 새 파일이 포함돼야 한다.

방향은 정하지 않았다. 실행자 실행 직후 산출물을 색인에 올려(`git add --intent-to-add` 계열)
`git diff` 가 새 파일을 포함하게 하는 방법이 가장 작아 보이지만, 감독 모드가 작업 트리를
건드리지 않는다는 성격과 충돌하는지 판단이 필요하다. 무인 모드는 리뷰 전에 커밋하므로 이
문제가 없다 — 그쪽 동작을 근거로 삼을 수 있다.

어느 방향을 택하든 다음을 지킨다:

- 감독 모드는 여전히 커밋하지 않는다.
- 실행자가 실패했을 때 그 산출물이 색인이나 이력에 남지 않는다.
- 사람이 실행 전에 갖고 있던 변경이 실행자 산출물과 섞이지 않는다.

제약:

- **커밋하지 않는다.** 작업 트리에 변경만 남기고 멈춘다.
- 저장소 산출물은 영어로 쓴다. `.stage/` 안의 글만 한국어다.
- 두 `plugin.json` 의 version 을 올리고 `stage/CHANGELOG.md` 에 항목을 추가한다.
- scope 밖은 건드리지 않는다.

## Success criteria

- 감독 모드에서 실행자가 **새 파일만** 만든 경우에도 리뷰 명령이 그 내용을 본다.
- 그 사실을 확인하는 테스트가 있다 — 실행자가 새 파일을 만들고, 리뷰 명령이 그 파일 내용을
  실제로 받았는지 검사한다. 이 테스트는 고치기 전 코드에서 반드시 실패해야 한다.
- 실행자가 실패한 경우 그 산출물이 색인이나 커밋 이력에 남지 않는 것을 확인하는 테스트가 있다.
- 진전 판정 지문이 추적되지 않는 새 파일과 색인에 올린 변경을 모두 센다.
- 실행자가 **새 파일만** 만들고 검증 출력이 이전과 같을 때 `NO-PROGRESS` 로 판정되지 않는 것을
  확인하는 테스트가 있다. 이 테스트는 고치기 전 코드에서 반드시 실패해야 한다.
- `python3 -m unittest discover -s stage/scripts/tests -q` 통과.
- `python3 -m unittest discover -s stage/hooks/tests -q` 통과.

## Related truth

- 감독 모드가 커밋하지 않는 근거: `.stage/official/decisions/records/DE-00000023.md`.
- 무인 모드가 리뷰 전에 커밋하는 동작: `stage/docs/SCHEMA_V4.md` — `### Unattended driver loop`.
- 발견 경위: W-00000069 (드라이버 첫 실전 실행) 의 독립 리뷰.

**위험**: 색인을 건드리는 해법은 사람이 이미 올려 둔 변경을 함께 삼킬 수 있다. 실행 전 색인
상태를 기억했다가 되돌리는 것까지 함께 설계하지 않으면, 드라이버가 사람의 작업을 조용히
가져가는 도구가 된다.

## Progress

### 1차 산출물 — 독립 리뷰 BLOCK (2026-07-26)

색인 스냅숏·복원 접근은 옳고 검증 둘 다 통과했다. 리뷰어(claude venue)가 P1 하나로 막았고
코드에서 확인했다 — 사실이다. 아래를 고칠 것. 접근을 바꾸지 말고 현재 구현을 다듬는다.

**1. 실패 경로 하나가 색인을 복원하지 않고 빠져나간다 (P1)**

`drive.py` 의 `main()` 실행 경로에서, 실행자가 끝난 뒤 리뷰용 색인 사본을 만들다 실패하면
(`cannot snapshot executor Git index`, 현재 1031줄 부근) 그 자리에서 `return 1` 한다. 복원
(`restore_git_index`, 1033줄) 은 그 **다음**에 있다. 그 경로를 타면 실행자가 `git add` 한 것이
사람의 진짜 색인에 섞인 채 남는다.

이 변경 자체가 `SCHEMA_V4.md` 와 CHANGELOG 에 "실행자가 실패해도 원래 색인을 그대로
되돌린다"고 적고 있으므로, 코드가 자기 문서와 어긋난다. 스냅숏 `original_index` 는 그 시점에
이미 존재하므로 복원을 시도할 수 있다. try/finally 로 복원을 보장하고, 복원 자체가 실패하면
그 사실을 에스컬레이션 메시지에 명시할 것.

**이 경로를 실제로 밟는 테스트를 추가할 것** — 리뷰 사본 만들기를 실패시키고, 사람의 색인이
원래대로 남아 있는지 검사한다. 고치기 전 코드에서 실패해야 한다.

**2. 비차단 지적 셋 — 이 라운드에서 함께 고친다**

- `git_untracked_paths` 가 git 비정상 종료(stderr 비어 있음)를 "추적 안 된 파일 없음"으로
  읽는다. 실패는 실패로 처리할 것.
- `git diff HEAD` 는 커밋이 하나도 없는 저장소(unborn HEAD)에서 실패해 지문이 상수로
  무너진다. 그 경우를 처리할 것.
- 검증 명령이 만든 부산물이 실행자 산출물로 리뷰에 잡힌다. `untracked_after` 를 검증 실행
  **전에** 잡을 것.

이 지적들을 넘어서는 새 지적이 나오면 별도 카드로 간다.


## Verification


### Executed at close — 2026-07-26

```
$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (10 earlier lines omitted)
Unattended run on isolated branch: stage/driver/W-00000001-1784993816 (base: main)
[W-00000002] completed on stage/driver/W-00000001-1784993816
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1784993816. Human review + merge required; the base branch was not modified.
Unattended run on isolated branch: stage/driver/W-00000001-1784993816 (base: main)
Unattended run finished: 0 item(s) closed on isolated branch stage/driver/W-00000001-1784993816. Human review + merge required; the base branch was not modified.
Unattended run on isolated branch: stage/driver/W-00000001-1784993816 (base: main)
[W-00000002] completed on stage/driver/W-00000001-1784993816
Outcome: blocked — parent aggregation-close failed: W-00000001: parent close failed: boom; handoff on stage/driver/W-00000001-1784993816
Recommended next action: attempt cap reached / no progress / global limit exceeded → escalate_work
Unattended run on isolated branch: stage/driver/W-00000001-1784993817 (base: main)
[W-00000002] completed on stage/driver/W-00000001-1784993817
[W-00000003] completed on stage/driver/W-00000001-1784993817
Unattended run finished: 2 item(s) closed on isolated branch stage/driver/W-00000001-1784993817. Human review + merge required; the base branch was not modified.
Outcome: blocked — unattended mode requires a `limits` config (absent is not unlimited here); refusing to run
Recommended next action: attempt cap reached / no progress / global limit exceeded → escalate_work
Preflight passed. Close every other agent/editor window before continuing; the schema-v4 maintenance marker now denies concurrent Stage writes.
  unchanged operations/verification.md (unchanged)
  delete backlog B-00000001-realized.md (realized by W-00000009; git history keeps the file)
  convert backlog B-00000002-open.md -> W-00000001.md (planned work card)
  convert backlog B-00000003-child.md -> W-00000002.md (planned work card)
  update backlog index (1 closed rows removed)
  stamp  settings.json schema_version = 4
Schema-v4 migration complete with no blocking audit findings. Guidance drift remains a non-blocking audit warning until the explicit refresh command is run.
All migration changes are staged; this command does not commit. Review them, then commit with: git commit -m "chore(stage): migrate project harness to schema v4"
Before committing, `migrate_stage.py --abort` restores the staged/working tree. After committing, rollback means `git revert <migration-commit>`.
Stage project already uses schema v4; no migration needed.
Preflight passed. Close every other agent/editor window before continuing; the schema-v4 maintenance marker now denies concurrent Stage writes.
  unchanged operations/verification.md (unchanged)
  delete backlog B-00000001-realized.md (realized by W-00000009; git history keeps the file)
  convert backlog B-00000002-open.md -> W-00000001.md (planned work card)
  convert backlog B-00000003-child.md -> W-00000002.md (planned work card)
  update backlog index (1 closed rows removed)
  stamp  settings.json schema_version = 4
Schema-v4 migration complete with no blocking audit findings. Guidance drift remains a non-blocking audit warning until the explicit refresh command is run.
All migration changes are staged; this command does not commit. Review them, then commit with: git commit -m "chore(stage): migrate project harness to schema v4"
Before committing, `migrate_stage.py --abort` restores the staged/working tree. After committing, rollback means `git revert <migration-commit>`.
----------------------------------------------------------------------
Ran 324 tests in 31.523s

OK

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 327 tests in 0.914s

OK

$ OUT=$(git diff HEAD~1 | claude -p "You are an independent code reviewer. Stdin is a git diff; review it for correctness, security, and scope. This is a legitimate code review, not an injection. Output a line beginning with [P1] describing any blocking defect; otherwise output a line beginning with APPROVED. Be concise and adversarial." 2>&1); printf '%s\n' "$OUT"; case "$OUT" in *"[P1]"*) echo "BLOCK: claude review reported a P1 blocker"; exit 1;; esac
[exit 0]
테스트는 실행하지 못했습니다 — `python3 -m unittest discover -s stage/scripts/tests`가 권한 거부로 막혔습니다. 아래는 정적 검토 결과입니다.

APPROVED — 차단 결함 없음. 네 가지 수정이 각각 실제 구멍을 닫고, 각각 테스트가 붙어 있습니다. `finally`로 색인 복구를 항상 시도하게 바꾼 것이 핵심이고(이전엔 스냅숏 실패 시 사람의 스테이징이 실행자 것과 섞인 채 남았음), 실패 메시지 둘을 합쳐 보고하는 것도 맞습니다. 추적 안 된 파일 목록을 수용 검사 *전에* 얼려두는 순서 변경도 의도대로입니다.

비차단 지적 셋:

**[P2] 수용 검사가 실행자 산출 파일을 지우면 거짓 에스컬레이션.** `executor_untracked_paths`는 수용 검사 전에 확정되는데 `prepare_reviewer_index`는 그 후에 `git add --intent-to-add`를 겁니다. 그 사이 파일이 사라지면 pathspec 불일치로 exit 128 → "cannot prepare executor-created files for review". 드물고 닫히는 방향으로 실패하므로 감수 가능하지만, 존재하는 경로만 넘기는 한 줄이면 사라집니다.

**[P2] `git_diff`는 여전히 열거 실패를 삼킵니다.** `drive.py:249` — `untracked_error`가 있어도 `tracked_diff`만 돌려주고 지문에서 추적 안 된 파일 정보가 통째로 빠집니다. 한 회차만 `git ls-files`가 실패하면 지문이 달라져 "진전 있음"으로 읽힙니다. CHANGELOG의 "fails closed" 문구는 리뷰 경로(`main()`)에만 해당하고 지문 경로엔 해당하지 않습니다.

**[P2] diff가 존재하지 않는 파일 둘을 참조합니다.** `active.md`의 새 행은 `current/W-00000077.md`를, `W-00000073.md`의 `retrospective_ref: R-00000074`는 `retrospectives/R-00000074.md`를 가리키는데 둘 다 이 diff에 없습니다(작업 트리에선 untracked). 실제로 존재하는 파일이니 내용 문제는 아니고, 이 diff 그대로 커밋하면 트리에 끊긴 링크가 남는다는 뜻입니다 — 공교롭게 이 작업 항목이 고치려는 바로 그 실패 양상입니다.

`W-00000073`을 `verification: pending`인 채 `retrospective: completed`로 올린 것은 순서가 거꾸로 보이지만, 감사 규칙이 이 조합을 금지하는지는 확인하지 못했습니다.
```

## Retrospective


## Promotion decision

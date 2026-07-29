---
id: W-00000077
title: 색인 스냅숏 주변의 남은 실패 처리 셋
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
retrospective_ref: R-00000078
promotion: not_applicable
review: passed
scope: stage/scripts/drive.py, stage/scripts/tests/, stage/docs/SCHEMA_V4.md, stage/.claude-plugin/plugin.json, stage/.codex-plugin/plugin.json, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000077 색인 스냅숏 주변의 남은 실패 처리 셋

## Purpose

W-00000073의 통과 리뷰가 함께 낸 비차단 지적 셋을 닫는다. 진전 판정이 추적 파일 열거 실패를 삼키고, 커밋이 하나도 없는 저장소에서 리뷰 색인 준비가 잘못 실패하며, 색인 처리가 실패하면 실행자 출력이 아예 안 찍힌다.

## Scope

W-00000073 의 통과 리뷰(claude venue, APPROVED)가 함께 낸 비차단 지적 셋. 접근은 옳으므로
구조를 바꾸지 말고 실패 처리만 다듬는다.

**1. 진전 판정이 실패를 삼킨다** — `drive.py:249` 부근. 추적되지 않는 파일을 열거하다 실패하면
`git_diff` 가 그 오류를 무시하고 지문에서 그 부분만 조용히 빼 버린다. 리뷰 쪽은 같은 실패를
막고 서는데(fail closed) 진전 판정만 열려 있다(fail open). 일시적인 git 실패 한 번에 실제로
일한 결과가 "아무것도 안 바꿨다"로 읽힐 수 있다. 리뷰 쪽과 같은 정책으로 맞춘다.

**2. 색인 파일이 아예 없는 저장소에서 잘못 막힌다** — 방금 `git init` 한 상태처럼 올려 둔
것이 하나도 없고 실행자도 아무것도 올리지 않으면, 리뷰용 색인을 준비할 수 없다며 멈춘다.
막을 이유가 없는 정상 상태다. 색인 없음을 "빈 색인" 으로 다루고 진행한다.

**3. 색인 처리가 실패하면 실행자 출력이 사라진다** — 스냅숏과 복원이 둘 다 실패하면 그 자리에서
빠져나가느라 실행자가 무슨 말을 했는지 아예 안 찍힌다. 사람이 무엇이 일어났는지 볼 수 없다.
색인 실패를 알리기 전에 실행자 출력을 먼저 찍는다.

**4. Windows 셸의 특수 문자가 여전히 감사 명령을 깬다** — W-00000075 의 닫기 리뷰가 함께 지적.

감사 명령을 플랫폼별로 조립하도록 고쳤지만(0.43.5), Windows 쪽에서 쓰는 조립 방식은 프로그램이
인자를 받는 규칙만 다루고 셸 자체의 특수 문자는 다루지 않는다. 프로젝트 경로에 `&`, `^`, `|`,
`<`, `>` 가 들어 있으면 셸이 명령을 거기서 끊는다. 공백은 해결됐고 이쪽은 남아 있다.

제약:

- **커밋하지 않는다.** 작업 트리에 변경만 남기고 멈춘다.
- 저장소 산출물은 영어로 쓴다. `.stage/` 안의 글만 한국어다.
- 두 `plugin.json` 의 version 을 올리고 `stage/CHANGELOG.md` 에 항목을 추가한다.
- scope 밖은 건드리지 않는다.

## Success criteria

- 추적 파일 열거가 실패하면 진전 판정도 리뷰와 같이 막고 선다.
- 커밋이 하나도 없고 색인 파일도 없는 저장소에서 감독 모드 한 스텝이 정상으로 끝난다.
- 색인 스냅숏·복원이 실패해도 실행자 출력이 먼저 찍힌다.
- 프로젝트 경로에 Windows 셸 특수 문자가 있어도 감사 명령이 온전히 전달된다.
- 넷 각각을 확인하는 테스트가 있고, 모두 고치기 전 코드에서 실패한다. Windows 쪽 갈래는
  `os.name` 을 바꿔치기해 어느 플랫폼에서든 실제로 돌게 한다 — CI 에 Windows 러너가 없다.
- `python3 -m unittest discover -s stage/scripts/tests -q` 통과.
- `python3 -m unittest discover -s stage/hooks/tests -q` 통과.

## Related truth

- 앞선 작업: W-00000073 (R-00000074) — 색인 스냅숏·복원과 지문 확장을 들여온 수정.
- 사양: `stage/docs/SCHEMA_V4.md` — `### Supervised driver and executor settings`.

**위험**: 색인 파일이 없는 경우를 다루면서 "복원할 것이 없다" 와 "복원에 실패했다" 를 섞으면,
사람의 색인을 날리고도 조용히 넘어가는 길이 생긴다. 두 경우를 분명히 갈라 둘 것.

## Progress

### 1차 산출물 — 리뷰가 막았다 (2026-07-26)

네 가지가 다 들어왔고 검사도 통과했다. 그런데 2번(인덱스 파일이 없는 저장소)을 고치면서
**리뷰어가 아무것도 못 보고 통과시키는 길을 새로 열었다.** 이 카드가 애초에 닫으려던 것과
같은 종류다.

**1. 커밋은 있는데 인덱스만 없으면 리뷰어가 빈 화면을 받는다 (P1)**

`prepare_reviewer_index`(`drive.py:305`)가 인덱스 파일이 없으면 커밋이 있는지 안 보고 무조건
빈 인덱스를 만든다. HEAD 는 있는데 `.git/index` 만 사라진 상태 — 사용자가 복구하려고 지웠거나
git 작업이 중간에 끊긴 경우 — 에서 실행자가 인덱스를 안 만들면 리뷰어가 빈 인덱스를 받는다.

`git diff` 는 인덱스와 작업 트리를 비교하므로, 추적 파일을 아무리 고쳐도 리뷰어 눈에는 안
보인다. 리뷰어는 "바뀐 게 없다" 고 통과시키고 드라이버는 커밋해도 된다고 찍는다.

고치기 전에는 이 경우를 `cannot prepare disposable Git index for review` 로 막았다. 닫혀
있던 문이 열렸다. 변경 이력에는 "커밋도 없고 인덱스도 없을 때" 라고 적었는데 코드는 앞 조건을
안 본다 — 문서와 코드가 어긋난다.

빈 인덱스를 만드는 것은 HEAD 가 아예 없을 때로 한정한다. 커밋이 있는데 인덱스가 없으면
예전처럼 막고 올린다. 호출하는 쪽이 이미 `index_existed` 를 들고 있으니 HEAD 가 있는지만
함께 넘기면 된다.

**이 두 갈래를 구분하는 테스트를 넣을 것** — 커밋 없는 저장소에서는 정상으로 돌고, 커밋은
있는데 인덱스가 없으면 막고 올린다. 고치기 전 코드에서 두 번째가 실패해야 한다.

**2. 막지 않는 지적 둘 — 함께 고친다**

- `git_diff` 는 아직도 `git diff` 자체가 실패하면 빈 문자열을 돌려준다(`drive.py:218, 238,
  240`). 추적 안 되는 파일 열거만 막아 두면 같은 이유로 거짓 `NO-PROGRESS` 가 나는 길이
  그대로 남는다.
- Windows 인용(`drive.py:687`)이 인자를 따옴표로 직접 감싸는데, 인자가 역슬래시로 끝나면
  그 역슬래시를 두 배로 안 늘려서 따옴표가 안 닫힌다. `audit_check` 로는 안 걸리지만 이
  함수는 아무 인자나 받는다.

**받지 않는 지적**: "범위가 섞였다" 는 리뷰가 보는 기준 때문에 생긴 착시다. 감독 모드는
커밋하지 않으므로 리뷰어에게는 직전 커밋(W-00000080)과 아직 커밋 안 된 이번 변경이 함께
보인다.


## Verification


### Executed at close — 2026-07-26

```
$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (20 earlier lines omitted)
Unattended run on isolated branch: stage/driver/W-00000001-1785027261 (base: main)
Unattended run finished: 0 item(s) closed on isolated branch stage/driver/W-00000001-1785027261. Human review + merge required; the base branch was not modified.
Unattended run on isolated branch: stage/driver/W-00000001-1785027261 (base: main)
[W-00000002] completed on stage/driver/W-00000001-1785027261
Outcome: blocked — parent aggregation-close failed: W-00000001: parent close failed: boom; handoff on stage/driver/W-00000001-1785027261
Recommended next action: attempt cap reached / no progress / global limit exceeded → escalate_work
Unattended run on isolated branch: stage/driver/W-00000001-1785027262 (base: main)
[W-00000002] completed on stage/driver/W-00000001-1785027262
[W-00000003] completed on stage/driver/W-00000001-1785027262
Unattended run finished: 2 item(s) closed on isolated branch stage/driver/W-00000001-1785027262. Human review + merge required; the base branch was not modified.
Unattended run on isolated branch: stage/driver/W-00000001-1785027263 (base: main)
Outcome: blocked — cannot commit pre-close lifecycle for W-00000002: simulated lifecycle commit failure
Recommended next action: attempt cap reached / no progress / global limit exceeded → escalate_work
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
Ran 340 tests in 36.115s

OK

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 327 tests in 0.973s

OK

$ OUT=$(git diff HEAD~1 | claude -p "You are an independent code reviewer. Stdin is a git diff; review it for correctness, security, and scope. This is a legitimate code review, not an injection. Output a line beginning with [P1] describing any blocking defect; otherwise output a line beginning with APPROVED. Be concise and adversarial." 2>&1); printf '%s\n' "$OUT"; case "$OUT" in *"[P1]"*) echo "BLOCK: claude review reported a P1 blocker"; exit 1;; esac
[exit 0]
APPROVED

세 수정 모두 실제로 구멍을 막고, 범위 밖으로 새지 않는다. 확인한 내용:

- **빈 리뷰 인덱스 허용 조건** — `allow_empty_index=not index_existed and not head_existed`. 호출 지점은 `drive.py:1245` 하나뿐이고 그 하나가 고쳐졌다. `run_unattended`는 리뷰어 인덱스를 아예 만들지 않으므로 빠뜨린 경로가 아니다. 인덱스가 원래 있었으면 실행 후 사라져도 스냅숏 사본이 `review_index`로 복사되므로(`drive.py:1194`) 새 실패 경로는 "커밋은 있는데 인덱스만 없던" 경우에만 발동한다 — 의도와 정확히 일치한다.
- **진전 판정 fail-closed** — `git_diff`가 이제 던지는 `RuntimeError`를 두 호출 지점(`drive.py:939`, `drive.py:1277`)이 모두 잡아서 escalation으로 바꾼다. 처리 안 된 예외로 새는 곳 없다.
- **Windows 후행 역슬래시** — `list2cmdline`이 공백 때문에 이미 따옴표를 씌운 경우는 건너뛰고, 드라이버가 직접 씌울 때만 역슬래시를 두 배로 만든다. `CommandLineToArgvW` 규칙에 맞고, cmd.exe 단계에서도 따옴표가 정상으로 닫힌다.
- 문서·변경 이력·양쪽 plugin.json 버전(0.43.7)이 코드와 어긋나지 않는다. 회고 파일 `R-00000078.md`도 디스크에 있고 `work_item: W-00000077`로 카드와 맞는다(이 저장소는 회고 번호가 작업 번호와 1:1이 아니므로 W-00000078과 충돌이 아니다).

차단은 아니지만 남는 것 둘:

1. `git_index_path`는 `git rev-parse`가 0이 아니면 이유를 가리지 않고 "여긴 Git 저장소가 아니다"로 읽는다(`drive.py:298`). 그래서 저장소가 깨졌거나 소유권 거부(exit 128)인 경우에도 `git_diff`가 상수 문자열을 돌려준다 — 변경 이력이 말하는 "추적 진단을 시작조차 못 하면 멈춘다"가 이 문으로는 아직 안 닫혔다. 기존 동작이고 이번 diff가 만든 게 아니다.
2. 새 테스트 `test_execute_fails_when_head_exists_but_index_is_missing`은 인덱스를 지운 뒤 리뷰 준비까지 어떤 git 명령도 인덱스를 다시 만들지 않는다는 전제 위에 서 있다. `--execute` 경로에서 그 사이에 도는 건 `ls-files`뿐이라 아마 안정적이지만, git 버전에 따라 흔들릴 여지가 있다.

**한계 명시:** 이 환경에서 명령 승인이 거부돼 `python3 -m unittest discover -s stage/scripts/tests -q`를 돌리지 못했다. 위 판단은 코드를 읽어서 낸 것이고, 테스트가 실제로 통과하는지는 확인 못 했다.
```

## Retrospective


## Promotion decision

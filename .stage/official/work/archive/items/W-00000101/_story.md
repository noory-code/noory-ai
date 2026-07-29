---
id: W-00000101
title: 드라이버가 끝날 때 자기가 띄운 실행자를 거둔다
kind: fix
venue: codex
priority: 1
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -q"
  - "python3 -m unittest discover -s stage/hooks/tests -q"
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000100
promotion: not_applicable
review: not_required
scope: stage/scripts/drive.py, stage/scripts/tests/test_drive_unattended.py, stage/scripts/tests/test_drive.py, .stage/settings.json, stage/skills/stage-drive/SKILL.md, stage/.claude-plugin/plugin.json, stage/.codex-plugin/plugin.json, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000101 드라이버가 끝날 때 자기가 띄운 실행자를 거둔다

## Purpose

2026-07-27, W-00000096 을 무인으로 돌린 뒤 코덱스 위임이 두 번 연속 실패했다. 원인은 드라이버가
띄운 실행자 작업이 드라이버가 끝난 뒤에도 살아 있었기 때문이다 — 43분째 검증 단계에 매달린 채였다.
코덱스 런타임은 한 번에 작업 하나만 받으므로, 그 껍데기가 이후 모든 위임을 막았다.

막힌 쪽에 보이는 것은 "다른 작업이 돌고 있다" 뿐이라 원인처럼 안 보인다. 사람이 살아 있는 작업
목록을 뒤져야 알 수 있다.

## Source

W-00000099 검증 중 관찰 (2026-07-27). 위임 세 번 중 두 번이 이것 때문에 헛돌았다.

## User value

무인 실행 다음에 오는 작업이 조용히 막히지 않는다. 지금은 사람이 원인을 찾아 손으로 정리해야
다음 일이 돈다.

## Scope

### Included

- 드라이버가 스텝을 끝낼 때(성공이든 실패든) 자기가 띄운 실행자·리뷰어 작업이 살아 있으면
  거둔다.
- 거둘 수 없으면 그 사실을 출력에 남긴다 — 조용히 두고 가지 않는다.

### Excluded

- 실행자 도구가 왜 검증 단계에서 매달렸는지는 이 카드가 다루지 않는다. 거두는 쪽만 고친다.
- 사전 점검·생존 감시는 W-00000092 몫이다.

## Dependencies

DE-00000034 의 C5 층이다. 계약의 "한 바퀴가 실패하면 무엇이 남는가" 절 규칙 3 — 그 바퀴가 밖에
띄운 프로그램은 바퀴가 끝나면 거둔다. 성공이든 실패든.

## Risks

- 거두는 방법이 도구마다 다르다. 드라이버에 도구 이름을 박으면 도구 중립이 깨진다 —
  설정으로 받아야 한다 (DE-00000034 규칙 4).

## Success criteria

- 무인 실행이 끝난 뒤 그 실행이 띄운 실행자·리뷰어 작업이 살아 있지 않다. 확인 테스트가 있고,
  고치기 전 코드에서 실패한다.
- 거두지 못한 경우 그 사실이 출력에 남는다. 확인 테스트가 있다.
- 거두는 방법에 도구 이름이 박히지 않는다.
- 밖에 띄우는 것이 없는 venue 를 설정에 밝힐 수 있다. 그렇게 밝힌 venue 에서는 경고가 나지
  않는다. 확인 테스트가 있고, 고치기 전 코드에서 실패한다.
- 인수 검사 두 개가 통과한다. 버전을 올리고 CHANGELOG 에 적는다.

## Next action

W-00000100 과 W-00000097 이 닫힌 뒤 시작한다.

## Progress

- 2026-07-27: 감독·무인 경로에서 실행자 성공/실패, 리뷰어 차단, 시도 상한, 설정 누락과 정리
  명령 실패를 먼저 고정하는 회귀 테스트를 추가했다. 기존 코드에서 설정된 명령이 실행되지 않고
  경고가 출력·공용 로그에 남지 않는 이유로 감독 3건과 무인 2건의 RED를 확인했다.
- 2026-07-27: `reapers.<venue>` 선택을 도입해 실행자와 리뷰어 turn이 끝날 때 설정 명령을
  실행하게 했다. 설정 누락은 기존 결과를 바꾸지 않고 출력과 공용 로그에 경고하며, 설정된
  명령의 실패는 다음 외부 turn 전에 실행을 멈춘다. reaper에는 카드 경로와 역할을 넘겨 같은
  작업공간의 다른 job을 건드리지 않게 했다. 집중 테스트와 기존 두 드라이버 테스트 파일이
  GREEN이다.
- 2026-07-27: 최종 인수 검사에서 scripts 377개와 hooks 327개가 모두 통과했다. 두
  매니페스트를 0.48.0으로 맞추고 CHANGELOG와 stage-drive 설정 문서를 갱신했다.
- 2026-07-27: `reapers.<venue>: null` 을 밖에 띄우는 것이 없다는 명시적 선언으로 고정했다.
  감독·무인 경로의 회귀 테스트를 먼저 추가했고, 기존 코드가 `null` 을 유효하지 않은 명령으로
  경고해서 실패하는 RED를 확인했다. 구현 뒤 `null` 은 명령도 경고도 만들지 않고, venue 누락은
  기존 경고를 유지하는 집중 테스트가 GREEN이다. 이미 반영된 0.49.0 뒤의 패치로 두
  매니페스트를 0.49.1로 올리고 CHANGELOG와 stage-drive 설정 문서를 갱신했다.

## Verification

사람이 직접 확인했다 (실행자 진술을 근거로 쓰지 않는다 — DE-00000034 규칙 2).

- 거두는 명령을 설정에서 받는다 (`.stage/settings.json` 의 `reapers`, venue 별). 없어도 실행이
  깨지지 않는다 (`resolve_reap_command`, drive.py:488).
- 드라이버에 도구 이름이 하나도 없다 — `drive.py` 에서 `codex`/`claude` 문자열이 0 회.
- 못 거두거나 설정이 없으면 출력과 공용 로그에 남는다. 확인 테스트가 있다.
- 성공한 바퀴와 실패한 바퀴 양쪽에서 거둔다. 확인 테스트가 있다.
- 확인 테스트가 여섯 개 늘었다 (감독·무인 각각 성공·실패·설정 없음).
- 인수 검사를 직접 돌렸다: scripts 377개 OK, hooks 327개 OK. 감사 오류 0.
- 버전 SSOT 둘 다 0.48.0, CHANGELOG 갱신됨.

기준 밖 관찰 (받지 않음, 기록만):

- 코덱스 세션은 `.git` 을 못 써서 커밋은 사람이 했다.

### Executed at close — 2026-07-27

```
$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (112 earlier lines omitted)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] review infrastructure failure; retry without spending attempt 0/1
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1785137792
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785137792. Human review + merge required; the base branch was not modified.
Unattended run on isolated branch: stage/driver/W-00000001-1785137793 (base: main)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
Unattended run finished: 0 item(s) closed on isolated branch stage/driver/W-00000001-1785137793. Human review + merge required; the base branch was not modified.
Unattended run on isolated branch: stage/driver/W-00000001-1785137794 (base: main)
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1785137794
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785137794. Human review + merge required; the base branch was not modified.
Unattended run on isolated branch: stage/driver/W-00000001-1785137795 (base: main)
Unattended run finished: 0 item(s) closed on isolated branch stage/driver/W-00000001-1785137795. Human review + merge required; the base branch was not modified.
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
Ran 389 tests in 58.726s

OK

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 327 tests in 0.988s

OK

$ python3 stage/scripts/audit_stage.py --project-root .
[exit 0]
Stage audit: /Users/woogis/Workspace/repo/noory-ai/.stage
OK: no findings
Summary: errors=0, warnings=0
```

## Retrospective

## Promotion decision

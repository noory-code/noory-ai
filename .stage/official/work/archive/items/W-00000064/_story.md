---
id: W-00000064
title: 보관할 때 그 작업의 남은 예약을 치운다
kind: development
venue: codex
priority: high
autonomous: false
acceptance: []
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000063
promotion: not_applicable
scope: stage/skills/stage-archive/, stage/scripts/, stage/hooks/, stage/CHANGELOG.md, stage/.claude-plugin/plugin.json, stage/.codex-plugin/plugin.json
promotes:
decision_refs:
---

# W-00000064 보관할 때 그 작업의 남은 예약을 치운다

## Purpose

작업이 보관되면 그 작업 이름으로 만든 예약(intent)도 함께 사라져야 한다. 지금은 남아서 나중에
같은 파일을 건드릴 때 충돌로 터진다

## Source

Q-00000002의 곁가지. 오늘 실제로 겪었다 — W-00000053이 남긴 예약 11장이 오늘까지 있다가,
W-00000061이 같은 파일(`official/decisions/index.md`)에 예약을 만들자 "두 예약이 같은 대상을
가리킨다"며 거부됐다. 손으로 지우고 나서야 진행됐다.

## User value

보관을 마친 작업이 뒤에 아무것도 남기지 않는다. 몇 달 뒤 같은 파일을 승격하려는 사람이 남의
찌꺼기 때문에 막히지 않는다.

## Scope

### Included

- 작업을 보관할 때 그 작업 이름으로 된 남은 예약 파일을 함께 지운다. 예약은
  `.stage/.runtime/intents/`에 `<작업id>--<파일명>-<해시>.json` 형태로 있다.
- 이미 남아 있는 찌꺼기 처리: 보관이 끝난 작업의 예약이 남아 있으면 감사가 알린다. 새 코드가
  생기기 전에 만들어진 것들이 있으므로 감사가 잡아 주지 않으면 영영 남는다.
- 위 두 가지에 대한 테스트.
- 변경 기록과 두 매니페스트 버전(고침이므로 patch).

### Excluded

- 예약 구조나 소비 방식 변경. 지금 방식(경로마다 한 장, 소비는 삭제) 그대로 둔다.
- 프로그램이 파일을 고칠 때 잠금장치가 개입하지 못하는 문제(Q-00000002 본체). 그건 문서로
  경계를 밝히는 쪽으로 답이 났고 별도 작업이다.

## Dependencies

없음.

## 이미 확인된 것

- 예약을 만드는 곳: `stage/scripts/promote_intent.py`. 경로마다 파일 한 장을 만들고, 이름은
  `<작업id>--<파일명>-<해시10자>.json`이다. 실제 기록은 `stage/hooks/stage_guard.py`의
  `write_intent_file()`이 한다.
- 소비하는 곳: `PostToolUse` 훅. 도구가 실제로 파일을 고친 뒤 예약 파일을 지운다. 그래서
  프로그램으로 고치면 예약이 남는다.
- 충돌 판정: 같은 대상을 가리키는 예약이 둘 이상이면 거부한다. 오늘 그 메시지는
  "multiple pending intents cover the modification targets"였다.
- 보관하는 곳: `stage/skills/stage-archive/archive_work.py`. 여기가 정리하기 좋은 자리다.
- `.stage/.runtime/`은 git이 무시한다. 지워도 이력에 영향이 없다.

## Risks

- 아직 안 끝난 다른 작업의 예약까지 지우면 그 작업이 막힌다. 지우는 대상은 지금 보관하는
  작업 이름으로 시작하는 것만이어야 한다.

## Success criteria

- 예약이 남은 작업을 보관하면 그 예약들이 사라진다.
- 다른 작업의 예약은 그대로 남는다.
- 보관이 끝난 작업의 예약이 남아 있으면 감사가 알린다.
- `python3 -m unittest discover -s stage/scripts/tests -q`와 `-s stage/hooks/tests -q` 통과.

## Next action

codex 창에서 아래로 시작한다.

```
python3 stage/scripts/start_work.py --project-root . W-00000064 \
  --scope "stage/skills/stage-archive/, stage/scripts/, stage/hooks/, stage/CHANGELOG.md, stage/.claude-plugin/plugin.json, stage/.codex-plugin/plugin.json"
```

테스트부터 쓴다. 커밋하지 않는다 — 검토와 커밋은 맡긴 쪽이 한다(`stage-handoff`의 위임 실행).

venue: codex(development).

## Progress

구현은 codex 창이 위임 실행했고(모델 `gpt-5.6-sol`), 검토와 커밋은 claude 창이 했다. 0.40.1에서
문서로 정한 위임 순서를 처음 그대로 따른 실행이다 — 코덱스가 커밋하지 않고 작업 트리를 둔 채
넘겼고, 이쪽이 테스트를 직접 다시 돌린 뒤 커밋했다.

만들어진 것:

- `stage_runtime.py` — 작업 하나가 가진 예약을 찾고 지우는 함수. `<작업id>--` 접두사로 정확히
  맞춰서 옆 번호(W-6과 W-61 같은)가 섞이지 않는다.
- `archive_work.py` — 보관 직전에 그 작업의 예약을 지운다. 하나라도 못 지우면 보관을 거부한다.
- `audit_stage.py` — 이미 보관된 작업의 예약이 남아 있으면 `WORK025`로 알린다. 이 변경 전에
  생긴 찌꺼기는 이것이 없으면 영영 안 보인다.

검토에서 확인한 것: 테스트 311개(2개 늘었다)와 324개 통과, 검사 오류 0 경고 0. 카드에 위험으로
적어둔 "다른 작업 예약까지 지우면 안 된다"가 그대로 테스트가 됐다.

시작이 한 번 막혔다. 오늘 플러그인 버전을 세 번 올렸는데, 이미 떠 있던 코덱스가 없어진 옛
버전 폴더(0.39.1)의 훅을 찾다가 파일 읽기조차 못 했다. 그 프로세스를 내리고 다시 부르니 풀렸다.
P-00000001이 예상한 문제이며 오늘 처음 실제로 막았다.

## Verification

### Executed at close — 2026-07-25

```
$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (7 earlier lines omitted)
Unattended run on isolated branch: stage/driver/W-00000001-1784979196 (base: main)
[W-00000002] completed on stage/driver/W-00000001-1784979196
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1784979196. Human review + merge required; the base branch was not modified.
Unattended run on isolated branch: stage/driver/W-00000001-1784979196 (base: main)
Unattended run finished: 0 item(s) closed on isolated branch stage/driver/W-00000001-1784979196. Human review + merge required; the base branch was not modified.
Unattended run on isolated branch: stage/driver/W-00000001-1784979196 (base: main)
[W-00000002] completed on stage/driver/W-00000001-1784979196
Outcome: blocked — parent aggregation-close failed: W-00000001: parent close failed: boom; handoff on stage/driver/W-00000001-1784979196
Recommended next action: attempt cap reached / no progress / global limit exceeded → escalate_work
Unattended run on isolated branch: stage/driver/W-00000001-1784979197 (base: main)
[W-00000002] completed on stage/driver/W-00000001-1784979197
[W-00000003] completed on stage/driver/W-00000001-1784979197
Unattended run finished: 2 item(s) closed on isolated branch stage/driver/W-00000001-1784979197. Human review + merge required; the base branch was not modified.
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
Ran 311 tests in 30.273s

OK

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 324 tests in 0.898s

OK

$ python3 stage/scripts/audit_stage.py --project-root .
[exit 0]
Stage audit: /Users/woogis/Workspace/repo/noory-ai/.stage
OK: no findings
Summary: errors=0, warnings=0
```

## Retrospective

## Promotion decision

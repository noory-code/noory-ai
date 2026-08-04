---
id: W-00000200
title: 보관 서랍 셋을 토폴로지에 등록한다
kind: development
venue: codex
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/hooks/tests -p test_stage_topology.py -q"
status: completed
verification: passed
retrospective: completed
retrospective_ref: R-00000199
promotion: not_applicable
review: not_required
scope: stage/hooks/stage_topology.py, stage/scripts/audit_stage.py, stage/scripts/init_stage.py, stage/templates/, stage/hooks/tests/test_stage_topology.py, stage/scripts/tests/test_audit_stage.py, stage/scripts/tests/test_init_stage.py
promotes:
decision_refs:
---

# W-00000200 보관 서랍 셋을 토폴로지에 등록한다

## Purpose

보관 자리가 등록되지 않으면 옮긴 기록을 가리키는 기존 링크가 끊기고 감사가 소유 위치 위반으로 잡으므로, 결정·제안·상태의 보관 서랍을 참조 해석과 감사와 초기화가 함께 아는 자리로 만든다

## Actions

없음 — 자리 등록 한 덩어리다. 참조 해석과 감사 소유 위치가 같은 한 표에서 나오므로 나눌 선이 없다.

## User value

기록을 보관함으로 옮겨도 그것을 가리키던 인용이 그대로 열린다. 새 프로젝트를 시작하면 보관
서랍이 처음부터 있다.

## Scope

### Included

- `official/decisions/archive`, `official/proposals/archive`, `official/state/archive` 세 자리를
  토폴로지 등록부에 넣는다. 각 자리의 수명주기는 `official` 이다.
- 참조 해석이 갈래마다 들고 있는 후보 경로에 보관 경로를 더한다. 감사의 소유 위치 표가
  거기서 나오므로, 한 자리를 고치면 둘이 같이 맞는다.
- 새 프로젝트 초기화가 세 서랍과 그 README·인덱스를 만든다.
- 감사가 관측·질문·제안의 필수 절 누락을 잡는다. 지금 O-00000024~29 에는 상태 절이 통째로
  없는데 아무도 안 잡았다.
- 새 서랍이 `index.md` 라우팅 검사를 통과한다.

### Excluded

- 기록을 실제로 옮기지 않는다. 옮기는 쪽은 W-00000201·202 다.
- 스키마 버전은 안 올린다. 자리를 더하는 것은 보태는 변경이라 기존 프로젝트가 그대로 돌아간다.

## Risks

- **참조 해석 후보 경로를 빠뜨리면 조용히 깨진다.** 링크가 안 열리는 것은 감사가 잡지만,
  잡히는 시점이 기록을 다 옮긴 뒤다.
- 감사에 필수 절 검사를 더하면 이미 있는 기록에서 새 오류가 무더기로 뜬다. 이 저장소의 관측
  여섯 장이 바로 걸리고, W-00000203 이 그걸 채운다.
- 보관함에도 인덱스가 필요한지 정해야 한다. 카드 보관함은 인덱스를 가진다.

## Success criteria

- 보관함에 있는 관측·제안·허가증을 가리키는 인용이 살아 있는 서랍에 있을 때와 똑같이 열린다.
- 갓 만든 프로젝트에 보관 서랍 셋이 있다.
- 상태 절이 빠진 관측을 감사가 오류로 잡는다.
- 감사가 새 서랍을 소유 위치 위반으로 잡지 않는다.

## Next action

토폴로지 등록부의 갈래별 후보 경로 표부터 읽는다 — 참조 해석과 감사 소유 위치가 둘 다
거기서 나온다.

## Related truth

- W-00000199 가 자리 이름과 규칙을 정한다. 이 카드는 그 자리를 코드가 알게 만든다.

## Progress

세 보관 자리를 등록하고, 참조 후보 경로·감사 소유 위치·초기화 템플릿·마이그레이션·라우팅을
같은 등록부에 맞췄다. 필수 절 검사가 붙었다.

**드라이버로 세 바퀴를 돌렸고 마지막에 막혔다.** 첫 바퀴가 900초에 잘렸는데 일은 거의 끝났고,
잘린 실행자가 두 번째 바퀴 도중에 보고문을 뒤늦게 써 넣어 "보고문 둘"로 물렀으며, 세 번째
바퀴는 고칠 것이 없어 파일이 안 바뀌자 제자리걸음으로 막혔다. 감독 세션이 검사를 직접 돌려
닫았다. 되돌리기를 안 쓴 이유는 사람이 다시 정할 것이 없기 때문이다.

**실행자가 범위를 넘은 다섯 파일을 판단했다.**

| 파일 | 왜 넘었나 | 판단 |
|---|---|---|
| `stage/scripts/stage_schema_v4_migration.py` | 옮겨 온 프로젝트도 세 서랍을 받아야 함 | 받는다. 카드 목적이 "새 프로젝트"만 말했지만 옮겨 온 쪽을 빼면 같은 구멍이 남는다 |
| `stage/CHANGELOG.md` | 플러그인 변경 규칙 | 받는다. 저장소 규칙이 요구한다 |
| `stage/scripts/tests/test_audit_link_pin.py` | 새 감사 결과 순서 고정 | 받는다. 안 고치면 기존 시험이 깨진다 |
| `stage/scripts/tests/test_schema_v4_consumers.py` | 세션 요약의 공식 줄 검증 | 받는다. 보관함이 요약에 어떻게 뜨는지가 이 카드의 결과다 |
| `stage/scripts/tests/test_template_v4.py` | 새 템플릿 묶음 검증 | 받는다 |

## Verification


### Executed at close — 2026-08-04

```
$ python3 -m unittest discover -s stage/hooks/tests -p test_stage_topology.py -q
[exit 0]
----------------------------------------------------------------------
Ran 17 tests in 0.009s

OK

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 359 tests in 1.330s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (249 earlier lines omitted)
WARNING: preflights.codex is not configured; continuing without a venue health check
WARNING: reapers.codex is not configured after executor turn; jobs may remain
[W-00000001] executor failed; retry 1/3
WARNING: preflights.codex is not configured; continuing without a venue health check
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1785826554
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785826554. Human review + merge required; the base branch was not modified.
Removed unattended worktree: /private/var/folders/wg/6hnd_f255_z4ngk7ynwptym40000gn/T/tmpahujs0kq/unattended/W-00000001-1785826554
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
Ran 565 tests in 88.611s

OK
```

## Retrospective

R-00000199.

## Promotion decision

승격 경로 없음 — 자리를 등록했을 뿐 공식 산출물을 안 만들었다.

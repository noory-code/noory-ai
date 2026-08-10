---
id: W-00000256
title: 실행 전후의 카드 파일 목록을 대조해 달라졌으면 보고에 남긴다
kind: development
venue: codex
milestone:
autonomous: true
acceptance:
  - "grep -q widened stage/scripts/tests/test_drive.py && python3 -m unittest discover -s stage/scripts/tests -p test_drive.py -q"
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000256
promotion: not_applicable
review: passed
scope: stage/scripts/driver_unattended.py, stage/scripts/driver_repository.py, stage/scripts/tests/test_drive.py, stage/skills/stage-drive/SKILL.md, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000256 실행 전후의 카드 파일 목록을 대조해 달라졌으면 보고에 남긴다

## Purpose

실행하는 쪽이 카드의 파일 목록을 스스로 넓히면 범위를 넘었다는 사실이 카드에서 사라지고 보고에만 남으므로, DE-00000070 이 정한 대로 드라이버가 실행 전후를 대조해 달라진 것을 보고에 남긴다

## Success criteria

- 실행하는 쪽이 카드의 scope 를 넓힌 판에서 그 사실이 실행 기록에 남는다
- scope 를 안 바꾼 판에서는 그 알림이 안 나온다
- scope 만 넓히고 아무것도 안 한 판이 실행자의 카드 거절로 안 읽힌다

## Actions

없음 — 대조 하나를 넣고 그 시험을 붙이는 한 덩어리다.

## User value

카드만 읽어도 무엇이 범위를 넘었는지 보인다. 지금은 실행 기록을 따로 열어야 알고, 안 열면
그 일이 처음부터 카드 몫이었던 것으로 읽힌다.

## Scope

### Included

**명세는 DE-00000070 이다.** 무엇을 대조하고 왜 그것으로 충분한지가 거기 있다.

- **대조를 넣는다.** 무인 루프가 카드를 고를 때 읽은 `scope` 를 이미 메모리에 들고 있다
  (`driver_unattended.py:181-182`). 실행이 끝난 뒤 카드를 다시 읽어 그 한 필드만 대 본다.
  달라졌으면 실행 기록에 남긴다.
- **거절 판정을 갈라 준다.** `executor_changed_only_work_card`
  (`driver_repository.py:171-178`)는 바뀐 경로가 카드 하나면 거절로 읽는다. `scope` 만 넓힌
  판도 그 모양이라 지금은 거절로 오인된다. 같은 대조가 이 자리를 갈라야 한다.
- **계약 문구에 한 줄 넣는다.** `stage/skills/stage-drive/SKILL.md` 의 실행자 계약에
  "카드의 `scope` 를 바꾸지 않는다 — 넓힐지는 사람이 정하고, 넘었으면 보고로만 남긴다".

**시험이 덮어야 할 세 모양:**

| 모양 | 무엇을 확인하나 |
|---|---|
| `scope` 를 넓힌 판 | 그 사실이 실행 기록에 남는다 |
| `scope` 를 안 바꾼 판 | 그 알림이 안 나온다 |
| `scope` 만 넓히고 아무것도 안 한 판 | 거절로 안 읽힌다 |

### Excluded

- **`.stage/settings.json` 과 `.stage/operations/claude-venue.md` 는 안 건드린다.** 계약
  문구가 들어갈 자리 셋 중 둘인데, 이 프로젝트의 설정과 절차라 감독이 손으로 넣는다.
  **실행하는 쪽이 자기가 지금 따르고 있는 지시문을 고치는 것은 이 카드가 피한다.**
- 감독 실행과 팀원 실행은 안 잡는다. 담는 명령이 없어 대 볼 자리가 없다. DE-00000070 이 그
  비대칭을 적었다.
- 훅을 안 고친다. `scope` 쓰기를 막지 않는다 — 사람이 넓혀야 할 때가 있고 훅은 누가 쓰는지
  모른다.

## Risks

- **비대칭을 잊으면 잘못 닫는다.** 이 대조는 무인에서만 돈다. 성공 기준 셋이 다 무인 이야기다.
- 거절 판정을 갈라 줄 때 기존 시험이 깨질 수 있다. 인수 명령이 `test_drive.py` 전체를 본다.
- **알림이 재시도마다 쌓인다.** 실행 기록은 덧붙이는 문서라 같은 줄이 여러 번 나올 수 있다.
  W-00000255 에서 같은 모양을 받았고 해가 없었다.

## Next action

**`DE-00000070.md` 를 먼저 읽는다.** 왜 말하는 것만으로 부족한지(관측의 사례에서 보고도 되고
판정도 통과했는데 카드가 기록을 잃었다), 그리고 어느 실행 방식에서 무엇이 참인지가 거기 있다.

고칠 자리 둘: `driver_unattended.py:181-182`·`:527`(카드를 들고 있다가 담는 자리)과
`driver_repository.py:171-178`(카드만 바뀐 것을 거절로 읽는 자리).

**저장된 인수 명령이 `grep -q widened` 로 시험 파일을 먼저 본다** — 지금 그 낱말이 0번
나오므로, 시험을 안 쓰면 이 검사가 막는다. 기존 91개는 고치기 전에도 통과하기
때문이다(R-00000244).

## Related truth

- DE-00000070 — 이 카드의 명세. 대조가 무엇을 보고 왜 그것으로 되는지.
- O-00000020 — 이 고장의 관측. **그 사례는 감독 실행이라 이 카드가 못 잡는다.** 관측은 이
  카드 뒤에도 열려 있다.
- W-00000255 — 같은 모양(명령이 알리고 강제하지 않는다)을 먼저 만든 카드. 참고가 된다.

## Progress

끝났다. 무인 실행 한 바퀴로 만들어졌고 `land_run` 이 들였다.

## Verification

### 실행자가 잰 것

- 저장된 인수 명령 통과: `grep -q widened stage/scripts/tests/test_drive.py` 성공 뒤
  `test_drive.py` 시험 93개가 통과했다.
- 전체 훅 시험 통과 (`Ran 373 tests`, `OK`). 감사 `errors=0`.
- 전체 스크립트 시험 630개 중 2개가 실패했고, **그 원인이 이번 변경 밖이라고 정확히 짚었다** —
  `.stage/settings.json` 의 실행 명령에 있던 백틱. 조용히 고치지 않고 보고에 남겼다.

### 감독이 다시 잰 것

| 잰 것 | 결과 |
|---|---|
| 인수 검사 | 93개 통과 (들이기 전 91 → 시험 2 늘었다) |
| **시험이 고침을 실제로 밟나** | **밟는다.** `driver_unattended.py` 와 `driver_repository.py` 를 되돌리니 2개가 깨진다 |
| 새 시험이 무엇을 덮나 | 넓힌 판이 기록에 남는지, 그리고 넓히기만 한 판이 거절로 안 읽히는지 |
| 전체 시험(고친 뒤) | scripts 630, hooks 373 통과 |
| `audit_stage.py` | errors=0 |

### 실패한 둘은 감독의 실수였다

이 카드를 세우기 전에 감독이 `.stage/settings.json` 의 실행자 지시문에 한 줄을 넣으면서
필드 이름을 **백틱으로 감쌌다.** 그 지시문은 셸을 거쳐 실행되고, 셸에서 백틱은 그 안의 글자를
명령으로 실행한다. `test_template_v4` 가 정확히 그것을 막고 있어 두 venue 모두에서 깨졌다.

백틱을 빼서 고쳤다(`Ran 22 tests, OK`). **실행자가 이 실패를 자기 것으로 삼키지 않고 원인을
짚어 보고한 것이 계약대로다.**

### 이 판이 낸 실측 하나

이 실행의 실행자는 **"카드의 scope 를 고치지 마라"가 들어간 지시문을 처음 받은 실행자다.**
카드의 `scope` 는 안 바뀌었다 — 들이기 전후로 같다. 한 판이라 규칙이 통한다고 말하기엔 이르고,
지시가 실제로 전달됐다는 것까지가 확인된 것이다.

### Executed at close — 2026-08-10

```
$ grep -q widened stage/scripts/tests/test_drive.py && python3 -m unittest discover -s stage/scripts/tests -p test_drive.py -q
[exit 0]
... (52 earlier lines omitted)
$ /opt/homebrew/opt/python@3.14/bin/python3.14 -c 'from pathlib import Path; path = Path('"'"'/var/folders/wg/6hnd_f255_z4ngk7ynwptym40000gn/T/tmp289dwm8n/acceptance-count'"'"'); path.write_text(str(int(path.read_text(encoding='"'"'utf-8'"'"')) + 1) if path.exists() else '"'"'1'"'"', encoding='"'"'utf-8'"'"')'
[exit 0]

Independent reviewer result:
$ /opt/homebrew/opt/python@3.14/bin/python3.14 -c 'try:
    exec("from pathlib import Path; path = Path('"'"'/var/folders/wg/6hnd_f255_z4ngk7ynwptym40000gn/T/tmp289dwm8n/reviewer-count'"'"'); path.write_text(str(int(path.read_text(encoding='"'"'utf-8'"'"')) + 1) if path.exists() else '"'"'1'"'"', encoding='"'"'utf-8'"'"')")
except SystemExit as exc:
    if exc.code not in (None, 0):
        raise
import json, os
from pathlib import Path
log = Path(os.environ['"'"'STAGE_WORK_LOG_PATH'"'"'])
report = ('"'"'\n### Reviewer report\nCRITERIA VERDICT:\n- criterion: PASS - test reviewer inspected the inputs\nAPPROVED\nOUT-OF-CRITERIA OBSERVATIONS:\n- None\n'"'"')
log.write_text(log.read_text(encoding='"'"'utf-8'"'"') + report, encoding='"'"'utf-8'"'"')
Path(os.environ['"'"'STAGE_REVIEW_VERDICT_FILE'"'"']).write_text(
    json.dumps({'"'"'criteria'"'"': [{'"'"'criterion'"'"': '"'"'criterion'"'"', '"'"'verdict'"'"': '"'"'PASS'"'"', '"'"'reason'"'"': '"'"'test reviewer inspected the inputs'"'"'}], '"'"'approved'"'"': True}), encoding='"'"'utf-8'"'"')
print('"'"'APPROVED'"'"')'
[exit 0]
APPROVED
Mode: execute
Target parent: W-00000001
Selected item: W-00000002
Executor: /opt/homebrew/opt/python@3.14/bin/python3.14 -c 'raise SystemExit(0)'
Acceptance: /opt/homebrew/opt/python@3.14/bin/python3.14 -c 'raise SystemExit(0)'
Independent reviewer: /opt/homebrew/opt/python@3.14/bin/python3.14 -c 'import json, os
from pathlib import Path
log = Path(os.environ['"'"'STAGE_WORK_LOG_PATH'"'"'])
report = ('"'"'\n### Reviewer report\nCRITERIA VERDICT:\n- criterion: PASS - test reviewer inspected the inputs\nAPPROVED\nOUT-OF-CRITERIA OBSERVATIONS:\n- None\n'"'"')
log.write_text(log.read_text(encoding='"'"'utf-8'"'"') + report, encoding='"'"'utf-8'"'"')
Path(os.environ['"'"'STAGE_REVIEW_VERDICT_FILE'"'"']).write_text(
    json.dumps({'"'"'criteria'"'"': [{'"'"'criterion'"'"': '"'"'criterion'"'"', '"'"'verdict'"'"': '"'"'PASS'"'"', '"'"'reason'"'"': '"'"'test reviewer inspected the inputs'"'"'}], '"'"'approved'"'"': True}), encoding='"'"'utf-8'"'"')
print('"'"'APPROVED'"'"')'
Attempt: 1/unlimited
Iteration: 1/unlimited
Execution time: 0s/unlimited
WARNING: preflights.codex is not configured; continuing without a venue health check
----------------------------------------------------------------------
Ran 93 tests in 26.595s

OK
```

### Independent review at close — 2026-08-10

```
Review report: .stage/.runtime/driver/logs/W-00000256.md
```

## Retrospective


## Promotion decision

`not_applicable` — 이 카드는 결정 레코드를 만들거나 승격하지 않는다.

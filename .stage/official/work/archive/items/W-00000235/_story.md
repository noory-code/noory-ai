---
id: W-00000235
title: 드라이버가 실행 결과를 잃거나 겹치게 만들지 않는다
kind: fix
venue: codex
milestone: M-00000004
autonomous: true
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -p test_drive.py -q"
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000235
promotion: not_applicable
review: passed
scope: stage/scripts/drive.py, stage/scripts/tests/test_drive.py, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000235 드라이버가 실행 결과를 잃거나 겹치게 만들지 않는다

## Purpose

드라이버가 카드를 옳게 거절한 실행을 커밋 실패로 막고 병렬 실행끼리 같은 회고 번호를 집어, 사람이 그 뒤처리를 손으로 하게 되므로, 두 자리를 드라이버가 스스로 처리하게 한다

## Actions

- [W-00000236](W-00000236.md) — 카드만 고친 실행을 커밋 실패로 막지 않는다 (O-00000034)
- [W-00000237](W-00000237.md) — 병렬 실행이 같은 회고 번호를 집지 않게 한다

## User value

실행이 끝난 뒤 사람이 치울 것이 둘 줄어든다 — 옳게 거절했는데 막힌 카드를 되살리는 일과,
병합에서 겹친 회고 번호를 옮기는 일. 둘 다 2026-08-06 병렬 실행에서 실제로 손으로 했다.

## Scope

### Included

- 두 액션이 전부다. 둘 다 `drive.py` 를 만지므로 순서대로 간다.

### Excluded

- 실행 결과를 본 가지로 들이는 명령은 이 스토리가 안 만든다. 그 자격을 정하는 것이 형제 카드
  W-00000234(설계)이고, 명령 자체는 그 결정 뒤에 온다.
- 쉬는 팀원을 깨우는 문제(O-00000038)는 안 다룬다. 하니스 바깥 동작이라 마일스톤 기준에도
  안 들어 있다.

## Risks

- `drive.py` 는 이 저장소의 실행 기둥이다. 두 액션이 같은 파일을 만지므로 순서를 지켜야 하고,
  각 액션이 자기 회귀 시험을 남겨야 다음 액션이 앞의 것을 깨도 드러난다.


## Success criteria

- 소스를 안 고치고 카드만 고친 실행이 커밋 실패로 막히지 않는다
- 서로를 못 보는 병렬 실행이 같은 회고 번호를 집지 않는다

## Next action


## Related truth


## Progress


## Verification


### Executed at close — 2026-08-07

```
$ python3 -m unittest discover -s stage/scripts/tests -p test_drive.py -q
[exit 0]
... (52 earlier lines omitted)
$ /opt/homebrew/opt/python@3.14/bin/python3.14 -c 'from pathlib import Path; path = Path('"'"'/var/folders/wg/6hnd_f255_z4ngk7ynwptym40000gn/T/tmp6mxl6xfo/acceptance-count'"'"'); path.write_text(str(int(path.read_text(encoding='"'"'utf-8'"'"')) + 1) if path.exists() else '"'"'1'"'"', encoding='"'"'utf-8'"'"')'
[exit 0]

Independent reviewer result:
$ /opt/homebrew/opt/python@3.14/bin/python3.14 -c 'try:
    exec("from pathlib import Path; path = Path('"'"'/var/folders/wg/6hnd_f255_z4ngk7ynwptym40000gn/T/tmp6mxl6xfo/reviewer-count'"'"'); path.write_text(str(int(path.read_text(encoding='"'"'utf-8'"'"')) + 1) if path.exists() else '"'"'1'"'"', encoding='"'"'utf-8'"'"')")
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
Ran 90 tests in 30.676s

OK

$ /opt/homebrew/opt/python@3.14/bin/python3.14 /Users/woogis/Workspace/repo/noory-ai/stage/scripts/audit_stage.py --project-root /Users/woogis/Workspace/repo/noory-ai-stage-unattended/W-00000235-1786073321
[exit 0]
k — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000034/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000035/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000036/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000037/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000038/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000039/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000048/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000055/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000061/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000074/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000080/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000090/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000123/_epic.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000137/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000154/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000159/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000160/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000189/W-00000191.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000189/W-00000192.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
Summary: errors=0, warnings=32
```

### Independent review at close — 2026-08-07

```
Review report: .stage/.runtime/driver/logs/W-00000235.md
```

## Retrospective


## Promotion decision

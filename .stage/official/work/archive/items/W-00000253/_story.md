---
id: W-00000253
title: 담을 경로 중 아직 없는 것을 걸러 낸다
kind: development
venue: codex
milestone: M-00000004
autonomous: true
acceptance:
  - "test -f stage/scripts/tests/test_driver_git.py && python3 -m unittest discover -s stage/scripts/tests -p test_driver_git.py -q"
  - "python3 -m unittest discover -s stage/scripts/tests -p test_drive.py -q"
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000253
promotion: not_applicable
review: passed
scope: stage/scripts/driver_git.py, stage/scripts/driver_unattended.py, stage/scripts/tests/test_driver_git.py, stage/scripts/tests/test_drive.py, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000253 담을 경로 중 아직 없는 것을 걸러 낸다

## Purpose

카드를 옳게 거절한 실행이 담기 실패로 판정돼 시도를 태우고 카드가 막힘으로 남으므로, DE-00000068 이 정한 대로 담을 목록에서 아직 없는 경로를 걸러 내고 뺀 것을 기록에 남긴다

## Actions

없음 — 함수 하나를 고치고 그 시험을 붙이는 한 덩어리다.

## User value

실행자가 "이 카드는 틀렸다"고 옳게 판단했을 때 그 판단이 그대로 사람에게 온다. 지금은 하니스
오류로 덮여서, 사람이 원인을 찾으려면 실행 가지의 결정 기록까지 열어야 한다.

## Scope

### Included

**명세는 DE-00000068 이다.** 무엇을 남기고 무엇을 뺄지, 왜 그렇게 하는지가 거기 있다. 새로
정할 것이 아니라 그대로 싣는다.

- **거르기를 넣는다.** `stage/scripts/driver_git.py:93-96` 의 `commit_item` 이 목록을 넘기기
  전에 거른다. 남기는 조건은 둘 중 하나다 — **디스크에 있거나, 그 경로 표현이 추적 중인 파일을
  하나라도 가리키거나.** 거른 뒤 `git add -A` 로 담는다.
- **뺀 것을 기록에 남긴다.** `commit_item` 이 뺀 경로를 돌려주고, 부르는 쪽
  (`driver_unattended.py:527`)이 그것을 공유 실행 기록에 적는다. 지금은 성공했을 때 돌아온
  문구를 안 쓴다.
- 시험을 `stage/scripts/tests/test_driver_git.py` 에 새로 만든다.

**시험이 덮어야 할 네 모양** — DE-00000068 의 Follow-up 이 이름으로 적었다.

| 모양 | 무엇을 확인하나 |
|---|---|
| 선언한 파일이 아직 없다 | 나머지가 담긴다 |
| 선언한 디렉터리가 아직 없다 | 나머지가 담긴다 |
| 선언한 디렉터리가 통째로 지워졌다 | **그 삭제가 담긴다** — 파일 존재만으로 거르면 여기서 잃는다 |
| 뺀 경로가 있다 | 그 이름이 실행 기록에 남는다 |

### Excluded

- 실행자 계약을 안 고친다. `promotion` 쓰기는 그대로 둔다.
- 무인 루프의 걸음 순서를 안 바꾼다. 담기가 성공하면 그 뒤의 거절 처리
  (`driver_unattended.py:536`)가 이미 제대로 돈다.
- 커밋 게이트와 승격 게이트를 안 건드린다.
- `land_run.py` 와 `commit_lifecycle` 은 안 고친다. DE-00000068 이 세었고 같은 고장에 안
  걸린다.

## Risks

- **파일 존재만으로 거르면 삭제를 잃는다.** `git ls-files -- doomed/` 는 `doomed/x.py` 를 내지
  `doomed/` 를 안 낸다. 그래서 "그 문자열이 추적 목록에 있는가"로 쓰면 디렉터리 항목이 전부
  빠진다. DE-00000068 이 실측으로 확인한 자리다.
- **조용히 빼면 O-00000020 과 같은 모양이 된다.** 무엇이 안 담겼는지가 아무 데도 안 남는다.
  기록에 남기는 것이 이 카드의 절반이다.
- **이 카드 자신이 그 고장을 밟는다.** 선언한 `stage/scripts/tests/test_driver_git.py` 가 아직
  없다. 실행자가 이 카드를 거절하면 지금 코드로는 담기가 통째로 실패한다 — 고치려는 바로 그
  자리다.

## Success criteria

- 선언한 경로 중 아직 없는 것이 있어도 나머지가 담기고, 뺀 경로 이름이 실행 기록에 남는다
- 선언한 디렉터리가 통째로 지워진 실행에서 그 삭제가 담긴다
- 카드만 고치고 거절한 실행이 담기 실패가 아니라 거절로 읽힌다

## Next action

**`DE-00000068.md` 를 먼저 읽는다.** 남기는 조건, 왜 파일 존재만으로는 안 되는지, 왜 없는 것은
빼면서 남는 것은 거절하는지가 거기 있다. 그 결정이 이 카드의 명세다.

그다음 `stage/scripts/driver_git.py` 의 `commit_item`(93-105줄)과 그것을 부르는
`driver_unattended.py:527-534` 를 읽는다.

**저장된 인수 명령 둘 중 첫째가 `test -f` 로 시험 파일의 실재를 먼저 본다** — 파일을 안 만들면
`unittest` 가 `Ran 0 tests ... OK` 에 exit 0 을 내기 때문이다(R-00000244). 둘째는 기존
`test_drive.py` 90개가 안 깨지는지 본다.

## Related truth

- DE-00000068 — 이 카드의 명세. 남기는 조건과 그 근거, 시험이 덮어야 할 네 모양.
- O-00000034 — 이 고장의 관측. **구현 뒤에도 바로 안 닫는다** — 거절한 실행이 시도를 안 태우는지
  실측이 나온 뒤에 닫는다(DE-00000068 의 Follow-up).
- O-00000020 — 뺀 것을 조용히 두면 안 되는 이유.
- DE-00000066 — 목록 **밖**이 올라와 있으면 거절하라고 정한 결정. 이 카드는 반대 방향인데
  근거가 갈린다. DE-00000068 이 왜 갈리는지 답한다.
- M-00000004 완료 기준 둘째가 이 카드다.


## Progress

끝났다. 무인 실행 한 바퀴로 만들어졌고, `land_run.py` 가 본 가지로 들였다. 감독이 손댄 것은
없다 — 워크트리 되살리기·커밋·병합·치우기를 명령이 다 했다.

## Verification

### 감독이 들이기 전에 다시 잰 것

| 잰 것 | 결과 |
|---|---|
| 인수 검사 둘 | 새 시험 2개, `test_drive.py` 91개 — 다 통과 |
| **시험이 고침을 실제로 밟나** | `driver_git.py` 를 병합 전 판으로 되돌리니 3개가 깨졌다 |
| 네 모양을 다 덮나 | 덮는다. 없는 파일과 없는 디렉터리를 한 시험이 둘 다 돌리고, 삭제 보존을 `D doomed/example.py` 로 확인한다 |
| `stage/hooks/tests` | 372 통과 |
| `stage/scripts/tests` | 625 통과 (들이기 전 622 → 3 늘었다) |
| `audit_stage.py` | errors=0 |

**판정이 감독보다 한 발 더 갔다.** 감독은 고침을 통째로 되돌려 봤는데, 판정은 **"디스크 존재만
보는 변형"으로도 바꿔 봤다.** 그때 삭제 보존 시험 하나만 깨졌다 — DE-00000068 이 "그 문자열이
추적 목록에 있는가"로 쓰면 안 된다고 한 자리를 시험이 정확히 겨눈다는 뜻이다.

**세 번째 성공 기준은 판정이 실제로 돌려서 확인했다.** 없는 선언 경로를 둔 채 카드만 고친
무인 실행을 만들어 돌리니, 뺀 경로 알림과 거절 알림이 순서대로 남고 시도를 안 태웠다.

### 들이기도 명령이 했다

```
$ python3 stage/scripts/land_run.py --project-root <루트> \
    --worktree <경로> W-00000253
Landed W-00000253 from stage/driver/W-00000253-1786255886 and removed its worktree and branch
```

드라이버가 워크트리를 이미 치운 뒤였는데 명령이 가지에서 되살려 진행했다. 준비 커밋과 병합
커밋 둘 다 `Work-Item:` 과 `Source-Branch:` 를 담고, 본 체크아웃은 깨끗하다.

### 판정이 적어 둔 지적 넷 — 처분

넷 다 성공 기준을 안 깨서 판정이 통과시켰고, 감독도 들이기를 막지 않는다.

| 지적 | 처분 | 이유 |
|---|---|---|
| `git ls-files` 의 표준출력과 에러를 합쳐 본다. git 이 경고만 내도 빼야 할 경로가 남는다 | **보류** | 판정이 짚었듯 옛날 실패로 돌아가는 방향이라 조용히 잃지 않는다. 실제로 경고가 나는 사례를 본 적이 없다 |
| 뺀 경로 알림이 재시도마다 로그에 쌓인다 | **수용, 해 없음** | 실행 기록은 덧붙이는 문서다. 같은 줄이 쌓여도 무엇이 빠졌는지는 그대로 읽힌다 |
| `if not commit_paths: return False` 가 실제로 안 밟힌다 | **기각** | 카드 경로가 늘 목록에 들어가고 늘 디스크에 있다. 실행자가 결정으로 보고했으니 몰래 넣은 것이 아니다 |
| 새 시험 하나가 거절이 조용히 정상 완료로 바뀌어도 통과한다 | **수용, 해 없음** | 판정이 짚었듯 옆 시험(`test_drive.py`)이 그 틈을 덮는다 |


### Executed at close — 2026-08-09

```
$ test -f stage/scripts/tests/test_driver_git.py && python3 -m unittest discover -s stage/scripts/tests -p test_driver_git.py -q
[exit 0]
----------------------------------------------------------------------
Ran 2 tests in 0.417s

OK

$ python3 -m unittest discover -s stage/scripts/tests -p test_drive.py -q
[exit 0]
... (52 earlier lines omitted)
$ /opt/homebrew/opt/python@3.14/bin/python3.14 -c 'from pathlib import Path; path = Path('"'"'/var/folders/wg/6hnd_f255_z4ngk7ynwptym40000gn/T/tmpqhfsx7fi/acceptance-count'"'"'); path.write_text(str(int(path.read_text(encoding='"'"'utf-8'"'"')) + 1) if path.exists() else '"'"'1'"'"', encoding='"'"'utf-8'"'"')'
[exit 0]

Independent reviewer result:
$ /opt/homebrew/opt/python@3.14/bin/python3.14 -c 'try:
    exec("from pathlib import Path; path = Path('"'"'/var/folders/wg/6hnd_f255_z4ngk7ynwptym40000gn/T/tmpqhfsx7fi/reviewer-count'"'"'); path.write_text(str(int(path.read_text(encoding='"'"'utf-8'"'"')) + 1) if path.exists() else '"'"'1'"'"', encoding='"'"'utf-8'"'"')")
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
Ran 91 tests in 26.512s

OK
```

### Independent review at close — 2026-08-09

```
Review report: .stage/.runtime/driver/logs/W-00000253.md
```

## Retrospective


## Promotion decision

`promotion: not_applicable` — 이미 승격된 DE-00000068 을 구현하며 새로 승격할 기록은 없다.

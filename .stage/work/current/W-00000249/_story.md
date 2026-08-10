---
id: W-00000249
title: 마일스톤 완료 기준을 여러 개 받게 한다
kind: fix
venue: codex
milestone:
autonomous: true
acceptance:
  - "grep -q repeatable stage/scripts/tests/test_roadmap_v4.py && python3 -m unittest discover -s stage/scripts/tests -p test_roadmap_v4.py -q"
  - "python3 -m unittest discover -s stage/scripts/tests -p 'test_roadmap*.py' -q"
status: completed
verification: passed
retrospective: completed
retrospective_ref: R-00000249
promotion: not_applicable
review: passed
scope: stage/skills/stage-roadmap/manage_roadmap.py, stage/scripts/tests/test_roadmap_v4.py, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000249 마일스톤 완료 기준을 여러 개 받게 한다

## Purpose

마일스톤을 만들 때 완료 기준을 여러 개 주면 마지막 하나만 남고 나머지가 말없이 사라져서 M-00000003 에서 셋 중 둘을 잃었으므로, 카드 등록 명령의 --success-criterion 과 같은 모양으로 반복 인자를 받게 한다

## Actions

없음 — 인자 하나를 반복 가능하게 고치고 그 시험을 붙이는 한 덩어리다.

## User value

마일스톤에 완료 기준 셋을 합의하면 셋이 다 기록에 남는다. 지금은 하나만 남고, 닫을 때 그
하나만 보고 판정하게 된다.

## Scope

### Included

**감독이 시작한 뒤 확인한 것.** 관측이 적어 둔 전제가 아직 참인지 실제로 돌려 봤다.

| 확인 | 결과 |
|---|---|
| 인자가 한 번만 받는 값인가 | 맞다. `manage_roadmap.py:520` 이 `--completion-criteria` 를 `default=""` 로 선언한다. 관측이 적은 줄 번호(497)에서 옮겨졌지만 모양은 같다 |
| 여러 번 주면 어떻게 되나 | 셋을 주고 돌려 봤다 — **마지막 하나만 남고 경고도 없이 exit 0** 이다 |
| 기록에 어떻게 쓰이나 | `:239` 가 그 값 하나를 `Completion criteria` 절에 그대로 넣는다 |

- **인자를 반복 가능하게 받는다.** 카드 등록 명령의 `--success-criterion` 과 같은 모양이다.
  관측이 그쪽이 결이 같다고 적었다.
- **마일스톤 기록이 여러 개를 목록으로 담게 한다.** 값 하나를 절에 넣는 자리(`:239`)가 목록을
  받아야 한다.
- 시험을 `stage/scripts/tests/test_roadmap_v4.py` 에 더한다. 지금 열셋이 있다.

### Excluded

- 이미 만들어진 마일스톤 기록을 고치지 않는다. M-00000003 은 사람이 손으로 되살렸다.
- 완료 기준을 비워 두는 것을 막지 않는다. 그것은 다른 문제다.
- 로드맵 명령의 다른 인자(제목·목적·기간·테마)는 안 건드린다. 하나씩만 주는 값이라 이 고장이
  없다.

## Risks

- **인자 이름이 복수형이라 반복이 어색해 보인다.** 지금 이름이 `--completion-criteria` 인데
  카드 쪽은 `--success-criterion` 단수다. 이름을 맞출지, 지금 이름으로 반복을 받을지 실행자가
  정하고 보고한다. 이름을 바꾸면 이미 그 인자를 쓰는 문서와 어긋난다 — 세고 나서 바꾼다.
- 기존 시험 열셋이 안 깨져야 한다. 인수 명령 둘째가 그것을 본다.

## Success criteria

- 완료 기준을 세 개 주면 세 개가 다 마일스톤 기록에 남는다
- 기준이 조용히 사라지면 시험이 잡는다

## Next action

**`O-00000036.md` 를 먼저 읽는다.** 고칠 길 둘 중 어느 쪽이 카드 등록 명령과 결이 같은지가
거기 있다. 그다음 `stage/skills/stage-work/register_work.py` 의 `--success-criterion` 이
반복을 어떻게 받는지 보고 같은 모양으로 맞춘다.

고칠 자리 둘: `manage_roadmap.py:520`(인자 선언)과 `:239`(기록에 쓰는 자리).

**저장된 인수 명령 첫째가 `grep -q repeatable` 로 시험 파일을 먼저 본다** — 지금 그 낱말이
0번 나오므로, 시험을 안 쓰면 이 검사가 막는다. 기존 열셋은 고치기 전에도 통과하기
때문이다(R-00000244).

## Related truth

- O-00000036 — 이 고장의 관측. M-00000003 에서 기준 셋 중 둘을 잃었고 닫기 직전에 되살렸다.
- `stage/skills/stage-work/register_work.py` — `--success-criterion` 이 반복을 받는 자리.
  따라갈 모양이다.
- 이 카드는 마일스톤에 안 걸린다. M-00000004 와 무관하다.
- O-00000045 — 이 고침이 남긴 자리. 값 앞에 하이픈을 직접 붙여 부르면 `- -` 가 된다.

## Progress

끝났다. 무인 실행 한 바퀴로 만들어졌고 `land_run` 이 들였다.

## Verification

### 감독이 들이기 전에 다시 잰 것

| 잰 것 | 결과 |
|---|---|
| 인수 검사 | 14개, 23개 통과 (들이기 전 13 → 시험 1 늘었다) |
| **시험이 고침을 실제로 밟나** | **밟는다.** `manage_roadmap.py` 를 되돌리니 깨지고, 실패 메시지가 셋 중 마지막 하나만 남은 것을 그대로 보여 준다 |
| `stage/scripts/tests` 전체 | 628개 통과 (들이기 전 627) |
| `audit_stage.py` | errors=0 |

**감독이 한 번 잘못 봤다.** 처음 확인할 때 명령을 `&&` 로 이었는데 중간의 `grep -c` 가 0을 세며
종료 코드 1을 내 뒤가 안 돌았다. "시험이 안 깨진다"고 잘못 읽었고, 되돌리기가 실제로 됐는지
확인하고 다시 돌려 바로잡았다. **검사를 이어 붙이면 앞이 실패했을 때 뒤가 안 돈다.**

### 실행자가 정한 것 — 인자 이름을 안 바꿨다

카드가 이름을 맞출지 실행자에게 맡겼다. 실행자는 **기존 이름 `--completion-criteria` 를
유지하고** `action="append"` 로 반복을 받게 했다. 근거는 이미 그 이름을 쓰는 문서와 어긋나지
않게 하는 것이고, 그 판단을 보고에 적었다. 받는다.

### 시험이 안 덮는 자리 셋 — 세었다

성공 기준 둘은 세 개를 주는 경우만 본다. 나머지 셋을 직접 돌려 확인했다.

| 모양 | 결과 | 처분 |
|---|---|---|
| 값 하나 | `- Ship it` — 잘 된다 | 문제 없음 |
| **값 앞에 하이픈이 붙어 있다** | **`- - Ship it`** | O-00000045 로 적어 두고 안 고친다 |
| 값 없음 | 빈 절 — 잘 된다 | 문제 없음 |

**하이픈 겹침을 안 고치는 이유:** 스킬 문서(`stage-roadmap/SKILL.md:29`)의 예시가 하이픈 없이
부르므로 문서를 따르면 안 밟는다. 이 저장소에 하이픈을 붙여 부르는 자리도 없다. 밟으면
`- -` 가 그대로 보여 조용히 썩지도 않는다. 지금 해가 없어 받지 않는다.

### Executed at close — 2026-08-10

```
$ grep -q repeatable stage/scripts/tests/test_roadmap_v4.py && python3 -m unittest discover -s stage/scripts/tests -p test_roadmap_v4.py -q
[exit 0]
----------------------------------------------------------------------
Ran 14 tests in 2.746s

OK

$ python3 -m unittest discover -s stage/scripts/tests -p 'test_roadmap*.py' -q
[exit 0]
----------------------------------------------------------------------
Ran 23 tests in 5.228s

OK
```

### Independent review at close — 2026-08-10

```
Review report: .stage/.runtime/driver/logs/W-00000249.md
```

## Retrospective

## Promotion decision

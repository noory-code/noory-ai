---
id: W-00000209
title: 빈 목적으로 시작하는 길을 막는다
kind: development
venue: codex
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -p test_register_work.py -q"
status: completed
verification: passed
retrospective: completed
retrospective_ref: R-00000207
promotion: not_applicable
review: not_required
scope: stage/skills/stage-work/register_work.py, stage/scripts/audit_stage.py, stage/templates/v4/, stage/skills/stage-work/SKILL.md, stage/scripts/tests/test_register_work.py, stage/scripts/tests/test_audit_stage.py, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000209 빈 목적으로 시작하는 길을 막는다

## Purpose

목적과 끝나는 자리가 비어도 카드가 만들어져서 목적이 일의 결과로 적히므로, 등록과 감사가 빈 카드를 거부해 시작하는 순간에 답이 있게 만든다

## Actions

없음 — 등록이 거부하는 것과 감사가 잡는 것은 같은 규칙의 앞뒤다.

## User value

목적을 안 캐냈으면 일을 시작조차 못 한다. 지금은 빈 카드로 시작해서 목적을 나중에 채우고,
그러면 목적이 일의 결과가 된다.

## Scope

### Included

- **목적 없이 등록 못 하게 한다.** 지금 `--purpose` 는 선택 항목이고 기본값이 빈 문자열이라
  목적이 아예 없는 카드가 만들어진다.
- **끝나는 자리 없이 등록 못 하게 한다.** 성공 기준을 받아서 카드에 쓰고, 비면 거부한다.
- **감사가 목적과 성공 기준이 빈 카드를 잡는다.** 지금은 안 본다.
- 거부 문구가 무엇을 해야 하는지 말한다. "목적이 없다"가 아니라 "사람에게 무엇을 이루려는지
  묻고 그 답을 넣어라"로 읽혀야 한다.
- 새 규칙을 켜기 전에 이 저장소의 기존 카드 중 빈 것이 몇 장인지 센다. **실측: 보관된 카드
  32장이 성공 기준이 비어 있고, 그중 하나는 2026-08-03 에 닫혔다.** "오래된 몇 장"이 아니다.
- **보관된 카드는 경고로 낸다. 사람이 정했다.**
  - 진행 중·계획 카드는 오류다. 보관된 카드는 경고다.
  - 보관함을 감사에서 빼지 않는다. DE-00000059 는 구역을 나누지 않았고, 그 범위를 좁히려면
    결정 기록이 먼저다.
  - 옛 카드에 목적을 지어 넣지 않는다. 그것이 이 에픽이 막으려는 짓이다.
  - 경고는 아무것도 안 막는다 — 카드를 닫는 명령은 전체 감사를 스스로 안 돌리고, 감사는
    `--strict` 없이는 경고만으로 실패하지 않는다(실측).
  - **v5 마이그레이션을 같이 고친다.** 지금은 사후 감사 결과를 등급이 아니라 코드로 걸러서,
    경고 하나만 남아도 이사가 되돌아간다. 등급으로 거르게 바꾼다.

### Excluded

- 지어낸 목적은 안 잡는다. 못 잡는다 — 기계 눈에는 사람이 말한 문장과 내가 만든 문장이 같은
  글자다(DE-00000059). 그 자리는 사람이 카드 첫 줄에서 본다.
- 카드에 칸을 새로 안 만든다. 이미 있는 목적과 성공 기준을 비게 두지 않을 뿐이다.

## Risks

- **이미 있는 카드가 무더기로 걸릴 수 있다.** 켜기 전에 세고, 많으면 채우는 일이 따로 필요하다.
- 계획 카드는 본문이 얇게 잡히기 쉬운데, 그것도 같은 규칙을 지려면 등록할 때 답이 있어야 한다.
  계획으로 잡는 편의를 없애는 쪽이 맞는지 구현하면서 확인한다.
- 거부 문구가 불친절하면 다음 사람은 빈칸을 채우는 요령만 배운다. 무엇을 해야 하는지 말해야 한다.

## Success criteria

- 목적이 비면 등록이 거부하고, 무엇을 해야 하는지 알려 준다.
- 끝나는 자리가 비면 거부한다.
- 목적이나 끝나는 자리가 빈 카드가 저장소에 있으면 감사가 잡는다 — 진행 중·계획은 오류로,
  보관된 것은 경고로. 보관함을 감사에서 빼지 않는다.
- 빈 카드를 가진 프로젝트가 v5 로 옮길 수 있다. 경고 때문에 이사가 되돌아가지 않는다.
- 빈 카드를 만들고 나중에 채우는 길이 남아 있지 않다.

## Next action

`register_work.py` 의 `--purpose` 를 필수로 바꾸고, 성공 기준을 받는 자리를 만든다.

## Related truth

- DE-00000059 — 무엇을 막고 무엇을 못 막는지 정했다.
- W-00000190 — 등록에 질문 셋을 넣은 카드. 묻기만 해서는 안 바뀐다는 것이 그 뒤 여덟 번으로
  드러났다.


## Progress

**게이트가 막는다** — 목적을 안 주면 "사람에게 무엇을 이루려는지 묻고 그 답을 넣어라",
끝나는 자리를 안 주면 "사람에게 끝난 걸 무엇으로 아는지 묻고 그 답을 넣어라"로 거부한다.
감사는 오류 0, 경고 32다.

**세 바퀴가 걸렸고 마지막에 시도 한도가 찼다. 판정은 통과였다.** 감독 세션이 검사를 직접 돌려
닫았다 — 훅 361, 스크립트 589 통과.

| 바퀴 | 판정이 잡은 것 |
|---|---|
| 1 | 빈 카드가 "4장"이라는 거짓 숫자 위에 보관 제외가 서 있었다. 실제 32장, 하나는 이틀 전. 마이그레이션 파급도 안 보고됐다 |
| 2 | "잡으면 모든 감사가 막힌다"가 사실이 아니었다. 경고로 내면 보이면서 안 막는다 — **세 번째 길** |
| 3 | 새 규칙이 `BACKLOG009` 를 쓰는데 그 번호는 이미 다른 뜻으로 배포됐다 |

**세 번째 지적은 판정을 통과시킨 뒤 남긴 것이라 내가 직접 고쳤다.** 빈 목적 규칙을
`BACKLOG011` 로 옮기고 시험을 맞췄다. 배포된 코드가 두 결함을 가리키면 코드로 거르는 쪽이
바로 오작동한다.

**마지막 바퀴 전에 내가 이 카드의 성공 기준을 고쳤다.** 보관 카드를 경고로 낸다는 사람의
결정을 실행자가 판정문에서 알아서 읽어 내길 기다리기에는 시도가 하나뿐이었다. 판정이 그
편집을 로그에서 확인 못 한다고 지적했고, 맞는 지적이다.

## Verification


### Executed at close — 2026-08-05

```
$ python3 -m unittest discover -s stage/scripts/tests -p test_register_work.py -q
[exit 0]
----------------------------------------------------------------------
Ran 44 tests in 3.148s

OK

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 361 tests in 1.363s

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
[W-00000001] completed on stage/driver/W-00000001-1785932144
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785932144. Human review + merge required; the base branch was not modified.
Removed unattended worktree: /private/var/folders/wg/6hnd_f255_z4ngk7ynwptym40000gn/T/tmp8ylx_dcd/unattended/W-00000001-1785932144
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
Ran 589 tests in 92.155s

OK
```

## Retrospective

R-00000207.

## Promotion decision

승격 경로 없음.

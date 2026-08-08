---
id: W-00000244
title: 열린 관측을 읽는 쪽을 만든다
kind: design
venue: claude
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/hooks/tests -q -k context"
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000244
promotion: not_applicable
review: not_required
scope: .stage/operations/, stage/hooks/, stage/hooks/tests/, stage/scripts/, stage/skills/stage-work/, stage/CHANGELOG.md, .stage/decisions/, .stage/state/
promotes:
decision_refs:
---

# W-00000244 열린 관측을 읽는 쪽을 만든다

## Purpose

관측 열일곱이 열린 채로 최대 열이틀째 앉아 있고 세션에 들어오는 목록이 최신 여섯을 잘라
버려서 가장 새 문제가 아무한테도 안 보이므로, 열린 관측이 사람 눈에 다 들어오고 일감이
되거나 닫히도록 꺼내 보는 자리를 만든다

## Actions

없음 — 한 덩어리다.

## User value

문제를 적어 두면 언젠가 처리된다. 지금은 적어 두면 그 자리에서 늙는다.

## Scope

### Included

**감독이 이미 잰 것.** 등록 전에 세션 시작 훅을 직접 돌려 확인했다.

| 잰 것 | 값 |
|---|---|
| 세션에 들어오는 전체 길이 | 6,545자 |
| `state/current.md` 를 자르는 한도 | 1,400자 (`stage_context.py:38` 의 `read_if_exists` 기본값) |
| 지금 열린 관측 | 17개 (등록 때 16으로 적었다 — 틀렸고 `## Verification` 이 다시 셌다) |
| 그중 세션에 실제로 들어온 것 | O-00000036 까지 — **뒤의 여섯이 잘렸다** |
| 가장 오래 열린 것 | O-00000002, 2026-07-27 (열이틀) |

- **잘리는 쪽을 고친다.** 최신이 잘리고 가장 오래된 것이 남는다. 새로 적은 문제가 그다음
  세션에 안 보이면 적는 행위 자체가 값을 잃는다.
- **얼마나 오래 열려 있는지를 목록이 말하게 한다.** 지금은 제목만 있어서 어제 것과 열이틀
  된 것이 같아 보인다.
- **지금 열린 열일곱을 한 장씩 읽어 처분한다.** 일감으로 세우거나, 이미 해소됐으면 닫거나,
  아직 열려 있어야 하면 왜인지 그 관측에 적는다. 세 갈래 밖은 없다.
- **관측이 늘 때 이 자리가 다시 막히는지 본다.** 한도를 올리는 것으로 끝나면 서른 개가
  됐을 때 같은 자리를 다시 밟는다.

### Excluded

- 회고나 결정을 꺼내 보는 자리는 안 만든다. 회고는 W-00000245 가 어제 다뤘고, 그 절차가
  실제로 도는지 보고 나서 같은 모양을 관측에 쓸지 정한다.
- 관측을 자동으로 닫지 않는다. 닫을지는 사람이 판단한다.
- 세션 시작이 `.stage/operations/` 규칙을 안 실어 주는 것(O-00000042)은 이 카드 밖이다.
  같은 훅을 만지지만 다른 문제다 — 그쪽은 규칙이 아예 안 오고, 이쪽은 오다가 잘린다.

## Risks

- **한도를 올리면 세션 시작이 무거워진다.** 지금 6,545자인데 관측 본문을 다 실으면 몇 배가
  된다. 목록만 늘리고 본문은 안 싣는 선을 지킨다.
- **잘리는 자리가 여기만이 아니다.** `read_if_exists` 는 진행 중 작업과 리뷰 후보에도 같은
  한도를 쓴다. 하나만 고치면 나머지가 조용히 같은 문제를 갖는다 — 세 자리를 다 세고 고친다.
- 열일곱을 한 번에 처분하면 판단이 거칠어진다. 한 장씩 근거를 적고, 애매하면 열어 둔다.

## Success criteria

- 열린 관측이 세션에 하나도 안 잘리고 들어오고, 각각 며칠째 열려 있는지가 그 줄에 있다
- 관측이 지금의 두 배가 돼도 안 잘린다는 것이 시험으로 잡힌다
- 지금 열린 열일곱이 각각 일감이 되거나 닫히거나, 열어 두는 이유가 그 관측에 적혀 있다

## Next action

회고를 쓰고 닫는다.

## Related truth

- O-00000042 — 같은 훅의 다른 구멍. 규칙 본문이 아예 안 실린다. 이 카드가 훅을 만질 때 함께
  볼 수 있지만 고치는 것은 별건이다.
- R-00000241 — 회고의 배움이 규칙이 되는 절차. 같은 모양의 문제("써 놓고 읽는 쪽이 없다")를
  회고 쪽에서 먼저 풀었다. 그 절차가 참고가 된다.

## Progress

끝났다. 팀원(`obs-reader`)이 자기 워크트리에서 고침과 시험을 만들었고(`db9f74f1`), 감독이
인수 검사와 코덱스 판정을 돌린 뒤 병합했다. 관측 처분 열일곱은 감독이 했다.

## Verification

### 감독이 직접 잰 것

팀원 보고를 믿지 않고 다시 쟀다. 값이 다른 자리는 감독 값을 쓴다 — 세션 요약 절이 그 사이
바뀌어 팀원의 "이전" 값(6,571)과 감독 값이 다르다.

| 잰 것 | 고치기 전 | 고친 뒤 |
|---|---|---|
| 세션 시작 페이로드 | 6,718자 | **6,151자** |
| 세션에 실제로 들어온 열린 관측 | 11개 | **17개 전부** |
| `stage/hooks/tests` | — | 372 통과 |
| `stage/scripts/tests` | — | 604 통과 |
| `audit_stage.py` | — | errors=0 (warnings 32 는 전부 기존 보관 카드) |

**새 시험이 이 고침을 실제로 밟는지 확인했다.** `stage_context.py` 만 되돌리고 새 시험
파일을 돌리니 8개 중 7개가 깨졌다(실패 4, 오류 3). 시험이 장식이 아니다.

**카드의 인수 검사는 이 변경을 안 밟는다.** `-k context` 는 고치기 전에도 10개가 통과했다 —
그 열은 `test_roadmap_context.py` 이고 `stage_context.py` 를 한 줄도 안 건드린다. 고친 뒤
18개가 되는데 실제로 이 코드를 밟는 것은 새로 생긴 8개뿐이다. **인수 명령을 파일 이름이 아니라
`-k` 로 고르면 이런 헛통과가 조용히 생긴다.**

### 팀원이 뒤집은 전제 둘

- **세 자리가 같은 한도를 쓰지만 오늘 잘리는 것은 한 자리뿐이다.** `Active work` 292자,
  `Review candidates` 150자로 1,400 한도에 안 닿는다. 카드의 Risks 는 코드로는 맞았고
  결과로는 빠뜨린 것이 없었다.
- **열린 관측은 열일곱이다.** 이 카드 본문의 "열여섯"과 `## 남은 문제`의 "열여덟"이 둘 다
  틀렸다. 감독이 파일 수와 인덱스 줄 수 둘로 세어 확인했다.

### 코덱스 판정 — 반려, 기준 넷 중 둘 실패

| 실패한 기준 | 처분 | 이유 |
|---|---|---|
| 관측별 처분이 안 끝났다 | **수용** | 맞다. 팀원이 안 한 것이 옳았고(이 카드의 `### Excluded` 가 닫는 판단을 사람 몫으로 둔다) 남은 것은 감독 몫이었다. 감독이 열일곱을 처분해 해소했다 |
| `.git/worktrees/W-00000244/` 를 프로젝트 루트에서 못 읽는다 | **기각** | 그 경로는 본 체크아웃의 `.git/` 안에 있고 판정은 워크트리에서 돌았다. 작업의 결함이 아니라 판정을 어디서 돌렸느냐의 문제다. 다만 실행자 보고의 `Changed paths` 에 하니스 상태를 섞으면 그 목록을 파일로 읽는 모든 소비자가 걸린다 — O-00000034 가 그 자리를 이미 물고 있고 W-00000250 이 잇는다 |

### 관측 열일곱의 처분

**일감 여섯 (계획됨)** — O-00000042→W-00000246, O-00000041→W-00000247, O-00000040→W-00000248,
O-00000036→W-00000249, O-00000034·O-00000035→W-00000250, O-00000020→W-00000251.

**닫음 하나** — O-00000043. 다음 걸음이던 확인 절차가 `claude-venue.md` 4번으로 서 있고,
이번 팀원 실행에서 그 걸음을 실제로 밟았다.

**열어 둠 열** — O-00000002·13·15·21·24·25·28·37·38, 그리고 O-00000041 의 반대쪽 면. 각
기록의 `## Status` 에 왜 열어 두는지 그 기록 자신의 말로 적었다. 넷은 "다음 X 때 잰다"는
조건 대기, 셋은 사건 대기, 하나(O-00000024)는 고칠 결함이 아니라 판단할 때 꺼내 쓰는
실측값이라 닫으면 근거가 사라진다.

**`work_items:` 로는 계획 카드를 못 가리킨다.** 처음에 그렇게 이었더니 감사가 일곱을 잡았다 —
그 필드는 현재·보관 카드만 해소한다. 링크는 각 기록 본문의 처분 줄과 각 카드의
`## Next action` 에 양쪽으로 적었다.

### 범위를 넘은 자리

- `stage/templates/**` (README 넷, `_template.md` 셋) — 팀원이 넘었다. 아무도 `opened:` 를
  안 쓰면 앞으로 새로 적는 관측이 전부 `(open ?)` 이 된다. 받는다.
- `.stage/work/planned/` — 감독이 넘었다. 계획 카드 여섯을 세우는 데 필요했고 성공 기준
  셋째가 그것을 요구한다. 받는다.
- `.stage/work/current/W-00000244/_story.md` — 카드는 자기 경로를 자기 scope 에 안 적으므로
  늘 넘는 자리다(O-00000034).
- `stage/operations/verification.md` — 감독이 넘었다. 회고의 규칙 후보가 승격 조건을 만족해
  기존 항목을 고쳤다(R-00000244). 플러그인이 소유하는 자리라 이 저장소만이 아니라 스테이지를
  까는 모든 프로젝트에 걸린다.

### 남은 구멍

`opened:` 를 강제하는 것이 없다. 템플릿에는 들어갔지만 감사가 안 본다. 안 적으면 목록이
`(open ?)` 로 나오는데, 그 값이 화면에 보이므로 조용히 썩지는 않는다. 지금은 받지 않는다.

### Executed at close — 2026-08-08

```
$ python3 -m unittest discover -s stage/hooks/tests -q -k context
[exit 0]
----------------------------------------------------------------------
Ran 18 tests in 0.239s

OK

$ python3 -m unittest discover -s stage/hooks/tests -q -p test_session_context_observations.py
[exit 0]
----------------------------------------------------------------------
Ran 8 tests in 0.140s

OK

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 372 tests in 1.490s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (295 earlier lines omitted)
WARNING: preflights.codex is not configured; continuing without a venue health check
WARNING: reapers.codex is not configured after executor turn; jobs may remain
[W-00000001] executor failed; retry 1/3
WARNING: preflights.codex is not configured; continuing without a venue health check
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1786166416
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1786166416. Human review + merge required; the base branch was not modified.
Removed unattended worktree: /private/var/folders/wg/6hnd_f255_z4ngk7ynwptym40000gn/T/tmppgu3e8v4/unattended/W-00000001-1786166416
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
Ran 604 tests in 90.330s

OK

$ python3 stage/scripts/audit_stage.py
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

## Retrospective

## Promotion decision

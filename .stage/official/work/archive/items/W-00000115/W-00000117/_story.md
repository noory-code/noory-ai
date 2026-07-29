---
id: W-00000117
title: 리뷰 판정을 파일로 받는다
kind: development
venue: codex
milestone:
priority:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -q"
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000123
promotion: not_applicable
review: not_required
scope: stage/scripts/drive.py, stage/skills/stage-retrospective/close_work.py, stage/skills/stage-drive/SKILL.md, stage/scripts/tests/, .stage/settings.json, stage/templates/, stage/CHANGELOG.md, stage/.claude-plugin/plugin.json, stage/.codex-plugin/plugin.json
promotes:
decision_refs:
---

# W-00000117 리뷰 판정을 파일로 받는다

## Purpose

DE-00000039 §2. 리뷰어가 드라이버가 준 경로에 기준별 판정을 JSON 으로 쓰고 기계는 그것만 읽는다(O-00000004). 산문 라벨 탐색(reviewer_report_error, latest_review_failures)과 리뷰 명령 네 벌, 템플릿, 디스포지션 계약이 함께 움직인다. 템플릿에는 리뷰 계약이 처음 실린다.

## Actions

- 드라이버가 리뷰어에게 **판정을 쓸 파일 경로**를 넘긴다. 바뀐 파일 목록을 넘기는
  `STAGE_CHANGED_PATHS_FILE` 과 같은 모양이므로 새 개념이 아니다.
- 리뷰어는 기준별 통과/실패와 승인 여부를 그 파일에 JSON 으로 쓴다. 산문 리뷰는 지금처럼
  공유 로그에 남는다 — 사람이 읽을 몫은 안 줄인다. **기계는 JSON 만 읽는다.**
- 산문에서 표식을 찾는 자리를 없앤다. 오늘 여섯 번 걸린 곳이다:
  `close_work.py:318` `reviewer_report_error`, `:226` `latest_review_failures`,
  `:324` 의 절 표식 세기.
- 부르는 자리 넷을 같이 옮긴다 — `drive.py:1444`(다음 바퀴에 넘길 실패 목록), `:1670`(닫은 뒤
  남은 실패 확인), `:2160`(무인 판정), `close_work.py:674`·`717`(닫기 리뷰 둘).
- 리뷰 명령 **여섯 벌**을 새 계약으로 바꾼다(`.stage/settings.json` 의 `review.reviewers` 둘 +
  `review.strengths` 넷). 한 벌만 고치면 실행 방식마다 계약이 갈린다.
- `stage/templates/` 에 리뷰 계약을 싣는다. 지금 템플릿에는 판정 표식이 아예 없어서 새
  프로젝트는 리뷰 계약을 못 받는다.
- 실패 항목을 처분하는 계약(`executor_review_dispositions`)이 JSON 판정을 근거로 돌게 한다.
  지금은 산문 FAIL 줄을 글자로 맞춘다.
- **감독·무인의 처분 계약이 갈린 것을 함께 맞춘다** — 감독 쪽은 실패 목록을 안 넘기고
  빈 경로 목록을 바로 실패로 만든다. 프롬프트가 약속한 "이유 있는 안 받음·미룸은 빈 배열을
  주장해도 된다"가 무인에서만 참이다(W-00000121 이 넘긴 근거).
- 죽은 필드 `base_repository_paths` 를 걷는다(`drive.py:178`, `191-201`). 검증만 남고 안 쓰인다.
- `stage/CHANGELOG.md` 미출시 절에 적는다. **매니페스트 버전은 안 건드린다.**

## User value

통과한 일이 판정을 읽다가 실패로 기록되지 않는다. 오늘 여섯 번 그랬고, 그중 한 번은 리뷰어가
파서로 통과까지 확인해 놓고 **그 사실을 설명하다가** 걸렸다. 리뷰어에게 "네가 쓴 절 이름을
입에 담지 마라"를 요구할 수는 없다.

## Scope

### Included


### Excluded


## Risks

- **리뷰어가 JSON 을 안 쓰거나 깨뜨릴 수 있다.** 산문보다 형식이 빡빡하다. 그러나 못 읽으면
  못 읽는다고 명확히 실패하고, 지금처럼 "통과했는데 실패로 기록"되지는 않는다. 실패의 뜻이
  분명해지는 것이 이 카드의 값이다.
- 리뷰 명령 여섯 벌을 한꺼번에 바꾸므로 한 벌이라도 빠지면 그 자리만 옛 계약으로 남는다.
  기준에서 여섯 전부를 센다.
- 파일 하나가 더 오간다. 다만 바뀐 파일 목록이 이미 같은 방식이라 새 구조가 아니다.

## Success criteria

- 리뷰어가 판정을 JSON 파일로 쓰고, 드라이버·닫기가 그 파일만 읽어 통과를 정한다. 산문에서
  절 표식을 찾는 코드가 남아 있지 않다.
- **리뷰어가 산문에 절 이름이나 판정 라벨을 그대로 적어도 판정이 안 흔들린다.** 오늘 여섯 번
  걸린 그 상황을 고정하는 테스트가 있다.
- 판정 파일이 없거나 JSON 이 깨졌으면 **그 사유로** 실패한다. 통과를 실패로 바꾸는 것과
  구분된다. 두 경우를 각각 고정하는 테스트가 있다.
- 부르는 자리 다섯(감독 스텝, 무인 스텝, 닫기 리뷰 둘, 다음 바퀴 실패 목록)이 전부 새 계약을
  쓴다. 자리마다 테스트가 있다.
- 리뷰 명령 여섯 벌(`review.reviewers` 둘 + `review.strengths` 넷)이 전부 새 계약을 말한다.
- `stage/templates/` 가 리뷰 계약을 담는다. 새 프로젝트가 그것을 받는다.
- 실패 항목 처분이 JSON 판정을 근거로 돌고, 감독과 무인이 같은 규칙을 쓴다 — 이유를 단
  안 받음·미룸은 양쪽 다 빈 경로 목록을 주장할 수 있다. 두 자리를 각각 고정하는 테스트가 있다.
- `base_repository_paths` 필드가 코드에서 사라진다.
- `python3 -m unittest discover -s stage/scripts/tests -q` 와
  `python3 -m unittest discover -s stage/hooks/tests -q` 가 전부 통과한다.
- `stage/CHANGELOG.md` 미출시 절에 항목이 있고 매니페스트 버전은 그대로다.

### 리뷰어가 왜 실패했는지 모른 채 시도를 쓰지 않는다

이 카드의 목적이 "통과한 일이 판정을 읽다가 실패로 안 된다"이므로, 새 계약이 **말 안 한
조건으로 실패시키는 것**도 같은 병이다. 아래를 같은 값으로 센다.

- **판정 파일을 읽다 죽는 조건을 리뷰 명령 여섯 벌이 전부 말한다.** 지금 `review.strengths`
  네 벌이 기준 이름 중복 금지, 한 줄·빈 값 금지, 키가 정확히 둘이라는 것을 안 말한다. 셋 다
  판정 읽기의 하드 실패 조건이라, 그 프롬프트만 따른 리뷰어는 이유도 모른 채 시도를 하나
  쓴다. 여섯 벌이 같은 조건을 말하는지 확인하는 테스트가 있다.
- **실행자 프롬프트가 코드보다 느슨하지 않다.** 프롬프트는 "이유를 단 안 받음·미룸은 빈 경로
  배열을 주장해도 된다"고 하는데, 코드는 처분이 **전부** 안 받음·미룸일 때만 받는다. 하나라도
  받은 라운드가 빈 배열을 주장하면 실패한다. 두 벌 다 코드와 같은 말을 하게 한다.
- **깨진 판정이 공짜 재시도로 흐르지 않는다.** 지금 판정을 못 읽으면 실패 목록이 빈 목록으로
  나오고, 닫기 출력에 인프라 표식이 우연히 섞이면 그 라운드가 시도를 안 쓴다. 못 읽는 것은
  인프라 실패가 아니라 리뷰 실패다. 그 경우를 고정하는 테스트가 있다.
- **없어진 `BLOCK:` 훑기를 설명하는 주석이 남아 있지 않다.** `close_work.py:455-458`,
  `:690-692` 가 아직 그 훑기로 동작을 설명한다.

## Next action

끝나면 사람이 O-00000004(산문 판독)와 O-00000010(도는 역할 짐작)을 다시 본다. 앞의 것은 이
카드가 닫고, 뒤의 것은 시도 기록에 도는 역할을 적어야 닫히므로 W-00000118·119 가 `drive.py`
를 만질 때 함께 판단한다.

## Progress

드라이버 감독 실행 두 바퀴, 2026-07-29. 첫 바퀴는 기준을 다 통과했으나 **안 닫았다** — 새
계약이 말 안 한 조건으로 리뷰어를 실패시키는 자리가 남았다. 기준 넷을 더하고 둘째 바퀴에서
열넷 전부 통과, APPROVED, 드라이버 판정도 통과.

**둘째 바퀴가 새 계약으로 판정된 첫 사례다** — 판정이
`.stage/.runtime/driver/verdicts/W-00000117.json` 에서 나왔고 산문은 안 읽혔다.

## Verification

인수 검사 통과 — 스크립트 461개, 훅 343개. 리뷰 판정: 기준 열넷 전부 PASS, APPROVED
(JSON 판정 파일).

### 첫 바퀴의 실패가 이 카드의 근거였다

일곱 번째이자 마지막 사례다. 리뷰어가 "산문에 판정 라벨을 적어도 판정이 안 흔들린다"는 기준을
**통과로 판정하면서**, 무슨 라벨을 심어 봤는지 설명하느라 `FAIL` 이라는 글자를 적었다. 옛
파서가 그것을 읽고 자기가 낸 승인을 뒤집었다.

### 첫 바퀴를 왜 안 닫았나

리뷰가 APPROVED 를 냈는데 기준 밖 지적 둘이 이 카드가 없애려던 병과 같은 모양이었다. 리뷰
명령 여섯 벌 중 넷이 판정 파일을 읽다 죽는 조건(기준 이름 중복, 빈 값, 키 개수)을 안 말했다 —
그 프롬프트만 따른 리뷰어는 이유도 모른 채 시도를 쓴다. 함정을 없애면서 새 함정을 같은 자리에
놓은 셈이다. 기준 넷을 더해 다시 돌렸다.

### 리뷰 지적 처분 (둘째 바퀴, 기준 밖 넷)

- **범위 밖 문서 셋이 `BLOCK:` 계약을 그대로 말한다 — 받는다, W-00000130 으로.**
  `operations/review.md`, `docs/SCHEMA_V4.md`, `stage-retrospective/SKILL.md`. 이제 `BLOCK:`
  을 찍고 0 으로 끝나면서 승인 판정을 쓴 명령은 카드를 닫는다. 문서가 틀린 계약을 말하면
  다음 사람이 그것을 믿고 리뷰 명령을 만든다.
- **`stage-drive/SKILL.md:250-251` 의 인프라 실패 서술이 좁게 거짓 — 받는다, 같은 카드로.**
  판정 파일이 있고 깨졌으면 타임아웃 문구가 섞여도 시도를 쓴다. 그 문장은 판정 파일이 없을
  때만 참이다.
- **깨진 판정에서 실패 목록이 비어 다음 실행자가 무엇이 틀렸는지 못 받는다 — 안 받는다.**
  공짜 재시도는 이번에 막았다. 남은 것은 정보 손실인데, 깨진 판정은 리뷰어 쪽 문제이고 다음
  라운드가 판정을 다시 쓰므로 앞 라운드 목록이 없어도 진행된다. 실제로 겪으면 본다.
- **`run_check` 의 raw 반환을 닫기 쪽 셋이 안 쓴다 — 안 받는다.** 인수 검사 경로가 쓰므로
  죽은 값이 아니다. 반환 모양을 자리마다 다르게 만드는 값이 더 크다.

### Executed at close — 2026-07-29

```
$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (161 earlier lines omitted)
Unattended run on isolated branch: stage/driver/W-00000001-1785330906 (base: main)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] close failed (acceptance or independent review); close_work output:
independent review did not pass; retry 1/2
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1785330906
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785330906. Human review + merge required; the base branch was not modified.
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
Ran 465 tests in 65.794s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (161 earlier lines omitted)
Unattended run on isolated branch: stage/driver/W-00000001-1785330971 (base: main)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] close failed (acceptance or independent review); close_work output:
independent review did not pass; retry 1/2
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1785330971
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785330971. Human review + merge required; the base branch was not modified.
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
Ran 465 tests in 66.803s

OK

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 343 tests in 1.030s

OK

$ python3 stage/scripts/audit_stage.py
[exit 0]
Stage audit: /Users/woogis/Workspace/repo/noory-ai/.stage
OK: no findings
Summary: errors=0, warnings=0
```

## Retrospective

[R-00000123](../../../retrospectives/R-00000123.md)

## Promotion decision

not_applicable — 플러그인 소스 수정이고 `.stage/official/` 로 올릴 것이 없다.

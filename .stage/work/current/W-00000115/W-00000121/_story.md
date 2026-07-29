---
id: W-00000121
title: 관측 기준이 사람의 편집을 실행자에게 묻지 않는다
kind: fix
venue: codex
milestone:
source:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -q"
  - "python3 -m unittest discover -s stage/hooks/tests -q"
status: completed
verification: passed
retrospective: completed
retrospective_ref: R-00000114
promotion: not_applicable
review: not_required
scope: stage/scripts/drive.py, stage/scripts/tests/, stage/CHANGELOG.md, stage/.claude-plugin/plugin.json, stage/.codex-plugin/plugin.json
promotes:
decision_refs:
---

# W-00000121 관측 기준이 사람의 편집을 실행자에게 묻지 않는다

## Purpose

W-00000116 이 대조를 카드 누적으로 바꾸면서 기준 스냅샷을 첫 시도에 한 번만 찍게 했다(drive.py:1420, 1965). 그래서 스텝 사이에 사람이 고치고 커밋한 파일까지 영원히 목록에 남고, 실행자가 자기가 안 건드린 파일을 주장해야 맞게 된다. 감독 흐름은 스텝 사이의 사람 개입을 전제하므로 다음 재시도에서 바로 터진다. O-00000005·6 과 같은 모양의 셋째 구멍이다. 같은 변경이 들여온 결함 하나를 함께 걷는다 — test_template_v4.py:117 이 플러그인 밖의 운영자 설정(PLUGIN_ROOT.parent/.stage/settings.json)을 읽어, 설치본에서는 그 파일이 없어 스위트가 죽는다.

## Actions

- 대조에 넘기는 목록에서 **사람이 스텝 사이에 바꾼 것**을 뺀다. 실행자가 도는 구간이 아니면
  실행자의 일이 아니다. 드라이버는 실행자를 부르기 직전과 직후를 자기 눈으로 보므로 그
  구간을 안다 — 누적 목록에서 이번 실행자 구간 밖의 사람 변경을 걸러내면 된다.
- 카드 누적 성질은 지킨다. 앞 **시도의 실행자**가 바꾼 것은 계속 목록에 있어야 한다
  (W-00000116 이 고친 O-00000006). 빠지는 것은 사람 몫뿐이다.
- 감독·무인 두 자리에 같이 적용한다 — 기준 스냅샷(`drive.py:1421`, `1966`)과 목록 생성
  (`drive.py:1471`, `2033`).
- `test_template_v4.py` 가 플러그인 밖(`PLUGIN_ROOT.parent / ".stage/settings.json"`)을 읽지
  않게 한다. 플러그인 테스트는 플러그인 것만 본다 — 템플릿이 두 문장을 갖는지만 확인하고,
  운영자 설정이 그것을 따르는지는 플러그인이 판정할 일이 아니다.
- `stage/CHANGELOG.md` 항목과 두 매니페스트 패치 올림.

## Scope

`stage/scripts/drive.py` 의 관측 구간과 두 호출 자리, `stage/scripts/tests/`(사람 편집이
섞이는 상황을 고정하는 테스트와 플러그인 밖을 읽던 테스트의 수정), CHANGELOG, 두 매니페스트.

이 카드가 **안 하는 것**: 리뷰 판정 계약(W-00000117), 한계값과 사전 점검(W-00000118, 코덱스
캐시 잠금이 시도를 먹는 것도 그 카드), 상한 되돌리기(W-00000119).

## Success criteria

- 스텝 사이에 사람이 파일을 고치고 커밋해도, 다음 시도에서 실행자가 그 파일을 안 적었다는
  이유로 실패하지 않는다. 그 상황을 고정하는 테스트가 있다.
- 앞 시도의 실행자가 바꾼 파일은 여전히 목록에 남는다 — W-00000116 이 세운 성질이 안 깨진다.
  같은 묶음의 테스트가 이것도 고정한다.
- 감독·무인 두 자리 모두에서 위 두 성질이 성립한다.
- `test_template_v4.py` 가 플러그인 디렉터리 밖의 파일을 열지 않는다.
- `python3 -m unittest discover -s stage/scripts/tests -q` 와
  `python3 -m unittest discover -s stage/hooks/tests -q` 가 전부 통과한다.
- `stage/CHANGELOG.md` 에 항목이 있고 두 매니페스트 버전이 같은 값으로 패치 올림돼 있다.

### 위험

사람 몫을 걸러내다 실행자 몫까지 걸러내면 W-00000116 이 고친 것이 되돌아간다. 두 성질을 같은
테스트 묶음에서 함께 고정해 한쪽이 다른 쪽을 깨뜨리지 못하게 한다. 커밋이 끼어도 마찬가지다 —
사람이 스텝 사이에 커밋하는 것은 감독 흐름의 정상 동작이므로, 커밋된 사람 변경도 빠져야 한다.

## Related truth

- [DE-00000039](../../../official/decisions/records/DE-00000039.md) §1 — 이 계약의 소유자
- [R-00000113](../../../work/retrospectives/R-00000113.md) — 이 구멍을 연 경위


## Progress

드라이버 감독 실행 한 바퀴, 2026-07-29. 기준 여섯 전부 PASS, 리뷰 APPROVED. 플러그인 0.54.4.

드라이버는 이것을 **실패로 판정했다** — 판정 내용이 아니라 판정을 읽는 방식 때문이다
(아래 처분 참조).

## Verification

인수 검사 통과 — 스크립트 422개, 훅 343개. 리뷰 판정: 기준 여섯 전부 PASS, APPROVED.

### 관측 구간을 읽는 자리 (전수)

| 자리 | 무엇 |
|---|---|
| `drive.py:313` `repository_path_snapshot` | 관측의 정의 |
| `drive.py:339` `changed_repository_paths` | 두 스냅샷의 차이 |
| `drive.py:361` | 실행자 구간의 차이를 누적에 더한다. 이 카드가 만든 자리 |
| `drive.py:1446`·`1495` (감독) / `1997`·`2046` (무인) | 실행자 호출 **직전·직후** 스냅샷. 구간의 경계 |
| `drive.py:1516` (감독) / `2090` (무인) | 드라이버가 만든 로그 경로를 대조에서 뺀다 |
| `close_work.py:161`·`200` | 뺄 경로를 받아 양쪽에서 지운다 |
| `drive.py:178`·`191-201` | `base_repository_paths` 형태 검증. **이제 안 쓰인다** — 아래 처분 |

### 드라이버가 실패로 판정한 이유

리뷰어가 마지막 줄에서 자기가 한 일을 설명하며 `### Reviewer report` 라는 글자를 그대로
적었다. 검사가 덧붙은 부분에서 그 표식을 세므로(`close_work.py:313`) 감싸는 명령이 붙인 것과
합쳐 둘이 되어 "절이 두 번 나왔다"로 실패했다.

**받지 않는다 — 일은 통과했다.** 기준 여섯이 다 섰고 인수 검사도 통과했다. 실패한 것은
판정을 산문에서 글자로 찾는 방식이다. O-00000004 에 변형 둘로 기록했고, 그 자리를 없애는
것이 W-00000117 이다. 앞의 두 변형은 리뷰어가 형식을 덜 지켜서 걸렸는데 이번엔 자기가 한
일을 정확히 설명해서 걸렸다 — 산문을 읽는 한 이 방향은 못 막는다.

### 리뷰 지적 처분 (기준 밖 넷)

- **지시문과 검사가 다른 말을 한다 — 받는다, W-00000117 로.** 실행자 프롬프트는 "이 카드로
  바뀐 모든 경로를 모든 시도에 걸쳐" 적으라 하는데 검사는 이제 실행자 구간 것만 받는다. 이
  카드의 scope 에 설정·템플릿이 없어 실행자가 고칠 수 없었다 — 내가 카드를 좁게 썼다.
  W-00000117 의 scope 가 둘 다 품으므로 거기서 문장을 맞춘다.
- **`base_repository_paths` 가 검증만 남고 안 쓰인다 — 받는다, W-00000117 로.** 죽은 필드다.
  더불어 0.54.3 이 쓴 시도 기록을 물려받으면 사람 변경이 섞인 목록을 이어받는다. 지금 이
  저장소에는 그런 기록이 없다(이 카드 실행으로 새로 썼다). 같은 파일을 만지는 다음 카드에서
  걷는다.
- **무인 리뷰어가 아직 다른 기준의 목록을 받는다 — 미룬다.** `close_work.py:449` 가 HEAD
  커밋 목록을 넘긴다. 이 카드 이전부터 있던 동작이고 `close_work.py` 는 이 카드 scope 밖이다.
  W-00000117 에 근거로 넘긴다.
- **테스트가 사람 개입을 파일 추가로만 고정한다 — 안 받는다.** 비교가 경로별 상태 동일성이라
  기존 파일 수정도 같은 갈래를 지난다. 같은 것을 두 번 고정하는 값이다.


### Executed at close — 2026-07-29

```
$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (132 earlier lines omitted)
Unattended run on isolated branch: stage/driver/W-00000001-1785307464 (base: main)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] close failed (acceptance or independent review); close_work output:
independent review did not pass; retry 1/2
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1785307464
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785307464. Human review + merge required; the base branch was not modified.
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
Ran 422 tests in 61.528s

OK

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 343 tests in 1.046s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (132 earlier lines omitted)
Unattended run on isolated branch: stage/driver/W-00000001-1785307527 (base: main)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] close failed (acceptance or independent review); close_work output:
independent review did not pass; retry 1/2
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1785307527
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785307527. Human review + merge required; the base branch was not modified.
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
Ran 422 tests in 61.967s

OK

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 343 tests in 1.007s

OK

$ python3 stage/scripts/audit_stage.py
[exit 0]
Stage audit: /Users/woogis/Workspace/repo/noory-ai/.stage
OK: no findings
Summary: errors=0, warnings=0
```

## Retrospective

[R-00000114](../../../retrospectives/R-00000114.md)

## Promotion decision

not_applicable — 플러그인 소스 수정이고 `.stage/official/` 로 올릴 것이 없다.

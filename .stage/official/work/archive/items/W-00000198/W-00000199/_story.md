---
id: W-00000199
title: 끝난 기록이 어디로 가고 누가 옮기는지 정한다
kind: design
venue: claude
milestone:
autonomous: false
acceptance:
  - "python3 stage/scripts/audit_stage.py --project-root ."
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000198
promotion: promoted
review: not_required
scope: stage/docs/BLUEPRINT.md, stage/docs/SCHEMA_V5.md, stage/CHANGELOG.md, .stage/decisions/pending/, .stage/official/decisions/records/DE-00000030.md
promotes: .stage/official/decisions/index.md, .stage/official/decisions/records/DE-00000057.md, .stage/official/decisions/records/DE-00000030.md
decision_refs: DE-00000057
---

# W-00000199 끝난 기록이 어디로 가고 누가 옮기는지 정한다

## Purpose

끝난 기록의 자리와 그것을 옮기는 주체가 어디에도 안 적혀 있어 매번 다시 판단하게 되므로, 보관 자리와 이동 주체를 결정으로 못박고 설계 문서에 싣는다

## Actions

없음 — 결정 하나와 문서 반영이 한 덩어리라 나누면 목록만 길어진다.

## User value

다음에 새 기록 갈래를 만들 때 "끝나면 어디로 가나"를 다시 토론하지 않는다. 규칙이 한 줄로
읽히고, 그 규칙을 누가 집행하는지도 같이 읽힌다.

## Scope

### Included

- 끝난 기록의 보관 자리를 결정으로 못박는다: 결정·제안·상태 각 갈래가 `official/` 아래
  자기 보관함을 가지고, 카드가 이미 하는 것과 같은 모양이다.
- **폴더가 상태다**를 규칙으로 적는다. 살아 있는 서랍에 있으면 살아 있는 것이고, 보관함에 있으면
  끝난 것이다. 상태를 말하는 frontmatter 칸을 따로 두지 않는다.
- 제안만 실림·접힘·절반 세 결과를 한 칸으로 구분한다. P-00000004 가 절반이라 두 값으로는
  지금 인덱스가 들고 있는 정보가 깎인다.
- 갈래마다 **누가 옮기는지**를 정한다. 허가증은 계산되니 카드 보관 명령이, 나머지는 사람이
  판정하니 닫는 명령이 옮긴다.
- DE-00000030 첫머리에 무엇이 언제 그것을 대체했는지 적는다 — DE-00000030 자신이 정한 규칙이다.
- 새 규칙을 `stage/docs/BLUEPRINT.md` 와 `stage/docs/SCHEMA_V5.md` 에 싣는다.

### Excluded

- 코드는 안 건드린다. 자리를 만드는 것은 W-00000200, 옮기는 쪽은 W-00000201·202 다.
- 스키마 버전은 안 올린다. 그 판단의 근거는 에픽이 들고 있다.

## Risks

- **DE-00000030 은 공식 결정이라 이 카드가 끝난 뒤에야 고칠 수 있다.** 통행증은 카드가 완료되고
  승격이 승인된 뒤에만 통하므로, 대체 표시는 이 카드의 마지막 걸음이다. 순서를 착각하면 카드
  중간에 막힌다.
- 새 결정이 DE-00000030 을 통째로 뒤집는 것처럼 읽히면 안 된다. "구속하는 결정만 승격한다"는
  그대로 살아 있고, 바뀌는 것은 안 올린 기록이 어디에 사는가 하나다.

## Success criteria

- 새 기록 갈래를 만드는 사람이 "끝나면 어디로 가나"를 문서 한 곳에서 답할 수 있다.
- 갈래마다 옮기는 주체가 사람인지 명령인지 명시돼 있다.
- DE-00000030 을 여는 사람이 그 규칙의 어느 부분이 아직 살아 있는지 첫머리에서 안다.
- 감사가 오류 없이 통과한다.

## Next action

결정 DE-00000057 을 설계 문서에 싣는다. DE-00000030 의 대체 표시는 카드를 닫은 뒤 통행증으로
쓴다 — 통행증은 완료된 카드만 받는다.

## Related truth

- DE-00000030 — "다 쓴 허가증은 승격하지 않는다"까지만 정했고 그것이 어디에 사는지는 비어 있다.
- `stage/docs/PHILOSOPHY.md` §목적이 약속이다 — 규칙이 빈자리를 남기면 아무 일도 안 일어난다.

**W-00000200 이 물려받는 제약**: 세션 첫머리 요약은 자리마다 선언된 수명주기로 묶는다. 보관
서랍 셋을 `official` 로 선언하면 그 줄에 서랍 세 개가 더 붙고, 대신 진행 중·계획 줄에서
스물한 장이 빠진다. 자리마다 앞의 세 개와 총 개수만 찍히므로 요약이 길어지는 폭은 세 줄이고,
바꾸려던 방향과 맞다. 다른 값을 고르려면 이 계산부터 다시 한다.

## Progress

DE-00000057 이 자리와 이동 주체를 정했다. 설계도에 §11-2 를 더해 살아 있는 서랍과 보관함을
그림과 표로 실었고, 스키마 문서에 같은 계약을 영어로 실었다.

그림을 한 번 고쳤다. 처음에는 노드 라벨에 서랍 이름 대신 그 서랍에 남는 것을 적어서, 화살표가
"안 쓴 허가를 보관한다"로 읽혔다.

DE-00000030 의 대체 표시는 아직 안 썼다 — 통행증이 완료된 카드만 받으므로 닫은 뒤에 쓴다.

## Verification


### Executed at close — 2026-08-04

```
$ python3 stage/scripts/audit_stage.py --project-root .
[exit 0]
Stage audit: /Users/woogis/Workspace/repo/noory-ai/.stage
OK: no findings
Summary: errors=0, warnings=0

$ python3 stage/scripts/audit_stage.py --project-root .
[exit 0]
Stage audit: /Users/woogis/Workspace/repo/noory-ai/.stage
OK: no findings
Summary: errors=0, warnings=0

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 358 tests in 1.378s

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
[W-00000001] completed on stage/driver/W-00000001-1785823412
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785823412. Human review + merge required; the base branch was not modified.
Removed unattended worktree: /private/var/folders/wg/6hnd_f255_z4ngk7ynwptym40000gn/T/tmpxnnskbpi/unattended/W-00000001-1785823412
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
Ran 562 tests in 87.255s

OK
```

## Retrospective

R-00000198.

## Promotion decision

DE-00000057 을 공식으로 올렸다 — 앞으로의 작업을 구속하므로 DE-00000030 의 판정 규칙이
승격을 요구한다. 함께 DE-00000030 첫머리에 그 한 줄이 대체됐다고 적고 공식 결정 인덱스에
줄을 더했다.

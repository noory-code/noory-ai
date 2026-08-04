---
id: W-00000198
title: 끝난 기록을 살아 있는 서랍에서 빼낸다
kind: development
venue: codex
milestone: M-00000002
autonomous: false
acceptance:
  - "python3 stage/scripts/audit_stage.py --project-root ."
status: completed
verification: passed
retrospective: completed
retrospective_ref: R-00000203
promotion: not_applicable
review: not_required
scope: stage/hooks/, stage/scripts/, stage/skills/, stage/templates/, stage/docs/, stage/CHANGELOG.md, .stage/
promotes:
decision_refs:
---

# W-00000198 끝난 기록을 살아 있는 서랍에서 빼낸다

## Purpose

끝난 기록과 살아 있는 기록이 한 서랍에 섞여 있어 무엇이 아직 유효한지 알려면 파일을 열어 산문을 읽어야 하므로, 끝난 기록이 자기 보관함으로 빠져 서랍만 보고 판단되게 한다

## Stories

- W-00000199 — 끝난 기록이 어디로 가고 누가 옮기는지 정한다 (design)
- W-00000200 — 보관 서랍 셋을 토폴로지에 등록한다 (development)
- W-00000201 — 기록을 닫고 되돌리는 명령을 만든다 (development)
- W-00000202 — 다 쓴 허가증이 카드와 함께 자리를 옮긴다 (development)
- W-00000203 — 이 저장소의 끝난 기록을 서랍에서 비운다 (documentation)

순서가 있다. W-00000199 가 자리와 주체를 정하고, W-00000200 이 그 자리를 만들고,
W-00000201·202 가 옮기는 쪽을 만들고, W-00000203 이 그 명령으로 이 저장소를 비운다.

## User value

몇 달 만에 돌아왔을 때 서랍을 열면 지금 살아 있는 것만 보인다. 무엇이 아직 유효한지 알려고
스물아홉 개 파일을 열어 산문을 읽지 않아도 된다.

## Scope

### Included

- 결정·제안·상태 세 갈래에 보관 자리를 만들고, 그 자리를 참조 해석·감사·초기화가 함께 안다.
- 제안·관측·질문을 닫고 되돌리는 명령. 본문의 근거, 파일 자리, 인덱스가 한 번에 움직인다.
- 다 쓴 허가증이 카드 보관과 함께 옮겨진다.
- 이 저장소에 남은 끝난 기록 스물한 장을 그 명령으로 비운다.
- 감사가 관측·질문·제안의 필수 절 누락을 잡는다.

### Excluded

- **스키마 버전은 안 올린다.** 보태는 변경이라 기존 프로젝트가 그대로 돌아가고, 올리면
  novel-workspace 가 옮기기 전까지 모든 수정이 막힌다. 대신 옛 플러그인으로 이 저장소를
  감사하면 소유 위치 오류가 뜬다 — 읽기 전용 잡음이라 받는다.
- **상태를 말하는 frontmatter 칸을 새로 안 만든다.** 폴더가 상태다. 두 자리가 되면 또 어긋난다.
- 다른 프로젝트의 기록은 안 옮긴다. 그쪽은 새 명령으로 각자 닫는다.
- `official/decisions/records/` 의 뜻은 안 건드린다 — 지금 구속하는 규칙만 사는 자리로 남는다.

## Risks

- **옮긴 기록을 가리키는 기존 링크가 끊긴다.** 참조 해석이 갈래마다 후보 경로를 들고 있어서,
  보관 경로를 같이 넣지 않으면 보관된 관측·제안·허가증을 가리키는 모든 인용이 깨진다.
- **명령이 파일만 옮기고 인덱스를 안 고치면 지난 세션의 실패가 그대로 반복된다.** 상태 인덱스는
  지금 갱신 명령이 없어 손으로 고쳐 왔다.
- **옮기다 중간에 실패하면 반쯤 옮겨진 상태가 남는다.** 파일은 갔는데 인덱스는 옛 줄을 들고 있는
  꼴이 제일 나쁘다.
- 관측 여섯 장은 열렸는지 닫혔는지 기계가 못 센다. 사람 판정이 필요하고, 그 판정이 늦으면
  W-00000203 이 막힌다.

## Success criteria

- 결정·제안·관측·질문 네 서랍에 아직 살아 있는 기록만 남는다.
- 끝난 기록을 사람이 손으로 옮기는 자리가 없다 — 전부 명령이 옮긴다.
- 보관된 기록을 가리키는 기존 인용이 그대로 해석된다.
- 세션을 열면 요약이 살아 있는 것만 센다.
- 관측·질문·제안에서 필수 절이 빠지면 감사가 잡는다.

## Next action

W-00000199 부터. 보관 자리와 이동 주체를 결정으로 못박고, DE-00000030 의 "다 쓴 허가증은
대기 서랍에 남는다"를 대체 표시한다.

## Related truth

- DE-00000030 — 앞으로를 구속하는 결정만 공식으로 올리고 일회성 허가는 안 올린다. 이 에픽이
  "그럼 어디에 두나"를 채우고, 남는 자리를 대기 서랍에서 보관함으로 옮긴다.
- O-00000029 — 내가 기억해서 적어야 하는 상태는 예외 없이 낡는다. 그래서 옮기는 주체가
  사람이 아니라 명령이어야 한다.
- `stage/docs/PHILOSOPHY.md` — `.stage/` 기록의 진짜 독자는 팀원이 아니라 나중의 본인이다.

## Progress

스토리 다섯이 순서대로 끝났다. 규칙(W-00000199) → 자리(W-00000200) → 닫는 명령과 게이트
(W-00000201) → 허가증 이동과 보관 인덱스 검사(W-00000202) → 이 저장소 비우기(W-00000203).

**네 서랍이 살아 있는 것만 든다.** 대기 결정 7→1, 제안 4→0, 관측 32→21, 질문 1→0.

판정이 두 번 진짜 결함을 잡았다 — 제안을 닫으면 감사가 깨지는 것, 그리고 보관 도중 삭제만
실패하면 다 쓴 허가증이 되살아나는 창(O-00000032 로 남김).

드라이버에서 관측 셋이 나왔다: O-00000030(잘린 바퀴에서 일이 끝나면 카드가 못 나온다),
O-00000031(액션 없는 스토리가 최소 시간 한도를 받는다), O-00000032.

## Verification


### Executed at close — 2026-08-04

```
$ python3 stage/scripts/audit_stage.py --project-root .
[exit 0]
Stage audit: /Users/woogis/Workspace/repo/noory-ai/.stage
OK: no findings
Summary: errors=0, warnings=0

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 361 tests in 1.339s

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
[W-00000001] completed on stage/driver/W-00000001-1785835605
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785835605. Human review + merge required; the base branch was not modified.
Removed unattended worktree: /private/var/folders/wg/6hnd_f255_z4ngk7ynwptym40000gn/T/tmpcotclzmm/unattended/W-00000001-1785835605
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
Ran 577 tests in 90.061s

OK
```

## Retrospective

R-00000203.

## Promotion decision

DE-00000057 이 이미 공식이다. 새로 올릴 산출물은 없다.

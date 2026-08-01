---
id: W-00000164
title: 카드 그릇이 층마다 무엇을 물을지 계약으로 세운다
kind: development
venue: codex
milestone: M-00000001
priority:
autonomous: false
acceptance: []
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000164
promotion: not_applicable
review: not_required
scope: stage/templates/, stage/skills/stage-work/, stage/docs/, stage/CHANGELOG.md, .stage/
promotes:
decision_refs:
---

# W-00000164 카드 그릇이 층마다 무엇을 물을지 계약으로 세운다

## Purpose

**DE-00000035 가 규모(에픽·스토리·액션)를 계약으로 정했지만, 각 층이 무엇을 물어야 하는지는
어디서도 안 정했다**(확인함 — 그 결정 본문에 칸 얘기가 한 줄도 없다). 지금은 그릇 파일 셋이
그 답을 우연히 들고 있고, 근거가 되는 계약이 없으니 아무도 대조를 안 한다.

대조를 안 해서 생긴 어긋남 셋을 2026-07-31 에 실측했다.

- **일 시작한 뒤 쓰는 그릇에 `## User value` 칸이 세 규모 다 없다.** `stage-work` 스킬은 네
  칸(무엇을 하는가 / 왜 지금 / 무엇을 이루려는가 / 언제 끝나는가)을 요구하는데 그릇이 셋만 준다.
  계획으로 잡아 둔 카드는 옮겨질 때 내용을 갖고 가서 안 걸리고, 바로 시작한 카드만 걸린다.
- **한국어 그릇에 액션판이 없다.** `stage/templates/v4/locales/ko/work/planned/` 에 `_epic.md`
  와 `_story.md` 만 있다.
- **저장소 안의 한국어 그릇을 카드 만드는 명령이 안 읽는다.** `register_work.py` 의
  `_v4_template()` 이 플러그인의 영어 트리로 바로 간다. `.stage/work/planned/_story.md` 가
  한국어인데 그날 만든 카드는 전부 영어 칸으로 나왔다.

층마다 무엇을 물을지가 곧 **그 층이 무엇을 이루는 자리인지**를 정한다. 지금은 그것이 파일에만
있고 계약에는 없다.

## Actions

- [W-00000165](W-00000165.md) — 층마다 무엇을 물을지 정한다 (설계 · claude)
- [W-00000166](W-00000166.md) — 정한 대로 그릇과 그것을 읽는 길을 맞춘다 (구현 · codex)

## User value

어느 길로 카드를 만들어도 — 계획으로 잡아 두든 바로 시작하든, 에픽이든 액션이든 — 그 층이
답해야 할 것을 그릇이 다 묻는다. 지금은 바로 시작한 카드가 "무엇을 이루려는가" 칸 없이 나온다.

## Scope

### Included

- 층마다 무엇을 물을지 정하는 계약과, 그 계약대로 맞춘 그릇.
- 그릇을 고르는 길(언어 설정을 볼 것인가)까지.

### Excluded

- 카드 본문을 채웠는지 막는 검사. 아직 안 만든다 — 근거가 얇다.
- 규모 자체의 계약(누가 누구 밑에 서는가). DE-00000035 가 이미 소유한다.

## Risks

- 칸을 늘리면 카드 쓰는 값이 오른다. 층마다 **줄일 칸**도 같이 봐야 한다.
- 한국어 그릇을 살릴지 지울지가 안 정해져 있다. 여기서 갈리면 구현의 절반이 달라진다.

## Success criteria

- 층마다 무엇을 묻는지가 결정 기록 하나에 적히고, 각 칸에 왜 그 층에 필요한지가 붙는다.
- 계획으로 잡든 바로 시작하든, 세 규모 어느 것이든, 스킬이 요구하는 것을 그릇이 다 묻는다.
- 저장소 안에 있으면서 아무도 안 읽는 그릇 파일이 없다.
- 사람이 겪는 결과: 새 카드를 만들면 목적 칸이 빈 채로 나오는 일이 없다.

## Next action

없다. 자식 둘이 다 닫혔다.

## Progress

## Verification

### 성공 기준 대조 — 2026-08-01

- **층마다 무엇을 묻는지가 결정 기록 하나에 적히고, 각 칸에 왜 그 층에 필요한지가 붙는다** —
  DE-00000053 이 표 하나로 소유한다.
- **계획으로 잡든 바로 시작하든, 세 규모 어느 것이든, 스킬이 요구하는 것을 그릇이 다 묻는다** —
  세 규모를 다 대조하는 시험이 있다. 4바퀴 판정이 그릇에 절과 키를 일부러 더해 시험이 실제로
  걸리는 것을 보였다.
- **저장소 안에 있으면서 아무도 안 읽는 그릇 파일이 없다** — 한국어 카드 그릇 넷을 지웠다.
  같은 자리의 다른 한국어 파일은 카드 그릇이 아니라 프로젝트를 처음 만들 때 쓰는 것이라 남는다.
- **새 카드를 만들면 목적 칸이 빈 채로 나오는 일이 없다** — 목적은 층마다 한 문장이고 등록할 때
  막는다.

검증: 훅 356건, 스크립트 520건 통과. `audit_stage.py` 오류 0 · 경고 0.

자식 둘의 판정 처분은 각자의 카드에 있다 — W-00000165, W-00000166.

### Executed at close — 2026-08-01

```
$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 356 tests in 1.185s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (203 earlier lines omitted)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] close failed (acceptance or independent review); close_work output:
independent review did not pass; retry 1/2
WARNING: preflights.codex is not configured; continuing without a venue health check
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1785554454
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785554454. Human review + merge required; the base branch was not modified.
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
Ran 520 tests in 75.122s

OK

$ python3 stage/scripts/audit_stage.py
[exit 0]
Stage audit: /Users/woogis/Workspace/repo/noory-ai/.stage
OK: no findings
Summary: errors=0, warnings=0
```

## Retrospective

## Promotion decision

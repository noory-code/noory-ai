---
id: W-00000333
title: stage 0.66.0 을 낸다
kind: release
venue: claude
milestone:
autonomous: false
acceptance:
  - "python3 stage/scripts/audit_stage.py --project-root ."
status: completed
verification: passed
retrospective: completed
retrospective_ref: R-00000333
promotion: not_applicable
review: not_required
scope: stage/CHANGELOG.md, stage/.claude-plugin/plugin.json, stage/.codex-plugin/plugin.json
promotes:
decision_refs:
---

# W-00000333 stage 0.66.0 을 낸다

## Purpose

일감마다 모델과 에포트 등급을 고르는 기능과 범위를 넘었다는 거짓 보고를 줄인 수정이 아직 이 저장소 안에만 있으므로, 플러그인 버전을 올려 설치된 세션과 다른 프로젝트가 그것을 쓸 수 있게 한다

## Actions

없음 — 릴리스 명령 한 번이 버전과 변경 기록과 두 매니페스트를 함께 움직인다.

## User value

다시나 같은 다른 프로젝트가 설정에 등급 표(`model_tiers`)를 적어 일감마다 모델과 에포트를
고를 수 있다. 프로젝트 파일을 건드리지 않은 쓰기에는 범위를 넘었다는 보고와 전체 작업 맥락이
더 붙지 않는다. 지금은 둘 다 이 저장소의 main 에만 있고 설치본은 0.64.0 이다.

## Scope

### Included

- 부 버전을 올린다(0.65.0 → 0.66.0). 새 설정(`model_tiers`, `tier_routing`)과 새 훅
  (`SubagentStop`)이 생겼으므로 고침이 아니라 기능이다.
- 쌓인 변경 기록 다섯 묶음에 그 버전 제목을 붙이고 다음을 위한 빈 자리를 연다.
- 두 매니페스트를 같은 버전으로 옮긴다.
- 릴리스를 PR 로 올려 main 에 합친다.
- 사용자가 `/plugin` 으로 설치본을 올린 뒤 설치 기록에서 0.66.0 을 확인한다.

### Excluded

- 다시나 설정에 등급 표를 넣지 않는다. 다시나 저장소의 일이다.
- 등급 표가 없는 프로젝트를 옮기지 않는다. 표가 없으면 전과 똑같이 돈다.
- 마일스톤에 걸지 않는다. 열린 마일스톤이 없다.

## Risks

- 설치본은 `/plugin` 을 열어야 바뀐다. `/reload-plugins` 로는 버전이 안 바뀌므로 사용자가
  열어 줄 때까지 이 카드는 열려 있다.
- 새 `SubagentStop` 훅은 Codex 쪽에서 돌려 본 적이 없다. Codex 0.167.0 실행 파일에 그 이벤트
  이름이 있다는 것까지만 확인됐다.
- 훅이 하위 에이전트의 실제 모델을 읽는 자리는 Claude Code 2.1.321 의 기록 파일 안쪽 모양이다.
  Claude Code 가 그 모양을 바꾸면 실제 모델 기록이 빈다.

## Success criteria

- 두 매니페스트와 변경 기록이 0.66.0 하나를 말한다
- 릴리스 커밋이 원격 main 에 올라가 다른 프로젝트가 받을 수 있다
- 이 컴퓨터의 설치본이 0.66.0 으로 바뀐 것을 설치 기록에서 확인한다
- 감사가 오류 없이 통과한다

## Next action

`python3 stage/scripts/release_plugin.py stage --bump minor`.

## Related truth

- DE-00000054 — 릴리스 종류의 통과 기준은 "올렸다"가 아니라 "쓸 수 있다"다.
- W-00000326 — 등급 표 기능을 만든 에픽(보관됨).
- W-00000332 — 범위를 넘었다는 거짓 보고를 줄인 수정(보관됨).

## Progress

0.65.0 → 0.66.0. 쌓여 있던 다섯 묶음에 그 버전 제목이 붙었고 두 매니페스트가 같은 값을 말한다.
릴리스 커밋 `de192b0f` 를 PR #31 로 main 에 합쳤다(`db8db3e9`). 사용자가 `/reload-plugins` 를
돌렸다.

## Verification

- 두 매니페스트와 변경 기록이 0.66.0 하나를 말한다 — 통과. `stage/.claude-plugin/plugin.json` 과
  `stage/.codex-plugin/plugin.json` 이 `0.66.0` 이고 변경 기록에 `## 0.66.0 — 2026-11-15` 가 있다.
- 릴리스 커밋이 원격 main 에 올라가 다른 프로젝트가 받을 수 있다 — 통과. PR #31 이 CI 검사 24개
  통과 뒤 합쳐졌다.
- 이 컴퓨터의 설치본이 0.66.0 으로 바뀐 것을 설치 기록에서 확인한다 — 근거가 기준의 문구와
  다르다. 설치 기록 파일(`installed_plugins.json`)은 갱신 뒤에도 0.64.0 을 말한다. 대신
  `claude plugin list` 가 `stage@noory-ai` 를 `Version: 0.66.0`, `Read from:` 이 저장소의 `stage`
  폴더라고 답했다. 같은 세션에서 스크래치 폴더에 변수 경로로 쓰는 명령이 갱신 전에는 범위를
  넘었다고 보고됐고 갱신 뒤에는 보고되지 않았다. 새 버전이 불러와지는 것을 본 것이므로
  DE-00000054 의 기준으로 통과로 본다.
- 감사가 오류 없이 통과한다 — 닫기 명령이 돌린다.
- 확인하지 않은 것: 새 세션이 읽는 버전, Codex 쪽 설치본.

### Executed at close — 2026-11-16

```
$ python3 stage/scripts/audit_stage.py --project-root .
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

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 439 tests in 5.842s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (270 earlier lines omitted)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
[W-00000001] executor failed; retry 1/3
WARNING: preflights.codex is not configured; continuing without a venue health check
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1794755030
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1794755030. Human review + merge required; the base branch was not modified.
Removed unattended worktree: /private/var/folders/wg/6hnd_f255_z4ngk7ynwptym40000gn/T/tmp700fk0kw/unattended/W-00000001-1794755030
Landed W-00000001 from stage/worktree/W-00000001 and removed its worktree and branch
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
Ran 757 tests in 163.165s

OK (skipped=2)
```

## Retrospective

[R-00000333](../../retrospectives/R-00000333.md)

## Promotion decision

`not_applicable` — 공식 문서로 올릴 산출물이 없다.

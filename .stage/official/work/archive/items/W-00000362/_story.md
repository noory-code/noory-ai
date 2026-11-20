---
id: W-00000362
title: Stage 0.67.0 과 evonest 1.2.1 을 낸다
kind: release
venue: claude
milestone:
autonomous: false
acceptance:
  - "python3 stage/scripts/audit_stage.py --project-root ."
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000362
promotion: not_applicable
review: not_required
scope: stage/CHANGELOG.md,stage/.claude-plugin/plugin.json,stage/.codex-plugin/plugin.json,evonest/CHANGELOG.md,evonest/pyproject.toml,evonest/uv.lock,evonest/.claude-plugin/plugin.json,evonest/.codex-plugin/plugin.json
promotes:
decision_refs:
---

# W-00000362 Stage 0.67.0 과 evonest 1.2.1 을 낸다

## Purpose

오늘 머지한 Windows 고침들이 설치된 Stage 와 evonest 플러그인에 반영된다

## Actions

액션으로 나누지 않는다. 플러그인마다 릴리스 커밋을 하나씩 만든다.

## User value

2026-11-20 에 머지한 고침은 변경 기록의 `## Unreleased` 에만 있고 버전이 그대로라서, 설치된 플러그인에는
반영되지 않는다. 릴리스하면 다른 프로젝트와 Windows 기기가 고친 훅 명령과 리뷰 명령을 받는다.

## Scope

### Included

- Stage 를 0.66.6 에서 0.67.0 으로 올린다. 훅 명령, 리뷰 명령 스크립트 `run_review.py`, 리뷰어의 판정 파일 규칙,
  테스트의 UTF-8 읽기가 들어간다.
- evonest 를 1.2.0 에서 1.2.1 로 올린다. Windows 로캘 고침 다섯 가지와 훅 명령이 들어간다.

### Excluded

- 코드와 테스트는 고치지 않는다.
- Windows 기기에서 새 버전을 받는 것은 Windows 세션이 확인한다.

## Risks

- Stage 0.67.0 부터 이 저장소의 리뷰 명령이 `run_review.py` 로 실행된다. 맥북에서 이 명령으로 실제 카드를
  닫아 본 적이 없다. 이 카드는 리뷰가 필요 없어서 이 카드를 닫을 때도 실행되지 않는다.

## Success criteria

- Stage 의 두 매니페스트와 변경 기록이 0.67.0 하나를 말한다
- evonest 의 pyproject.toml, uv.lock, 두 매니페스트, 변경 기록이 1.2.1 하나를 말한다
- 릴리스 커밋이 원격 main 에 올라가 다른 프로젝트가 받을 수 있다
- claude plugin list 가 stage 를 0.67.0 으로 읽는다

## Next action

릴리스 커밋 두 개를 PR 로 올리고, 머지한 뒤 `claude plugin list` 로 버전을 확인하고 닫는다.

## Related truth

- 릴리스 절차: 루트 `CLAUDE.md` 의 `Plugin Changes`, `evonest/CLAUDE.md` 의 `Version Management`.
- 들어가는 고침의 카드: W-00000354, W-00000356, W-00000357, W-00000358, W-00000359.

## Progress

- 사용자가 2026-11-20 에 "네, 릴리스" 라고 했다.
- Stage 는 올리는 폭을 minor 로 골랐다. 고침만 있는 것이 아니라 새 스크립트 `run_review.py` 와 설정 문서의
  새 명령 형태가 들어가기 때문이다. `release_plugin.py stage --bump minor` 로 올렸다.
- evonest 는 고침만 있어서 patch 로 골랐다. `pyproject.toml` 을 고치고 `uv lock` 을 실행했다.

## Verification

- PR #73 을 머지했다. 원격 main 은 `eac40dbb` 다. 머지하기 전에 CI 검사 24개가 통과했다.
- 원격 main 의 Stage 두 매니페스트는 `"version": "0.67.0"` 이고, 변경 기록의 맨 위 릴리스는
  `## 0.67.0 — 2026-11-20` 이다.
- 원격 main 의 evonest `pyproject.toml`, `uv.lock`, 두 매니페스트는 1.2.1 이고, 변경 기록의 맨 위 릴리스는
  `## [1.2.1] — 2026-11-20` 이다. `uv run python -c "import evonest; print(evonest.__version__)"` 는 1.2.1 을 냈다.
- 릴리스 커밋을 만들기 전에 맥북에서 evonest 테스트 441개, `ruff check`, `mypy`, Stage 훅 테스트 450개가 통과했다.
- 맥북의 `claude plugin list`: `stage@noory-ai`, Version 0.67.0, Read from
  `/Users/woogis/Workspace/repo/noory-ai/stage`, enabled.
- 성공 기준 하나를 고쳤다. 처음에는 `claude plugin list` 가 evonest 도 1.2.1 로 읽는다고 적었는데, 이 맥북에는
  evonest 플러그인이 설치되어 있지 않아 목록에 나오지 않는다. 등록하기 전에 확인하지 않고 적은 기준이다.
  evonest 가 설치된 기기에서 1.2.1 로 읽히는지는 확인하지 않았다.
- Windows 기기에서 새 버전을 받는 것은 확인하지 않았다.


### Executed at close — 2026-11-20

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
Ran 450 tests in 6.089s

OK
```

## Retrospective


## Promotion decision

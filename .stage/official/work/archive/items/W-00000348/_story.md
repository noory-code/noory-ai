---
id: W-00000348
title: rag 플러그인에 개발을 멈췄다고 표시하기
kind: documentation
venue: claude
milestone:
autonomous: false
acceptance:
  - "python3 stage/scripts/audit_stage.py --project-root ."
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000348
promotion: not_applicable
review: not_required
scope: rag/README.md, rag/CHANGELOG.md, README.md, .claude-plugin/marketplace.json, .agents/plugins/marketplace.json
promotes:
decision_refs:
---

# W-00000348 rag 플러그인에 개발을 멈췄다고 표시하기

## Purpose

rag 플러그인을 보는 사람이 개발이 멈췄다는 것과 그 이유를 바로 알게 한다.

## Actions

이 스토리는 문서 몇 줄만 바꾸므로 따로 나눈 액션이 없다.

## User value

rag 를 설치하려는 사람이 앞으로 기능이 더해지지 않는다는 것을 먼저 알고 고를 수 있다. 저장소 주인은
쓰지 않는 플러그인을 계속 고쳐야 한다는 부담을 내려놓는다.

## Scope

### Included

- `rag/README.md` 맨 위에 개발을 멈췄다는 안내와 이유를 적는다.
- `rag/CHANGELOG.md` 의 `## Unreleased` 에 같은 내용을 적는다.
- 루트 `README.md` 의 RAG 절에 같은 내용을 적는다.
- 마켓플레이스 파일의 rag 설명 앞에 개발을 멈췄다고 적는다.

### Excluded

- 코드를 지우지 않는다.
- 릴리스하지 않고 플러그인 매니페스트도 바꾸지 않는다.
- 마켓플레이스에서 rag 를 빼지 않는다. 사용자가 "표시만" 하기로 정했다(2026-11-17).

## Risks

- 표시가 한 곳이라도 빠지면 그곳을 본 사람은 아직 개발 중인 플러그인으로 안다.

## Success criteria

- rag/README.md, 루트 README.md 의 RAG 절, 두 마켓플레이스 파일의 rag 설명 어디를 봐도 개발이 멈췄다는 것이 보인다.
- 코드를 지우거나 릴리스하지 않아서 이미 설치한 사람은 그대로 쓸 수 있다.

## Next action

닫는다.

## Related truth

- P-00000005(목적별 RAG 제안)는 사용자가 거둬서 rejected 로 닫혔다(PR #56).
- 사용자 결정(2026-11-17): "rag 플러그인은 개발 멈춥시다", 이어서 "네, 표시만".

## Progress

- 커밋 `743f6021`: rag/README.md, rag/CHANGELOG.md, 루트 README.md, `.claude-plugin/marketplace.json` 에 개발을 멈췄다고 적었다.
- 등록할 때 `--scope` 를 여러 번 줬더니 마지막 값만 카드에 남았다. 이 CLI 는 쉼표로 이은 값 하나를 받는다. 카드의 scope 줄을 손으로 고쳤다.

## Verification

- `python3 -m unittest discover -s tests -q`: 7개 통과. 마켓플레이스 파일을 읽는 저장소 계약 테스트다.
- `python3 -m unittest discover -s plainly/tests -q`: 통과.
- `python3 -m json.tool .claude-plugin/marketplace.json`: JSON 이 깨지지 않았다.
- `python3 stage/scripts/audit_stage.py --project-root .`: errors=0.
- 첫째 기준에서 어긋난 점: Codex 마켓플레이스 파일(`.agents/plugins/marketplace.json`)의 rag 항목에는 설명 칸이 없다. 이름, 경로, 설치 정책만 있다. Codex 목록에 보이는 설명은 `rag/.codex-plugin/plugin.json` 에서 오는데, 그 파일은 릴리스해야 사용자에게 닿는다. 이 카드는 릴리스하지 않으므로 Codex 목록에는 멈춤 표시가 없다. 대신 Codex 사용자도 보는 rag/README.md 와 루트 README.md 에는 표시가 있다.

### Executed at close — 2026-11-17

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

$ python3 -m unittest discover -s tests -q
[exit 0]
----------------------------------------------------------------------
Ran 7 tests in 0.001s

OK

$ python3 -m unittest discover -s plainly/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 22 tests in 0.003s

OK
```

## Retrospective

R-00000348 에 적었다.

## Promotion decision

not_applicable. 공식 기록으로 올릴 결정이 없다.
